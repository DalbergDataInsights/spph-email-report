from extract.data import helper
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime


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

    def get_treemap(self, figure_object, data, figure_colors, **kwargs):

        fig = go.Figure()
        # We can add types here
        fig_type = getattr(go, figure_object)

        # figure_colors = self.colors.get("fig")

        for name, df in data.items():

            treemap_df = self.build_hierarchical_dataframe(
                df.reset_index(),
                levels=df.index.names,
                value_column=df.columns[0],
                total_id=name,
            )

            scale_max = round(
                df[df.columns[0]].max() / df[df.columns[0]].sum() * 100, 2
            )

            fig.add_trace(
                fig_type(
                    parents=treemap_df["parent"],
                    labels=treemap_df["id"],
                    values=treemap_df["value"],
                    branchvalues="total",
                    marker=dict(
                        colors=treemap_df["color"],
                        colorscale=figure_colors,
                        cmin=0,
                        cmid=scale_max / 3,
                        cmax=scale_max,
                    ),
                    textinfo="label+value+percent parent",
                )
            )
            fig.update_layout(
                margin=dict(t=20, b=20, r=20, l=20),
                width=900,
                height=400,
                autosize=False,
            )

        return fig

    # HELPER - TREEMAP

    def build_hierarchical_dataframe(self, df, levels, value_column, total_id="total"):
        levels = levels[::-1]
        df_all_trees = pd.DataFrame(columns=["id", "parent", "value", "color"])
        for i, level in enumerate(levels):
            df_tree = pd.DataFrame(columns=["id", "parent", "value", "color"])
            dfg = df.groupby(levels[i:]).sum()
            dfg = dfg[dfg[dfg.columns[0]] > 0]
            dfg = dfg.reset_index()
            df_tree["id"] = dfg[level].copy()
            if i < len(levels) - 1:
                df_tree["parent"] = dfg[levels[i + 1]].copy()
            else:
                df_tree["parent"] = total_id
            df_tree["value"] = dfg[value_column]
            df_tree["color"] = dfg[value_column]
            df_all_trees = df_all_trees.append(df_tree, ignore_index=True)
        total = pd.Series(
            dict(
                id=total_id,
                parent="",
                value=df[value_column].sum(),
                color=df[value_column].sum(),
            )
        )
        df_all_trees = df_all_trees.append(total, ignore_index=True)
        try:
            df_all_trees["color"] = (
                df_all_trees["color"] / df_all_trees["color"].max() * 100
            )
        except ZeroDivisionError as e:
            print(e)
        return df_all_trees

    #########
    # STYLE #
    #########

    def style_figure(self, fig):

        fig.update_layout(
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
            ),
            margin=dict(l=50, r=50, b=50, t=50, pad=2),
            autosize=False,
            width=900,
            height=500,
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

    def get_figure_title(self, title, data, aggs):
        format_aggs = []
        datetime.strftime("%B %Y") 
        # TODO
        for agg in aggs:
            if agg == "date":
                format_aggs.append(
                    data.reset_index().date.max()
                )  
                data.date.strftime("%B %Y")  # 20201001 -> Oct 2020
                print(format_aggs)
            elif agg == "district":
                format_aggs.append(data.reset_index().id[0])
            elif agg == "ratio":
                format_aggs.append(self.get_time_diff_perc(data))
           # elif agg == "sum_positive": 
                #format_aggs.append(data.get("reported_positive")) 
            
        return title.format(*format_aggs)