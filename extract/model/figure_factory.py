from extract.dataset import helper
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


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
                    textposition="outside",
                    # customdata =
                    texttemplate="%{x:}",
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
            margin=dict(l=20, r=20, b=20, t=20, pad=2),
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
        indicator = db.datasets.get("district_dated").columns[-1]
        for agg in aggs:
            parsed = ""
            if agg == "date":
                data = db.datasets.get("district_dated")
                parsed = data.reset_index().date.max().strftime("%B %Y")
            elif agg == "district":
                data = db.datasets.get("district_dated")
                parsed = data.reset_index().id[0]
            elif agg == "indicator_view":
                parsed = db.get_indicator_view(indicator)
            elif agg == "ratio":
                parsed = self.__get_percentage_difference_between_time(db.datasets.get("district"))
            elif agg == "facility_count_reported":
                parsed = str(self.__get_positive_reporting(db.datasets.get("reporting_district")))
            elif agg == "facility_count":
                parsed = str(db.datasets.get("district_dated").reset_index().facility_name.count())
            elif agg == "top_facility":
                from ..dataset.transform import bar_district_plot
                data = bar_district_plot(db.datasets).get("district")
                parsed = data.sort_values(by=indicator, ascending=False).reset_index().facility_name.iloc[0]
            elif agg == "top_facility_contribution":
                from ..dataset.transform import bar_district_plot
                data = bar_district_plot(db.datasets).get("district").reset_index()
                facility_name = data.sort_values(by=indicator, ascending=False).reset_index().facility_name.iloc[0]
                facility_value = data.loc[data.facility_name == facility_name, indicator].item()
                parsed = str(round(facility_value/data[indicator].sum(),2) * 100) + "%"
            elif agg=="ratio_country":
                parsed = self.__get_percentage_difference_between_time_country(db.datasets.get("country"))
            elif agg=="reference_date":
                data = db.datasets.get("country")
                data_today= data.reset_index().date.max()
                parsed = (data_today - relativedelta(years=1)).strftime("%B %Y")
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


    def __get_percentage_difference_between_time(self, data):
        indicator = data.columns[-1]
        data = data.reset_index()
        max_date = data.date.max()
        previous_month = (max_date - timedelta(days=1)).replace(day=1)

        ratio_value = round(
            (
                (data.loc[data.date == max_date, indicator].item() -
                data.loc[data.date == previous_month, indicator].item()) /
                data.loc[data.date == previous_month, indicator].item()
            )
            * 100
        )
        description = self.__get_percentage_description(ratio_value)

        return description


    def __get_positive_reporting(self, data):

        indicator = data.columns[-1]
        data = data.reset_index()
        max_date = data.date.max()
        data = data[data[indicator]==3].reset_index(drop=True)
        reported_positive = str(data[data.date == max_date][indicator].count())

        return reported_positive


    def __get_percentage_difference_between_time_country(self, data):
        indicator = data.columns[-1]
        data = data.reset_index()
        max_date = data.date.max()
        previous_year = (max_date - relativedelta(years=1))
        print(previous_year)

        ratio_value = round(
            (
                (data.loc[data.date == max_date, indicator].item() -
                data.loc[data.date == previous_year, indicator].item()) /
                data.loc[data.date == previous_year, indicator].item()
            )
            * 100
        )
        description = self.__get_percentage_description(ratio_value)

        return description