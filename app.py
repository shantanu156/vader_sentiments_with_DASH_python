##############################################################################
                                # Loading libraries
##############################################################################

#pip install dash
#pip install pandas
#pip install yfinance
#pip install scipy
#pip install dash-auth
#pip install plotly
#pip install dash_bootstrap_components
                                

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from datetime import datetime
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objs as go
import dash_auth
import dash_bootstrap_components as dbc
import matplotlib.pyplot as plt
from io import BytesIO
from wordcloud import WordCloud,STOPWORDS
import base64

# importing below class from fetch_sentiments
from fetch_sentiments import tweet_sentiments

##############################################################################
                               # Initiating Dash
##############################################################################

# specifying set of username and password allowed to access the web
USERNAME_PASSWORD_PAIRS = [['admin','password']]

external_stylesheets = ['/assets/style.css',dbc.themes.SOLAR]   # or CERULEAN

PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"

# Initiating Dash application here
app = dash.Dash(external_stylesheets=external_stylesheets)
app.title = "Sentiment Analyzer"
auth = dash_auth.BasicAuth(app,USERNAME_PASSWORD_PAIRS)
server = app.server


##############################################################################
                                # Front End
##############################################################################

# part of Navbar to add NavItem to navbar
contact = dbc.Row(
    [
        dbc.Col(dbc.NavItem(dbc.NavLink("About", href="https://en.wikipedia.org/wiki/Sentiment_analysis"))),
        dbc.Col(dbc.NavItem("Team Sentiments"),width='auto', style={'paddingLeft':20, 'color':'white'}),
    ],
    no_gutters=True,
    className="ml-auto flex-nowrap mt-3 mt-md-0",
    align="center",
    style={"paddingTop": 10},
)

# this add navbar
logo = dbc.Navbar(
    dbc.Container(
        
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(html.Img(src=PLOTLY_LOGO, height="45px"),style={'paddingRight':15}),
                        dbc.Col(dbc.NavbarBrand("Sentiment Analyzer", className="ml-2", style = {'fontSize':25})),
                    ],
                    align="left",
                    no_gutters=True,
                ),
                href="#",
            ),
            dbc.NavbarToggler(id="navbar-toggler"),
            dbc.Collapse(
                dbc.Nav(contact, className="ml-auto", navbar=True),
                id="navbar-collapse",
                navbar=True,
            ),
        ]
    ),
    color="dark",
    dark=True,
    className="mb-5",
    style = {'fontSize':18, 'height':80}
)


# Specifying color for background and text
colors = {
    'background': '#edf6f9',
    'text': '#000000'
}   


app.layout = html.Div(style={'backgroundColor': colors['background']},children=[
    logo, 

    dbc.Row(
            dbc.Col(
                    html.H3(' Enter tickers of company here:', 
                            style={'paddingRight':'30px',
                                    'textAlign': 'left',
                                    'fontSize':20,
                                    'margin':'30px 0px 15px 30px'}))),
    dbc.Row(
            dbc.Col(
                    dcc.Input(id='my_ticker_symbol',
                                value='TSLA,AAPL,FB',
                                style={'height':40, 
                                        'width':280, 
                                        'margin':'0px 0px 10px 30px',
                                        'fontSize':20}))),
    dbc.Row([
            dbc.Col(
                    html.H3(' Select start and end dates:',
                            style={'paddingRight':'30px',
                                    'textAlign': 'left',
                                    'fontSize':20,
                                    'margin':'30px 0px 15px 30px'})),
            dbc.Col(
                    html.H3(' Enter the keyword for Sentiment Analysis:', 
                            style={'textAlign': 'left',
                                    'margin':'30px 0px 15px 30px',
                                    'fontSize':20}))]),
    dbc.Row([
            dbc.Col(
                    dcc.DatePickerRange(id='my_date_picker',
                                        min_date_allowed=datetime(2005, 1, 1),
                                        max_date_allowed=datetime.today(),
                                        start_date=datetime(2016, 1, 1),
                                        end_date=datetime(2020, 12, 31),
                                        style={'height':40, 
                                                'margin':'0px 0px 10px 30px'})), 

            dbc.Col(
                    dbc.Button("Get Trend Line", color="info", className="mr-1",
                                n_clicks = 0,
                                id='submit-button',
                                style={'height':40,
                                        'fontSize':18, 
                                        'marginLeft':'-10px',
                                        'marginBottom':'20px',
                                        'textAlign':'center'})),
            dbc.Col(
                    dcc.Input(id='my_keyword',
                                value='#tesla',
                                style={'height':40, 
                                        'width':280, 
                                        'margin':'0px 0px 10px 30px',
                                        'fontSize':20})),
            dbc.Col(
                    dbc.Button("Fetch Sentiments", color="info", className="mr-1",
                                n_clicks = 0,
                                id='submit-button2',
                                style={'height':40,
                                        'fontSize':18, 
                                        'marginLeft':'0px',
                                        'marginBottom':'20px',
                                        'textAlign':'center'}))]),
    html.Hr(),
    html.Div([
        html.Div([
            dcc.Loading(id="loading-1", 
                        children=[dcc.Graph(id='my_graph1',figure={})], 
                        type="default")],
                        style={'width':'50%','display':'inline-block'}),
        html.Div([
            dcc.Loading(id="loading-2", 
                        children=[dcc.Graph(id='my_graph2',figure={})], 
                        type="default")],
                        style={'width':'50%','display':'inline-block'})
            ]),
    html.Div([
        html.H3(' Word Cloud', 
                style={'paddingRight':'30px',
                        'textAlign': 'center',
                        'fontSize':20,
                        'margin':'20px 0px 20px 0px'}),
        html.Div([
            dcc.Loading(id="loading-3", 
                        children=[html.Img(id='image_wc')], 
                        type="default")]),
        ], style={'text-align':'center', 'marginTop':'20px'})
])

##############################################################################
                            # Call Back for 1st Graph
##############################################################################


def plot_wordcloud(words):
    wc = WordCloud(background_color='white', width=1000, height=500, stopwords = STOPWORDS)
    word_text = ' '.join(words)
    wc.generate(word_text)
    return wc.to_image()


# In this callback, its generating Cummulative return graph of all the stocks entered
# Here there are multiple inputs and just one output graph
@app.callback(
    Output('my_graph1', 'figure'),
    [Input('submit-button', 'n_clicks')],
    [State('my_ticker_symbol', 'value'),
    State('my_date_picker', 'start_date'),
    State('my_date_picker', 'end_date')])
def update_graph(n_clicks, stock_ticker, start_date, end_date):
    
    # Update graph only after user clicks on Submit button
    if n_clicks is not None and n_clicks > 0:
        
        # Converting the entered dates into Date Time object in python
        start = datetime.strptime(start_date[:10], '%Y-%m-%d')
        end = datetime.strptime(end_date[:10], '%Y-%m-%d')
        
        # Converting the added stock tickers into list of stocks to process
        stock_ticker  = stock_ticker.split(",")
        
        # Adding the stocks together to show them on trend line
        stock_ticker = list(set(stock_ticker))
        
        # Below code add all the data into the graph as per requirement.
        # Here we are calculating the cummulative sum of the percent change
        # day wise so to reflect how the stock is performing.
        traces = []
        for tic in stock_ticker:
            # Downloading the stock data as per entered dates and tickers
            df = yf.download(tic, start=start, end=end)
            # Calculating cummulative percent change of "Adj Close" of each stock
            df = ((df["Adj Close"].pct_change()+1).cumprod())
            traces.append({'x':df.index, 'y': df, 'name':tic})
            
        # Passing the data collected above in below code to reflect the graph
        # as per entered stock tickers.
        fig = {'data': traces,
               'layout': {'title':', '.join(stock_ticker)+' Cummulative Returns',
                          'plot_bgcolor': colors['background'],
                          'paper_bgcolor': colors['background'],
                          'xaxis' : {'title': 'Year','automargin':True},
                          'yaxis' : {'title': 'Cummulative Return','automargin':True},
                          'font': {'color': colors['text']}}
               }
        
        # Retuning 'fig' as the output graph to show on dashboard
        return fig
    
    # If user has not clicked the Submit button below code just shows the 
    # skeleton of the graph which is completely empty.
    else:
        fig={'layout': {
                'plot_bgcolor': colors['background'],
                'paper_bgcolor': colors['background'],
                'title':'Cummulative Return',
                'xaxis' : {'title': 'Year','automargin':True},
                'yaxis' : {'title': 'Cummulative Return','automargin':True},
                'font': {'color': colors['text']}}
                }
        
        # Returning 'fig' as the output graph to show on dashboard
        return fig
    

##############################################################################
                            # Call Back for other Graphs
##############################################################################


@app.callback(
    [Output('my_graph2', 'figure'),
     Output('image_wc', 'src')],
    Input('submit-button2', 'n_clicks'),
    State('my_keyword', 'value'))
def update_graph2(n_clicks, my_keyword):
    
    # Update graph only after user clicks on Submit button
    if n_clicks is not None and n_clicks > 0:
        
        search_term = my_keyword
        
        fetch_results   = tweet_sentiments(search_term)
        [df,word_cloud] = fetch_results.get_tweet_sentiment()
        
        traces = []
        traces.append({'x':df.Date, 'y': df.positive*5, 'name':'Positive'})
        traces.append({'x':df.Date, 'y': df.negative*5, 'name':'Negative'})
        # traces.append({'x':df.Date, 'y': df.neutral, 'name':'Neutral'})
        
        
        img = BytesIO()
        plot_wordcloud(word_cloud).save(img, format='PNG')
        fig2 = 'data:image/png;base64,{}'.format(base64.b64encode(img.getvalue()).decode())
            
        # Passing the data collected above in below code to reflect the graph
        # as per entered stock tickers.
        fig1 = {'data': traces,
               'layout': {'title':'Sentiments',
                          'plot_bgcolor': colors['background'],
                          'paper_bgcolor': colors['background'],
                          'xaxis' : {'title': 'Date','automargin':True},
                          'yaxis' : {'title': 'Sentiments','automargin':True, 'range':[0,100]},
                          'font': {'color': colors['text']}}
                }
        
        
        # Below returning all the three graphs to show it on the dashboard
        return [fig1,fig2]
    
    # If user has not clicked the Submit button below code just shows the 
    # skeleton of the graph which is completely empty.
    else:
                
        fig1={'layout': {
                'title':'Sentiments',
                'plot_bgcolor' : colors['background'],
                'paper_bgcolor': colors['background'],
                'xaxis' : {'title': 'Date','automargin':True},
                'yaxis' : {'title': 'Sentiments','automargin':True},
                'font': {'color': colors['text']}}
                }
        
        # Returning 'fig' as the output graph to show on dashboard
        return [fig1,None]

# Run the defined application
if __name__ == '__main__':
    app.run_server()
