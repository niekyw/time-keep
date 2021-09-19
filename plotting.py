from bokeh.plotting import figure
from bokeh.embed import components
from datetime import datetime, timedelta, tzinfo
from sqlite3 import Connection
from typing import Optional

from pydantic import BaseModel
from fastapi import Depends, FastAPI, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import main
from math import pi

import pandas as pd

from bokeh.palettes import Accent
from bokeh.plotting import figure, show
from bokeh.transform import cumsum


def make_pie_chart(username: str,
                   min_time: Optional[datetime] = None,
                   max_time: Optional[datetime] = None,
                   categories: Optional[set[str]] = None,
                   db=Depends(main.get_db)):
    task_list = main.get_user_logs(username, min_time, max_time, categories, db=db)

    x = {task.name: task.length for task in task_list}
    if categories is not None:
        title_string = " & ".join(categories)
    else:
        title_string = "All categories"

    data = pd.Series(x).reset_index(name='value').rename(columns={'index': 'task'})
    data['angle'] = data['value'] / data['value'].sum() * 2 * pi
    data['color'] = Accent[len(x)]

    p = figure(height=350, title=title_string, toolbar_location=None,
               tools="hover", tooltips="@task: @value", x_range=(-0.5, 1.0))

    p.wedge(x=0, y=1, radius=0.4,
            start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
            line_color="white", fill_color='color', legend_field='task', source=data)

    p.axis.axis_label = None
    p.axis.visible = False
    p.grid.grid_line_color = None

    return components(p)
