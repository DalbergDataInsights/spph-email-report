import calendar
import json
import os
import smtplib
import ssl
from dateutil.relativedelta import relativedelta
from dotenv import find_dotenv, load_dotenv
import dataset
import emails
import extract
import figures
from config import get_config
from emails.model import EmailTemplateParser
from extract.model import Database
from datetime import datetime, timedelta
import os

# The change of directory (chdir) below is necessary for cron job (scheduler)
cwd = os.getcwd()
script_dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_dir)

load_dotenv(find_dotenv())


def run_extract(config, db, figure_pipeline):
    """
    Fetches the date from the config. file, sets control variables, initiates run function (extract/__init__.py), which results in the visualisations as output
    """
    date = config.get("date")
    if len(date) == 6:
        target_date = datetime.strptime(date, "%Y%m")
    elif len(date) != 6:
        if date == "now":
            date = datetime.now() - relativedelta(months=1)
            target_date = date.strftime("%Y%m")
            with open("config/config.json") as f:
                data = json.load(f)
                data["date"] = target_date
            with open("config/config.json", "w") as f:
                json.dump(data, f, indent=2)
        else:
            print(
                'The date in config.json is defined incorrectly. Possible: "now", "YYYYMM"'
            )
            exit()
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


def run_emails(config, engine, email_template, recipients):
    """
    Receives a complete template from  emails/model.py and send it from the defined email address to the recipients from email_recipients.json
    """
    parser = EmailTemplateParser("data/viz", email_template, config)

    smtp = smtplib.SMTP(host=engine.get("smtp"), port=587)
    smtp.starttls(context=ssl.create_default_context())
    smtp.login(engine.get("username"), engine.get("password"))

    for recipient in recipients:
        print(f"Running email send for {recipient}")
        emails.run(engine.get("username"), recipient, parser, smtp)

    smtp.quit()


def run_next_month(config):
    """
    Fetches the date from config and increments one month
    """
    reporting_date = datetime.strptime(config.get("date"), "%Y%m")
    now = datetime.today().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    if reporting_date == now:
        print("The figures are up to date, try later")

    elif now > reporting_date:
        print("Changing date...")
        next_date = reporting_date + relativedelta(months=1)
        next_date = next_date.strftime("%Y%m")

        with open("config/config.json") as f:
            data = json.load(f)
            data["date"] = next_date
        with open("config/config.json", "w") as f:
            json.dump(data, f, indent=2)
    else:
        print("Normalizing date...")
        now = datetime.today().strftime("%Y%m")
        with open("config/config.json") as f:
            data = json.load(f)
            data["date"] = now
        with open("config/config.json", "w") as f:
            json.dump(data, f, indent=2)


def run(pipeline):
    """
    Calls the run functions above, adds configurations to the existing run functions from the .env file.
    Each pipe is for different functions:
    "extract" - creates and prints the visualisations;
    "email" - composes and sends emails;
    "increment-date" - increments one month.
    """

    # Configurations:
    DATABASE_URI = os.environ["DATABASE"]  # sets the Database
    config = get_config("config")
    email_template = get_config("email_template")  # sets the template
    recipients = get_config("email_recipients")  # sets the recipients
    # sets sender's email incl. credentials

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

        elif pipe == "increment-date":
            run_next_month(config)


if __name__ == "__main__":
    run(["extract", "email", "increment-date"])
