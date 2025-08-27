import pandas as pd
import dash
from dash import html, dcc, Input, Output
import plotly.express as px


spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H1(
        'SpaceX Launch Records Dashboard',
        style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}
    ),
    
    
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': '所有发射场', 'value': 'ALL'},
            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
        ],
        value='ALL',
        placeholder="在此选择发射场",
        searchable=True
    ),
    html.Br(),
    
    
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),
    
    html.P("Payload range (Kg):"),
    
    
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={i: f'{i}' for i in range(0, 10001, 2000)},  # 与max匹配的刻度
        value=[min_payload, max_payload]
    ),
    
    
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])  


@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    filtered_df = spacex_df.copy()
    
    if entered_site == 'ALL':
        success_counts = filtered_df.groupby('Launch Site')['class'].sum().reset_index()
        fig = px.pie(
            success_counts,
            values='class',
            names='Launch Site',
            title='各发射场成功发射次数'
        )
    else:
        site_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        outcome_counts = site_df['class'].value_counts().reset_index()
        outcome_counts.columns = ['outcome', 'count']
        outcome_counts['outcome'] = outcome_counts['outcome'].map({1: '成功', 0: '失败'})
        fig = px.pie(
            outcome_counts,
            values='count',
            names='outcome',
            title=f'{entered_site} 发射结果'
        )
    return fig

@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & 
                           (spacex_df['Payload Mass (kg)'] <= high)]
    
    if entered_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
    
    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title='载荷质量与发射成功相关性',
        labels={'class': '发射结果（1=成功，0=失败）'}
    )
    return fig

if __name__ == '__main__':
    app.run(debug=True)
