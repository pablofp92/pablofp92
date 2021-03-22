# -*- coding: utf-8 -*-
"""
Created on Sat Mar 13 16:53:26 2021

@author: pablo
"""

import pandas as pd 

import json
import plotly.express as px
#import plotly.io as pio
#pio.renderers.default='browser'

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output




############# DASH

dfprovinciascausas = pd.read_csv('incendios-cantidad-causas-provincia.csv', sep = ';', encoding='latin-1')
dfsuperficieprovincias = pd.read_csv('superficie-incendiada-provincias-tipo-de-vegetacion.csv', sep = ';', encoding='latin-1')

dfsuperficieprovincias = dfsuperficieprovincias.rename(columns = {'superficie_afectada_por_incendios_anio' : 'incendio_anio', 'superficie_afectada_por_incendios_provincia': 'incendio_provincia'} )
df = pd.merge(dfprovinciascausas, dfsuperficieprovincias, how='outer', on=['incendio_anio', 'incendio_provincia'])
df = df.rename(columns = {'incendio_provincia' : 'Provincia'} )

with open('provincia.json', encoding='utf-8') as provincias:
  provincias_shape = json.load(provincias)

YEARS = df.incendio_anio.unique()
CAUSAS = {'Número total': 'incendio_total_numero', 'Negligencia': 'incendio_negligencia_numero', 'Intencional': 'incendio_intencional_numero',
          'Natural': 'incendio_natural_numero', 'Desconocida': 'incendio_desconocida_numero',
          'Superficie afectada en hectareas': 'superficie_afectada_por_incendios_total_hectareas',
          'Superficie afectada (ha) en bosque nativo': 'superficie_afectada_por_incendios_bosque_nativo_hectareas',
          'Superficie afectada (ha) en bosque cultivado': 'superficie_afectada_por_incendios_bosque_cultivado_hectareas',
          'Superficie afectada (ha) en arbustales':  'superficie_afectada_por_incendios_arbustal_hectareas',
          'Superficie afectada (ha) en pastizales':  'superficie_afectada_por_incendios_pastizal_hectareas',
          'Superficie afectada (ha) en vegetación sin determinar': 'superficie_afectada_por_incendios_sin_determinar_hectareas'         
          }


external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
                "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.layout = html.Div(
    children =[
        html.Div(
            children=[
                html.H1(children= "Mapa de incendios de la República Argentina", className = "header-title"),
                html.P(
                    children = " Se denomina Incendio forestal a cualquier fuego que se extiende sin control en terreno forestal afectando vegetación \
                        que no estaba destinada a arder. Datos del Ministerio de Ambiente y Desarrollo Sostenible. Dirección Nacional de Bosques. \
                        Seleccione año y tipo de incendio:", className ="header-description"
                ),
            ],
            className="header",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="Años", className="menu-title"),
                        dcc.Dropdown(
                            id='select_anios', 
                            options=[{'label': k, 'value': k} for k in YEARS],
                            value=YEARS[0],
                            className ="dropdown",
                    ),
                ] 
        ),
        html.Div(
            children=[
                html.Div(children="Representación", className="menu-title"),
                dcc.Dropdown(
                id='select_causa', 
                options=[{'label': k, 'value': CAUSAS[k]} for k in CAUSAS],
                value='incendio_total_numero',
                 className ="dropdown",
                ),
            ],
            ),
        ],
        className="menu",
    ),
    html.Div(
        children=[
            html.Div(
                children= dcc.Graph(
                    id="choropleth"
                ),
                className="card",
            ),
        ],
        className = "wrapper",
    ),
    html.Div(
        children=[
            html.Footer( children ="Hecho por Pablo Perez https://pablofp92.github.io/data/ -  https://linkedin.com/in/pablofprz",
               className  = "footer"
            ),
        ],
        className = "footer",
    ),
    
 ]
)


@app.callback(
    Output("choropleth", "figure"), 
    [Input("select_anios", "value"),
     Input("select_causa", "value")])



def display_choropleth(anio, causa):
    data_select =  df[df.incendio_anio == int(anio)]

    fig = px.choropleth(
        data_select, geojson=provincias_shape, color=str(causa),
        locations="Provincia", featureidkey="properties.nam",
        projection="mercator", 
        scope = 'south america')
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.update_layout(title=f"<b>{anio}</b>", title_x=0.5)

    return fig    



if __name__ == "__main__":
    app.run_server(debug=False)
