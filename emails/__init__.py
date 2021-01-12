
# 5. Load and send full email to yourself
# 6. celebrate

from emails.model import Email


def run(send_from, send_to, recipient, parser, smtp):

    message = parser.get_parsed_message(recipient.get("filters"))
    email = Email(message)
    email.set_subject(parser.get_parsed_subject(recipient.get("filters")))
    email.send(smtp, send_from, send_to)


def compose_email(parser, filters, **kwargs):
    message = parser.get_parsed_message(filters)
    email = Email(message)
    email.to_file(**kwargs)


def send(smtp, send_from, send_to, fname, subject="Automated email"):
    email = Email.from_file(fname)
    email.set_subject(subject)
    email.send(smtp, send_from, send_to)


def to_pdf(msg_fname, pdf_fname):
    email = Email.from_file(msg_fname)
    email.to_pdf(pdf_fname)
