import datetime as dt
import os
import time
from zoneinfo import ZoneInfo

from pymongo import MongoClient
import pprint

from generation_donnes import generation_donnees
from utils.interface_query_db import InterfaceQueryDb


class InterfacePostgres(InterfaceQueryDb):
    @classmethod
    def read_at_timestamp(self, timestamp: dt.datetime, model, identifiants_sites: [str], *args, **kwargs):
        debut = time.time()
        _ = list(model.objects.filter(id_site__in=identifiants_sites, horodate=timestamp))
        fin = time.time()
        return fin - debut
    @classmethod
    def read_between_dates(self, date_debut: dt.datetime, date_fin: dt.datetime, model, identifiants_sites: [str], *args, **kwargs):
        debut = time.time()
        _ = list(model.objects.filter(id_site__in=identifiants_sites, horodate__gte=date_debut, horodate__lte=date_fin))
        fin = time.time()
        return fin - debut
    @classmethod
    def update_at_timestamp(self, timestamp: dt.datetime, model, identifiants_sites: [str], *args, **kwargs):
        # if len(identifiants_sites) == 1:
        #     debut = time.time()
        #     element = model.objects.using('postgres').filter(id_site=identifiants_sites[0], horodate=timestamp)
        #     element.valeur = 42
        #     element.save(using='postgres')
        #     fin = time.time()
        # else:
        debut = time.time()
        model.objects.filter(id_site__in=identifiants_sites, horodate=timestamp).update(valeur=42)
        fin = time.time()
        return fin - debut

    @classmethod
    def update_between_dates(self, date_debut: dt.datetime, date_fin: dt.datetime, model, identifiants_sites: [str], *args, **kwargs):
        debut = time.time()
        model.objects.filter(id_site__in=identifiants_sites, horodate__gte=date_debut, horodate__lte=date_fin).update(valeur=42)
        fin = time.time()
        return fin - debut

    @classmethod
    def ajout_element_en_fin_de_courbe_de_charge(self, model, nombre_elements: int, nombre_courbes: int, *args, **kwargs):
        liste = []
        for i in range(nombre_courbes):
            derniere_entree = model.objects.filter(id_site=i).latest("horodate").horodate
            elements_a_inserer, _ = generation_donnees(1, derniere_entree + dt.timedelta(minutes=5),
                                                       derniere_entree + dt.timedelta(minutes=5*nombre_elements), model, i, True, 'postgres')
            liste.extend(elements_a_inserer)
        temps = 0.0
        for i in liste:
            debut = time.time()
            model.objects.from_csv(i)
            fin = time.time()
            temps = temps + (fin-debut)
            os.remove(i)
        return temps

    @classmethod
    def write(self, model, liste_a_ecrire: [], *args, **kwargs):
        if len(liste_a_ecrire) == 0:
            raise ValueError('vous avez oublié de spécifier les fichiers contenant les informations à mettre en base')
        temps = 0.0
        for i in liste_a_ecrire:
            debut = time.time()
            model.objects.from_csv(i)
            fin = time.time()
            temps = fin - debut
            os.remove(i)
        return temps




class InterfaceTimescale(InterfaceQueryDb):

    @classmethod
    def read_at_timestamp(self, timestamp: dt.datetime, model, identifiants_sites: [str], *args, **kwargs):
        debut = time.time()
        _ = list(model.objects.filter(id_site__in=identifiants_sites, horodate=timestamp))
        fin = time.time()
        return fin - debut

    @classmethod
    def read_between_dates(self, date_debut: dt.datetime, date_fin: dt.datetime, model, identifiants_sites: [str], *args, **kwargs):
        debut = time.time()
        _ = list(model.objects.filter(id_site__in=identifiants_sites, horodate__gte=date_debut, horodate__lte=date_fin))
        fin = time.time()
        return fin - debut

    @classmethod
    def update_at_timestamp(self, timestamp: dt.datetime, model, identifiants_sites: [str], *args, **kwargs):
        if len(identifiants_sites) == 1:
            debut = time.time()
            element = model.objects.filter(id_site=identifiants_sites[0], horodate=timestamp)
            element.valeur = 42
            element.save(using='postgres')
            fin = time.time()
        else:
            debut = time.time()
            model.objects.filter(id_site__in=identifiants_sites, horodate=timestamp).update(valeur=42)
            fin = time.time()
        return fin - debut

    @classmethod
    def update_between_dates(self, date_debut: dt.datetime, date_fin: dt.datetime, model, identifiants_sites: [str], *args, **kwargs):
        debut = time.time()
        model.objects.filter(id_site__in=identifiants_sites, horodate__gte=date_debut, horodate__lte=date_fin).update(valeur=42)
        fin = time.time()
        return fin - debut

    @classmethod
    def ajout_element_en_fin_de_courbe_de_charge(self, model, nombre_elements: int, nombre_courbes: int, *args,
                                                 **kwargs):
        liste = []
        for i in range(nombre_courbes):
            print('récupération de la dernière entrée')
            derniere_entree = model.objects.filter(id_site=i).latest("horodate").horodate
            # print(model.objects.filter(id_site=i).latest("horodate"))
            print('récupération terminée')
            elements_a_inserer, _ = generation_donnees(1, derniere_entree + dt.timedelta(minutes=5),
                                                       derniere_entree + dt.timedelta(minutes=5 * nombre_elements),
                                                       model, i, False, 'timescale')
            print('génération de données terminée')
            liste.extend(elements_a_inserer)
        print(liste)
        debut = time.time()
        model.objects.bulk_create(liste, batch_size=20000)
        fin = time.time()
        return fin - debut

    @classmethod
    def write(self, model, liste_a_ecrire: [], *args, **kwargs):

        # if len(liste_a_ecrire) == 0:
        #     raise ValueError('vous avez oublié de spécifier les fichiers contenant les informations à mettre en base')
        # temps = 0.0
        # for i in liste_a_ecrire:
        #     debut = time.time()
        #     print(len(liste_a_ecrire))
        #     print('debut de l"insertion')
        #     model.object_copy.from_csv(i)
        #     print('debut de l"insertion')
        #     fin = time.time()
        #     temps = fin - debut
        #     os.remove(i)
        #     print(f'temps={temps}')
        # return temps


        debut = time.time()
        print(len(liste_a_ecrire))
        print('début du bulk create')
        # model.objects.bulk_create(liste_a_ecrire[0:10], batch_size=200000)
        model.objects.bulk_create(liste_a_ecrire, batch_size=200000)
        print('fin du bulk create')
        fin = time.time()
        print(f'temps={fin - debut}')
        return fin - debut


class InterfaceMongo(InterfaceQueryDb):

    @classmethod
    def read_at_timestamp(self, timestamp: dt.datetime, model, identifiants_sites: [int], *args, **kwargs):
        client = MongoClient("mongo", 27017)
        db = client.mongo
        collection = db.TimeSerieElementMongo
        debut = time.time()
        _ = list(collection.find({"id_site": {'$in': identifiants_sites}, "horodate": timestamp.astimezone(ZoneInfo("UTC"))}))
        # for i in collection.find({"id_site": {'$in': identifiants_sites}, "horodate": timestamp.astimezone(ZoneInfo("UTC"))}):
        #     print(i)
        fin = time.time()
        return fin - debut

    @classmethod
    def read_between_dates(self, date_debut: dt.datetime, date_fin: dt.datetime, model, identifiants_sites: [int], *args, **kwargs):
        client = MongoClient("mongo", 27017)
        db = client.mongo
        collection = db.TimeSerieElementMongo
        debut = time.time()
        _ = list(collection.find({"id_site": {'$in': identifiants_sites}, "horodate": {'$lte': date_debut.astimezone(ZoneInfo("UTC")), '$gte': date_fin.astimezone(ZoneInfo("UTC"))}}))
        # for i in collection.find({"id_site": {'$in': identifiants_sites}, "horodate": {'$lte': date_fin.astimezone(ZoneInfo("UTC")), '$gte': date_debut.astimezone(ZoneInfo("UTC"))}}):
        #     print(i)
        fin = time.time()
        return fin - debut

    @classmethod
    def update_at_timestamp(self, timestamp: dt.datetime, model, identifiants_sites: [int], *args, **kwargs):
        client = MongoClient("mongo", 27017)
        db = client.mongo
        collection = db.TimeSerieElementMongo
        debut = time.time()
        collection.update({'id_site': {'$in': identifiants_sites},
                           'horodate': timestamp},
                          {'$set': {'valeur': 42}}, upsert=False)
        fin = time.time()
        return fin - debut

    @classmethod
    def update_between_dates(self, date_debut: dt.datetime, date_fin: dt.datetime, model, identifiants_sites: [int], *args, **kwargs):
        client = MongoClient("mongo", 27017)
        db = client.mongo
        collection = db.TimeSerieElementMongo
        debut = time.time()
        collection.update({'id_site': {'$in': identifiants_sites},
                           'horodate': {'$gte': date_debut, '$lte': date_fin}},
                          {'$set': {'valeur': 42}}, upsert=False)
        fin = time.time()
        return fin - debut

    @classmethod
    def ajout_element_en_fin_de_courbe_de_charge(self, model, nombre_elements: int, nombre_courbes: int, *args, **kwargs):
        client = MongoClient("mongo", 27017)
        db = client.mongo
        collection = db.TimeSerieElementMongo
        # print(f'liste des collections {db.list_collection_names()}')
        liste_elements_a_inserer = []
        for i in range(nombre_courbes):
            derniere_entree = kwargs['date_fin']
            for k in collection.find({"id_site": i}):
                if derniere_entree < k['horodate']:
                    derniere_entree = k['horodate']
            element_a_inserer, _ = generation_donnees(1,
                                                      derniere_entree + dt.timedelta(minutes=5),
                                                      derniere_entree + dt.timedelta(minutes=5 * nombre_elements), model, i,
                                                      False, 'mongo')
            liste_elements_a_inserer.extend(element_a_inserer)
        debut = time.time()
        collection.insert_many(liste_elements_a_inserer)
        fin = time.time()
        return fin - debut

    @classmethod
    def write(self, model, liste_a_ecrire: [], *args, **kwargs):
        client = MongoClient("mongo", 27017)
        db = client.mongo
        collection = db.TimeSerieElementMongo
        debut = time.time()
        collection.insert_many(liste_a_ecrire)
        fin = time.time()
        print(f'nombre de documents injectés: {collection.count_documents({})}')
        return fin - debut