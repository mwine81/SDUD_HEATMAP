---
title: Sdud Nadac
marimo-version: 0.13.15
---

```python {.marimo}
import marimo as mo
import polars as pl
from polars import col as c
import polars.selectors as cs
import plotly.express as px
import plotly.graph_objects as go
# load data/sdud.parquet in lazy mode
sdud = pl.scan_parquet('data/sdud.parquet')
# load data/product_ids.parquet in lazy mode
product_ids = pl.scan_parquet('data/product_id.parquet')
# load data/date_id.parquet in lazy mode
date_id = pl.scan_parquet('data/date_id_filtered.parquet')
```

```python {.marimo}

def create_selection(data, key_col, value_col, start_value = 0):
    key = data.select(key_col).collect().to_series().to_list()
    value = data.select(value_col).collect().to_series().to_list()
    return mo.ui.dropdown({k:v for k, v in zip(key, value)}, value=key[0], searchable=True)
    
date_selection = create_selection(date_id, 'formatted_date', 'date_id',start_value=-1)
brand_generic = mo.ui.dropdown({"Brand":1, 'Generic':0}, value='Brand')
brand_selection = create_selection(product_ids.filter(c.is_brand), 'product', 'product_id')
generic_selections = create_selection(product_ids.filter(c.is_brand == False), 'product', 'product_id')
ffsu_dropdown = mo.ui.dropdown(options={'FFSU':[True],'MCOU':[False],'ALL':[True, False]}, value='ALL')
metric = mo.ui.dropdown(options={'Markup per Unit': 'markup_per_unit', 'Payment per Unit': 'payment_per_unit'}, value='Markup per Unit')
```

```python {.marimo}
product_selection =brand_selection if brand_generic.value else generic_selections 
```

```python {.marimo hide_code="true"}
[
date_selection,
brand_generic,
product_selection,
ffsu_dropdown,
metric
]
```

```python {.marimo hide_code="true"}
def markup_per_unit() -> pl.Expr:
    return ((c.total - c.nadac) / c.units).round(2).alias('markup_per_unit')

def payment_per_unit() -> pl.Expr:
    return (c.total / c.units).round(2).alias('payment_per_unit')

def nadac_per_unit():
    return (c.nadac / c.units).round(2).alias('nadac_per_unit')

data = (
sdud
.filter(c.date_id == date_selection.value)
#  filter by brand or generic based on brand_generic value
.filter(
c.product_id == product_selection.value
)
.filter(c.is_ffsu.is_in(ffsu_dropdown.value))
.group_by('state')
.agg(pl.col(pl.Float64).sum())
.with_columns(markup_per_unit(),payment_per_unit(), nadac_per_unit())
)
```

```python {.marimo hide_code="true"}
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

chart = mo.ui.plotly(create_choropleth(data, metric.value))
```

```python {.marimo}
chart
```

```python {.marimo}
data.sort(c.state).collect()
```

```python {.marimo}
states = data.select(c.state).unique().sort('state').collect().to_series().to_list()

state_selection = mo.ui.dropdown(states, value=states[0], searchable=True)
state_selection


```

```python {.marimo}
def state_data(state, product_id):
    return (
        pl.scan_parquet('data/sdud.parquet')
        .filter(c.product_id == product_id)
        .filter(c.state == state)
        .group_by(c.date_id)
        .agg(pl.col(pl.Float64).sum().round(4))
        .join(date_id, on='date_id')
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

```

```python {.marimo}
state_df = state_data(state_selection.value, product_selection.value)
state_df.collect()
```

```python {.marimo}


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
    # Melt to long format for plotly express
    df_long = df.unpivot(
        index=["date"],
        on=["nadac_per_unit", "payment_per_unit"],
        variable_name="Metric",
        value_name="Value"
    )
    df_long_pd = df_long.to_pandas()

    fig = px.line(
        df_long_pd,
        x="date",
        y="Value",
        color="Metric",
        markers=True,
        line_dash="Metric",
        color_discrete_map={
            "nadac_per_unit": "#1f77b4",
            "marked_up_per_unit": "#ff7f0e"
        },
        labels={
            "date": "Date",
            "Value": "Dollars per Unit",
            "Metric": ""
        },
        title=f"NADAC & Marked Up per Unit Over Time ({state})"
    )

    fig.update_traces(
        hovertemplate="Date: %{x|%b %Y}<br>%{legendgroup}: $%{y:,.2f}<extra></extra>",
        line=dict(width=3),
        marker=dict(size=6)
    )

    fig.update_layout(
        title={
            "text": f"NADAC & Marked Up per Unit Over Time ({state})",
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 22, "family": "Arial, sans-serif"}
        },
        xaxis=dict(
            title="Date",
            tickformat="%b %Y",
            showgrid=True,
            gridcolor="#e5e5e5",
            tickfont=dict(size=13)
        ),
        yaxis=dict(
            title="Dollars per Unit",
            tickprefix="$",
            showgrid=True,
            gridcolor="#e5e5e5",
            tickfont=dict(size=13)
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(size=14)
        ),
        font=dict(family="Arial, sans-serif"),
        plot_bgcolor="white",
        width=950,
        height=550,
        margin=dict(l=60, r=30, t=80, b=60)
    )

    return fig


mo.ui.plotly(plot_state_timeseries(state_df, state_selection.value))
```

```python {.marimo}

```