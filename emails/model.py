import config
import json
import calendar

import os

from email.message import EmailMessage
from email.utils import make_msgid
import mimetypes

# email_message = EmailMessage()

# email_message.set_content(get_content("template")) # !IMPORTANT content has to contain images and shit
# email_message["Subject"] = email_template.get("subject")
# email_message["From"] = engine.get("from")
# email_message["To"] = recipients.get("district")

# smtp = smtplib.SMTP(engine.get("smtp"))
# smtp.send_message(email_message)
# smtp.quit()


class EmailTemplateParser:
    def __init__(self, data_folder, email_template, config):
        self.folder = data_folder
        self.template = email_template
        self.config = config
        self.payload = {}

    def get_parsed_message(self, filters):
        message = EmailMessage()
        parsed_message = []
        payloads = []
        for item in self.template.get("body"):
            msg = self.parse_item(item, filters)
            if msg:
                parsed_message.append(msg)
        message.add_alternative(f"<html><body>{''.join(parsed_message)}<body><html>", subtype="html")
        # add images to payload
        message = self.set_payload(message)
        return message

    def set_payload(self, message):
        
        for cid, fname in self.payload.items():
            with open(fname, "rb") as f:
                message.get_payload()[0].add_related(f.read(),
                                                     maintype="image",
                                                     subtype="png",
                                                     cid=cid)
            
        return message

    def get_parsed_subject(self, filters):
        return self.parse_item(self.template.get("subject"), filters)

    ###########
    # PARSERS #
    ###########

    def parse_item(self, item, filters):
        if "%date%" in item:
            item = self.__parse_date(item)
        elif "%image" in item:
            item = self.__parse_image(item, filters)
        elif "%district%" in item:
            item = self.__parse_district(item, filters)
        elif "%title" in item:
            item = self.__parse_image_title(item, filters)
        else:
            item = item
        return item

    def __parse_date(self, item):

        date = self.config.get("date")
        year = date[:4]
        month = date[-2:]
        month = calendar.month_name[int(month)]
        date = f"{month} {year}"

        item = item.replace("%date%", date)

        return item + "<br>"

    def __parse_image(self, item, filters, mime_type=True):
        try:
            _, indicator, image_file_name = item.split("%")[1].split(".")
        except ValueError as e:
            print(e)
            print(
                f"Image tag {item} in email template does not contain engought parameters! Please use %image.<indicator>.<figure_number>%"
            )
            return None

        image_cid = make_msgid()
        item = f'<img src="cid:{image_cid[1:-1]}">'
        # filename is based on district
        district = filters.get("district")
        fname = f"{self.folder}/{district}/{self.config.get('date')}/{indicator}/{image_file_name}.png"
        self.payload[image_cid] = fname
        return item + "<br>"

    def __parse_image_title(self, item, filters):
        try:
            _, indicator, figure = item.split("%")[1].split(".")
        except ValueError as e:
            print(e)
            print(
                f"Image tag {item} in email template does not contain engought parameters! Please use %image.<indicator>.<figure_number>%"
            )
            return None
        # filename is based on district
        district = filters.get("district")
        fname = f"{self.folder}/{district}/{self.config.get('date')}/{indicator}/titles.json"
        with open(fname, "r") as f:
            title = json.load(f).get(figure)
        item = item.replace(f"%title.{indicator}.{figure}%", title)

        return item + "<br>"

    def __parse_district(self, item, filters):
        item = item.replace("%district%", filters.get("district"))
        return item + "<br>"

class Email:
    def __init__(self, smtp, send_to, send_from, message):
        self.smtp = smtp
        self.send_to = send_to
        self.send_from = send_from
        self.message = message
        # self.message = MIMEMultipart("related")
        # self.message.attach(message)

    def set_subject(self, subject):
        self.message["Subject"] = subject

    def send(self):
        # self.message["From"] = self.send_from
        # self.message["To"] = self.send_to
        self.smtp.sendmail(self.send_from, self.send_to, self.message.as_string())



