from abc import abstractmethod
import datetime as dt


class InterfaceQueryDb:

    @abstractmethod
    def read_at_timestamp(self, timestamp: dt.datetime, model, identifiants_sites: [], *args, **kwargs):
        raise NotImplemented()

    @abstractmethod
    def read_between_dates(self, date_debut: dt.datetime, date_fin: dt.datetime, model, identifiants_sites: [], *args, **kwargs):
        raise NotImplemented()

    @abstractmethod
    def update_at_timestamp(self, timestamp: dt.datetime, model, identifiants_sites: [], *args, **kwargs):
        raise NotImplemented()

    @abstractmethod
    def update_between_dates(self, date_debut: dt.datetime, date_fin: dt.datetime, model, identifiants_sites: [int], *args, **kwargs):
        raise NotImplemented()

    @abstractmethod
    def ajout_element_en_fin_de_courbe_de_charge(self, timestamp: dt.datetime, model, identifiants_sites: [], *args, **kwargs):
        raise NotImplemented()

    @abstractmethod
    def write(self, model, identifiants_sites: [], *args, **kwargs):
        raise NotImplemented()

