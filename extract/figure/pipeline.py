from extract import dataset
from ..dataset.transform import (
    scatter_district_plot,
    bar_district_plot,
    scatter_reporting_district_plot,
)



pipeline = [
    {
        "type": "scatter",
        "transform": scatter_district_plot,
        "color": {
            2018: "rgb(185, 221, 241)",
            2019: "rgb(106, 155, 195)",
            2020: "rgb(200, 19, 60)",
        },
        "title": "The total {} in {} in {} <b>{} </b> from the month before",
        "title_args": ["indicator_view", "district", "date", "ratio"]
    },
    {
        "type": "bar",
        "transform": bar_district_plot,
        "color": {"district": "rgb(42, 87, 131)"},
        "args": {"bar_mode": "overlay"},
        "title": "{} contributes <b>{}</b> of {} in {} in {}",
        "title_args": ["top_facility", "top_facility_contribution", "indicator_view", "date", "district"]
    },
    {
        "type": "bar",
        "transform": scatter_reporting_district_plot,
        "color": {
            "Reported one or above for selected indicator": "rgb(42, 87, 131)",
            "Reported null or zero for selected indicator": "rgb(247, 190, 178)",
            "Did not report on their 105:1 form": "rgb(211, 41, 61)",
        },
        "args": {"bar_mode": "stack"},
        "title": "Of the {} health facilities expected to report in {}, <b>{} health facilities</b> reported with a number different from zero for the {} in {}",
        "title_args": ["facility_count", "district", "facility_count_reported", "indicator_view", "date"]
    }
]
