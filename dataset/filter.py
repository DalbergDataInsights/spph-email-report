from datetime import datetime


def by_dates(df, target_year, target_month, reference_year, reference_month):
    min_date = None
    max_date = None
    reverse = False

    df = df.sort_values(["date"])

    target_date = datetime.strptime(f"{target_month} 1 {target_year}", "%b %d %Y")
    reference_date = datetime.strptime(
        f"{reference_month} 1 {reference_year}", "%b %d %Y"
    )

    if reference_date <= target_date:
        max_date = target_date
        min_date = reference_date
    elif target_date < reference_date:
        max_date = reference_date
        min_date = target_date
        reverse = True

    min_mask = df.date >= min_date
    df = df.loc[min_mask].reset_index(drop=True)

    max_mask = df.date <= max_date
    df = df.loc[max_mask].reset_index(drop=True)

    if reverse:
        df = df.reindex(index=df.index[::-1])
    return df


def by_district(df, district):
    mask = df.id == district
    df = df.loc[mask].reset_index(drop=True)
    return df
