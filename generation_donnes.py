import random
import datetime as dt
import pandas as pd
from utils.localtime import localised_year_interval, localise_date, localise_datetime
import numpy as np
from utils.singleton import SingletonMeta


class SingletonData(metaclass=SingletonMeta):
    def __init__(self, min_start_date: dt.date = None, max_end_date: dt.date = None):
        self.sd = localise_date(min_start_date)
        self.ed = localise_date(max_end_date)
        idx = pd.date_range(self.sd, self.ed, freq='5min')
        self.init_df = pd.DataFrame(index=idx, data={"valeur": np.random.rand(len(idx), )})

    def get_init_df(self, rand_days=0):
        sd = self.sd + dt.timedelta(days=random.randint(0, rand_days))
        ed = self.ed - dt.timedelta(days=random.randint(0, rand_days))
        return self.init_df.loc[sd: ed]


def generation_donnees(nombre_sites: int, date_debut: dt.datetime, date_fin: dt.datetime, model,
                       identifiant_max, export: bool, base, rand_days: int):
    liste_elements = []
    site = identifiant_max
    for i in range(nombre_sites):

        identifiant_max += 1

        courbe_du_site = SingletonData(date_debut.date(), date_fin.date()).get_init_df(rand_days=rand_days)


        courbe_du_site["id_site"] = str(site)
        courbe_du_site["dernier_flux"] = False
        courbe_du_site["identifiant_flux"] = np.random.randint(0, 10000, courbe_du_site.shape[0])
        if base == 'questdb':
            courbe_du_site["date_reception_flux"] = courbe_du_site.index.astype('datetime64[ns, Europe/Paris]')
            courbe_du_site["horodate"] = courbe_du_site.index.astype('datetime64[ns, Europe/Paris]')

        else:
            courbe_du_site["date_reception_flux"] = courbe_du_site.index
            courbe_du_site["horodate"] = courbe_du_site.index

        if export:
            courbe_du_site.to_csv(f'tmp/df_{site}.csv', index=False)
            liste_elements.append(f'tmp/df_{site}.csv')
        else:
            if base == 'mongo':  # or base == 'influxdb':
                liste_elements.extend(courbe_du_site.to_dict('records'))
            elif base == 'questdb' or base == 'influxdb':
                liste_elements.append(courbe_du_site)
            else:
                liste_elements.extend([model(**i) for i in courbe_du_site.to_dict('records')])


        site += 1
    return liste_elements, identifiant_max


def generation_pour_ajout_donnees(nombre_sites: int, date_debut: dt.datetime, date_fin: dt.datetime, model,
                                  identifiant_max, export: bool, base):
    liste_elements = []
    site = identifiant_max
    date_debut = localise_date(date_debut)
    date_fin = localise_date(date_fin)
    for i in range(nombre_sites):

        print(f'site={site}')
        identifiant_max += 1

        index = pd.date_range(date_debut, date_fin, freq="5min")

        valeurs_aleatoires = np.random.rand(len(index), 1)
        courbe_du_site = pd.DataFrame(valeurs_aleatoires, columns=["valeur"], index=index)
        courbe_du_site["id_site"] = str(site)
        courbe_du_site["dernier_flux"] = False
        courbe_du_site["identifiant_flux"] = np.random.randint(0, 10000, len(index))
        if base == 'questdb':
            courbe_du_site["date_reception_flux"] = courbe_du_site.index.map(pd.Timestamp.timestamp).astype('datetime64[ns, Europe/Paris]')
            courbe_du_site["horodate"] = courbe_du_site.index.map(pd.Timestamp.timestamp).astype('datetime64[ns, Europe/Paris]')

        else:
            courbe_du_site["date_reception_flux"] = courbe_du_site.index
            courbe_du_site["horodate"] = courbe_du_site.index

        if export:
            courbe_du_site.to_csv(f'tmp/df_{site}.csv', index=False)
            liste_elements.append(f'tmp/df_{site}.csv')
        else:
            if base == 'mongo':
                liste_elements.extend(courbe_du_site.to_dict('records'))
            elif base == 'questdb' or base == 'influxdb':
                liste_elements.append(courbe_du_site)
            else:
                liste_elements.extend([model(**i) for i in courbe_du_site.to_dict('records')])


        site += 1
    return liste_elements, identifiant_max
