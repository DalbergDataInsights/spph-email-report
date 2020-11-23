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
    },
    {
        "type": "bar",
        "transform": bar_district_plot,
        "color": {'district': "rgb(42, 87, 131)"},
        "args": {"bar_mode": "overlay"}
        
    },
    {
        "type": "bar",
        "transform": scatter_reporting_district_plot,
        "color": {
            "Reported a positive number": "rgb(42, 87, 131)",
            "Did not report a positive number": "rgb(247, 190, 178)",
            "Did not report on their 105:1 form": "rgb(211, 41, 61)"},
        "args": {"bar_mode": "stack"}
    },
]
