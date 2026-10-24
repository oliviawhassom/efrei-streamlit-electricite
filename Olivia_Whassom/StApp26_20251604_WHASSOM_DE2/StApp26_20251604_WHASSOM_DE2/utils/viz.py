import math
import plotly.express as px
import plotly.graph_objects as go

from utils.config import COLORS, GROUP_COLORS

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def _base(fig, title, height=420):
    fig.update_layout(
        title=dict(text=title, x=0),
        height=height,
        margin=dict(l=10, r=10, t=60, b=10),
        legend_title_text="",
        font=dict(size=13),
        plot_bgcolor="white",
    )
    fig.update_xaxes(showgrid=False, linecolor="#888")
    fig.update_yaxes(gridcolor="#e5e5e5")
    return fig


def area_chart(df, share=False):
    fig = px.area(
        df,
        x="month",
        y="gwh",
        color="source",
        color_discrete_map=COLORS,
        groupnorm="percent" if share else None,
    )
    if share:
        fig.update_yaxes(title="Share of production (%)")
        fig.update_traces(hovertemplate="%{x|%b %Y}<br>%{y:.1f} %<extra>%{fullData.name}</extra>")
    else:
        fig.update_yaxes(title="Production (GWh per month)")
        fig.update_traces(hovertemplate="%{x|%b %Y}<br>%{y:,.0f} GWh<extra>%{fullData.name}</extra>")
    fig.update_xaxes(title="Month")
    return _base(fig, "Monthly electricity production by source")


def line_chart(df, x, y, color, title, xtitle, ytitle, cmap=None, hline=None, height=420):
    fig = px.line(df, x=x, y=y, color=color, markers=True, color_discrete_map=cmap)
    fig.update_xaxes(title=xtitle, dtick=1)
    fig.update_yaxes(title=ytitle, rangemode="tozero")
    if hline is not None:
        fig.add_hline(y=hline[0], line_dash="dot", line_color="#666", annotation_text=hline[1], annotation_position="top left")
    fig.update_traces(hovertemplate="%{x}<br>%{y:.1f}<extra>%{fullData.name}</extra>")
    return _base(fig, title, height)


def bar_chart(df, x, y, title, xtitle, ytitle, color=None, cmap=None, height=420):
    # horizontal bars: x is the number, y is the category (names are long)
    fig = px.bar(df, x=x, y=y, orientation="h", color=color, color_discrete_map=cmap)
    fig.update_xaxes(title=xtitle)
    fig.update_yaxes(title=ytitle, autorange="reversed")
    fig.update_traces(hovertemplate="%{y}<br>%{x:,.1f}<extra></extra>")
    return _base(fig, title, height)


def map_chart(df, value, value_label):
    d = df.copy()
    d["size"] = d["total"].clip(lower=1)
    fig = px.scatter_mapbox(
        d,
        lat="lat",
        lon="lon",
        size="size",
        color=value,
        hover_name="region",
        hover_data={"lat": False, "lon": False, "size": False, value: ":,.1f", "total": ":,.0f"},
        color_continuous_scale="Viridis",
        size_max=45,
        zoom=4.2,
        center={"lat": 46.6, "lon": 2.5},
        mapbox_style="carto-positron",
        labels={value: value_label, "total": "Total (GWh)"},
    )
    fig.update_layout(height=520, margin=dict(l=0, r=0, t=40, b=0), title=dict(text="Regions on the map (bubble size = total production)", x=0))
    return fig


def small_multiples(df):
    n = df["region"].nunique()
    rows = math.ceil(n / 4)
    fig = px.line(
        df,
        x="year",
        y="renew_share",
        facet_col="region",
        facet_col_wrap=4,
        markers=True,
        color_discrete_sequence=[GROUP_COLORS["Renewable"]],
    )
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1], font=dict(size=11)))
    fig.update_yaxes(range=[0, 100], title_text="", gridcolor="#e5e5e5")
    fig.update_xaxes(title_text="", showgrid=False, tickformat="d", nticks=4)
    fig.update_traces(hovertemplate="%{x}<br>%{y:.1f} %<extra></extra>")
    fig.update_layout(
        height=230 * rows + 90,
        margin=dict(l=50, r=10, t=60, b=50),
        title=dict(text="Renewable share of production, one panel per region (same 0 to 100 % scale)", x=0),
        plot_bgcolor="white",
        font=dict(size=12),
    )
    fig.add_annotation(text="Year", x=0.5, y=-0.08, xref="paper", yref="paper", showarrow=False)
    fig.add_annotation(text="Renewable share (%)", x=-0.05, y=0.5, xref="paper", yref="paper", showarrow=False, textangle=-90)
    return fig


def box_chart(df, order):
    fig = px.box(
        df,
        x="region",
        y="renew_share",
        points="outliers",
        category_orders={"region": order},
        color_discrete_sequence=[GROUP_COLORS["Renewable"]],
    )
    fig.update_xaxes(title="Region", tickangle=-35)
    fig.update_yaxes(title="Monthly renewable share (%)", range=[0, 100])
    return _base(fig, "How much does the monthly renewable share vary inside each region?", 480)


def heatmap(pivot, source_label):
    fig = go.Figure(
        go.Heatmap(
            z=pivot.values,
            x=[str(c) for c in pivot.columns],
            y=[MONTH_NAMES[i - 1] for i in pivot.index],
            colorscale="YlOrRd",
            colorbar=dict(title="GWh"),
            hovertemplate="%{y} %{x}<br>%{z:,.0f} GWh<extra></extra>",
        )
    )
    fig.update_yaxes(title="Month", autorange="reversed")
    fig.update_xaxes(title="Year", type="category")
    return _base(fig, "Seasonality of " + source_label + " production (GWh per month)", 420)
