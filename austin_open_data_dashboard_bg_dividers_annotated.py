# ------------------------------------------
# City of Austin Open Data Dashboard (Dash)
# Tabs: PARD 311 & Traffic Incidents
# Features: Year dropdown filter, background images, visual dividers
# Author: Tanvi Sharma (PyTexas 2025)
# ------------------------------------------


import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

# Initialize the Dash app
app = Dash(__name__)

# Load and process PARD 311 data
df_pard = pd.read_csv("PARD_311_Data_20250411.csv")
df_pard['Created Date'] = pd.to_datetime(df_pard['Created Date'], errors='coerce')
df_pard['Year'] = df_pard['Created Date'].dt.year

# Load and process Traffic data
df_traffic = pd.read_csv("RealTime_Traffic_Incident_Reports_20250411.csv")
df_traffic['Published Date'] = pd.to_datetime(df_traffic['Published Date'], errors='coerce')
df_traffic['Year'] = df_traffic['Published Date'].dt.year
df_traffic['Published Date Only'] = df_traffic['Published Date'].dt.date

# Define layout and structure of the app
app.layout = html.Div([
    html.Link(rel='stylesheet', href='/assets/styles.css'),
    html.H1("City of Austin Open Data Dashboard", style={'textAlign': 'center'}),
    dcc.Tabs(id="tabs", value='tab-pard', children=[
        dcc.Tab(label='PARD 311', value='tab-pard'),
        dcc.Tab(label='Traffic Incidents', value='tab-traffic'),
    ]),
    html.Div(id='tabs-content')
])

# Update tab content dynamically based on active tab selection
@app.callback(Output('tabs-content', 'children'), Input('tabs', 'value'))
def render_tab(tab):
    if tab == 'tab-pard':
        years = sorted(df_pard['Year'].dropna().unique())
        options = [{'label': 'All Years', 'value': 'all'}] + [{'label': str(y), 'value': y} for y in years]
        return html.Div([
            html.Label("Filter by Year:", style={'color': 'white'}),
            dcc.Dropdown(id='pard-year-dropdown', options=options, value='all'),
            html.Div(id='pard-charts', className='tab-section pard-bg')
        ])
    elif tab == 'tab-traffic':
        years = sorted(df_traffic['Year'].dropna().unique())
        options = [{'label': 'All Years', 'value': 'all'}] + [{'label': str(y), 'value': y} for y in years]
        return html.Div([
            html.Label("Filter by Year:", style={'color': 'white'}),
            dcc.Dropdown(id='traffic-year-dropdown', options=options, value='all'),
            html.Div(id='traffic-charts', className='tab-section traffic-bg')
        ])

# Update PARD 311 plots based on selected year
@app.callback(Output('pard-charts', 'children'), Input('pard-year-dropdown', 'value'))
def update_pard_charts(selected_year):
    filtered_df = df_pard.copy() if selected_year == 'all' else df_pard[df_pard['Year'] == selected_year]
    year_label = "All Years" if selected_year == 'all' else str(selected_year)

    top_types = filtered_df['SR Description'].value_counts().head(10).reset_index()
    top_types.columns = ['SR Description', 'Count']
    timeline = filtered_df.groupby(filtered_df['Created Date'].dt.date).size().reset_index(name='Request Count')

    return [
        html.Div(dcc.Graph(figure=px.bar(top_types, x='SR Description', y='Count',
                 title=f'Top PARD 311 Service Requests - {year_label}')), className='graph-block'),
        html.Hr(),
        html.Div(dcc.Graph(figure=px.line(timeline, x='Created Date', y='Request Count',
                 title=f'PARD 311 Requests Over Time - {year_label}')), className='graph-block')
    ]

# Update Traffic Incident plots based on selected year
@app.callback(Output('traffic-charts', 'children'), Input('traffic-year-dropdown', 'value'))
def update_traffic_charts(selected_year):
    filtered_df = df_traffic.copy() if selected_year == 'all' else df_traffic[df_traffic['Year'] == selected_year]
    year_label = "All Years" if selected_year == 'all' else str(selected_year)

    top_types = filtered_df['Issue Reported'].value_counts().head(10).reset_index()
    top_types.columns = ['Issue Reported', 'Count']
    timeline = filtered_df.groupby('Published Date Only').size().reset_index(name='Incident Count')

    return [
        html.Div(dcc.Graph(figure=px.bar(top_types, x='Issue Reported', y='Count',
                 title=f'Top Traffic Incident Types - {year_label}')), className='graph-block'),
        html.Hr(),
        html.Div(dcc.Graph(figure=px.line(timeline, x='Published Date Only', y='Incident Count',
                 title=f'Traffic Incidents Over Time - {year_label}')), className='graph-block')
    ]

# Run the Dash server locally
if __name__ == '__main__':
    app.run(debug=True)
