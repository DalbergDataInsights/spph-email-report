# import geopandas as gpd
# for districts (emails)
from dataset.transform import (
    scatter_district_plot,
    bar_district_plot,
    scatter_reporting_district_plot,
    scatter_country_plot,
)


pipeline = [
    {
        "type": "scatter",  # Sets pipeline for the figure_1 (indicator's overview scatter at district level)
        "transform": scatter_district_plot,
        "color": {
            2018: "rgb(185, 221, 241)",
            2019: "rgb(106, 155, 195)",
            2020: "rgb(200, 19, 60)",
            2021: "rgb(255, 131, 0)",
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
            2018: "rgb(185, 221, 241)",
            2019: "rgb(106, 155, 195)",
            2020: "rgb(200, 19, 60)",
            2021: "rgb(255, 131, 0)",
        },
        "title": """Across the country, in {} the {} is amounted to <b>{}</b> """,
        "title_args": [
            "date",
            "indicator_view",
            "latest_value",
        ],
    },
]
