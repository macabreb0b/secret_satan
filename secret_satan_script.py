import csv
import sys
import random
from collections import namedtuple
import datetime

NAME_COLUMN_LABEL = "My name is..."
EMAIL_COLUMN_LABEL = "My email address is..."
EXCLUSIONS_COLUMN_LABEL = "Exclusions"
PREVIOUS_VICTIMS_COLUMN_LABEL = "Previous victims"
TIMESTAMP_COLUMN_LABEL = "Timestamp"

COLUMNS_TO_EXCLUDE_FROM_EMAIL = [
    TIMESTAMP_COLUMN_LABEL, 
    EXCLUSIONS_COLUMN_LABEL, 
    PREVIOUS_VICTIMS_COLUMN_LABEL,
]

class Email(namedtuple('Email', [
    'subject', 
    'body'
])):
    pass

def make_name_to_form_responses_from_reader(reader):
    """
    take CSV reader input and generate dict(name, dict(form question, form response))
    """

    name_to_form_responses = {}

    header_row = None
    for row in reader:
        # get header row
        if not header_row:
            header_row = row
            # this script requires that columns "Exclusions" and "Previous victims" have been added pre-execution
            assert EXCLUSIONS_COLUMN_LABEL in header_row
            assert PREVIOUS_VICTIMS_COLUMN_LABEL in header_row
            continue

        form_responses_for_user = {}
        i = 0
        while i < len(header_row):
            column_name = header_row[i]
            # be sure to strip() to avoid bugs with keying on a name/email with trailing spaces
            form_responses_for_user[column_name] = row[i].strip() 
            i = i + 1

        user_name = form_responses_for_user[NAME_COLUMN_LABEL]

        if user_name in name_to_form_responses:
            # TODO - should probably just key on email, which will always be unique
            raise "Names are not unique"

        name_to_form_responses[user_name] = form_responses_for_user

    return name_to_form_responses

def assign_victims(name_to_form_responses):
    """
    generate dict(satan_name, victim_name)
    """

    all_names = name_to_form_responses.keys()

    did_succeed = False
    tries = 0
    while not did_succeed:
        tries += 1
        did_succeed = True

        satan_to_victim = {}
        remaining_victims = [name for name in all_names]
        for satan_name in all_names:
            satan_form_responses = name_to_form_responses[satan_name]

            available_victims = [
                victim_name for victim_name in remaining_victims if (
                    # can't be your own victim
                    victim_name != satan_name
                ) and (
                    # filter exclusions
                    victim_name.lower() not in satan_form_responses[EXCLUSIONS_COLUMN_LABEL].lower()
                ) and (
                    # filter previous victims
                    victim_name.lower() not in satan_form_responses[PREVIOUS_VICTIMS_COLUMN_LABEL].lower()
                )
            ]

            try:
                victim_name = random.choice(available_victims)
                satan_to_victim[satan_name] = victim_name

                remaining_victims.remove(victim_name)
            except IndexError:
                # no valid victims remaining for this satan, we need to restart
                did_succeed = False

        assert tries < 1000, 'could not generate valid assignment set in 1000 tries'

    # just some checks
    assert list(satan_to_victim.keys()).sort() == list(satan_to_victim.values()).sort(), 'satan and victim lists must match'
    assert len(satan_to_victim) == len(name_to_form_responses), 'must assign all names'

    return satan_to_victim


def render_email_body(victim_form_responses):
    """
    given the victim's form data, generate formatted email body text
    """

    LINE_BREAK = '\n\n'

    MESSAGE_BODY_COMMON = """Find your "victim's" form responses below. Do your "worst" ;)

Please refer to the game guidelines:

> As a Satan, your job is to get your assignee a "gift". This might be:
> - A nice gift that may or may not be slightly evil. (You're welcome to play like a regular secret santa.)
> - The worst gift they've ever received.
> - Anything else you think is appropriate. You're the Satan!
> 
> Please do your best to postmark your gifts, pull your hijinks, or do whatever else you need to by 1/15/25!
> 
> If you're buying stuff please try to stick to like under $50 or whatever.
> 
> Send your gift from "satan" 😈
> 
> All Secret Satans will be revealed in 2025... since we're doing it remotely we'll start a thread where everyone can share what gift they got, and then guess who their Satan was!
"""

    DISCLAIMER = """
P.S. If you don't know your "victim" well, take this as an opportunity to ask around or stalk them to get to know them better!
P.P.S. Remember the game runner does not know the assignments, so take care not to reveal secret information...
"""

    form_response_body = LINE_BREAK.join([
        f'{form_response_question}:\n{victim_form_responses[form_response_question]}'
        for form_response_question
        in list(victim_form_responses.keys()) if form_response_question not in COLUMNS_TO_EXCLUDE_FROM_EMAIL
    ])

    message_body = MESSAGE_BODY_COMMON + LINE_BREAK + form_response_body + LINE_BREAK + DISCLAIMER

    return message_body


def write_assignments_to_file(satan_to_victim):
    """
    write satan / victim assignments to a file to make it easier to check later on
    """

    current_timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    with open(f'DO_NOT_OPEN_TIL_XMAS_{current_timestamp}_assignments.csv', 'w') as csvfile:
        SATAN_NAME_LABEL = 'satan_name'
        VICTIM_NAME_LABEL = 'victim_name'
        fieldnames = [SATAN_NAME_LABEL, VICTIM_NAME_LABEL]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for satan_name in list(satan_to_victim.keys()):
            row_as_dict = {
                SATAN_NAME_LABEL: satan_name,
                VICTIM_NAME_LABEL: satan_to_victim[satan_name],
            }
            writer.writerow(row_as_dict)

def make_emails(satan_to_victim, name_to_form_responses):
    """
    generate list of Email objects
    """

    emails = []
    for satan_name in list(satan_to_victim.keys()):
        victim_form_responses = name_to_form_responses[satan_to_victim[satan_name]]
        emails.append(
            Email(
                to_address=name_to_form_responses[satan_name][EMAIL_COLUMN_LABEL],
                body=render_email_body(
                    victim_form_responses=victim_form_responses,
                ),
                subject=f'Your secret satan "victim" is... {victim_form_responses[NAME_COLUMN_LABEL]}'
            ),
        )

    return emails

# ---- BEGIN SCRIPT ACTIONS ----

CSV_INPUT_FILE_NAME = "some-file-name" # replace with csv input file name

SEND_EMAILS = False # ONLY SET TO TRUE WHEN READY TO LAUNCH
if SEND_EMAILS:
    # conditionally import this file because it launches the Google App
    from email_client import send_email

with open(CSV_INPUT_FILE_NAME) as csv_input:
    my_reader = csv.reader(csv_input)
    name_to_form_responses = make_name_to_form_responses_from_reader(reader=my_reader)

satan_to_victim = assign_victims(name_to_form_responses=name_to_form_responses)

# store responses for later
write_assignments_to_file(satan_to_victim=satan_to_victim)

for email in make_emails(
    satan_to_victim=satan_to_victim, 
    name_to_form_responses=name_to_form_responses,
):
    if SEND_EMAILS:
        send_email(
            email=email,
        )
    else:
        # we're in test mode, print to console.
        print(email.to_address)
        print(email.subject)
        print(email.body)