from datetime import datetime
from typing import Optional

from fastapi import Depends, APIRouter, Request
from fastapi.templating import Jinja2Templates
from math import pi

import pandas as pd

from bokeh.palettes import Accent, Accent8
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.transform import cumsum
from bokeh.embed import json_item
import json

import database_interactions
import task_routes


router = APIRouter(prefix="/plots")
templates = Jinja2Templates(directory="templates")


@router.get("/{username}", response_model=Optional[str])
def make_pie_chart(username: str,
                   min_time: Optional[datetime] = None,
                   max_time: Optional[datetime] = None,
                   categories: Optional[set[str]] = None,
                   db=Depends(database_interactions.get_db)
                   ):
    task_list = task_routes.get_user_logs(username, min_time, max_time, categories, db)
    if not task_list:
        return None
    x = {task.name: task.length for task in task_list}
    if categories is not None:
        title_string = " & ".join(categories)
    else:
        title_string = "All categories"

    data = pd.Series(x).reset_index(name='value').rename(columns={'index': 'task'})
    data['angle'] = data['value'] / data['value'].sum() * 2 * pi
    if len(x) in Accent:
        data['color'] = Accent[len(x)]  # TODO: errors for len(x) = 1 case
    else:
        data['color'] = Accent8[:len(x)]

    p = figure(height=350, title=title_string, toolbar_location=None,
               tools="hover", tooltips="@task: @value", x_range=(-0.5, 1.0))

    p.wedge(x=0, y=1, radius=0.4,
            start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
            line_color="white", fill_color='color', legend_field='task', source=data)

    p.axis.axis_label = None
    p.axis.visible = False
    p.grid.grid_line_color = None
    return json.dumps(json_item(p))