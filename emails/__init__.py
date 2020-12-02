
# 5. Load and send full email to yourself
# 6. celebrate

from emails.model import Email


def run(send_from, recipient, parser, smtp):

    message = parser.get_parsed_message(recipient.get("filters"))
    email = Email(
        smtp=smtp,
        send_to=recipient.get("recipients"),
        send_from=send_from,
        message=message)
    email.set_subject(parser.get_parsed_subject(recipient.get("filters")))
    email.send()
