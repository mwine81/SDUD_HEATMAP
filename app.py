from dash import Dash, dependencies, Output, Input
from dash import html, dcc
from helper import product_dropdown, date_dropdown, ffsu_dropdown, map_df, product,dates, metric_dropdown, state_data
from figures import create_choropleth, plot_state_timeseries
from polars import col as c
import json

app = Dash(__name__)

app.layout = html.Div([
    # Header Section
    html.Div([
        html.H1("Drug Pricing Analytics Dashboard", className="main-title"),
        html.P("Analyze NADAC and payment per unit pricing trends across states", 
               className="subtitle")
    ], className="header-section"),
    
    # Controls Section
    html.Div([
        html.Div([
            html.Label("Select Product:", className="control-label"),
            product_dropdown()
        ], className="control-group", style={"width": "100%", "gridColumn": "1 / -1"}),
        
        html.Div([
            html.Label("Select Date:", className="control-label"),
            date_dropdown()
        ], className="control-group"),
        
        html.Div([
            html.Label("FFSU Selection:", className="control-label"),
            ffsu_dropdown()
        ], className="control-group"),
        
        html.Div([
            html.Label("Select Metric:", className="control-label"),
            metric_dropdown()
        ], className="control-group"),
    ], className="controls-container"),
    
    # Main Chart Section
    html.Div([
        html.Div([
            html.H3("State-by-State Analysis", className="chart-title"),
            html.P("Click on a state to view detailed time series data", 
                   className="chart-subtitle"),
            dcc.Graph(id='heatmap-graph', className="main-chart")
        ], className="graph-container")
    ], className="main-chart-section"),
    
    # State Detail Section
    html.Div(id='state-chart', className="state-chart-section"),
    
], className="dashboard-container")

@app.callback(
    Output('heatmap-graph', 'figure'),
    [Input('product-dropdown', 'value'),
     Input('date-dropdown', 'value'),
     Input('ffsu-checklist', 'value'),
     Input('metric-dropdown', 'value')]
)
def update_heatmap(product_value, date_value, ffsu_value, metric_value):
    product_id = product.filter(c.product == product_value).select(c.product_id).collect().item()
    date_id = dates.filter(c.formatted_date == date_value).select(c.date_id).collect().item()
    
    df = map_df(date_id, product_id, ffsu_value)

    return create_choropleth(df, metric_value)


@app.callback(
    Output('state-chart', 'children'),
    Input('heatmap-graph', 'clickData'),
    Input('product-dropdown', 'value')
    )
def display_hover_data(clickData, product_value):
    if clickData is None:
        return html.Div([
            html.Div([
                html.I(className="fas fa-chart-line", style={"fontSize": "3rem", "color": "#64748b", "marginBottom": "1rem"}),
                html.H4("Select a State to View Time Series", style={"color": "#64748b", "marginBottom": "0.5rem"}),
                html.P("Click on any state in the map above to see pricing trends over time", 
                       style={"color": "#94a3b8", "fontSize": "1.1rem"})
            ], style={
                "textAlign": "center", 
                "padding": "3rem 2rem",
                "backgroundColor": "#ffffff",
                "borderRadius": "8px",
                "border": "2px dashed #e2e8f0",
                "margin": "2rem 0"
            })
        ])
    
    product_id = product.filter(c.product == product_value).select(c.product_id).collect().item()
    state = (clickData['points'][0]['customdata'][0])
    data = state_data(state, product_id)

    return html.Div([
        html.Div([
            html.H3(f"Time Series Analysis - {state}", className="chart-title"),
            html.P("Historical pricing trends for the selected product and state", 
                   className="chart-subtitle"),
            dcc.Graph(figure=plot_state_timeseries(data, state), id='state-timeseries-graph', className="detail-chart")
        ], className="graph-container")
    ])


if __name__ == '__main__':
    app.run(debug=True, port=8051)