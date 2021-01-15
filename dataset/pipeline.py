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
    """
    Prepares data for the indicator overview scatter plot at the district level (figure_1).
    Fetches data from database for requested indicators and district(s).
    Returns dataframe with date, id (district name) and value (as indicator name) columns.
    Index column is numerical.
    """

    df = db.raw_data

    df = db.filter_by_indicator(df, indicator)

    df = filter.by_district(df, district)

    df, index, _ = helper.get_ratio(df, indicator, agg_level="district")

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
    """
    Prepares data for the bar chart with individual facilities contribution (figure_2).
    Fetches data from database for requested indicators and district(s), retrives facilities names.
    Returns dataframe with date, id (district name), facility name and value (as indicator name) columns.
    Date column serves as index.
    """

    df = db.raw_data

    indicator = db.switch_indic_to_numerator(indicator)

    df = db.filter_by_indicator(df, indicator)

    df = helper.get_ratio(df, indicator, agg_level="facility")[0]

    df_district_dated = filter.by_dates(
        df, target_year, target_month, reference_year, reference_month
    )

    df_district_dated = filter.by_district(df_district_dated, district)

    return df_district_dated


def scatter_reporting_district_data(db, *, indicator, district, **kwargs):
    """
    Prepares data for the scatter plot with reporting rates (figure_2).
    Fetches data from database for requested indicators and district(s), retrives facilities names.
    Returns dataframe with id (district name), facility name, date and value (as indicator name) columns.
    Index column is numerical.
    """

    df = db.rep_data

    indicator = db.switch_indic_to_numerator(indicator, popcheck=False)

    df = db.filter_by_indicator(df, indicator)

    df = filter.by_district(df, district)

    return df


def scatter_country_data(db, *, indicator, **kwargs):
    """
    Prepares data for the indicator overview scatter plot at the country level (figure_4).
    Fetches data from database for requested indicators and district(s), retrives facilities names.
    Returns dataframe with date and value (as indicator name) columns.
    Date serves as an index column.
    """

    df = db.raw_data

    df = db.filter_by_indicator(df, indicator)

    df, index, _ = helper.get_ratio(df, indicator, agg_level="country")

    df = df.set_index(index)

    return df