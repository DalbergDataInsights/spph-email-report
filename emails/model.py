from datetime import datetime
from email import message, policy
import config
import json
import calendar
from dateutil.relativedelta import relativedelta
import pandas as pd

import os

from email.message import EmailMessage
from email.utils import make_msgid
from email.parser import BytesParser
import mimetypes
import weasyprint
from weasyprint import HTML
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from io import BytesIO
import mailparser



class EmailTemplateParser:
    """
    Assembles components into one email 
    
    """
    def __init__(self, data_folder, email_template, config):
        self.folder = data_folder
        self.template = email_template
        self.config = config
        self.payload = {}

    def get_parsed_message(self, filters):
        """
        the function consolidates the template and varying elements (items) along with pictures into one email
        to add pictures set_payload is defined below
        """
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
        """
        The function appends subject from email_template to the email
        """
        return self.parse_item(self.template.get("subject"), filters)

    ###########
    # PARSERS #
    ###########

    def parse_item(self, item, filters):
        """
        It parses items to replace in the template. 
        The function finds an item with the defined names. 
        Example: %date% in the template is replaced with the value, assigned in individual parsing function, see: def __parse_date()
        To change or add an item, add it to the email_template surrounded by % and defiine the replacement value in the individual function 
        and add to the current function
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
        elif "%extraction_month%" in item: 
            # it parses also the date of the next report's publishing 
            item = self.__parse_extraction_month(item, filters) 
        else:
            item = item
        return item

    def __parse_date(self, item, filters):

        date = self.config.get("date")
        year = date[:4]
        month = date[-2:]
        month = calendar.month_name[int(month)]
        #Current date is below: 
        date = f"{month} {year}"
        #Date of the data extraction: 
        extraction_date = pd.to_datetime(date) + relativedelta(months=1)
        extraction_date=extraction_date.strftime("%B")
        #Due to presence of multiple values to replace in one line or string, the chained .replace() is required
        item = item.replace("%district%", filters.get("district")).replace("%date%", date).replace("%extraction_month%", extraction_date) 

        return item

    def __parse_extraction_month(self, item, filters): 
        """
        the function parses varying dates for the email, incl. date of the data extraction from DHIS2 and date of the next report
        """
        date = self.config.get("date")
        extraction_date = pd.to_datetime(date, format='%Y%m') 
        extraction_date = extraction_date + relativedelta(months=1)
        future_report_month= extraction_date + relativedelta(months=2)
        extraction_date=extraction_date.strftime("%B")
        future_report_month=future_report_month.strftime("%B")
        item=item.replace("%extraction_month%",extraction_date).replace("%future_report_month%", future_report_month )   

        return item

    def __parse_image(self, item, filters, mime_type=True):
        """
        The function parses already existing pictures (see: data/viz) and inserts them into emails.
        The name of the vizualization is of the predifined form in the template (<div>%image.INDICATOR'S NAME.figure_1%<div/>), 
        so that it defines the type of the object (%image.), indicator's name (.INDICATOR'S NAME.) and the particular figure, defined by number (.figure1/2/3%).
        In case of deviating formatting, the figure won't be attached and the error message appears on the terminal

        """
        try:
            _, indicator, image_file_name = item.split("%")[1].split(".")
        except ValueError as e:
            print(e)
            print(
                f"Image tag {item} in email template does not contain engough parameters! Please use %image.<indicator>.<figure_number>%"
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
        item = item.replace("%district%", filters.get("district"))
        return item

    def __parse_recipients_name(self, item, filters):
        #chained replace is necessary because the names are in one line in the email template
        item = item.replace("%recipients_name%", filters.get("recipients_name")).replace("%biostatistician_name%", filters.get("biostatistician_name"))
        return item
 

class Email:
    """
    
    You can create Emails from text like that:
        email = Email("This is a long message of an email")
    Tip:
        Use EmailTemplateParser with HTML template to create elaborate HTML emails automatically

    You can also create Emails from earlier create files:
        email = Email.from_file("/path/to/file.msg")

    Once created, you may save the file:
        email.to_file("/path/to/file.html")

    Or send it using Python native smtp profile
        email.send(smtp, from@mail.com, "to@mail.com, anotherto@mail.com")

    """
    def __init__(self, message):
        self.message = message
      

    def set_subject(self, subject):
        self.message["Subject"] = subject

    def send(self, smtp, send_from, send_to):
        smtp.sendmail(send_from, send_to, self.message.as_string())

    def to_file(self, fname, directory="./data/emails/"): # < fname = "./html/message.msg"

        assert len(fname.split("/")) == 1, "Please use directory keyword for directory"

        if not os.path.exists(directory):
            os.makedirs(directory)

        with open(directory + fname, "wb") as f:
            f.write(bytes(self.message))


    @staticmethod
    def from_file(fname):
        with open(fname, "rb") as f:
            message = BytesParser(policy=policy.default).parse(f)
        return Email(message)

    def to_pdf(self, fname, directory="./data/emails/pdf"):

        mail = mailparser.parse_from_file_msg(self.message)

        body = weasyprint.HTML(self.message.as_string())
        with open(fname, "wb") as f:
            f.write(body)

        #"./data/emails/AMURU/202010.msg"
        #html = mail.body
        #html=render_to_string(html)
        #weasyprint.HTML(string=html).write_pdf(directory + fname)


        #html = render_to_string(self.message)
        #result = BytesIO()
        #pdf = pisa.pisaDocument(BytesIO(html.encode("utf-8")), result)
        #if not pdf.err:
            #return result.getvalue()
        #return None    


      