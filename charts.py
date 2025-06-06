#%%
import plotly.express as px
import plotly.graph_objects as go
import polars as pl
from polars import col as c
import pandas as pd

schema = {'state': pl.String, 'units': pl.Float64, 'rx_count': pl.Float64, 'total': pl.Float64, 'medicaid_reimbursed': pl.Float64, 'nadac': pl.Float64, 'markup_per_unit': pl.Float64, 'payment_per_unit': pl.Float64, 'nadac_per_unit': pl.Float64}

example_data = pl.scan_parquet(r"C:\Users\mwine\Downloads\download.parquet")


metric = ['markup_per_unit', 'payment_per_unit']

def create_choropleth(data: pl.LazyFrame, metric: str = metric[0]):
    """
    Create a choropleth map using Plotly Express.

    Args:
        data (pl.LazyFrame): Polars LazyFrame containing the data.
        metric (str): The metric to visualize on the map.

    Returns:
        plotly.graph_objects.Figure: A Plotly figure object for the choropleth map.
    """
    # fields that are currency are total, medicaid_reimbursed, nadac, markup_per_unit, payment_per_unit, nadac_per_unit
    currency_fields = {'total', 'medicaid_reimbursed', 'nadac', 'markup_per_unit', 'payment_per_unit', 'nadac_per_unit'}
    
    # Collect the data
    df = data.collect()
    
    # Determine if the metric is a currency field
    is_currency = metric in currency_fields
    
    # Create the choropleth map
    fig = px.choropleth(
        df, 
        locations='state', 
        locationmode="USA-states", 
        color=metric, 
        scope="usa",
        color_continuous_scale="Viridis",
        title=f"{metric.replace('_', ' ').title()} by State"
    )
    
    # Update layout for professional appearance
    fig.update_layout(
        title={
            'text': f"{metric.replace('_', ' ').title()} by State",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'family': 'Arial, sans-serif'}
        },
        font={'family': 'Arial, sans-serif'},
        coloraxis_colorbar={
            'title': {
                'text': metric.replace('_', ' ').title(),
                'font': {'size': 14}
            },
            'tickfont': {'size': 12}
        },
        geo={
            'showframe': False,
            'showcoastlines': True,
            'projection_type': 'albers usa'
        },
        width=900,
        height=600
    )
    
    # Format currency fields appropriately
    if is_currency:
        fig.update_coloraxes(
            colorbar_tickformat='$,.2f'
        )
        fig.update_traces(
            hovertemplate='<b>%{location}</b><br>' +
                         f'{metric.replace("_", " ").title()}: $%{{z:,.2f}}<extra></extra>'
        )
    else:
        fig.update_traces(
            hovertemplate='<b>%{location}</b><br>' +
                         f'{metric.replace("_", " ").title()}: %{{z:,.2f}}<extra></extra>'
        )
    
    return fig

load_date_id_table = pl.scan_parquet('data/date_id_filtered.parquet')

def state_data(state, product_id):
    return (
    pl.scan_parquet('data/sdud.parquet')
    .filter(c.product_id == product_id)
    .filter(c.state == state)
    .group_by(c.date_id)
    .agg(pl.col(pl.Float64).sum().round(4))
    .join(load_date_id_table, on='date_id')
    .with_columns(pl.date(c.year,c.quarter.cast(pl.String).replace({'1':1, '2':4, '3':7, '4':10}).cast(pl.Int8), 1))
    .sort('date')
    .with_columns(
    # calculate total_per_unit
    total_per_unit=(c.total / c.units).round(4),
    # calculate nadac_per_unit
    nadac_per_unit=(c.nadac / c.units).round(4),
    # calculate payment_per_unit
    payment_per_unit=((c.total / c.units).round(4)
    )
    ))

state_df = state_data('CA', 200)

def plot_state_timeseries(state_df: pl.LazyFrame, state: str = "State"):
    """
    Plots a time series line chart for nadac_per_unit and payment_per_unit from a Polars LazyFrame.

    Args:
        state_df (pl.LazyFrame): Polars LazyFrame with 'date', 'nadac_per_unit', and 'payment_per_unit' columns.
        state (str): State abbreviation for the chart title.

    Returns:
        plotly.graph_objects.Figure: The time series line chart.
    """
    df = state_df.collect().sort("date")
    df = df.select([
        pl.col("date"),
        pl.col("nadac_per_unit"),
        pl.col("payment_per_unit")
    ])
    
    # Rename columns for better legend display
    df = df.rename({
        "nadac_per_unit": "NADAC per Unit", 
        "payment_per_unit": "Payment per Unit"
    })
    
    # Melt to long format for plotly express
    df_long = df.unpivot(
        index=["date"],
        on=["NADAC per Unit", "Payment per Unit"],
        variable_name="Metric",
        value_name="Value"
    )
    df_long_pd = df_long.to_pandas()

    # Professional color scheme
    fig = px.line(
        df_long_pd,
        x="date",
        y="Value",
        color="Metric",
        markers=True,
        color_discrete_map={
            "NADAC per Unit": "#2E86AB",
            "Payment per Unit": "#F24236"
        },
        labels={
            "date": "Date",
            "Value": "Price per Unit ($)",
            "Metric": ""
        }
    )

    # Enhanced styling for each trace
    for i, trace in enumerate(fig.data):
        trace.update(
            line=dict(width=4, shape='spline', smoothing=0.3),
            marker=dict(size=8, line=dict(width=2, color='white')),
            hovertemplate="<b>%{fullData.name}</b><br>" +
                         "Date: %{x|%b %Y}<br>" +
                         "Price: $%{y:,.2f}<extra></extra>"
        )
        # Add different line style for second metric
        if i == 1:
            trace.update(line=dict(width=4, dash='dash', shape='spline', smoothing=0.3))

    fig.update_layout(
        title={
            "text": f"<b>NADAC vs Payment Price Comparison - {state}</b>",
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 26, "family": "Arial, sans-serif", "color": "#2c3e50"}
        },
        xaxis=dict(
            title=dict(text="<b>Date</b>", font=dict(size=16, color="#2c3e50")),
            tickformat="%b '%y",
            showgrid=True,
            gridcolor="rgba(128, 128, 128, 0.2)",
            gridwidth=1,
            tickfont=dict(size=14),
        
            showline=True,
            linewidth=2,
            linecolor="#bdc3c7"
        ),
        yaxis=dict(
            title=dict(text="<b>Price per Unit ($)</b>", font=dict(size=16, color="#2c3e50")),
            tickprefix="$",
            tickformat=",.2f",
            showgrid=True,
            gridcolor="rgba(128, 128, 128, 0.2)",
            gridwidth=1,
            tickfont=dict(size=14),
            showline=True,
            linewidth=2,
            linecolor="#bdc3c7",
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor="#ecf0f1"
        ),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.98,
            xanchor="right",
            x=0.98,
            font=dict(size=14, family="Arial, sans-serif"),
            bgcolor="rgba(248, 249, 250, 0.9)",
            bordercolor="#bdc3c7",
            borderwidth=1,
            itemsizing="constant"
        ),
        font=dict(family="Arial, sans-serif", size=14, color="#2c3e50"),
        plot_bgcolor="white",
        paper_bgcolor="#fafbfc",
        width=1100,
        height=650,
        margin=dict(l=80, r=80, t=100, b=80),
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor="white",
            bordercolor="#bdc3c7",
            font=dict(size=13, family="Arial, sans-serif")
        )    )

    return fig

plot_state_timeseries(state_df, 'WV')

#create_choropleth(example_data, metric[0])
# %%
