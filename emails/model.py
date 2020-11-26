from extract.data import transform
import config
import json
import calendar

from email import encoders
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import smtplib

from email.message import EmailMessage

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

    def get_parsed_message(self, filters):
        parsed_message = MIMEMultipart()
        for item in self.template.get("body"):
            msg = self.parse_item(item, filters)
            if msg:
                parsed_message.attach(msg)

            # !TODO all parsing cases
        return parsed_message

    def get_parsed_subject(self, filters):
        return self.parse_item(self.template.get("subject"), filters, mime_type=False)

    ###########
    # PARSERS #
    ###########

    def parse_item(self, item, filters, mime_type=True):
        if "%date%" in item:
            item = self.__parse_date(item, filters, mime_type)

        elif "%image" in item:
            item = self.__parse_image(item, filters, True)

        elif "%district%" in item:
            item = self.__parse_district(item, filters, mime_type)
        elif "%title" in item:
            item = self.__parse_image_title(item, filters, mime_type)
        else:
            item = MIMEText(item)

        return item

    def __parse_date(self, item, filters, mime_type=True):

        date = self.config.get("date")
        year = date[:4]
        month = date[-2:]
        month = calendar.month_abbr[int(month)]
        date = f"{month} {year}"

        item = item.replace("%date%", date)
        if mime_type:
            item = MIMEText(item)
        return item

    def __parse_image(self, item, filters, mime_type=True):
        try:
            _, indicator, image_file_name = item.split("%")[1].split(".")
        except ValueError as e:
            print(e)
            print(
                "Image tag in email template does not contain engought parameters! Please use %image.<indicator>.<figure_number>%"
            )
            return None
        # filename is based on district
        district = filters.get("district")
        fname = f"{self.folder}/{district}/{self.config.get('date')}/{indicator}/{image_file_name}.png"
        with open(fname, "rb") as f:
            item = f.read()
        if mime_type:
            item = MIMEImage(item)
        return item

    def __parse_image_title(self, item, filters, mime_type=True):
        try:
            _, indicator, figure = item.split("%")[1].split(".")
        except ValueError as e:
            print(e)
            print(
                "Image tag in email template does not contain engought parameters! Please use %image.<indicator>.<figure_number>%"
            )
            return None
        # filename is based on district
        district = filters.get("district")
        fname = f"{self.folder}/{district}/{self.config.get('date')}/{indicator}/titles.json"
        with open(fname, "r") as f:
            title = json.load(f).get(figure)
        item = item.replace(f"%title.{indicator}.{figure}%", title)
        if mime_type:
            item = MIMEText(item)
        return item

    def __parse_district(self, item, filters, mime_type=True):
        item = item.replace("%district%", filters.get("district"))
        if mime_type:
            item = MIMEText(item)
        return item


class Email:
    def __init__(self, smtp, send_to, send_from, message):
        self.smtp = smtp
        self.send_to = send_to
        self.send_from = send_from
        self.message = message

    def set_subject(self, subject):
        self.message["Subject"] = subject

    def send(self):
        print(self.message)
        # self.smtp.sendmail(self.send_from, self.send_to, self.message)


# parser = EmailTemplateParser(template, data_folder)
# smtp_server = smtplib.SMTP("smtp-mail.outlook.com", 587)
# smtp_server.starttls()
# smtp_server.login('email', ' pass')
# smtp_server.quit()

# from district in districts:
#     email = Email(smtp, to, from)
#     email.set_subject(config.get("date"))
#     email.attach_message(parser.get_parsed_message(district)
#     email.send()
