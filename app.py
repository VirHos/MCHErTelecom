from flask import Flask, render_template
import json
from flask import request
import random
import pandas as pd
import plotly.graph_objects as go
import plotly
import plotly.express as px
from get_recomendation import get_best_intersec_points

app = Flask(__name__)

spheredict = {'Автосалон': 'автосалон',
'Аттракционы': 'аттракционная техника с механическим приводом, установленная в скверах и парках',
'Бар': 'бар',
'Библиотека': 'библиотеки',
'Буфет': 'буфет',
'Гипермаркет': 'гипермаркет',
'Дом быта': 'комплексное предприятие бытового обслуживания',
'Закусочная': 'закусочная',
'Иные объекты бытового обслуживания': 'иные объекты бытового обслуживания',
'Кафе': 'кафе',
'Киоск': 'киоск',
'Ломбард': 'услуги ломбарда',
'Магазин': 'магазин',
'Магазин с алкоголем': 'объекты розничной торговли и общественного питания, имеющие лицензию на розничную продажу алкогольной продукции с указанием срока ее дейст',
'Магазин-салон': 'магазин-салон',
'Минимаркет': 'минимаркет',
'Музей': 'музеи',
'Передвижной торговый объект': 'передвижной торговый объект (тележки, лотки, палатки и иные специальные приспособления)',
'Продажа транспортных билетов': 'точки продажи билетов для проезда на наземном городском пассажирском транспорте',
'Ремонт металлоизделий': 'ремонт и изготовление металлоизделий',
'Ремонт обуви': 'ремонт, окраска и пошив обуви',
'Ремонт одежды и обуви': 'ремонт и пошив швейных, меховых и кожаных изделий, головных уборов и изделий текстильной галантереи, ремонт, пошив и вязание трикотажных изделий',
'Ремонт техники': 'ремонт и техническое обслуживание бытовой радиоэлектронной аппаратуры, бытовых машин и бытовых приборов, техники',
'Ремонт часов': 'ремонт часов',
'Ремонт ювелирных изделий': 'ремонт ювелирных изделий',
'Ресторан': 'ресторан',
'Салон красоты': 'парикмахерские и косметические услуги',
'Сауна': 'услуги саун',
'Специализированный непродуктовый магазин': 'прочие специализированные непродовольственные предприятия торговли',
'Специализированный продуктовый магазин': 'прочие специализированные продовольственные предприятия торговли',
'Столовая': 'столовая',
'Супермаркет': 'супермаркет',
'Товары для детей': 'товары для детей',
'Товары для дома': 'товары для дома',
'Товары для женщин': 'товары для женщин',
'Универсам': 'универсам',
'Фастфуд': 'предприятие быстрого обслуживания',
'Фотоателье': 'фотоателье, фотоуслуги',
'Химчистка': 'химическая чистка и крашение',
}

def create_graph():

    points = pd.read_csv("./data/train_points.csv",sep=';',encoding = 'cp1251')
    #points = pd.read_excel("./data/data-4275-2021-05-28.xlsx",engine='openpyxl')

    fig = px.scatter_mapbox(points, lat="lat", lon="long",  hover_data={'lat':False,'long':False,"Средняя проходимость в день":True},#hover_name="Средняя проходимость в день",
                            color_discrete_sequence=["slateblue"], zoom=11, height=500)
    fig.update_layout(mapbox_style="open-street-map")


    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def create_graph_rec(points):
    print(points)
    #points = pd.read_excel("./data/data-4275-2021-05-28.xlsx",engine='openpyxl')

    fig = px.scatter_mapbox(points, lat="lat", lon="long", hover_data={'lat':True,'long':True,"concurents_cnt":True},#hover_name="Средняя проходимость в день",
                            color_discrete_sequence=["black"], zoom=11, height=500)
    fig.update_layout(mapbox_style="open-street-map")


    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == "POST":
        sphere = request.form.get('sphere')
        day = request.form.get('day')
        night = request.form.get('night')
        dayornight = request.form.get('dayornight')
        print(sphere, day, night)
        #print(get_best_intersec_points('кинотеатры'))
        #print(get_best_intersec_points('кафе'))
        #print(spheredict[sphere])
        print(spheredict[sphere])
        print(int(day.split(',')[0]))
        print(int(night.split(',')[1]))
        return render_template('index.html', my_graph=create_graph_rec(\
            get_best_intersec_points(spheredict[sphere],day_flag=dayornight!='True',  #FLAG TRUE - day FALSE-Night
                             day_l=int(day.split(',')[0]), #low day bound
                             day_u=int(day.split(',')[1]), #up day bound
                             night_l=int(night.split(',')[0]), #low night bound
                             #night_u=int(night.split(',')[1])\
        )), spheredict=spheredict, defselected=sphere)
    return render_template('index.html', my_graph=create_graph(), spheredict=spheredict,defselected='Бар')


@app.route('/team/')
def profile():
    return render_template('team.html')


if __name__ == '__main__':
    app.run()