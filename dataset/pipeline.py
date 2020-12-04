from datetime import datetime

from . import filter
from . import helper


def get():
    return {
        "district": scatter_district_data,
        "district_dated": bar_district_dated_data,
        "reporting_district": scatter_reporting_district_data,
        "country": scatter_country_data,
    }


def scatter_district_data(db, *, indicator, district, **kwargs):

    df = db.raw_data

    df = db.filter_by_indicator(df, indicator)

    df = filter.by_district(df, district)

    df, index = helper.get_ratio(df, indicator, agg_level="district")

    df = df.set_index(index)

    return df


def bar_district_dated_data(
    db,
    *,
    indicator,
    district,
    target_year,
    target_month,
    reference_year,
    reference_month,
    **kwargs,
):

    df = db.raw_data

    indicator = db.switch_indic_to_numerator(indicator)

    df = db.filter_by_indicator(df, indicator)

    df = helper.get_ratio(df, indicator, agg_level="facility")[0]

    # TODO check how the date function works such that it shows only target date

    df_district_dated = filter.by_dates(
        df, target_year, target_month, reference_year, reference_month
    )

    df_district_dated = filter.by_district(df_district_dated, district)

    return df_district_dated


def scatter_reporting_district_data(db, *, indicator, district, **kwargs):

    df = db.rep_data

    indicator = db.switch_indic_to_numerator(indicator, popcheck=False)

    df = db.filter_by_indicator(df, indicator)

    df = filter.by_district(df, district)

    return df


def scatter_country_data(db, *, indicator, **kwargs):

    df = db.raw_data

    df = db.filter_by_indicator(df, indicator)

    df, index = helper.get_ratio(df, indicator, agg_level="country")

    df = df.set_index(index)

    return df