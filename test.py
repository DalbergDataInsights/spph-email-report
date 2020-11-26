

import smtplib
from config import get_config
from emails.model import EmailTemplateParser, Email


email_template = get_config("email_template")
config = get_config("config")

parser = EmailTemplateParser("data/viz", email_template, config)

recipients = get_config("email_recipients")
engine = get_config("email_engine")

# server = smtplib.SMTP_SSL(host='smtp-mail.outlook.com', 587)
# server.starttls()
# server.ehlo()
# server.login("from_email", "password")

smtp = ""

# TODO
# 1. Finish all parsers
# 1.1 Finish title parses (ratio! etc)
# 2. Figure out smtp
# 3. Translate to HTML

for recipient in recipients:  # main loop
    message = parser.get_parsed_message(recipient.get("filters"))
    email = Email(
        smtp=smtp,
        send_to=recipient.get("recipients"),
        send_from=engine.get("email"),
        message=message,
    )
    email.set_subject(parser.get_parsed_subject(recipient.get("filters")))
    email.send()
    # create EMAIL
    # server.sendmail("from_email"", "target@example.com", msg)

# server.quit()