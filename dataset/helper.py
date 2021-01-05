import numpy as np
import pandas as pd
import calendar
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta



def get_ratio(df, indicator, agg_level):
    """
    Aggregates the ratio properly using weights

    """
    # TODO Link to the index_columns defined in the database object
    # TODO find a way to delete the hardcoded name mapping step

    index = ["date", "id", "facility_name"]

    if agg_level == "country":
        index = [index[0]]

    if agg_level == "district":
        index = index[:2]

    df = df.groupby(index, as_index=False).sum()

    col_count = len(set(df.columns).difference(set(index)))

    isratio = False

    if col_count == 2:

        isratio = True

        weighted_ratio = [x for x in df.columns if x.endswith("__wr")][0]
        weight = [x for x in df.columns if x.endswith("__w")][0]

        df[indicator] = (df[weighted_ratio] / df[weight]) * 1000

        df = df.replace([np.inf, -np.inf], np.nan)

        df = df.drop(columns=[weighted_ratio, weight])

    return df, index, isratio


def check_index(df, index=["id", "date", "facility_name"]):
    """
    Check that the dataframe is formatted in the expected way, with expected indexes. Restructure the dataframe (set the indices) if this is not the case.
    """
    if df.index.values != index:

        df = df.reset_index(drop=True).set_index(index)
    return df


def get_year_and_month_cols(df):

    df = df.reset_index()

    df["year"] = pd.DatetimeIndex(df["date"]).year
    df["month"] = pd.DatetimeIndex(df["date"]).strftime("%b")

    df = df.set_index(["date", "year", "month"])

    return df


def get_sub_dfs(df, select_index, values, new_index):
    """
    Extract and return a dictionary of dictionaries splitting each original dictionary df entry into traces based on values
    """

    traces = {}
    for value in values:
        sub_df = df[df.index.get_level_values(select_index) == value]
        sub_df = sub_df.groupby(new_index).sum()
        sub_df = sub_df.reindex(calendar.month_abbr[1:], axis=0)
        traces[value] = sub_df

    return traces


def get_num(df, value=3):
    """
    Gets a dataframe of the count of the specified value for each column; expects index formatting including date and id
    """
    df_count_all = []
    for date in list((df.index.get_level_values("date")).unique()):
        count_for_date = (df.loc[date] == value).sum()
        df_count_for_date = (pd.DataFrame(count_for_date)).transpose()
        df_count_for_date.index = [date]
        df_count_all.append(df_count_for_date)
    new_df = pd.concat(df_count_all)
    return new_df


def get_df_compare(
    df,
    indicator,
    target_year,
    target_month,
    reference_year,
    reference_month,
    aggregation_type,
    report=False,
    index=["id"],
):

    date_list = get_date_list(
        target_year, target_month, reference_year, reference_month
    )

    df = filter_df_for_compare(df, date_list, aggregation_type)

    df = pivot_df_for_figure(df, indicator)

    if report:
        df = get_reporting_rate_of_districts(df)

    df = compare_between_dates(df, indicator, date_list, aggregation_type)

    df = df.set_index(index)

    return df


def get_date_list(target_year, target_month, reference_year, reference_month):

    target_date = datetime.strptime(f"1 {target_month} {target_year}", "%d %b %Y")
    reference_date = datetime.strptime(
        f"1 {reference_month} {reference_year}", "%d %b %Y"
    )

    date_list = [
        target_date,
        target_date + relativedelta(months=1),
        target_date + relativedelta(months=2),
        reference_date,
        reference_date + relativedelta(months=1),
        reference_date + relativedelta(months=2),
    ]

    return date_list


def filter_df_for_compare(df, date_list, aggregation_type):

    if aggregation_type == "Compare three months moving average":
        df = df[df.date.isin(date_list)]
    else:
        df = df[df.date.isin([date_list[0], date_list[3]])]
    return df


def pivot_df_for_figure(df, indicator):

    if "facility_name" in list(df.columns):
        df = df.pivot_table(
            columns="date", values=indicator, index=["id", "facility_name"]
        )
    else:
        df = df.pivot_table(columns="date", values=indicator, index=["id"])
    return df


def get_reporting_rate_of_districts(df):

    dates = list(df.columns)

    df = df.reset_index()

    reporting_df = pd.DataFrame({"id": list(df.id.unique())})

    for c in dates:
        reporting_df[c] = None
        reporting = []
        for district in df.id.unique():
            district_df = df[df.id == district]
            total_facilities = (district_df[c] != 0).sum()
            reported_facilities = len(district_df[district_df[c] == 3])
            report_rate = round(reported_facilities / total_facilities, 4)
            reporting.append(report_rate)
        reporting_df[c] = reporting

    reporting_df = reporting_df.set_index("id")

    return reporting_df


def compare_between_dates(df, indicator, date_list, aggregation_type):

    if aggregation_type == "Compare three months moving average":

        df[date_list[0]] = df[date_list[:3]].mean(axis=1)
        df[date_list[3]] = df[date_list[3:]].mean(axis=1)

    df[indicator] = (df[date_list[0]] - df[date_list[3]]) / df[date_list[3]]

    df = df.replace([np.inf, -np.inf], np.nan)

    df[indicator] = df[indicator].apply(lambda x: round(x, 4))

    df = df[[indicator]].reset_index()
    df = df[~pd.isna(df[indicator])]

    return df
