from .pipeline import pipeline
from ..model import FigureFactory


def get(data):
    ff = FigureFactory()
    figures = []
    figure_titles = []
    for figure in pipeline:
        d = figure.get("transform")(data)
        figures.append(
            ff.get_figure(
                figure.get("type"), d, figure.get("color"), **figure.get("args", {})
            )
        )
        figure_titles.append(
            ff.get_figure_title(
                figure.get("title"), data.get(figure.get("title_data")), ["district", "date", "ratio"]
            )
        )
    return figures, figure_titles
