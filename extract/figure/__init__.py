from .pipeline import pipeline
from ..model import FigureFactory



def get(db):
    data = db.datasets
    ff = FigureFactory()
    figures = []
    figure_titles = []
    for figure in pipeline:
        d = figure.get("transform")(data)
        try:
            figures.append(
                ff.get_figure(
                    figure.get("type"), d, figure.get("color"), **figure.get("args", {})
                    )
                    )
            figure_titles.append(
                ff.get_figure_title(
                    figure.get("title", ""), db, figure.get("title_args", [])
                    )
                    )                 
        except: 
            print("no data available for this indicator")
            figures.append(None) 
            figure_titles.append(None)
    return figures, figure_titles 
    

