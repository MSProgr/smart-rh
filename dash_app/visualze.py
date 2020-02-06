import dash
import dash_core_components as dcc 
import dash_html_components as html 
from dash.dependencies import Input,Output

import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

df = pd.read_csv('test.csv')

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
	dcc.Dropdown(id='the_continent',options=[{'label':c,'value':c} for c in df['continent'].unique()]),
	html.Br(),
	dcc.Dropdown(id='the_column',options=[{'label':c,'value':c} for c in df.columns]),
	dcc.Graph(id='my_graph'),
	html.Br(),
	dcc.Slider(id='my_slider',min=df['year'].min(),max=df['year'].max(),value=df['year'].min(),
		marks={str(year):str(year) for year in df['year'].unique()},step=None),

	html.Br(),

    dcc.Graph(id='the_graph'),
    dcc.Slider(id='the_slider',min = df['year'].min(),max=df['year'].max(),value=df['year'].min(),
    	marks={str(year):str(year) for year in df['year'].unique()},step=None)
])

@app.callback(Output('the_graph','figure'),[Input('the_slider','value')])
def update_figure(slider_value):
	try:
		extracted = df[df['year']==slider_value]
		traces = []
		continent = extracted.continent.unique()
		for i in continent:
			continent_data = extracted[extracted['continent']==i]
			traces.append(dict(x=continent_data['gdpPercap'],y=continent_data['lifeExp'],text=continent_data['continent'],mode='markers',
				opacity=0.7,marker={'size': 15,'line': {'width': 0.5, 'color': 'white'}},name=i))
		return { 'data' : traces,
				'layout': dict(
			            xaxis={'type': 'log', 'title': 'GDP Per Capita','range':[2.3, 4.8]},
			            yaxis={'title': 'Life Expectancy', 'range': [20, 90]},
			            margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
			            legend={'x': 0, 'y': 1},
			            hovermode='closest',
			            transition = {'duration': 500},
			        )
				}
	except:
		return {}


@app.callback(Output('my_graph','figure'),[Input('the_continent','value'),Input('the_column','value'),Input('my_slider','value')])
def plot_continent_data(the_continent,the_column,year_value):
	try:
		continent_data = df[df['continent']==the_continent]
		dataset = continent_data[continent_data['year']==year_value]
		x = dataset['country']
		y = dataset[the_column]
		return {
			'data':[{'x':x,'y':y,'mode':'markers','text':dataset['country']+" - "+dataset['continent'],"opacity":0.7,
					'marker':{'size': 15,'line': {'width': 0.5, 'color': 'white'}}}],
			'layout': dict(
			            margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
			            legend={'x': 0, 'y': 1},
			            hovermode='closest',
			            transition = {'duration': 500})
		}
	except:
		return {}



if __name__ == '__main__':
	app.run_server(debug=True)