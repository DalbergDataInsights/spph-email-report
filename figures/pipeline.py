# for districts (emails)
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dataset.transform import (
    scatter_district_plot,
    bar_district_plot,
    scatter_reporting_district_plot,
    scatter_country_plot,
)

year_current = datetime.now() - relativedelta(
    months=1
)  # we must take the monthly lag into account, otherwise a problem for December data might occur at the end of January (it's the next year already) if we use datetime.now().year directly.

pipeline = [
    {
        "type": "scatter",  # Set pipeline for the figure_1 (indicator's overview scatter at district level)
        "transform": scatter_district_plot,
        "color": {
            year_current.year - 2: "rgb(185, 221, 241)",
            year_current.year - 1: "rgb(106, 155, 195)",
            year_current.year: "rgb(200, 19, 60)",
        },
        "title": "The total {} in {} in {} <b>{}</b> from the month before",
        "title_args": ["indicator_view", "district", "date", "ratio"],
    },
    {
        "type": "bar",  # Sets pipeline for the figure_2 (individual facilities contribution bar)
        "transform": bar_district_plot,
        "color": {"district": "rgb(42, 87, 131)"},
        "args": {"bar_mode": "overlay"},
        "title": "{} contributes <b>{}</b> to the {} in {} in {}",
        "title_args": [
            "top_facility",
            "top_facility_contribution",
            "indicator_view",
            "date",
            "district",
        ],
    },
    {
        "type": "scatter",  # Sets pipeline for the figure_3 (% reporting scatter)
        "transform": scatter_reporting_district_plot,
        "color": {
            "Percentage of facilities expected to report which reported on their 105-1 form": "rgb(106, 155, 195)",
            "Percentage of reporting facilities that reported a value of one or above for this indicator": "rgb(200, 19, 60)",
        },
        "title": "In {}, in {}, of the <b>{}</b> health facilities expected to report <b>(100%)</b>, only <b>{}</b> <b>({}%)</b> reported one or above for the {}. ",
        "title_args": [
            "district",
            "date",
            "facility_count",
            "facility_count_reported",
            "reporting_positive",
            "indicator_view",
        ],
    },
    {
        "type": "scatter",  # Sets pipeline for the figure_4 (indicator's overview scatter at country level)
        "transform": scatter_country_plot,
        "color": {
            year_current.year - 2: "rgb(185, 221, 241)",
            year_current.year - 1: "rgb(106, 155, 195)",
            year_current.year: "rgb(200, 19, 60)",
        },
        "title": """Across the country, in {} the {} is amounted to <b>{}</b> """,
        "title_args": [
            "date",
            "indicator_view",
            "latest_value",
        ],
    },
]
