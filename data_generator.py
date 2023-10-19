import random
import datetime as dt
import pandas as pd
from utils.localtime import localised_year_interval, localise_date, localise_datetime
import numpy as np
from utils.singleton import SingletonMeta


class DataFaker(metaclass=SingletonMeta):
    """
    le signleton qui crée un index lorsqu'il est appelé pour la première fois et renvoie la partie demandée pour
    accélérer la création des pandas dataframes
    """
    __current_id = 0

    def __init__(self, min_start_date: dt.datetime = None, max_end_date: dt.datetime = None):
        self.sd = min_start_date
        self.ed = max_end_date
        idx = pd.date_range(self.sd, self.ed, freq='5min')
        self.init_df = pd.DataFrame(index=idx, data={"valeur": np.random.rand(len(idx), )})

    def _get_init_df(self, size=1):
        assert size > 0
        total_size = self.init_df.shape[0]
        max_end = total_size - size
        radom_start = random.randint(0, max_end)
        return self.init_df.iloc[radom_start: radom_start + size]

    def get_new_id_site(self):
        self.__current_id += 1
        return self.__current_id

    def get_current_id_site(self):
        self.__current_id += 1
        return self.__current_id

    def generate_fake_dataframe(self, size: int, export=False) -> pd.DataFrame:
        """
        une fonction créée pour générer les données de remplissage
        Args:
            :param export: un booléen pour spécifier si les courbes de charges doivent être enregistrées dans des fichiers CSV
        :return:
            pd.DataFrame
        """

        courbe_du_site = self._get_init_df(size=size).copy()
        id_site = self.get_current_id_site()
        courbe_du_site["id_site"] = id_site
        courbe_du_site["horodate"] = courbe_du_site.index

        if export:
            courbe_du_site.to_csv(f'tmp/df_{id_site}.csv', index=False)

        return courbe_du_site
