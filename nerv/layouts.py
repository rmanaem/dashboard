"""Layout of the app."""
import datetime
import os

import dash_bootstrap_components as dbc
import plotly.express as px
from dash import dcc, html

from nerv.utility import DBC_THEMES, generate_summary


def navbar():
    """
    Generates the app navigation bar.

    Returns
    -------
    dash_bootstrap_components._components.Container.Container
        The navigation bar is made up of various dash bootstrap components
        and dash core components wrapped with a dash bootstrap componenets
        container component.
    """
    brand = dbc.NavLink(
        [
            html.I(className="bi bi-bar-chart-line-fill"),
            html.B(" Ne"),
            "uroimaging ",
            html.B("R"),
            "esults ",
            html.B("V"),
            "isualization",
        ],
        href="#",
    )

    home = dbc.NavLink("Home", href="/")

    docs = dbc.NavLink(
        "Docs",
        external_link=True,
        href="https://rmanaem.github.io/nerv/",
    )

    settings = dbc.NavLink(
        html.I(className="bi bi-gear-fill"),
        id="settings",
        href="#",
    )

    github = dbc.NavLink(
        html.I(className="bi bi-github"),
        external_link=True,
        href="https://github.com/rmanaem/nerv",
    )

    navbar = dbc.NavbarSimple(
        [home, docs, settings, github],
        brand=brand,
        fluid=True,
        sticky="top",
    )

    offcanvas = dbc.Offcanvas(
        [
            html.P("Theme: "),
            dcc.Dropdown(
                options=[{"label": str(i), "value": DBC_THEMES[i]} for i in DBC_THEMES],
                value=DBC_THEMES["BOOTSTRAP"],
                clearable=False,
                id="themes",
                persistence=True,
            ),
        ],
        id="offcanvas",
        placement="end",
        scrollable=True,
        title="Settings",
    )

    spinner = dbc.Spinner(
        [
            navbar,
            offcanvas,
            dcc.Store(id="store", storage_type="local"),
            dcc.Location(id="url"),
            html.Div(id="content"),
            html.Div(id="blank_output"),
        ],
        delay_hide=250,
        delay_show=250,
        fullscreen=True,
        type="grow",
    )

    return dbc.Container(
        spinner,
        fluid=True,
    )


def index_layout(path):
    """
    Generates the index page layout.

    Parameters
    ----------
    path : str
        Path of the directory of directories containing files to be visualized.

    Returns
    -------
    dash_bootstrap_components._components.Container.Container
        The index page layout made up of various dash bootstrap components
        and dash core components wrapped with a dash bootstrap componenets
        container component.
    """
    dirs = sorted([d for d in os.listdir(path)])
    return dbc.Container(
        [
            dcc.Link(
                [
                    dbc.Card(
                        [
                            html.H5(d),
                            html.P(
                                "Last modified: "
                                + datetime.datetime.fromtimestamp(
                                    os.path.getmtime(os.path.join(path, d))
                                ).strftime("%c"),
                                className="small",
                            ),
                        ],
                        body=True,
                    )
                ],
                href="/" + d,
                id=d,
                className="m-2 col-md-3 text-center",
            )
            for d in dirs
        ],
        className="d-flex flex-row flex-wrap justify-content-center align-items-center",
    )


def vis_layout(df):
    """
    Generates the visualization layout.

    Parameters
    ----------
    df : pandas.core.frame.DataFrame
        Dataframe containing the data for graphs.

    Returns
    -------
    dash_bootstrap_components._components.Tabs.Tabs
        The visualization layout made up of various dash bootstrap components and
        dash core components.
    """
    hist_plot = dcc.Graph(
        id="histogram",
        figure=px.histogram(
            df[df["Result"] != -1],
            x="Result",
            color="Dataset-Pipeline",
            color_discrete_map={
                k: v
                for k, v in zip(
                    df["Dataset-Pipeline"].unique().tolist(),
                    df["Color"].unique().tolist(),
                )
            },
            barmode="overlay",
            marginal="rug",
            hover_data=df.columns,
        )
        .update_layout(
            xaxis_title=r"$\text {Hippocampus Volume } (mm^3)$",
            yaxis_title="Count",
            xaxis={
                "rangeslider": {"visible": True},
                "range": [
                    -1000,
                    df["Result"].max() + 1000,
                ],
            },
        )
        .update_xaxes(
            ticks="outside",
            tickwidth=2,
            tickcolor="white",
            ticklen=10,
        ),
        config={"displaylogo": False},
        mathjax=True,
    )

    summary = generate_summary(df)

    hist_metadata = html.Div(id="hist-metadata-div")

    hist_tab = dbc.Tab(
        [
            dbc.Row(
                [
                    dbc.Col(hist_plot, width="9"),
                    dbc.Col(
                        [dbc.Row(dbc.Col(summary)), dbc.Row(dbc.Col(hist_metadata))]
                    ),
                ],
            ),
        ],
        label="Distribution Plot",
    )

    x_dropdown = dcc.Dropdown(
        id="x",
        options=[
            {
                "label": k,
                "value": v,
            }
            for k, v in zip(
                df["Dataset-Pipeline"].unique().tolist(),
                df["Dataset-Pipeline"].unique().tolist(),
            )
        ],
        value=df["Dataset-Pipeline"].unique().tolist()[0],
        placeholder="x",
    )

    y_dropdown = dcc.Dropdown(
        id="y",
        options=[
            {
                "label": k,
                "value": v,
            }
            for k, v in zip(
                df["Dataset-Pipeline"].unique().tolist(),
                df["Dataset-Pipeline"].unique().tolist(),
            )
        ],
        value=df["Dataset-Pipeline"].unique().tolist()[-1],
        placeholder="y",
    )

    scatter_plot = dcc.Graph(
        id="scatter",
        figure=px.scatter(
            df,
            x=df[df["Dataset-Pipeline"] == df["Dataset-Pipeline"].unique().tolist()[0]][
                "Result"
            ],
            y=df[
                df["Dataset-Pipeline"] == df["Dataset-Pipeline"].unique().tolist()[-1]
            ]["Result"],
            marginal_x="histogram",
            marginal_y="histogram",
            color_discrete_sequence=px.colors.qualitative.G10[::-1],
        ).update_layout(
            xaxis={"rangeslider": {"visible": True}},
            xaxis_title=df["Dataset-Pipeline"].unique().tolist()[0],
            yaxis_title=df["Dataset-Pipeline"].unique().tolist()[-1],
        ),
        config={"displaylogo": False},
    )

    scatter_metadata = html.Div(id="scatter-metadata-div")

    scatter_tab = dbc.Tab(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Row([dbc.Col(x_dropdown), dbc.Col(y_dropdown)]),
                            dbc.Row(dbc.Col(scatter_plot)),
                        ],
                        width="9",
                    ),
                    dbc.Col(scatter_metadata),
                ]
            )
        ],
        label="Joint Plot",
    )

    return dbc.Tabs(
        [hist_tab, scatter_tab],
    )
