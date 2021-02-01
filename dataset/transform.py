from . import helper
import pandas as pd


def scatter_district_plot(df):
    """
    Get data from pipeline for the figure_1 and transforms to the visualisation-friendly format: splits data by year and month.
    Returns dictionary.

    """

    df_district = df.get("district")

    df_district = df_district[df_district[df_district.columns[-1]] > 0]

    df_district = helper.get_year_and_month_cols(df_district)

    df_district = helper.get_sub_dfs(
        df_district, "year", [2018, 2019, 2020, 2021], "month"
    )

    return df_district


def scatter_reporting_district_plot(data):
    """
    Get data from pipeline for the figure_3. Filters out the facilities that are not supposed to deliver any report, collects values for the last 12 month from the last reporting date.
    Returns dictionary.

    """

    data = data.get("reporting_district")
    reporting_date = data.date.max()
    data = data[
        (data.date <= reporting_date)
        & (data.date >= reporting_date - pd.DateOffset(months=12))
    ]
    # Set index
    data = helper.check_index(data)
    # Remove unnecessary index values
    data = data.droplevel(["id"])
    # Count number of positive_indic
    df_positive = helper.get_num(data, 3)
    # Count number of no_positive_indic
    df_no_positive = helper.get_num(data, 2)
    # Count number of no_form_report
    df_no_form_report = helper.get_num(data, 1)

    reported = round(
        (
            (
                (df_positive + df_no_positive)
                / (df_positive + df_no_positive + df_no_form_report)
            )
            * 100
        ),
        1,
    )
    reported = reported.sort_index()
    reported_positive = round(((df_positive / (df_positive + df_no_positive)) * 100), 1)
    reported_positive = reported_positive.sort_index()

    data = {
        "Percentage of facilities expected to report which reported on their 105-1 form": reported,
        "Percentage of reporting facilities that reported a value of one or above for this indicator": reported_positive,
    }
    return data


def bar_district_plot(data):
    """
    Get data from pipeline for the figure_2. Fetches the facilities with top-12 contribution, merges the rest under "Others".
    Returns dictionary.

    """
    data_in = data.get("district_dated")
    val_col = data_in.columns[-1]
    data_in = data_in.reset_index()
    data_in = data_in[data_in.date == data_in.date.max()]
    data_in = data_in[["facility_name", val_col]].groupby(by=["facility_name"]).sum()
    data_in = data_in[data_in[val_col] > 0]
    data_in = data_in.sort_values(val_col, ascending=False).reset_index()
    data_in.loc[data_in.index >= 12, "facility_name"] = "Others"
    data_in = data_in.groupby("facility_name").sum().sort_values(val_col)
    custom_dict = {"Others": 99}
    data_in = data_in.sort_values(
        by=["facility_name"], key=lambda x: x.map(custom_dict)
    )
    return {"district": data_in}


def scatter_country_plot(df):
    """
    Get data from pipeline for the figure_4 and separates the data by year and month.
    Returns dictionary.

    """

    df_country = df.get("country")

    df_country = df_country[df_country[df_country.columns[-1]] > 0]

    df_country = helper.get_year_and_month_cols(df_country)

    df_country = helper.get_sub_dfs(
        df_country, "year", [2018, 2019, 2020, 2021], "month"
    )

    return df_country
