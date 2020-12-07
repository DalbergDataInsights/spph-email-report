from . import helper


def scatter_country_plot(df):

    df_country = df.get("country")

    df_country = df_country[df_country[df_country.columns[-1]] > 0]

    df_country = helper.get_year_and_month_cols(df_country)

    df_country = helper.get_sub_dfs(df_country, "year", [2018, 2019, 2020], "month")

    return df_country


def map_country_compare_plot(data):

    data = data.get("dated_compare").copy()

    data[data.columns[-1]] = data[data.columns[-1]] * 100

    data_out = {"Change between reference and target date": data}

    return data_out


def bar_country_compare_plot(data):

    data = data.get("dated_compare")

    data["rank"] = data[data.columns[-1]].rank(ascending=True, method="min")
    data = data[data["rank"] < 11].sort_values(by="rank")
    data.drop("rank", axis=1, inplace=True)
    data_out = {"Top/Bottom 10": data}

    return data_out


def reporting_count_transform(data):
    """
    Counts occurrence of type of reporting label for each date, returning dictionary
    """
    data = data.get("reporting_country")
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
            (df_positive + df_no_positive)
            / (df_positive + df_no_positive + df_no_form_report)
        )
        * 100
    )
    reported_positive = round((df_positive / (df_positive + df_no_positive)) * 100)

    data = {
        "Percentage of facilities expected to report which reported on their 105-1 form": reported,
        "Percentage of reporting facilities that reported a value of one or above for this indicator": reported_positive,
    }

    return data
