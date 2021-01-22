import calendar
import json
import os
from email.message import EmailMessage
from email.utils import make_msgid

import pandas as pd
from dateutil.relativedelta import relativedelta


class EmailTemplateParser:
    """
    Fetches elements of an email together and inserts into the template to create the full email

    """

    def __init__(self, data_folder, email_template, config):
        self.folder = data_folder
        self.template = email_template
        self.config = config
        self.payload = {}

    def get_parsed_message(self, filters):
        """
        Gets body from the email_template and inserts items (changing elements) in it.

        """
        message = EmailMessage()
        parsed_message = []
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
        """
        Defines payload to append images

        """
        for cid, fname in self.payload.items():
            with open(fname, "rb") as f:
                message.get_payload()[0].add_related(
                    f.read(), maintype="image", subtype="png", cid=cid
                )

        return message

    def get_parsed_subject(self, filters):
        """
        The function appends subject from email_template to the email
        """
        return self.parse_item(self.template.get("subject"), filters)

    ###########
    # PARSERS #
    ###########

    def parse_item(self, item, filters):
        """
        Finds items by keywords in the template and replaces them with the parsed objects

        """
        if "%date%" in item:
            item = self.__parse_date(item, filters)
        elif "%image" in item:
            item = self.__parse_image(item, filters)
        elif "%district%" in item:
            item = self.__parse_district(item, filters)
        elif "%title" in item:
            item = self.__parse_image_title(item, filters)
        elif "%recipients_name%" in item:
            item = self.__parse_recipients_name(item, filters)
        elif "%following_reporting_date%" in item:
            # it parses also the date of the next report's
            item = self.__parse_following_date(item, filters)
        else:
            item = item
        return item

    def __parse_date(self, item, filters):
        """
        Finds all mentions of %date% in the template and replaces with the date from config.json

        """
        date = self.config.get("date")
        year = date[:4]
        month = date[-2:]
        month = calendar.month_name[int(month)]
        # Current date is below:
        date = f"{month} {year}"
        # Date of the data extraction, relativedelta(day=31) assigns the last day of the month:
        extraction_date = pd.to_datetime(date) + relativedelta(day=31)
        extraction_date = extraction_date.strftime("%d %B, %Y")
        # Due to presence of multiple values to replace in one line or string, the chained .replace() is required
        item = (
            item.replace("%district%", filters.get("district"))
            .replace("%date%", date)
            .replace("%extraction_date%", extraction_date)
        )

        return item

    def __parse_following_date(self, item, filters):
        """
        Replaces %following_reporting_date% and %future_report_date% with the date of the next report and the date of the next email dissemination respectively.
        """
        date = self.config.get("date")
        following_date = pd.to_datetime(date, format="%Y%m")
        following_date = following_date + relativedelta(months=1)
        future_report_month = following_date + relativedelta(months=2)
        following_date = following_date.strftime("%B %Y")
        future_report_month = future_report_month.strftime("%B %Y")
        item = item.replace("%following_reporting_date%", following_date).replace(
            "%future_report_date%", future_report_month
        )

        return item

    def __parse_image(self, item, filters, mime_type=True):
        """
        Gets already existing pictures from data/viz and inserts into emails. Parses by %image as a keyword in the template.
        The name of the vizualization is of the predifined form in the template (%image.INDICATOR'S NAME.figure_1%).
        In case of deviating formatting, the figure won't be attached and the error message pops up.

        """
        try:
            _, indicator, image_file_name = item.split("%")[1].split(".")
        except ValueError as e:
            print(e)
            print(
                f"Image tag {item} in email template does not contain enough parameters! Please use %image.<indicator>.<figure_number>%"
            )
            return None

        image_cid = make_msgid()
        image_html = f'<img src="cid:{image_cid[1:-1]}">'
        item = item.replace(f"%image.{indicator}.{image_file_name}%", image_html)
        # filename is based on district
        district = filters.get("district")
        fname = f"{self.folder}/{district}/{self.config.get('date')}/{indicator}/{image_file_name}.png"
        if not os.path.isfile(fname):
            return '<p align="center">Due to the lack of data on this indicator in the reporting month, no visualization is available </p>'
        self.payload[image_cid] = fname

        return item

    def __parse_image_title(self, item, filters):
        """
        Gets titles from titles.json in data/viz and inserts into emails as captions. Parses by %title as a keyword in the template.
        The name of the vizualization is of the predifined form in the template (%title.INDICATOR'S NAME.figure_1%).
        In case of deviating formatting, the figure won't be attached and the error message pops up.

        """

        try:
            _, indicator, figure = item.split("%")[1].split(".")
        except ValueError as e:
            print(e)
            print(
                f"Image tag {item} in email template does not contain engought parameters! Please use %title.<indicator>.<figure_number>%"
            )
            return None
        # filename is based on district
        district = filters.get("district")
        fname = f"{self.folder}/{district}/{self.config.get('date')}/{indicator}/titles.json"
        with open(fname, "r") as f:
            title = json.load(f).get(figure, f"No data for {indicator}")
        item = item.replace(f"%title.{indicator}.{figure}%", title or "")

        return item

    def __parse_district(self, item, filters):
        """
        Searches %district% keyword in the template and replaces it with the district defined in email_recipients.json

        """
        item = item.replace("%district%", filters.get("district"))
        return item

    def __parse_recipients_name(self, item, filters):
        """
        Searches %recipients_name% keyword in the template and replaces it with the recipient's name defined in email_recipients.json for each district.

        """
        # chained replace is necessary because the names are in one line in the email template
        item = item.replace(
            "%recipients_name%", filters.get("recipients_name")
        ).replace("%biostatistician_name%", filters.get("biostatistician_name"))
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
        self.smtp.sendmail(self.send_from, self.send_to, self.message.as_string())
