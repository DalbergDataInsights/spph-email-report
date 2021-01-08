import dataset
#for districts (emails)
from dataset.transform import (
    scatter_district_plot,
    bar_district_plot,
    scatter_reporting_district_plot,
    scatter_country_plot,
)
#for country (monthly report)
from dataset.national_transform import (
    bar_country_compare_plot,
    scatter_country_plot,
    map_country_compare_plot,
    reporting_count_transform,
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
        "title": "The total {} in {} in {} <b>{}</b> from the month before",
        "title_args": ["indicator_view", "district", "date", "ratio"],
    },
    {
        "type": "bar",
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
        "type": "bar",
        "transform": scatter_reporting_district_plot,
        "color": {
            "Reported one or above for selected indicator": "rgb(42, 87, 131)",
            "Reported null or zero for selected indicator": "rgb(247, 190, 178)",
            "Did not report on their 105:1 form": "rgb(211, 41, 61)",
        },
        "args": {"bar_mode": "stack"},
        # Of the 36 health facilities in Amuru, 16 health facilities reported with a number different from zero for the number of women attending their first ANC visit in September 2020
        "title": "Of the {} health facilities expected to report in {}, <b>{} health facilities</b> reported with a number different from zero for the {} in {}",
        "title_args": [
            "facility_count",
            "district",
            "facility_count_reported",
            "indicator_view",
            "date",
        ],
    },
    {
        "type": "scatter",
        "transform": scatter_country_plot,
        "color": {
            2018: "rgb(185, 221, 241)",
            2019: "rgb(106, 155, 195)",
            2020: "rgb(200, 19, 60)",
        },
        "title": """Across the country, in {} the {} is amounted to <b>{}</b> """,
        "title_args": [
            "date",
            "indicator_view",
            "latest_value",
            
        ],
    }
]

#import geopandas as gpd

national_pipeline = [
    {
        "type": "scatter",
        "transform": scatter_country_plot,
        "color": {
            2018: "rgb(185, 221, 241)",
            2019: "rgb(106, 155, 195)",
            2020: "rgb(200, 19, 60)",
        },
        "title": """Across the country, the {} {} between {} and {} """,
        "title_args": [
            "indicator_view",
            "ratio_year",
            "date_reference",
            "date_national",
        ],
    },
    {
        "type": "bar",
        "transform": bar_country_compare_plot,
        "color": {
            "Top/Bottom 10": "rgb(211, 41, 61)",
        },
        "args": {"bar_mode": "overlay"},
        "title": "The {} {} between {} and {}",
        "title_args": [
            "indicator_view",
            "ratio_year",
            "date_reference",
            "date_national",
        ],
    },
    {
        "type": "map",
        "transform": map_country_compare_plot,
        "color": {
            "Change between reference and target date": [
                "#b00d3b",
                "#f77665",
                "#dedad9",
                "#96c0e0",
                "#3c6792",
            ],
        },
        "args": {
            "bar_mode": "overlay",
            "tolerance": 0.005,
            "locations": "id",
           # "gdf": gpd.read_file("./data/shapefiles/shapefile.shp"),
        },
        "title": "The {} {} between {} and {}",
        "title_args": [
            "indicator_view",
            "ratio_year",
            "date_reference",
            "date_national",
        ],
    },
    {
        "type": "scatter",
        "transform": reporting_count_transform,
        "color": {
            "Percentage of facilities expected to report which reported on their 105-1 form": "rgb(106, 155, 195)",
            "Percentage of reporting facilities that reported a value of one or above for this indicator": "rgb(200, 19, 60)",
        },
        "title": "Reporting: on {}, {} of facilities reported on their 105:1 form, and, out of those, {} reported one or above for {}",
        "title_args": [
            "date_national",
            "reporting_reported",
            "reporting_positive",
            "indicator_view",
        ],
    }
]
