import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import numpy as np

import json
import math


class FigureFactory:

    default_colors = {
        "title": "white",
        "subtitle": "rgb(34, 94, 140)",
        "text": "#363638",
        "fig": ["#b00d3b", "#f77665", "#e2d5d1", "#96c0e0", "#3c6792"],
    }

    def get_figure(self, figure_type, data, colors=None, **kwargs):
        if not colors:
            colors = self.default_colors
        if figure_type == "scatter":
            return self.get_bar_or_scatter("Scatter", data, colors, **kwargs)
        elif figure_type == "bar":
            return self.get_bar_or_scatter("Bar", data, colors, **kwargs)
        elif figure_type == "treemap":
            return self.get_treemap("Treemap", data, colors, **kwargs)
        elif figure_type == "map":
            return self.get_map(
                figure_object="Choroplethmapbox", data=data, colors=colors, **kwargs
            )

    def get_map(
        self, figure_object="Choroplethmapbox", data=None, colors=None, **kwargs
    ):

        FigType = getattr(go, figure_object)

        choropleth_map = go.Choroplethmapbox()

        locations = kwargs.pop("locations")
        geojson, bounds = self.__get_geo_data(
            kwargs.pop("gdf"), kwargs.pop("tolerance")
        )

        for df in data.values():

            lower_bound, upper_bound = self.get_range(df[df.columns[0]])
            colorscale = self.get_custom_colorscale((lower_bound, upper_bound), colors)

            choropleth_map = FigType(
                z=df[df.columns[0]],
                geojson=geojson,
                locations=df.reset_index()[locations],
                hovertemplate="%{location} <br>" + ": %{z}" + "<extra></extra>",
                marker_opacity=1,
                marker_line_width=1,
                colorscale=colorscale,
                zmin=lower_bound,
                zmax=upper_bound,
            )

        fig = go.Figure(choropleth_map)

        # Update the map
        fig.update_layout(
            mapbox_style="carto-positron",
            mapbox_zoom=5.50,
            mapbox_center=bounds.get("center"),
        )

        return fig

    def get_bar_or_scatter(
        self, figure_object, data, figure_colors, bar_mode=None, **kwargs
    ):
        fig = go.Figure()

        FigType = getattr(go, figure_object)

        for name, df in data.items():
            fig.add_trace(
                FigType(
                    x=df.index,
                    y=df[df.columns[0]],
                    name=name,
                    marker_color=figure_colors.get(
                        name, next(iter(figure_colors.values()))
                    ),
                    hoverinfo="x+y",
                )
            )
            if bar_mode == "overlay":
                fig.update_traces(
                    textposition="inside",
                    # customdata =
                    texttemplate="%{x:%}",
                    orientation="h",
                    y=df.index,
                    x=df[df.columns[0]],
                    showlegend=False,
                    hoverinfo="none",
                )

        self.style_figure(fig)

        if figure_object == "Bar":
            fig.update_layout(barmode=bar_mode)
        elif figure_object == "Scatter":
            fig.update_traces(marker=dict(symbol="square", size=10))
            fig.update_traces(line=dict(width=2))

        return fig

    #########
    # STYLE #
    #########

    def style_figure(self, fig):

        fig.update_layout(
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
            ),
            margin=dict(l=20, r=20, b=1, t=20, pad=2),
            autosize=False,
            width=800,
            height=400,
        )

        fig.update_layout(
            {
                "plot_bgcolor": "rgba(255, 255, 255, 1)",
                "paper_bgcolor": "rgba(255, 255, 255, 1)",
            },
            xaxis=dict(showgrid=False, zeroline=False, rangemode="tozero"),
            yaxis=dict(
                showgrid=True, zeroline=False, rangemode="tozero", gridcolor="LightGray"
            ),
        )

    def get_figure_title(self, title, db, aggs):
        format_aggs = []
        indicator = next(iter(db.datasets.values())).columns[-1]
        for agg in aggs:
            parsed = ""
            if agg == "date":
                data = db.datasets.get("district_dated")
                parsed = data.reset_index().date.max().strftime("%B %Y")
            if agg == "date_national":
                data = db.datasets.get("country")
                parsed = data.reset_index().date.max().strftime("%B %Y")
            elif agg == "district":
                data = db.datasets.get("district_dated")
                parsed = data.reset_index().id[0]
            elif agg == "indicator_view":
                parsed = db.get_indicator_view(indicator)
            elif agg == "date_reference":
                data = db.datasets.get("country")
                max_date = data.reset_index().date.max()
                parsed = max_date.replace(year=max_date.year - 1).strftime("%B %Y")
            elif agg == "ratio":
                data = db.datasets.get("district")
                max_date = data.reset_index().date.max()
                min_date = (max_date - timedelta(days=1)).replace(day=1)
                parsed = self.__get_percentage_difference_between_time(
                    data, min_date, max_date
                )
            elif agg == "ratio_year":
                data = db.datasets.get("country")
                max_date = data.reset_index().date.max()
                min_date = max_date.replace(year=max_date.year - 1)
                parsed = self.__get_percentage_difference_between_time(
                    data, min_date, max_date
                )
            elif agg == "facility_count_reported":
                parsed = str(
                    self.__get_positive_reporting(db.datasets.get("reporting_district"))
                )
            elif agg == "facility_count":
                parsed = str(
                    db.datasets.get("district_dated")
                    .reset_index()
                    .facility_name.count()
                )
            elif agg == "top_facility":
                from dataset.transform import bar_district_plot

                data = bar_district_plot(db.datasets).get("district")
                parsed = (
                    data.sort_values(by=indicator, ascending=False)
                    .reset_index()
                    .facility_name.iloc[0]
                )
            elif agg == "top_facility_contribution":
                from dataset.transform import bar_district_plot

                data = bar_district_plot(db.datasets).get("district").reset_index()
                facility_name = (
                    data.sort_values(by=indicator, ascending=False)
                    .reset_index()
                    .facility_name.iloc[0]
                )
                facility_value = data.loc[
                    data.facility_name == facility_name, indicator
                ].item()
                parsed = (
                    str(round(facility_value / data[indicator].sum(), 2) * 100) + "%"
                )
            elif agg == "reference_date":
                data = db.datasets.get("country")
                data_today = data.reset_index().date.max()
                parsed = (data_today - relativedelta(years=1)).strftime("%B %Y")
            elif agg == "reporting_positive":
                from dataset.national_transform import reporting_count_transform

                data = reporting_count_transform(db.datasets).get(
                    "Percentage of reporting facilities that reported a value of one or above for this indicator"
                )
                date = next(iter(db.datasets.values())).reset_index().date.max()
                parsed = data.loc[date][0]
            elif agg == "reporting_reported":
                from dataset.national_transform import reporting_count_transform

                data = reporting_count_transform(db.datasets).get(
                    "Percentage of facilities expected to report which reported on their 105-1 form"
                )
                date = next(iter(db.datasets.values())).reset_index().date.max()
                parsed = data.loc[date][0]
            format_aggs.append(parsed)
        return title.format(*format_aggs)

    def __get_percentage_description(self, value):
        absolute_value = abs(value)
        if value >= 0.1:
            description = f"increased by {absolute_value}%"
        elif absolute_value < 0.1:
            description = "remained stable"
        elif value <= 0.1:
            description = f"decreased by {absolute_value}%"
        return description

    def __get_percentage_difference_between_time(self, data, min_date, max_date):
        indicator = data.columns[-1]
        data = data.reset_index()

        ratio_value = round(
            (
                (
                    data.loc[data.date == max_date, indicator].item()
                    - data.loc[data.date == min_date, indicator].item()
                )
                / data.loc[data.date == min_date, indicator].item()
            )
            * 100
        )
        description = self.__get_percentage_description(ratio_value)

        return description

    def __get_positive_reporting(self, data):

        indicator = data.columns[-1]
        data = data.reset_index()
        max_date = data.date.max()
        data = data[data[indicator] == 3].reset_index(drop=True)
        reported_positive = str(data[data.date == max_date][indicator].count())

        return reported_positive

    def __get_geojson_from_data(self, data, id="id"):
        assert id in data.columns, f"GeoDataFrame should contain {id} column"
        geojson_df = json.loads(data.set_index(id).to_json())

        return geojson_df

    def __get_geo_data(self, gdf, tolerance=None, id="id"):
        """Defines the json data for mapping from a geopandas dataframe.

        Args:
            gdf([type]): [description]
            tolerance(float, optional): Allows for faster loading time of map during callback by "rounding" the borders(higher values=faster loading=less precision on border outline). Defaults to None.
            geometry(str, optional): [description]. Defaults to 'geometry'.
            id(str, optional): [description]. Defaults to 'id'.
        """
        if tolerance:
            gdf["geometry"] = gdf["geometry"].simplify(tolerance=tolerance)
        # Set bounds
        bounds = gdf.bounds
        bounds = {
            "xmin": bounds.minx.min(),
            "xmax": bounds.maxx.max(),
            "ymin": bounds.miny.min(),
            "ymax": bounds.maxy.max(),
        }
        bounds["center"] = {
            "lon": np.mean([bounds.get("xmin"), bounds.get("xmax")]),
            "lat": np.mean([bounds.get("ymin"), bounds.get("ymax")]),
        }

        geojson = self.__get_geojson_from_data(gdf, id=id)

        return geojson, bounds

    def get_range(self, data):

        if True:

            q1 = data.quantile(0.25)
            q3 = data.quantile(0.75)
            iqr = q3 - q1
            lower_bound = max(data.min(), (q1 - 1.5 * iqr))
            upper_bound = min(data.max(), (q3 + 1.5 * iqr))

        else:

            lower_bound = data.min()
            upper_bound = data.max()

        return (lower_bound, upper_bound)

    def get_custom_colorscale(self, ranges, colors):

        # TODO Find more stable fix, not using name
        colorlist = next(iter(colors.values()))
        min_color_nb = 0
        max_color_nb = -1

        colorlist_lenght = len(colorlist)
        assert colorlist_lenght in [
            2,
            3,
            5,
        ], "Color list should include 2,3, or 5 colors"

        lower_bound, upper_bound = ranges

        center_value = 0

        if colorlist_lenght == 2:
            colorscale = [
                [0.0, colorlist[min_color_nb]],
                [1.0, colorlist[max_color_nb]],
            ]

        else:

            if lower_bound <= center_value <= upper_bound:

                center_norm = (center_value - lower_bound) / (upper_bound - lower_bound)

                if math.isnan(center_norm):
                    center_norm = 0

                colorscale = [
                    [0.0, colorlist[min_color_nb]],
                    [center_norm / 2, colorlist[1]],
                    [center_norm, colorlist[2]],
                    [center_norm + (1 - center_norm) / 2, colorlist[3]],
                    [1.0, colorlist[max_color_nb]],
                ]
            else:
                if center_value <= lower_bound:
                    min_color_nb = math.floor(colorlist_lenght / 2)
                else:
                    max_color_nb = math.floor(colorlist_lenght / 2)
                colorscale = [
                    [0.0, colorlist[min_color_nb]],
                    [1.0, colorlist[max_color_nb]],
                ]

        colorscale = [x for x in colorscale if x]

        return colorscale