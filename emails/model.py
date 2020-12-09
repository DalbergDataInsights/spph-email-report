import config
import json
import calendar

import os

from email.message import EmailMessage
from email.utils import make_msgid
import mimetypes


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
        message.add_alternative(
            '<html><body style="{}">{}<body><html>'.format(
                self.template.get("meta"), "".join(parsed_message)
            ),
            subtype="html",
        )
        # add images to payload
        message = self.set_payload(message)
        return message

    def set_payload(self, message):

        for cid, fname in self.payload.items():
            with open(fname, "rb") as f:
                message.get_payload()[0].add_related(
                    f.read(), maintype="image", subtype="png", cid=cid
                )

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
        elif "%recipients_name%" in item:
            item = self.__parse_recipients_name(item, filters)
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

        return item

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
        image_html = f'<img src="cid:{image_cid[1:-1]}">'
        item = item.replace(f"%image.{indicator}.{image_file_name}%", image_html)
        # filename is based on district
        district = filters.get("district")
        fname = f"{self.folder}/{district}/{self.config.get('date')}/{indicator}/{image_file_name}.png"
        if not os.path.isfile(fname):
            return '<p align="center">Due to the lack of data on this indicator in the reporting month, no visualization of individual facilities\' contribution available </p>'
        self.payload[image_cid] = fname

        return item + "<br style=\"line-height:1px\">"

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
            title = json.load(f).get(figure, f"No data for {indicator}")
        item = item.replace(f"%title.{indicator}.{figure}%", title or "")

        return item + "<br>"

    def __parse_district(self, item, filters):
        item = item.replace(
            "%biostat_name%", filters.get("biostatistician_name")
        ).replace("%district%", filters.get("district"))
        return item

    def __parse_recipients_name(self, item, filters):
        item = item.replace("%recipients_name%", filters.get("recipients_name"))
        return item


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
        self.smtp.sendmail(self.send_from, self.send_to, self.message.as_string())

    def to_html(self, fname):
        pass

    def from_html(self, fname):
        pass

    def to_pdf(self, fname):
        pass
