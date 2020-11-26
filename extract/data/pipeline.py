from datetime import datetime
from extract.data.helper import get_time_diff_perc
from . import filter
from . import helper




def get():
    return {
        "district": scatter_district_data,
        "district_dated": bar_district_dated_data,
        "reporting_district": scatter_reporting_district_data,
        
        

    }


def scatter_district_data(db, *, indicator, district, **kwargs):

    df = db.raw_data

    df = db.filter_by_indicator(df, indicator)

    df = filter.by_district(df, district)

    df, index = helper.get_ratio(df, indicator, agg_level="district")

    df = df.set_index(index)
    

    title = f" Total {db.get_indicator_view(indicator)} in {district} district"

    df = df.rename(columns={indicator: title})

    return df



def get_scatter_district_title(data, indicator_view_name, **controls):
    
    district_descrip = get_time_diff_perc(data, **controls)
    
    title = f'''The number of {indicator_view_name} in {controls.get('district')} in {controls.get('target_month')}-{controls.get('target_year')} 
             {district_descrip} from the month before'''
    
    return title

    

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

    title = f'"Contribution of individual facilities to {db.get_indicator_view(indicator)} in {district} district'

    df_district_dated = df_district_dated.rename(columns={indicator: title})
    

    return df_district_dated

def get_title_district_bar(indicator_view_name, **controls):
    
    title = f'''Contribution of individual facilities in {controls.get('district')} district to the {indicator_view_name}
            on {controls.get('target_month')}-{controls.get('target_year')}'''

    return title

    



    


def scatter_reporting_district_data(db, *, indicator, district, **kwargs):

    df = db.rep_data

    indicator = db.switch_indic_to_numerator(indicator, popcheck=False)

    df = db.filter_by_indicator(df, indicator)

    df = filter.by_district(df, district)

    title = f"Total number of facilities reporting on their 105:1 form, and reporting a non-zero number for {db.get_indicator_view(indicator)} in {district} district"

    df = df.rename(columns={indicator: title})

    return df

def get_rep_positive(data, **controls):
   
    target_year = controls.get("target_year")
    target_month = controls.get("target_month")

    try:

        date_reporting = datetime.strptime(
            f"{target_month} 1 {target_year}", "%b %d %Y"
        )

        try:
            reported_positive = data\
                .get("Reported a positive number")\
                .loc[date_reporting][0]
        except Exception:
            reported_positive = 0
    
    except Exception:
        reported_positive = "unknown"

        return reported_positive

def get_title_scatter_reporting_country(data, indicator_view_name, **controls):
   
    descrip_positive = get_rep_positive(data, **controls)

    title = f'''
            Of the facilities in  {controls.get('district')}, 
            {descrip_positive} reported with a number different from zero for {indicator_view_name} in {controls.get('target_month')}-{controls.get('target_year')}'''

    return title