import random
import datetime as dt
import pandas as pd
from utils.localtime import localised_year_interval, localise_date, localise_datetime
import numpy as np
from utils.singleton import SingletonMeta


class SingletonData(metaclass=SingletonMeta):
    """
    le signleton qui crée un index lorsequ'il est appelé pour la première fois et renvoie la partie demandée pour
    accélérer la création de pandas dataframes
    """
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
                       export: bool, base, rand_days: int):
    """
    une fonction créée pour générer les données de remplissage
    :param nombre_sites: le nombre de courbes de charge à créer
    :param date_debut: la date du premier point des courbes de charge
    :param date_fin: la date du dernier point des courbes de charge
    :param model: le model à utiliser (utilisé en cas de sérialisation en objet)
    :param export: un booléen pour spécifier si les courbes de charges doivent être enregistrées dans des fichiers CSV
    :param base: le nom de la base de données (sert à savoir quel traitement appliquer aux données créées)
    :param rand_days: l'écart toléré entre les dates de début et de fin pour ajouter de l'aléatoire
    :return: les données dans le format attendu par la méthode associée à la base de données
    """
    liste_elements = []
    site = 0
    for i in range(nombre_sites):

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
    return liste_elements, site


def generation_pour_ajout_donnees(nombre_sites: int, date_debut: dt.datetime, date_fin: dt.datetime, model,
                                  identifiant_max, export: bool, base):
    """
    cette fonction est pensée pour la création de données dans le cadre de leur utilisation dans une requête d'ajout de
     données. elle est différente de la première car elle doit permettre de créer des données qui sont hors de l'intervalle
     donné pour le remplissage.
    :param nombre_sites: le nombre de courbes de charge à créer
    :param date_debut: la date du premier élément de chaque courbe
    :param date_fin: la date du dernier élément de chaque courbe
    :param model: le model à utiliser (utilisé en cas de sérialisation en objet)
    :param export: un booléen pour spécifier si les courbes de charges doivent être enregistrées dans des fichiers CSV
    :param base: le nom de la base de données (sert à savoir quel traitement appliquer aux données créées)
    :param identifiant_max: l'identifiant maximum déjà présent en base (pour éviter de réécrire sur des courbes qui existent déjà)
    :return:
    """
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
