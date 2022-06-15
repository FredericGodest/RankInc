import pandas as pd
import numpy as np
import plotly.graph_objects as go
from dotenv import dotenv_values
import os

def get_id():
    # PROD MOD
    if os.environ.get("ENV") == "PROD":
        id = os.environ.get("SHEET_ID")

    # TEST MOD
    else:
        config = dotenv_values(".env")
        id = config["SHEET_ID"]

    return id

def get_df():
    id = get_id()
    sheet_name = "EntrepriseFR"
    url = f"https://docs.google.com/spreadsheets/d/{id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

    df = pd.read_csv(url)

    col_list = []
    for col_name in df.columns:
        if not "Unnamed" in col_name:
            col_list.append(col_name)

    df = df[col_list]
    df = df.drop(["BPA", "Ticker Google", "Ticker", "dividende"], axis=1)
    df = df.set_index("Name")

    return df


def str2float(df):
    for col_name in df.columns:
        df[col_name] = df[col_name].str.replace(",", ".")
        df[col_name] = df[col_name].str.replace("TBD", "NaN")
        if col_name != "secteur":
            df[col_name] = df[col_name].astype(float)

    df = df[df["PER" ] >0]
    df = df[(df["Marge Brute [%]"].abs() < 100) & (df["Marge Nette [%]"].abs() < 100)]

    return df


def table_ranked(df, sector):
    df_secteur = df[df["secteur"] == sector]
    rank_list = {
        "capitalisation": [0.5, True],
        "rendement dividende [%]": [2, True],
        "payout ratio [%]": [5, False],
        "ROE": [6, True],
        "ROA": [4, True],
        "Marge Brute [%]": [7, True],
        "Marge Nette [%]": [6, True],
        "PER": [4, False],
        "Dette/Capitaux Propre [%]": [5, False],
        "Prog Profit [%]": [5, True]
    }

    for el in list(rank_list.keys()):
        ascended = rank_list[el][1]
        weight = rank_list[el][0]
        df_secteur[el + "_rank"] = df_secteur[el].rank(ascending=ascended) * weight

    rank_list_name = list(rank_list.keys())
    df_secteur["Total point"] = df_secteur[rank_list_name].sum(axis=1)
    df_secteur["Rank"] = df_secteur["Total point"].rank(ascending=False)

    save_col = [col for col in df_secteur.columns if not "_rank" in col]
    df_secteur = df_secteur[save_col].sort_values(by="Rank")
    df_secteur = df_secteur.drop("Total point", axis=1)

    return df_secteur

def plot_bar(df, sector):
    df_plot = df[df["secteur"] == sector].drop(["secteur", "capitalisation", "cours"], axis=1).mean()
    y = df_plot.to_numpy()
    x = df_plot.index

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=x,
        y=y,
        text=y,
        name='Moyennes du secteur',
        marker_color='blue'
    ))

    df_plot = df.drop(["secteur", "capitalisation", "cours"], axis=1).mean()
    y = df_plot.to_numpy()
    fig.add_trace(go.Bar(
        x=x,
        y=y,
        text=y,
        name='Moyennes du marché',
        marker_color='lightsalmon'
    ))

    fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    fig.update_layout(title=sector,
                      yaxis_title="valeur",
                      legend=dict(
                          x=0,
                          y=1.0,
                          bgcolor='rgba(255, 255, 255, 0)',
                          bordercolor='rgba(255, 255, 255, 0)'
                      ))

    return fig


def sector_analysis(df, sector):
    df_ranked = table_ranked(df, sector)
    fig = plot_bar(df, sector)

    return fig, df_ranked


def multiplot(df):
    figs = []
    multiplot_df = df.drop(["capitalisation", "cours"], axis=1).groupby(by=["secteur"]).mean()

    for col_name in multiplot_df.columns:
        y = multiplot_df[col_name].to_numpy()
        x = multiplot_df.index
        mean = multiplot_df[col_name].mean()

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=x,
            y=y,
            text=y,
            marker_color='blue'
        ))

        fig.add_hline(y=mean, line_width=2, line_color="lightsalmon")

        fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
        mean = "{:.2f}".format(mean)
        fig.update_layout(title=f"{col_name}, Moyenne = {mean}",
                          yaxis_title="valeur moyenne",
                          legend=dict(
                              x=0,
                              y=1.0,
                              bgcolor='rgba(255, 255, 255, 0)',
                              bordercolor='rgba(255, 255, 255, 0)'
                          ))
        figs.append(fig)

    return figs