import json
import os

from . import figure


def run(db, config, pipeline, folder="viz"):
    """
    Gets figures and titles, stores visualizations and captions in the respective folders, skipping broken viz
    """

    db.run_pipeline(config)

    fig_pipeline, fig_titles = figure.get(db, pipeline)

    # Save figures

    path = f"data/{folder}/{config.get('district', 'national')}/{config.get('date')}/{config.get('indicator')}"
    if not os.path.exists(path):
        os.makedirs(path)
    with open(f"{path}/titles.json", "w") as f:
        # fig_titles = [] -> {}
        # zip([1, 2 , 3 ], [a, b, c]) -> {1:a, 2:b, 3:c}
        figure_range = [f"figure_{x}" for x in range(1, len(fig_titles) + 1)]
        fig_titles = dict(zip(figure_range, fig_titles))
        json.dump(fig_titles, f)
    for i in range(0, len(fig_pipeline)):
        filename = f"{path}/figure_{i+1}.png"
        if fig_pipeline[
            i
        ]:  # if an exception happens during the image extraction, None is appended to the figure list
            fig_pipeline[i].write_image(filename)
