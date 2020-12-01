

import smtplib
import ssl
from config import get_config
from emails.model import EmailTemplateParser, Email


email_template = get_config("email_template")
config = get_config("config")

parser = EmailTemplateParser("data/viz", email_template, config)

recipients = get_config("email_recipients")
engine = get_config("email_engine")


# smtp = ''
smtp = smtplib.SMTP(host=engine.get("smtp"), port=587)
smtp.starttls(context=ssl.create_default_context())
smtp.login("valeriya.cherepova@dalberg.com", "Flowers253311")


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
    

smtp.quit()