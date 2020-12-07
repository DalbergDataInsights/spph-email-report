import calendar

import os
import smtplib
import ssl
from datetime import datetime, timedelta

from six import get_function_closure

# from dateutil.relativedelta import relativedelta

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
    # get the date
    target_date = datetime.strptime(config.get("date"), "%Y%m")
    print(f"Launching figure generation for {target_date}")
    reference_date = (target_date - timedelta(days=1)).replace(day=1)

    # for each district
    # TODO separate district, date and indicator filter
    # TODO filter by date
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
    # get the date
    target_date = datetime.strptime(config.get("date"), "%Y%m")
    print(f"Launching figure generation for {target_date}")
    reference_date = target_date.replace(year=target_date.year - 1)

    db.filter_by_policy("Correct outliers - using standard deviation")

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
        extract.run(db, controls, figure_pipeline, folder="national")


def run_emails(config, engine, email_template, recipients):

    parser = EmailTemplateParser("data/viz", email_template, config)

    smtp = smtplib.SMTP(host=engine.get("smtp"), port=587)
    smtp.starttls(context=ssl.create_default_context())
    smtp.login(engine.get("username"), engine.get("password"))

    for recipient in recipients:
        print(f"Running email send for {recipient}")
        emails.run(engine.get("username"), recipient, parser, smtp)

    smtp.quit()


def run(pipeline):

    # Configs
    DATABASE_URI = os.environ["DB_URI"]
    config = get_config("config")
    email_template = get_config("email_template")
    recipients = get_config("email_recipients")
    engine = {
        "smtp": os.environ["SMTP"],
        "username": os.environ["USERNAME"],
        "password": os.environ["PASSWORD"],
    }

    for pipe in pipeline:

        if pipe == "extract":
            db = Database(DATABASE_URI)
            pipeline = dataset.pipeline.get()
            db.init_pipeline(pipeline)
            run_extract(config, db, figures.pipeline)

        elif pipe == "email":
            run_emails(config, engine, email_template, recipients)

        elif pipe == "extract_country":
            config = get_config("config_national")
            db = Database(DATABASE_URI)
            pipeline = dataset.national_pipeline.get()
            db.init_pipeline(pipeline)
            run_extract_contry(config, db, figures.national_pipeline)


# TODO make sure that email runs
# TODO separate email html save from send
# TODO email to pdf implementation

if __name__ == "__main__":
    run(["email"])