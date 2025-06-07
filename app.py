from dash import Dash, dependencies, Output, Input
from dash import html, dcc
from helper import product_dropdown, date_dropdown, ffsu_dropdown, map_df, product,dates, metric_dropdown, create_choropleth, state_data, plot_state_timeseries
from polars import col as c
import json
app = Dash(__name__)

app.layout = html.Div([
    product_dropdown(),
    date_dropdown(),
    ffsu_dropdown(),
    metric_dropdown(),
    html.H1("Dash Heatmap App"),
    dcc.Graph(id='heatmap-graph'),
    html.Div(id='state-chart'),
])

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
        return html.Div("Hover over a state to see the time series data.")
    product_id = product.filter(c.product == product_value).select(c.product_id).collect().item()
    state = (clickData['points'][0]['customdata'][0])
    data = state_data(state, product_id)

    return dcc.Graph(figure=plot_state_timeseries(data, state), id='state-timeseries-graph')


if __name__ == '__main__':
    app.run(debug=True)