import random
import datetime as dt
from zoneinfo import ZoneInfo

import pandas as pd

from utils.localtime import localised_year_interval
import numpy as np

def generation_donnees_pandas(annee_debut: int, annee_fin: int):
    sd, ed = localised_year_interval([annee_debut, annee_fin])
    idx = pd.date_range(sd, ed, freq="5min")
    data = np.random.rand(len(idx), 1)
    df = pd.DataFrame(data, index=idx)
    df.columns = ["valeur"]
    return df


def generation_donnees(nombre_sites: int, dates_debut: list | dt.datetime, dates_fin: list | dt.datetime, model, identifiant_max, export: bool, base):
    zone = ZoneInfo("UTC")
    liste_elements = []
    site = identifiant_max
    for i in range(nombre_sites):

        print(f'site={site}')
        identifiant_max += 1

        if isinstance(dates_debut, dt.datetime):
            index = pd.date_range(dates_debut.astimezone(zone), dates_fin.astimezone(zone), freq="5min")
        else:
            date_debut = dt.datetime(random.randint(dates_debut[0].year, dates_debut[1].year), random.randint(dates_debut[0].month, dates_debut[1].month), random.randint(dates_debut[0].day, dates_debut[1].day), random.randint(dates_debut[0].hour, dates_debut[1].hour), random.choice([0,5,10,15,20,25,30,35,40,45,50,55])).astimezone(zone)
            date_fin = dt.datetime(random.randint(dates_fin[0].year, dates_fin[1].year), random.randint(dates_fin[0].month, dates_fin[1].month), random.randint(dates_fin[0].day, dates_fin[1].day), random.randint(dates_fin[0].hour, dates_fin[1].hour), random.choice([0,5,10,15,20,25,30,35,40,45,50,55])).astimezone(zone)
            index = pd.date_range(date_debut, date_fin, freq="5min")
            print(f'date_debut={date_debut}')
        valeurs_aleatoires = np.random.rand(len(index), 1)
        courbe_du_site = pd.DataFrame(valeurs_aleatoires, columns=["valeur"], index=index)
        courbe_du_site["id_site"] = site
        courbe_du_site["dernier_flux"] = False
        courbe_du_site["identifiant_flux"] = np.random.randint(0, 10000, len(index))
        if base == 'questdb':
            courbe_du_site["date_reception_flux"] = index.map(pd.Timestamp.timestamp).astype(int)
            courbe_du_site["horodate"] = courbe_du_site.index.map(pd.Timestamp.timestamp).astype(int)
        else:
            courbe_du_site["date_reception_flux"] = index
            courbe_du_site["horodate"] = courbe_du_site.index
        courbe_du_site.iloc[-1, 2] = True

        if export:
            courbe_du_site.to_csv(f'tmp/df_{site}.csv', index=False)
            liste_elements.append(f'tmp/df_{site}.csv')
        else:
            if base == 'mongo':
                liste_elements.extend(courbe_du_site.to_dict('records'))
            else:
                liste_elements.extend([model(**i) for i in courbe_du_site.to_dict('records')])

        site += 1
    print("fin création objects")
    return liste_elements, identifiant_max




