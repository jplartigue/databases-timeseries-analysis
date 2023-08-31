import datetime as dt
import os
import time
from zoneinfo import ZoneInfo

from pymongo import MongoClient

# from influxable import Influxable
# from influxable.db import Field

# from benchmark_app_for_databases.models import TimeserieElementInflux
import psycopg2 as pg
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
    def read_between_dates(self, date_debut: dt.datetime, date_fin: dt.datetime, model, identifiants_sites: [str],
                           *args, **kwargs):
        debut = time.time()
        _ = list(model.objects.filter(id_site__in=identifiants_sites, horodate__gte=date_debut, horodate__lte=date_fin))
        fin = time.time()
        return fin - debut

    @classmethod
    def update_at_timestamp(self, timestamp: dt.datetime, model, identifiants_sites: [str], *args, **kwargs):
        debut = time.time()
        model.objects.filter(id_site__in=identifiants_sites, horodate=timestamp).update(valeur=42)
        fin = time.time()
        return fin - debut

    @classmethod
    def update_between_dates(self, date_debut: dt.datetime, date_fin: dt.datetime, model, identifiants_sites: [str],
                             *args, **kwargs):
        debut = time.time()
        model.objects.filter(id_site__in=identifiants_sites, horodate__gte=date_debut, horodate__lte=date_fin).update(
            valeur=42)
        fin = time.time()
        return fin - debut

    @classmethod
    def ajout_element_en_fin_de_courbe_de_charge(self, model, nombre_elements: int, nombre_courbes: int, *args,
                                                 **kwargs):
        liste = []
        for i in range(nombre_courbes):
            derniere_entree = model.objects.filter(id_site=i).latest("horodate").horodate
            elements_a_inserer, _ = generation_donnees(1, derniere_entree + dt.timedelta(minutes=5),
                                                       derniere_entree + dt.timedelta(minutes=5 * nombre_elements),
                                                       model, i, True, 'postgres')
            liste.extend(elements_a_inserer)
        temps = 0.0
        for i in liste:
            debut = time.time()
            model.objects.from_csv(i)
            fin = time.time()
            temps = temps + (fin - debut)
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
            temps = temps + (fin - debut)
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
    def read_between_dates(self, date_debut: dt.datetime, date_fin: dt.datetime, model, identifiants_sites: [str],
                           *args, **kwargs):
        debut = time.time()
        _ = list(model.objects.filter(id_site__in=identifiants_sites, horodate__gte=date_debut, horodate__lte=date_fin))
        fin = time.time()
        return fin - debut

    @classmethod
    def update_at_timestamp(self, timestamp: dt.datetime, model, identifiants_sites: [str], *args, **kwargs):
        debut = time.time()
        model.objects.filter(id_site__in=identifiants_sites, horodate=timestamp).update(valeur=42)
        fin = time.time()
        return fin - debut

    @classmethod
    def update_between_dates(self, date_debut: dt.datetime, date_fin: dt.datetime, model, identifiants_sites: [str],
                             *args, **kwargs):
        debut = time.time()
        model.objects.filter(id_site__in=identifiants_sites, horodate__gte=date_debut, horodate__lte=date_fin).update(
            valeur=42)
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

        if len(liste_a_ecrire) == 0:
            raise ValueError('vous avez oublié de spécifier les fichiers contenant les informations à mettre en base')
        temps = 0.0
        for i in liste_a_ecrire:
            debut = time.time()
            print(len(liste_a_ecrire))
            print('debut de l"insertion')
            model.object_copy.from_csv(i)
            print('debut de l"insertion')
            fin = time.time()
            temps = temps + (fin - debut)
            os.remove(i)
            print(f'temps={temps}')
        return temps

        # debut = time.time()
        # print(len(liste_a_ecrire))
        # print('début du bulk create')
        # # model.objects.bulk_create(liste_a_ecrire[0:10], batch_size=200000)
        # model.objects.bulk_create(liste_a_ecrire, batch_size=200000)
        # print('fin du bulk create')
        # fin = time.time()
        # print(f'temps={fin - debut}')
        # return fin - debut


class InterfaceMongo(InterfaceQueryDb):

    @classmethod
    def read_at_timestamp(self, timestamp: dt.datetime, model, identifiants_sites: [int], *args, **kwargs):
        client = MongoClient("mongo", 27017)
        db = client.mongo
        collection = db.TimeSerieElementMongo
        debut = time.time()
        _ = list(collection.find(
            {"id_site": {'$in': identifiants_sites}, "horodate": timestamp.astimezone(ZoneInfo("UTC"))}))
        # for i in collection.find({"id_site": {'$in': identifiants_sites}, "horodate": timestamp.astimezone(ZoneInfo("UTC"))}):
        #     print(i)
        fin = time.time()
        return fin - debut

    @classmethod
    def read_between_dates(self, date_debut: dt.datetime, date_fin: dt.datetime, model, identifiants_sites: [int],
                           *args, **kwargs):
        client = MongoClient("mongo", 27017)
        db = client.mongo
        collection = db.TimeSerieElementMongo
        debut = time.time()
        _ = list(collection.find({"id_site": {'$in': identifiants_sites},
                                  "horodate": {'$lte': date_debut.astimezone(ZoneInfo("UTC")),
                                               '$gte': date_fin.astimezone(ZoneInfo("UTC"))}}))
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
    def update_between_dates(self, date_debut: dt.datetime, date_fin: dt.datetime, model, identifiants_sites: [int],
                             *args, **kwargs):
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
    def ajout_element_en_fin_de_courbe_de_charge(self, model, nombre_elements: int, nombre_courbes: int, *args,
                                                 **kwargs):
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
                                                      derniere_entree + dt.timedelta(minutes=5 * nombre_elements),
                                                      model, i,
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


class InterfaceQuestdb(InterfaceQueryDb):
    @classmethod
    def read_at_timestamp(self, timestamp: dt.datetime, model, identifiants_sites: [str], *args, **kwargs):

        conn_str = 'user=admin password=quest host=questdb port=8812 dbname=qdb'
        with pg.connect(conn_str) as connection:
            # Open a cursor to perform database operations

            with connection.cursor() as cur:
                # Query the database and obtain data as Python objects.
                timestamp = int(timestamp.timestamp() * 1000)


                debut = time.time()
                cur.execute(f"SELECT * FROM test WHERE horodate = {timestamp} AND id_site BETWEEN {identifiants_sites[0]} AND {identifiants_sites[-1]};")
                records = cur.fetchall()
                # print(f'records = {records}')
                fin = time.time()

        # debut = time.time()
        # _ = list(model.objects.filter(id_site__in=identifiants_sites, horodate=timestamp))
        # fin = time.time()
        return fin - debut

    @classmethod
    def read_between_dates(self, date_debut: dt.datetime, date_fin: dt.datetime, model, identifiants_sites: [str],
                           *args, **kwargs):
        conn_str = 'user=admin password=quest host=questdb port=8812 dbname=qdb'
        with pg.connect(conn_str) as connection:
            # Open a cursor to perform database operations

            with connection.cursor() as cur:
                # Query the database and obtain data as Python objects.
                date_debut = int(date_debut.timestamp() * 1000)
                date_fin = int(date_fin.timestamp() * 1000)

                debut = time.time()
                cur.execute(
                    f"SELECT * FROM test WHERE horodate >= {date_debut} AND horodate <= {date_fin} AND id_site BETWEEN {identifiants_sites[0]} AND {identifiants_sites[-1]};")
                records = cur.fetchall()
                print(f'records = {records}')
                fin = time.time()

        # debut = time.time()
        # _ = list(model.objects.filter(id_site__in=identifiants_sites, horodate=timestamp))
        # fin = time.time()
        return fin - debut

    @classmethod
    def update_at_timestamp(self, timestamp: dt.datetime, model, identifiants_sites: [str], *args, **kwargs):

        conn_str = 'user=admin password=quest host=questdb port=8812 dbname=qdb'
        with pg.connect(conn_str) as connection:
            # Open a cursor to perform database operations

            with connection.cursor() as cur:
                # Query the database and obtain data as Python objects.
                timestamp = int(timestamp.timestamp() * 1000)

                debut = time.time()
                cur.execute(f"UPDATE test valeur=42 WHERE horodate = {timestamp} AND id_site BETWEEN {identifiants_sites[0]} AND {identifiants_sites[-1]};")
                fin = time.time()

        # debut = time.time()
        # _ = list(model.objects.filter(id_site__in=identifiants_sites, horodate=timestamp))
        # fin = time.time()
        return fin - debut

    @classmethod
    def update_between_dates(self, date_debut: dt.datetime, date_fin: dt.datetime, model, identifiants_sites: [str],
                             *args, **kwargs):
        conn_str = 'user=admin password=quest host=questdb port=8812 dbname=qdb'
        with pg.connect(conn_str) as connection:
            # Open a cursor to perform database operations

            with connection.cursor() as cur:
                # Query the database and obtain data as Python objects.
                date_debut = int(date_debut.timestamp() * 1000)
                date_fin = int(date_fin.timestamp() * 1000)

                debut = time.time()
                cur.execute(
                    f"UPDATE test valeur=42 WHERE horodate >= {date_debut} AND horodate <= {date_fin} AND id_site BETWEEN {identifiants_sites[0]} AND {identifiants_sites[-1]};")
                records = cur.fetchall()
                print(f'records = {records}')
                fin = time.time()

        # debut = time.time()
        # _ = list(model.objects.filter(id_site__in=identifiants_sites, horodate=timestamp))
        # fin = time.time()
        return fin - debut

    @classmethod
    def ajout_element_en_fin_de_courbe_de_charge(self, model, nombre_elements: int, nombre_courbes: int, *args,
                                                 **kwargs):

        liste_elements_a_inserer = []
        conn_str = 'user=admin password=quest host=questdb port=8812 dbname=qdb'
        with pg.connect(conn_str) as connection:

            with connection.cursor() as cur:
                cur.execute(f"SELECT horodate FROM test WHERE id_site BETWEEN 0 AND {nombre_courbes - 1} GROUP BY id_site, horodate;")
                records = cur.fetchall()

                print(f'toutes les dates {records[-10:]}')
                print(f'element = {records[0][0]}')

                requete = ""
                for i in records:
                    elements_a_inserer, _ = generation_donnees(1, i[0] + dt.timedelta(minutes=5), i[0] + dt.timedelta(minutes=5 * nombre_elements), model, 0, False, 'questdb')
                    liste_elements_a_inserer.append(elements_a_inserer)


        temps = self.write(model, liste_elements_a_inserer)

        return temps

    @classmethod
    def write(self, model, liste_a_ecrire: [], *args, **kwargs):
        temps = 0.0
        batch_size = 10000


        conn_str = 'user=admin password=quest host=questdb port=8812 dbname=qdb'
        with pg.connect(conn_str) as connection:  #, autocommit=True

            with connection.cursor() as cur:
                cur.execute('CREATE TABLE IF NOT EXISTS test(horodate DATE, identifiant_flux INT, id_site BIGINT, date_reception_flux DATE, dernier_flux BOOLEAN, valeur FLOAT);')

                nombre_tours = len(liste_a_ecrire) // batch_size
                reste = len(liste_a_ecrire) % batch_size
                print(f'nombre de tours à faire {nombre_tours}')
                for i in range(nombre_tours):
                    print(i)
                    requete = "INSERT INTO test (horodate, identifiant_flux, id_site, date_reception_flux, dernier_flux, valeur) VALUES"
                    for i in liste_a_ecrire[0:batch_size]:
                        i.horodate = i.horodate * 1000
                        i.date_reception_flux = i.date_reception_flux * 1000
                        requete = requete + f" ({i.horodate}, {i.identifiant_flux}, {i.id_site}, {i.date_reception_flux}, {i.dernier_flux}, {i.valeur}),"

                    requete = requete[0:-1] + ";"
                    debut = time.time()
                    cur.execute(requete)
                    fin = time.time()
                    temps = temps + (fin - debut)
                    liste_a_ecrire = liste_a_ecrire[batch_size:]
                    requete = ""
                if reste != 0:
                    requete = "INSERT INTO test (horodate, identifiant_flux, id_site, date_reception_flux, dernier_flux, valeur) VALUES"
                    for i in liste_a_ecrire:
                        i.horodate = i.horodate * 1000
                        i.date_reception_flux = i.date_reception_flux * 1000
                        requete = requete + f" ({i.horodate}, {i.identifiant_flux}, {i.id_site}, {i.date_reception_flux}, {i.dernier_flux}, {i.valeur}),"

                    requete = requete[0:-1] + ";"

                    debut = time.time()
                    cur.execute(requete)
                    fin = time.time()
                    temps = temps + (fin - debut)
                    requete = ""
                liste_a_ecrire.clear()
                print('it just works !')

        # if len(liste_a_ecrire) == 0:
        #     raise ValueError(
        #         'vous avez oublié de spécifier les fichiers contenant les informations à mettre en base')
        # temps = 0.0
        # for i in liste_a_ecrire:
        #     debut = time.time()
        #     model.objects.from_csv(i)
        #     fin = time.time()
        #     temps = fin - debut
        #     os.remove(i)

        return temps





# class Interfaceinfluxdb(InterfaceQueryDb):
#
#     @classmethod
#     def read_at_timestamp(self, timestamp: dt.datetime, model, identifiants_sites: [], *args, **kwargs):
#         client = Influxable(
#             base_url='http://influxdb:8086',
#             database_name='influxdb',
#             user='test',
#             password='password',
#         )
#         debut = time.time()
#         elements = TimeserieElementInflux.get_query().select('*').where(Field('horodate') == timestamp, Field('id_site') in identifiants_sites).evaluate()
#         fin = time.time()
#         print(f'element est de type {type(elements)} et ressemble à ça: {elements}')
#         return fin - debut
#
#     @classmethod
#     def read_between_dates(self, date_debut: dt.datetime, date_fin: dt.datetime, model, identifiants_sites: [], *args, **kwargs):
#         client = Influxable(
#             base_url='http://influxdb:8086',
#             database_name='influxdb',
#             user='test',
#             password='password',
#         )
#         debut = time.time()
#         elements = TimeserieElementInflux.get_query().select('*').where(Field('horodate') > date_debut, Field('horodate') < date_fin, Field('id_site') in identifiants_sites).evaluate()
#         fin = time.time()
#         return fin - debut
#
#     @classmethod
#     def update_at_timestamp(self, timestamp: dt.datetime, model, identifiants_sites: [], *args, **kwargs):
#         client = Influxable(
#             base_url='http://influxdb:8086',
#             database_name='influxdb',
#             user='test',
#             password='password',
#         )
#         debut = time.time()
#         elements = TimeserieElementInflux.get_query().select('*').where(Field('horodate') == timestamp, Field('id_site') in identifiants_sites).evaluate()
#         fin = time.time()
#         return fin - debut
#
#     @classmethod
#     def update_between_dates(self, date_debut: dt.datetime, date_fin: dt.datetime, model, identifiants_sites: [], *args, **kwargs):
#         client = Influxable(
#             base_url='http://influxdb:8086',
#             database_name='influxdb',
#             user='test',
#             password='password',
#         )
#
#     @classmethod
#     def ajout_element_en_fin_de_courbe_de_charge(self, timestamp: dt.datetime, model, identifiants_sites: [], *args, **kwargs):
#         client = Influxable(
#             base_url='http://influxdb:8086',
#             database_name='influxdb',
#             user='test',
#             password='password',
#         )
#
#     @classmethod
#     def write(self, model, liste_a_ecrire: [], *args, **kwargs):
#         client = Influxable(
#             base_url='http://influxdb:8086',
#             database_name='influxdb',
#             user='test',
#             password='password',
#         )
#         debut = time.time()
#         TimeserieElementInflux.bulk_save(liste_a_ecrire)
#         fin = time.time()
#         return fin-debut
