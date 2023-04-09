# coding=utf-8
import pandas as pd
import geopandas
import matplotlib.pyplot as plt
import contextily as ctx
import sklearn.cluster
import numpy as np
# muzete pridat vlastni knihovny


def make_geo(df=pd.read_pickle("accidents.pkl.gz")) -> geopandas.GeoDataFrame:
    """ Konvertovani dataframe do geopandas.GeoDataFrame se spravnym kodovani"""
    df = df.dropna(subset=['d', 'e'])
    gdf = geopandas.GeoDataFrame(
        df, geometry=geopandas.points_from_xy(df.d, df.e), crs="EPSG:5514")
    return gdf


def plot_geo(gdf=make_geo(), fig_location: str = None,
             show_figure: bool = False):
    """ Vykresleni grafu s nehodami s alkoholem pro roky 2018-2021 """
    gdf['p2a'] = pd.to_datetime(gdf['p2a'])
    gdf['p2a'] = gdf['p2a'].dt.strftime('%Y')
    years = ['2018', '2019', '2020', '2021']
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    ax = axes.flatten()

    for i, year in enumerate(years):
        gdf[(gdf['p11'] >= 3) & (gdf['region'] == 'JHC') & (gdf['p2a'] == year)].plot(
            ax=ax[i], markersize=2)
        ctx.add_basemap(ax[i], crs=gdf.crs.to_string(), source=ctx.providers.Stamen.Terrain,
                        alpha=1)
        ax[i].set_axis_off()
        ax[i].set_title(f"JHC kraj ({year})")

    fig.suptitle('Pozice nehod pod vlivem alkoholu nebo drog', fontsize=17)

    if show_figure:
        plt.show()

    if fig_location:
        fig.savefig(fig_location)


def plot_cluster(gdf=make_geo(), fig_location: str = None,
                 show_figure: bool = False):
    """ Vykresleni grafu s lokalitou vsech nehod v kraji shlukovanych do clusteru """

    gdf = gdf[(gdf['region'] == 'JHC') & ((gdf['p36'] == 1)
                                          | (gdf['p36'] == 2) | (gdf['p36'] == 3))]

    """Zvolil jsem Agglomerative Clustering z duvodu NoN-Ellipsoidal formy a různé hůstoty dat.
       Zkoušel jsem takže tyto metody:
       * K-means - podobný výsledek, ale nevýhoda nastavovaní vhodného random state pro vyhovující výsledek
       * Gaussian Mixture - nevyhovující výsledek, předpokládám že se nejedná data s Gaussovým rozložením
       * DBSCAN - nevyhovující výsledek, protože příliš malá vzdálenost mezi daty
    """
    coords = np.dstack([gdf.geometry.x, gdf.geometry.y]).reshape(-1, 2)
    db = sklearn.cluster.AgglomerativeClustering(n_clusters=20).fit(coords)
    gdf_cluster = gdf.copy()
    gdf_cluster['cluster'] = db.labels_
    gdf_cnt = gdf_cluster.dissolve(
        by="cluster", aggfunc={"p1": "count"}).rename(columns=dict(p1="cnt"))

    fig = plt.figure(figsize=(16, 8))
    ax = plt.gca()
    gdf_cnt.plot(ax=ax, markersize=2, column=gdf_cnt['cnt'], legend=True)
    ctx.add_basemap(ax, crs=gdf.crs.to_string(),
                    source=ctx.providers.Stamen.TonerLite, zoom=10, alpha=1)
    plt.axis("off")
    plt.title('Nehody v JHC kraji na silnicích 1.,2. a 3. třídy', fontsize=17)

    if show_figure:
        plt.show()

    if fig_location:
        fig.savefig(fig_location)


if __name__ == "__main__":
    # zde muzete delat libovolne modifikace
    gdf = make_geo(pd.read_pickle("accidents.pkl.gz"))
    plot_geo(gdf, "geo1.png", True)
    plot_cluster(gdf, "geo2.png", True)
