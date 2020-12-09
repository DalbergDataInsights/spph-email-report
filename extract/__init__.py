import json
import os

import numpy as np
import pandas as pd

from . import figure, model


def run(db, config, pipeline, folder="viz"):

    db.run_pipeline(config)

    fig_pipeline, fig_titles = figure.get(db, pipeline)

    # 4. Save figures

    path = f"data/{folder}/{config.get('district', 'default')}/{config.get('date')}/{config.get('indicator')}"
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
        if fig_pipeline[i]: # if an exception happens during the image extraction, None is appended to the figure list
            fig_pipeline[i].write_image(filename)
