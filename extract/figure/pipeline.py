from extract import data
from extract.data.pipeline import get_scatter_district_title, get_title_district_bar, get_title_scatter_reporting_country
from ..data.transform import (
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
        "title": "The number of women attending their first ANC visit in {} in {} decreased by {} from the month before",
        "title_data": "district",
    },
    {
        "type": "bar",
        "transform": bar_district_plot,
        "color": {"district": "rgb(42, 87, 131)"},
        "args": {"bar_mode": "overlay"},
        "title": get_title_district_bar, 
       # "Together, {} and {} contribute to {} of all women attending their first ANC visit in September 2020 in {}",
        "title_data": "district",
    },
    {
        "type": "bar",
        "transform": scatter_reporting_district_plot,
        "color": {
            "Reported a positive number": "rgb(42, 87, 131)",
            "Did not report a positive number": "rgb(247, 190, 178)",
            "Did not report on their 105:1 form": "rgb(211, 41, 61)",
        },
        "args": {"bar_mode": "stack"},
        "title": get_title_scatter_reporting_country, #"Of the {} health facilities in {}, {} health facilities reported with a number different from zero for the number of women attending their first ANC visit in {}",
        "title_data": "district",
    },
]
