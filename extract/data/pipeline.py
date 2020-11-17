from . import filter
from . import helper



def get():
    return {
        "district": scatter_district_data,
        "district_dated": tree_map_district_dated_data,
        "reporting_district": scatter_reporting_district_data,
    }


def scatter_district_data(db, *, indicator, district, **kwargs):

    df = db.raw_data

    df = db.filter_by_indicator(df, indicator)

    df = filter.by_district(df, district)

    df, index = helper.get_ratio(df, indicator, agg_level="district")

    df = df.set_index(index)

    title = f"Total {db.get_indicator_view(indicator)} in {district} district"

    df = df.rename(columns={indicator: title})

    return df


def tree_map_district_dated_data(
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
    
    df_district_dated = df_district_dated.nlargest(12, indicator)

    #if len(df_district_dated) >= 12 :
    
    #df_district_dated_top = df_district_dated.nlargest(12, indicator)
    #df_district_dated.loc[len(df_district_dated_top)] = ['Others', df_district_dated.loc[~df_district_dated_top.facility_name.isin(df_district_dated.facility_name), indicator].sum()]
    
    #df_district_dated = (df_district_dated.groupby(indicator).sum()
                #.sort_values(indicator, ascending=False)
                
   #df_district_dated.loc[df_district_dated.index >= 12, indicator]= "Others"

    #df_district_dated = df_district_dated.sort_values(indicator, ascending=False).index[12:].sum()
    


    #not_top = df_district_dated.sum().sort_values(indicator, ascending=False).index[12:]
    #df_district_dated = df_district_dated.replace(not_top, 'Other')


    
    #df_district_dated_large = df_district_dated.nlargest(12, indicator)
    #df_district_dated_other = df.sort_values(indicator, ascending=False).indicator[12:].sum()
    #df_district_dated.loc[len(df_district_dated_large)] = ["others", df_district_dated_other]
   
    

    title = f'"Contribution of individual facilities to {db.get_indicator_view(indicator)} in {district} district'

    df_district_dated = df_district_dated.rename(columns={indicator: title})

    return df_district_dated
    


def scatter_reporting_district_data(db, *, indicator, district, **kwargs):

    df = db.rep_data

    indicator = db.switch_indic_to_numerator(indicator, popcheck=False)

    df = db.filter_by_indicator(df, indicator)

    df = filter.by_district(df, district)

    title = f"Total number of facilities reporting on their 105:1 form, and reporting a non-zero number for {db.get_indicator_view(indicator)} in {district} district"

    df = df.rename(columns={indicator: title})

    return df
