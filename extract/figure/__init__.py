from .pipeline import pipeline
from ..model import FigureFactory


def get(data):
    ff = FigureFactory()
    figures = []
    for figure in pipeline:
        figures.append(
            ff.get_figure(
                figure.get("type"), figure.get("transform")(data), figure.get("color"), **figure.get("args", {})
            )
        )
    return figures
