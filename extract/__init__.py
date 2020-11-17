import os
import numpy as np
import pandas as pd

from . import data
from . import model
from . import figure


def run(db, config):

    # 1. Define filters pipeline

    pipeline = data.pipeline.get()

    # 2. Run pipeline for current config
    db.init_pipeline(pipeline)

    db.run_pipeline(config)

    # 3. Get figures based on the current data

    fig_pipeline = figure.get(db.datasets)

    # 4. Save figures

    path = f"data/viz/{config.get('district')}/{config.get('date')}/{config.get('indicator')}"
    if not os.path.exists(path):
        os.makedirs(path)

    for i in range(0, len(fig_pipeline)):
        filename = f"{path}/figure_{i+1}.png"
        fig_pipeline[i].write_image(filename)
