import calendar
import json

import os
import smtplib
import ssl
from datetime import date, datetime, timedelta
import pandas as pd

from six import get_function_closure

from dateutil.relativedelta import relativedelta

import emails
import extract
from config import get_config
from dotenv import find_dotenv, load_dotenv
from emails.model import EmailTemplateParser
from extract.model import Database
import dataset
import figures

load_dotenv(find_dotenv())


def run_extract(config, db, figure_pipeline):
    """"
    Function to create figures and captions for districts
    """""
    date = config.get("date")
    if type(date) == int: 
        date= date.strptime("%Y%m")
    elif type(date) == str: 
        if date == "now":
            date = datetime.now() - relativedelta(months=1)
            date = date.strftime("%Y%m")
            with open('config/config.json') as f:
                data = json.load(f)
                data["date"] = date
            with open('config/config.json', 'w') as f:
                json.dump(data, f, indent=2)
        else: 
            print("The date in config.json is defined incorrectly. Possible: \"now\", \"YYYYMM\"")
            exit()
    target_date = datetime.strptime(date, "%Y%m") # gets date from config.json
    print(f"Launching figure generation for {target_date}")
    reference_date = (target_date - timedelta(days=1)).replace(day=1)

    # for each district
    for district in config.get("districts"):
        # TODO filter by district
        print(f"Running the pipeline of figures for {district}")
        for indicator in config.get("indicators"):
            # TODO filter by indicator
            print(f"Running the pipeline of figures for {indicator}")
            controls = {
                "date": target_date.strftime("%Y%m"),
                "district": district,
                "indicator": indicator,
                "target_year": str(target_date.year),
                "target_month": calendar.month_abbr[target_date.month],
                "reference_year": str(reference_date.year),
                "reference_month": calendar.month_abbr[reference_date.month],
            }
            extract.run(db, controls, figure_pipeline)


def run_extract_contry(config, db, figure_pipeline):
    '''
    Function to create figures and captions for the whole country
    '''
    target_date = datetime.strptime(config.get("date"), "%Y%m") # gets date from config.json
    print(f"Launching figure generation for {target_date}")
    reference_date = target_date.replace(year=target_date.year - 1)

    # db.filter_by_policy("Correct outliers - using standard deviation")

    for indicator in config.get("indicators"):
        # TODO filter by indicator
        print(f"Running the pipeline of figures for {indicator}")
        controls = {
            "date": target_date.strftime("%Y%m"),
            "indicator": indicator,
            "target_year": str(target_date.year),
            "target_month": calendar.month_abbr[target_date.month],
            "reference_year": str(reference_date.year),
            "reference_month": calendar.month_abbr[reference_date.month],
            "trends_map_compare_agg": "Compare month of interest to month of reference",
        }
        extract.run(db, controls, figure_pipeline)
 
def save_emails(config, engine, email_template, recipients):
    parser = EmailTemplateParser("data/viz", email_template, config)

    for recipient in recipients:
        print(f"Running email send for {recipient}")
        emails.compose_email(parser, recipient.get("filters"), fname=f'{config.get("date")}.msg', directory=f'./data/emails/{recipient.get("filters").get("district")}/')

                             
def send_emails(config, engine, email_template, recipients):
    '''
    Function to parse a completed template and send it from a later defined email address to recipients
    '''  

    parser = EmailTemplateParser("data/viz", email_template, config)

    smtp = smtplib.SMTP(host=engine.get("smtp"), port=587)
    smtp.starttls(context=ssl.create_default_context())
    smtp.login(engine.get("username"), engine.get("password"))

    for recipient in recipients:
        print(f"Running email send for {recipient}")
        emails.send(smtp, 
                    send_from=engine.get("username"), 
                    send_to=recipient.get("recipients"),
                    fname=f'./data/emails/{recipient.get("filters").get("district")}/{config.get("date")}.msg',
                    subject =parser.get_parsed_subject(recipient.get("filters"))
                    ) 


def save_emails_to_pdf(config, engine, email_template, recipients):
    parser = EmailTemplateParser("data/viz", email_template, config)

    for recipient in recipients:
        emails.to_pdf(msg_fname=f'./data/emails/{recipient.get("filters").get("district")}/{config.get("date")}.msg',
                      pdf_fname=f'./data/emails/{recipient.get("filters").get("district")}/{config.get("date")}.pdf')

def run_next_month(config):
    reporting_date = datetime.strptime(config.get("date"), "%Y%m")
    now = datetime.today().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    if reporting_date==now: 
        print("The figures are up to date, try later")
        
    elif now > reporting_date: 
        print("Changing date...") 
        next_date = reporting_date  + relativedelta(months=1)
        next_date = next_date.strftime("%Y%m")
        
        with open('config/config.json') as f:
            data = json.load(f)
            data["date"] = next_date
        with open('config/config.json', 'w') as f:
            json.dump(data, f, indent=2)   
    else: 
        print("Normalizing date...")
        now = datetime.today().strftime("%Y%m")
        with open('config/config.json') as f:
            data = json.load(f)
            data["date"] = now
        with open('config/config.json', 'w') as f:
            json.dump(data, f, indent=2) 

def run(pipeline):
    '''
    Main function, which calls the functions above using the customised configurations
    '''

    # Configurations: 
    DATABASE_URI = os.environ["DATABASE"] # sets the Database 
    config = get_config("config")
    email_template = get_config("email_template") #sets the template
    recipients = get_config("email_recipients") #sets the recipients
    #sets sender's email incl. credentials 

    engine = {
        "smtp": os.environ["SMTP"],
        "username": os.environ["USERNAME"],
        "password": os.environ["PASSWORD"],
    }


    for pipe in pipeline:

        if pipe == "extract": #creates and prints images for districts' emails
            db = Database(DATABASE_URI) 
            pipeline = dataset.pipeline.get()
            db.init_pipeline(pipeline)
            run_extract(config, db, figures.pipeline)

        elif pipe == "extract_country":
            config = get_config("config_national")
            db = Database(DATABASE_URI)
            pipeline = dataset.national_pipeline.get()
            db.init_pipeline(pipeline)
            run_extract_contry(config, db, figures.national_pipeline)

        elif pipe == "email_create":
            save_emails(config, engine, email_template, recipients)

        elif pipe == "email_send":
            send_emails(config, engine, email_template, recipients)

        elif pipe == "email_to_pdf":
            save_emails_to_pdf(config, engine, email_template, recipients)

        elif pipe == "increment-date":
            run_next_month(config)



if __name__ == "__main__":
    run(["extract"])

