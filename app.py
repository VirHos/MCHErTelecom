from flask import Flask, render_template
import json
from flask import request
import random
import pandas as pd
import plotly.graph_objects as go
import plotly
import plotly.express as px

app = Flask(__name__)


def create_graph():

    points = pd.read_csv("./data/train_points_with_prohod.csv",sep=';',encoding = 'cp1251')
    #points = pd.read_excel("./data/data-4275-2021-05-28.xlsx",engine='openpyxl')

    fig = px.scatter_mapbox(points, lat="lat", lon="long",  hover_data=["Средняя проходимость в день"],#hover_name="Средняя проходимость в день",
                            color_discrete_sequence=["slateblue"], zoom=11, height=500)
    fig.update_layout(mapbox_style="open-street-map")


    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

@app.route('/')
def main():

    return render_template('index.html', my_graph=create_graph())


@app.route('/team/')
def profile():
    return render_template('team.html')


if __name__ == '__main__':
    app.run()