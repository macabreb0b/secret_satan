import csv
import sys
import random
from collections import namedtuple
from email_client import send_email

class Email(namedtuple('Email', [
    'subject', 
    'body'
])):
    pass

def make_name_to_form_responses_from_reader(reader):
    name_to_form_responses = {}

    header_row = None
    for row in reader:
        if not header_row:
            header_row = row
            continue

        form_responses_for_user = {}
        i = 0
        while i < len(header_row):
            column_name = header_row[i]
            form_responses_for_user[column_name] = row[i]
            i = i + 1

        user_name = form_responses_for_user["My name is..."]
        name_to_form_responses[user_name] = form_responses_for_user

    return name_to_form_responses

def assign_victims(name_to_form_responses):
    all_names = name_to_form_responses.keys()

    did_succeed = False
    while not did_succeed:
        did_succeed = True

        satan_to_victim = {}
        remaining_victims = [name for name in all_names]
        for satan_name in all_names:
            available_victims = [
                victim_name for victim_name in remaining_victims if (
                    # can't be your own victim
                    victim_name != satan_name
                ) and (
                    # filter exclusions
                    name_to_form_responses[victim_name]["My email address is..."].lower() not in name_to_form_responses[satan_name]['Exclusions'].lower()
                )
            ]

            try:
                victim_name = random.choice(available_victims)
                satan_to_victim[satan_name] = victim_name
                remaining_victims.remove(victim_name)
            except IndexError:
                # no valid victims remaining for this satan, we need to restart
                did_succeed = False

        # if this fails we did not succeed
        assert list(satan_to_victim.keys()).sort() == list(satan_to_victim.values()).sort()

    return satan_to_victim


def render_email(victim_form_responses):
    subject_line = f'Your secret satan "victim" is... {victim_form_responses["My name is..."]}'
    
    LINE_BREAK = '\n\n'

    MESSAGE_BODY_COMMON = """Find your "victim's" form responses below. Do your "worst" ;)

Please refer to the game guidelines:

> As a Satan, your job is to get your assignee a "gift". This might be:
> - A nice gift that may or may not be slightly evil. (You're welcome to play like a regular secret santa.)
> - The worst gift they've ever received.
> - Anything else you think is appropriate. You're the Satan.
> 
> Please do your best to postmark your gifts, pull your hijinks, or do whatever else you need to by 1/13/24! (Extending this deadline by a week bc the Automatic Satan Assigner was late.)
> 
> If you're buying a gift please try to stick to like under $50 or whatever.
> 
> Send your gift from "satan" 😈
> 
> All Secret Satans will be revealed in 2024... since we're doing it remotely we'll either do a zoom or have a thread where everyone can share what gift they got, and then guess who their Satan was!
"""

    DISCLAIMER = """PS: if there is no answer for "Check this box if you DON\'T want any funny business:" then that means they did not check this box."""


    form_response_body = LINE_BREAK.join([
        f'{form_response_question}:\n{victim_form_responses[form_response_question]}'
        for form_response_question
        in list(victim_form_responses.keys()) if form_response_question not in ['Timestamp', 'Exclusions']
    ])

    message_body = MESSAGE_BODY_COMMON + LINE_BREAK + form_response_body + LINE_BREAK + DISCLAIMER

    return Email(subject=subject_line, body=message_body)

with open("input.csv") as csv_input:
    my_reader = csv.reader(csv_input)
    name_to_form_responses = make_name_to_form_responses_from_reader(reader=my_reader)

satan_to_victim = assign_victims(name_to_form_responses=name_to_form_responses)

for satan_name in list(satan_to_victim.keys()):
    email = render_email(
        victim_form_responses=name_to_form_responses[satan_to_victim[satan_name]],
    )
    satan_email_address = name_to_form_responses[satan_name]['My email address is...']
    send_email(
        target_email_address=satan_email_address,
        email=email,
    )