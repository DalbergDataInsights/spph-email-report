from ..model import FigureFactory


def get(db, pipeline):
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
        except Exception as e:
            print(e)
            figures.append(None)
        try:
            figure_titles.append(
                ff.get_figure_title(
                    figure.get("title", ""), db, figure.get("title_args", [])
                )
            )
        except Exception as e:
            print(e)
            figures[-1] = None
            figure_titles.append("")
    return figures, figure_titles
