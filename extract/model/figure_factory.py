from datetime import timedelta
from itertools import cycle

import plotly.graph_objects as go
from dataset import helper
from plotly.validators.scatter.marker import SymbolValidator


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

    def get_bar_or_scatter(
        self, figure_object, data, figure_colors, bar_mode=None, **kwargs
    ):
        """
        Gets data from transform and pipeline and creates figures. Function creates both bar and scatter plots using if-condition
        """
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
                    texttemplate="%{x}",
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
            """ Assigns different symbols to each data line in scatter plots"""
            raw_symbols = [1, 2, 18]
            markers = cycle(raw_symbols)
            fig.update_traces(mode="lines+markers")
            for d in fig.data:
                d.marker.symbol = next(markers)
                d.marker.size = 10
            fig.update_traces(line=dict(width=2))

        return fig

    #########
    # STYLE #
    #########

    def style_figure(self, fig):
        """ 1. Calibrates the size of the visualisation; 2. Sets the style of the grids and background"""
        fig.update_layout(
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1.02
            ),
            margin=dict(l=20, r=20, b=0.5, t=20, pad=2),
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
        """
        Extracts and returns the arguments of the titles predefined in the figures' pipeline (figures/pipeline.py)
        data is called from db

        """
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

            elif agg == "latest_value":
                data = db.datasets.get("country")
                value = data.reset_index().iloc[-1, -1].item()
                parsed = str(round(value, 2))

            elif agg == "ratio":
                data = db.datasets.get("district")
                max_date = data.reset_index().date.max()
                min_date = (max_date - timedelta(days=1)).replace(day=1)
                parsed = self.__get_percentage_difference_between_time(
                    data, min_date, max_date
                )
            elif agg == "facility_count_reported":
                parsed = str(
                    self.__get_positive_reporting(db.datasets.get("reporting_district"))
                )
            elif agg == "facility_count":
                data = db.datasets.get("reporting_district")
                data = helper.check_index(data)
                data = data.droplevel(["id"])
                df_positive = helper.get_num(data, 3)
                df_no_positive = helper.get_num(data, 2)
                df_no_form_report = helper.get_num(data, 1)

                positive = df_positive.iloc[-1].item()
                no_positive = df_no_positive.iloc[-1].item()

                no_report = df_no_form_report.iloc[-1].item()

                parsed = str(positive + no_positive + no_report)
            elif agg == "top_facility":
                from dataset.transform import bar_district_plot

                data = bar_district_plot(db.datasets).get("district")
                parsed = data.reset_index().facility_name.iloc[-1]

            elif agg == "top_facility_contribution":
                from dataset.transform import bar_district_plot

                data = bar_district_plot(db.datasets).get("district").reset_index()
                facility_name = data.reset_index().facility_name.iloc[-1]
                facility_value = data.loc[
                    data.facility_name == facility_name, indicator
                ].item()
                parsed = str(round(facility_value / data[indicator].sum() * 100)) + "%"

            elif agg == "reporting_positive":
                from dataset.transform import scatter_reporting_district_plot

                data = scatter_reporting_district_plot(db.datasets).get(
                    "Percentage of reporting facilities that reported a value of one or above for this indicator"
                )
                parsed = data.iloc[-1].item()

            elif agg == "reporting_reported":
                from dataset.transform import scatter_reporting_district_plot

                data = scatter_reporting_district_plot(db.datasets).get(
                    "Percentage of facilities expected to report which reported on their 105-1 form"
                )
                parsed = data.iloc[-1].item()

            format_aggs.append(parsed)
        return title.format(*format_aggs)

    def __get_percentage_description(self, value):
        """ "
        Returns description of direction of the change in a value (increase/decrease/stable)

        """
        absolute_value = abs(value)
        if value >= 0.1:
            description = f"increased by {absolute_value}%"
        elif absolute_value < 0.1:
            description = "remained stable"
        elif value <= 0.1:
            description = f"decreased by {absolute_value}%"
        return description

    def __get_percentage_difference_between_time(self, data, min_date, max_date):
        """
        Parses the value for a given date and returns the string with the percentage and its description
        """
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
        """
        Returns the number of facilities reported positive from the set of facilities expected to report for reporting bar chart (more info in dataset/transform.py )
        """

        indicator = data.columns[-1]
        data = data.reset_index()
        max_date = data.date.max()
        data = data[data[indicator] == 3].reset_index(drop=True)
        reported_positive = str(data[data.date == max_date][indicator].count())

        return reported_positive
