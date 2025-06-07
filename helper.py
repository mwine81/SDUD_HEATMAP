import polars as pl
from polars import col as c 
import polars.selectors as cs
from config import sdud_path, product_path, dates_path
from dash import dcc
import plotly.express as px

# Lazy load dataframes
sdud = pl.scan_parquet(sdud_path)
product = pl.scan_parquet(product_path)
dates = pl.scan_parquet(dates_path)

def product_dropdown():
    """
    Create a dropdown component for product selection.
    """
    options = product.select(c.product).collect().to_series().to_list()
    return dcc.Dropdown(
        id="product-dropdown",
        options=options,
        value='metFORMIN HCl ER Oral Tablet Extended Release 24 Hour 500 MG',  # Default to the first product
        searchable=True,
        clearable=True,
        style={"width": "100%"},
    )

def date_dropdown():
    """
    Create a dropdown component for date selection.
    """
    options = dates.select(c.formatted_date).collect().to_series().to_list()
    return dcc.Dropdown(
        id="date-dropdown",
        options=options,
        value=options[-1],  # Default to the last date
        searchable=True,
        clearable=True,
        style={"width": "100%"},
    )

def ffsu_dropdown():
    """
    Create a dropdown component for FFSU selection.
    """
    return dcc.Checklist(
        id="ffsu-checklist",
        options=[
            {'label': 'FFSU', 'value': True},
            {'label': 'Non-FFSU', 'value': False}
        ],
        value=[True, False],  # Default to both options selected
        labelStyle={'display': 'block'},
    )

# metric dropdown
def metric_dropdown():
    """
    Create a dropdown component for metric selection.
    """
    return dcc.Dropdown(
        id="metric-dropdown",
        options=[
         'markup_per_unit', 'payment_per_unit'
        ],
        value='markup_per_unit',  # Default to markup_per_unit
        searchable=True,
        style={"width": "100%"},
    )

def markup_per_unit() -> pl.Expr:
    return ((c.total - c.nadac) / c.units).round(2).alias('markup_per_unit')

def payment_per_unit() -> pl.Expr:
    return (c.total / c.units).round(2).alias('payment_per_unit')

def nadac_per_unit():
    return (c.nadac / c.units).round(2).alias('nadac_per_unit')

def map_df(date_id, product_id, ffsu):
        return (
        sdud
        .filter(c.date_id == date_id)
        #  filter by brand or generic based on brand_generic value
        .filter(
        c.product_id == product_id)
        .filter(c.is_ffsu.is_in(ffsu))
        .group_by('state')
        .agg(pl.col(pl.Float64).sum())
        .with_columns(markup_per_unit(),payment_per_unit(), nadac_per_unit())
        )

def create_choropleth(data: pl.LazyFrame, metric: str):
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
        title=f"{metric.replace('_', ' ').title()} by State",
        custom_data=['state'],
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

def state_data(state, product_id):
    return (
        sdud
        .filter(c.product_id == product_id)
        .filter(c.state == state)
        .group_by(c.date_id)
        .agg(pl.col(pl.Float64).sum().round(4))
        .join(dates, on='date_id')
        .with_columns(
            pl.date(
                c.year,
                c.quarter.cast(pl.String).replace({'1': 1, '2': 4, '3': 7, '4': 10}).cast(pl.Int8),
                1
            ).alias("date")
        )
        .sort('date')
        .with_columns(
            # calculate total_per_unit
            total_per_unit=(c.total / c.units).round(4),
            # calculate nadac_per_unit
            nadac_per_unit=(c.nadac / c.units).round(4),
            # calculate payment_per_unit
            payment_per_unit=(c.total / c.units).round(4)
        )
    )

def plot_state_timeseries(state_df: pl.LazyFrame, state: str = "State"):
    """
    Plots an enhanced time series line chart for nadac_per_unit and payment_per_unit.

    Args:
        state_df (pl.LazyFrame): Polars LazyFrame with 'date', 'nadac_per_unit', and 'payment_per_unit' columns.
        state (str): State abbreviation for the chart title.

    Returns:
        plotly.graph_objects.Figure: The enhanced time series line chart.
    """
    # Optimize data processing with Polars
    df_long = (
        state_df
        .collect()
        .sort("date")
        .select([
            pl.col("date"),
            pl.col("nadac_per_unit"),
            pl.col("payment_per_unit")
        ])
        .unpivot(
            index=["date"],
            on=["nadac_per_unit", "payment_per_unit"],
            variable_name="Metric",
            value_name="Value"
        )
        .with_columns([
            pl.col("Metric").str.replace("_per_unit", "").str.replace("_", " ").str.to_titlecase().alias("Metric_Label")
        ])
        .to_pandas()
    )

    # Enhanced color scheme with better contrast
    color_map = {
        "nadac_per_unit": "#2E86AB",      # Professional blue
        "payment_per_unit": "#A23B72"     # Complementary magenta
    }
    
    # Create the line plot
    fig = px.line(
        df_long,
        x="date",
        y="Value",
        color="Metric",
        markers=True,
        color_discrete_map=color_map,
        labels={
            "date": "Date",
            "Value": "Price per Unit ($)",
            "Metric": ""
        }
    )

    # Enhanced trace styling
    fig.update_traces(
        hovertemplate="<b>%{fullData.name}</b><br>" +
                     "Date: %{x|%b %Y}<br>" +
                     "Price: $%{y:,.2f}<extra></extra>",
        line=dict(width=4),
        marker=dict(size=8, line=dict(width=2, color="white")),
        connectgaps=True
    )

    # Professional layout with enhanced styling
    fig.update_layout(
        title={
            "text": f"<b>Drug Pricing Comparison: NADAC vs Payment per Unit</b><br><sup>State: {state}</sup>",
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 24, "family": "Inter, Arial, sans-serif", "color": "#2c3e50"}
        },
        xaxis=dict(
            title=dict(
                text="<b>Date</b>",
                font=dict(size=16, color="#34495e")
            ),
            tickformat="%b %Y",
            showgrid=True,
            gridcolor="#ecf0f1",
            gridwidth=1,
            tickfont=dict(size=13, color="#7f8c8d"),
            showline=True,
            linewidth=2,
            linecolor="#bdc3c7",
            mirror=True,
            rangeslider=dict(
                visible=True,
                thickness=0.08,
                bgcolor="#f8f9fa",
                bordercolor="#dee2e6",
                borderwidth=2
            ),
            rangeselector=dict(
                buttons=[
                    dict(count=6, label="6M", step="month", stepmode="backward"),
                    dict(count=1, label="1Y", step="year", stepmode="backward"),
                    dict(count=2, label="2Y", step="year", stepmode="backward"),
                    dict(step="all", label="All")
                ],
                bgcolor="#f8f9fa",
                activecolor="#3498db",
                bordercolor="#dee2e6",
                borderwidth=1,
                font=dict(size=12, color="#495057"),
                x=0.01,
                y=1.02
            )
        ),
        yaxis=dict(
            title=dict(
                text="<b>Price per Unit ($)</b>",
                font=dict(size=16, color="#34495e")
            ),
            tickprefix="$",
            tickformat=",.2f",
            showgrid=True,
            gridcolor="#ecf0f1",
            gridwidth=1,
            tickfont=dict(size=13, color="#7f8c8d"),
            showline=True,
            linewidth=2,
            linecolor="#bdc3c7",
            mirror=True,
            zeroline=True,
            zerolinecolor="#e74c3c",
            zerolinewidth=2
        ),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.15,
            xanchor="center",
            x=0.5,
            font=dict(size=14, color="#2c3e50"),
            bgcolor="rgba(255, 255, 255, 0.9)",
            bordercolor="#bdc3c7",
            borderwidth=1,
            itemsizing="constant"
        ),
        font=dict(family="Inter, Arial, sans-serif"),
        plot_bgcolor="#ffffff",
        paper_bgcolor="#fafbfc",
        width=1000,
        height=600,
        margin=dict(l=80, r=40, t=120, b=120),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="rgba(255, 255, 255, 0.95)",
            bordercolor="#bdc3c7",
            font_size=13,
            font_family="Inter, Arial, sans-serif"
        ),
        # Add subtle shadow effect
        annotations=[
            dict(
                text="Data shows pricing trends over time",
                xref="paper", yref="paper",
                x=1, y=0,
                xanchor="right", yanchor="bottom",
                showarrow=False,
                font=dict(size=11, color="#95a5a6"),
                bgcolor="rgba(255, 255, 255, 0.8)",
                bordercolor="#ecf0f1",
                borderwidth=1
            )
        ]
    )

    # Add professional styling touches
    fig.update_xaxes(
        showspikes=True,
        spikecolor="#95a5a6",
        spikesnap="cursor",
        spikemode="across",
        spikethickness=1
    )
    
    fig.update_yaxes(
        showspikes=True,
        spikecolor="#95a5a6",
        spikesnap="cursor",
        spikemode="across",
        spikethickness=1
    )
    
    return fig
