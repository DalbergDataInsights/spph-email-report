import extract
from dotenv import find_dotenv, load_dotenv
from config import get_config
import os
from extract.model import Database
from datetime import datetime, timedelta
import calendar


load_dotenv(find_dotenv())


def run():

    config = get_config("config")

    # init databast
    # Linter - black !TODO
    DATABASE_URI = os.environ["HEROKU_POSTGRESQL_CYAN_URL"]
    db = Database(DATABASE_URI)

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
            extract.run(db, controls)


run()
