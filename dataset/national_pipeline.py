from datetime import datetime
from . import helper
from . import filter
from calendar import month_abbr


def get():
    return {
        "country": scatter_country_data,
        "dated_compare": map_bar_country_compare_data,
        "reporting_country": bar_reporting_country_data,
    }


def bar_reporting_country_data(
    db,
    *,
    indicator,
    target_year,
    target_month,
    reference_year,
    reference_month,
    **kwargs,
):

    df = db.rep_data

    indicator = db.switch_indic_to_numerator(indicator, popcheck=False)

    df = db.filter_by_indicator(df, indicator)

    date_list = helper.get_date_list(
        target_year, target_month, reference_year, reference_month
    )

    min_date = min(date_list[0], date_list[3])
    max_date = max(date_list[0], date_list[3])

    df = df[(df.date >= min_date) & (df.date <= max_date)]

    return df


def scatter_country_data(db, *, indicator, target_month, target_year, **kwargs):

    df = db.raw_data

    df = db.filter_by_indicator(df, indicator)

    min_date = df.reset_index().date.min()

    df = filter.by_dates(
        df, target_year, target_month, min_date.year, month_abbr[min_date.month]
    )

    df, index = helper.get_ratio(df, indicator, agg_level="country")[0:2]

    df = df.set_index(index)

    return df


def map_bar_country_compare_data(
    db,
    *,
    indicator,
    target_year,
    target_month,
    reference_year,
    reference_month,
    trends_map_compare_agg,
    **kwargs,
):

    df = db.raw_data

    df = db.filter_by_indicator(df, indicator)

    df = helper.get_ratio(df, indicator, agg_level="district")[0]

    df = helper.get_df_compare(
        df,
        indicator,
        target_year,
        target_month,
        reference_year,
        reference_month,
        trends_map_compare_agg,
    )

    if trends_map_compare_agg == "Compare three months moving average":
        quarter = "the three months periods ending in "
    else:
        quarter = ""

    try:
        df = df.drop(["rank"], axis=1)
    except:
        print("No rank column")

    return df
