import datetime as dt
import gc
import os
import time
from zoneinfo import ZoneInfo

import pymongo
from pympler import tracker
import pandas as pd

from influxdb import DataFrameClient

from psycopg2.extras import execute_batch
from pymongo import MongoClient
import psycopg2 as pg

import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS




from generation_donnes import generation_donnees, generation_pour_ajout_donnees
from utils.interface_query_db import InterfaceQueryDb

from questdb.ingress import Sender

from utils.localtime import localise_datetime


class InterfacePostgres(InterfaceQueryDb):
    @classmethod
    def read_at_timestamp(self, timestamp: dt.datetime, model, identifiants_sites: [str], *args, **kwargs):

        for i in range(10):
            _ = list(model.objects.filter(id_site__in=identifiants_sites, horodate=timestamp))
        debut = time.time()
        _ = list(model.objects.filter(id_site__in=identifiants_sites, horodate=timestamp))
        fin = time.time()
        return fin - debut

    @classmethod
    def read_between_dates(self, date_debut: dt.datetime, date_fin: dt.datetime, model, identifiants_sites: [str],
                           *args, **kwargs):

        for i in range(10):
            _ = list(model.objects.filter(id_site__in=identifiants_sites, horodate__gte=date_debut, horodate__lte=date_fin))
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
            elements_a_inserer, _ = generation_pour_ajout_donnees(1, derniere_entree + dt.timedelta(minutes=5),
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
            # model.objects.bulk_create(liste_a_ecrire, batch_size=1000000)
            fin = time.time()
            temps = temps + (fin - debut)
            os.remove(i)
        return temps


class InterfaceTimescale(InterfaceQueryDb):

    @classmethod
    def read_at_timestamp(self, timestamp: dt.datetime, model, identifiants_sites: [str], *args, **kwargs):

        for i in range(10):
            _ = list(model.objects.filter(id_site__in=identifiants_sites, horodate=timestamp))

        debut = time.time()
        _ = list(model.objects.filter(id_site__in=identifiants_sites, horodate=timestamp))
        fin = time.time()
        return fin - debut

    @classmethod
    def read_between_dates(self, date_debut: dt.datetime, date_fin: dt.datetime, model, identifiants_sites: [str], *args, **kwargs):

        for i in range(10):
            _ = list(model.objects.filter(id_site__in=identifiants_sites, horodate__gte=date_debut, horodate__lte=date_fin))
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
            elements_a_inserer, _ = generation_pour_ajout_donnees(1, derniere_entree + dt.timedelta(minutes=5),
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
            print('fin de l"insertion')
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

        for i in range(10):
            _ = list(collection.find(
                {"id_site": {'$in': identifiants_sites}, "horodate": timestamp.astimezone(ZoneInfo("UTC"))}))

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

        for i in range(10):
            _ = list(collection.find({"id_site": {'$in': identifiants_sites},
                                      "horodate": {'$lte': date_debut.astimezone(ZoneInfo("UTC")),
                                                   '$gte': date_fin.astimezone(ZoneInfo("UTC"))}}))
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
        print(f'liste des collections {db.list_collection_names()}')
        liste_elements_a_inserer = []
        for i in range(nombre_courbes):
            derniere_entree = dt.datetime(1981, 4, 2)
            for k in collection.find({"id_site": f'{i}'}).sort([('horodate', pymongo.DESCENDING),]).limit(1):

                if derniere_entree < k['horodate']:
                    derniere_entree = k['horodate']
                # derniere_entree = k
            # derniere_entree = collection.find({"id_site": i}).sort([{'horodate', pymongo.DESCENDING}]).limit(1)['horodate']
            print(f'date ultime = {derniere_entree}')
            element_a_inserer, _ = generation_donnees(1,
                                                      derniere_entree + dt.timedelta(minutes=5),
                                                      derniere_entree + dt.timedelta(minutes=5 * nombre_elements),
                                                      model, i,
                                                      False, 'mongo', 0)
            liste_elements_a_inserer.extend(element_a_inserer)
        debut = time.time()
        collection.insert_many(liste_elements_a_inserer)
        fin = time.time()
        return fin - debut

    @classmethod
    def write(self, model, liste_a_ecrire: [], *args, **kwargs):
        client = MongoClient("mongo", 27017)
        db = client.mongo
        match model.__name__:
            case "TimeSerieElementMongo":
                collection = db.TimeSerieElementMongo
                debut = time.time()
                collection.insert_many(liste_a_ecrire)
                fin = time.time()
            case "TimeSerieElementMongoIndexHorodate":
                collection = db.TimeSerieElementMongoIndexHorodate
                collection.create_index('horodate', unique=False)
                debut = time.time()
                collection.insert_many(liste_a_ecrire)
                fin = time.time()
            case "TimeSerieElementMongoIndexSite":
                collection = db.TimeSerieElementMongoIndexSite
                collection.create_index('id_site', unique=False)
                debut = time.time()
                collection.insert_many(liste_a_ecrire)
                fin = time.time()
            case _:
                collection = db.TimeSerieElementMongoIndexHorodateSite
                collection.create_index('horodate', unique=False)
                collection.create_index('id_site', unique=False)
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

                liste = '('
                for i in identifiants_sites:
                    liste = liste + f"'{i}',"
                liste = liste[0:-1] + ')'

                for i in range(10):
                    cur.execute(f"SELECT * FROM {model().name} WHERE horodate = {timestamp} AND id_site IN {liste};")
                    records = cur.fetchall()


                debut = time.time()
                cur.execute(f"SELECT * FROM {model().name} WHERE horodate = {timestamp} AND id_site IN {liste};")
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
                date_debut = int(date_debut.timestamp() * 1000000)
                date_fin = int(date_fin.timestamp() * 1000000)

                liste = '('
                for i in identifiants_sites:
                    liste = liste + f"'{i}',"
                liste = liste[0:-1] + ')'

                for i in range(10):
                    cur.execute(f"SELECT * FROM {model().name} WHERE horodate >= {date_debut} AND horodate <= {date_fin} AND id_site IN {liste};")

                debut = time.time()
                cur.execute(f"SELECT * FROM {model().name} WHERE horodate >= {date_debut} AND horodate <= {date_fin} AND id_site IN {liste};")
                records = cur.fetchall()
                fin = time.time()
                del records

        return fin - debut

    @classmethod
    def update_at_timestamp(self, timestamp: dt.datetime, model, identifiants_sites: [str], *args, **kwargs):

        conn_str = 'user=admin password=quest host=questdb port=8812 dbname=qdb'
        with pg.connect(conn_str) as connection:
            # Open a cursor to perform database operations

            with connection.cursor() as cur:
                # Query the database and obtain data as Python objects.
                timestamp = int(timestamp.timestamp() * 1000000)

                liste = '('
                for i in identifiants_sites:
                    liste = liste + f"'{i}',"
                liste = liste[0:-1] + ')'

                debut = time.time()
                cur.execute(f"UPDATE {model().name} SET valeur=42 WHERE horodate = {timestamp} AND id_site IN {liste};")
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
                date_debut = int(date_debut.timestamp() * 1000000)
                date_fin = int(date_fin.timestamp() * 1000000)

                liste = '('
                for i in identifiants_sites:
                    liste = liste + f"'{i}',"
                liste = liste[0:-1] + ')'

                debut = time.time()
                cur.execute(f"UPDATE {model().name} SET valeur=42 WHERE horodate >= {date_debut} AND horodate <= {date_fin} AND id_site IN {liste};")
                records = cur.fetchall()
                # print(f'records = {records}')
                fin = time.time()
                del records

        # debut = time.time()
        # _ = list(model.objects.filter(id_site__in=identifiants_sites, horodate=timestamp))
        # fin = time.time()
        gc.collect()
        return fin - debut

    @classmethod
    def ajout_element_en_fin_de_courbe_de_charge(self, model, nombre_elements: int, nombre_courbes: int, *args, **kwargs):

        liste_elements_a_inserer = []
        conn_str = 'user=admin password=quest host=questdb port=8812 dbname=qdb'
        with pg.connect(conn_str) as connection:

            with connection.cursor() as cur:
                print(f'max = {nombre_courbes}')
                liste = '('
                for i in range(nombre_courbes):
                    # cur.execute(f"SELECT MAX(horodate) FROM {model.name} WHERE id_site IN ('{i}');")  # WHERE id_site IN {liste}
                    # cur.execute(f"SELECT id_site FROM {model.name};")
                    # records = cur.fetchall()
                    # for j in records:
                    #     print(j)
                    # liste.append(records[0])
                    # time.sleep(20)
                    # print(liste)
                    liste = liste + f"'{i}',"
                liste = liste[0:-1] + ')'
                # print(f"\n\n\nSELECT MAX(horodate) FROM {model().name} WHERE id_site IN {liste} GROUP BY id_site;\n\n\n")

                cur.execute(f"SELECT MAX(horodate) FROM {model().name} WHERE id_site IN {liste} GROUP BY id_site;")
                # cur.execute(f'SELECT * FROM {model.name} WHERE id_site IN {liste};')  #WHERE id_site IN {liste}
                records = cur.fetchall()

                # print(f'toutes les dates {records[-10:]}')
                # print(f'element = {records[0][0]} de type {type(records[0][0])}')
                # time.sleep(20)
                # print(f'element = {records[0][0]}')

                site = 0
                for i in records:
                    elements_a_inserer, _ = generation_pour_ajout_donnees(1, i[0] + dt.timedelta(minutes=5), i[0] + dt.timedelta(minutes=5 * nombre_elements), model, 0, False, 'questdb')
                    liste_elements_a_inserer.extend(elements_a_inserer)
                    site += 1


        print(f'liste elements a insérer: {liste_elements_a_inserer}')
        del records
        temps = self.write(model, liste_elements_a_inserer)

        gc.collect()
        return temps

    @classmethod
    def write(self, model, liste_a_ecrire: [], *args, **kwargs):

        # print(f'nom de la table = {model().name}')


        conn_str = 'user=admin password=quest host=questdb port=8812 dbname=qdb'
        with pg.connect(conn_str) as connection:  #, autocommit=True

            with connection.cursor() as cur:
                match model.__name__:
                    case "TimeserieElementQuestdbPartition":
                        cur.execute(f'CREATE TABLE IF NOT EXISTS {model().name} (horodate TIMESTAMP, identifiant_flux INT, id_site SYMBOL, date_reception_flux TIMESTAMP, dernier_flux BOOLEAN, valeur FLOAT) timestamp(horodate) PARTITION BY MONTH;')
                    case "TimeSerieElementQuestdb":
                        cur.execute(f'CREATE TABLE IF NOT EXISTS {model().name} (horodate TIMESTAMP, identifiant_flux INT, id_site SYMBOL, date_reception_flux TIMESTAMP, dernier_flux BOOLEAN, valeur FLOAT);')
                    case "TimeSerieElementQuestdbIndexSite":
                        cur.execute(f'CREATE TABLE IF NOT EXISTS {model().name} (horodate TIMESTAMP, identifiant_flux INT, id_site SYMBOL INDEX CAPACITY 1000000, date_reception_flux TIMESTAMP, dernier_flux BOOLEAN, valeur FLOAT);')
                    case _:
                        cur.execute(f'CREATE TABLE IF NOT EXISTS {model().name} (horodate TIMESTAMP, identifiant_flux INT, id_site SYMBOL INDEX CAPACITY 1000000, date_reception_flux TIMESTAMP, dernier_flux BOOLEAN, valeur FLOAT) timestamp(horodate) PARTITION BY MONTH;')

        with Sender('questdb', 9009) as sender:
            ultra_dataframe = liste_a_ecrire[0]
            # print(ultra_dataframe)
            if len(liste_a_ecrire) > 1:
                for i in liste_a_ecrire[1:]:
                    ultra_dataframe = pd.concat([ultra_dataframe, i], axis=0)
                    # print(f'ultra_dataframe = {ultra_dataframe}')
                debut = time.time()
                sender.dataframe(
                    ultra_dataframe,
                    table_name=model().name,  # Table name to insert into.
                    symbols=['id_site'],
                    at='date_reception_flux')
                # sender.dataframe(
                #     ultra_dataframe,
                #     table_name=model().name)
                fin = time.time()
            else:
                debut = time.time()
                sender.dataframe(
                    ultra_dataframe,
                    table_name=model().name,  # Table name to insert into.
                    symbols=['id_site'],
                    at='date_reception_flux')
                fin = time.time()

        return fin - debut





class Interfaceinfluxdb(InterfaceQueryDb):

    @classmethod
    def read_at_timestamp(self, timestamp: dt.datetime, model, identifiants_sites: [], *args, **kwargs):
        client = influxdb_client.InfluxDBClient(
            url="http://influxdb:8086",
            token="token",
            org="holmium",
            username="test",
            password="password"
        )

        query_api = client.query_api()

        if len(identifiants_sites) > 1:
            query = f'from(bucket:"test") |> range(start: {localise_datetime(timestamp).isoformat()}, stop: {localise_datetime(timestamp + dt.timedelta(minutes=4)).isoformat()}) |> filter(fn: (r) => r.id_site =~ /[{identifiants_sites[0]} - {identifiants_sites[-1]}]$/)'
        else:
            query = f'from(bucket:"test") |> range(start: {localise_datetime(timestamp).isoformat()}, stop: {localise_datetime(timestamp + dt.timedelta(minutes=4)).isoformat()}) |> filter(fn: (r) => r.id_site == "{identifiants_sites[0]}")'

        print(query)

        for i in range(10):
            result = query_api.query(org="holmium", query=query)

        debut = time.time()
        result = query_api.query(org="holmium", query=query)
        fin = time.time()

        client.__del__()
        return fin - debut

    @classmethod
    def read_between_dates(self, date_debut: dt.datetime, date_fin: dt.datetime, model, identifiants_sites: [], *args, **kwargs):
        client = influxdb_client.InfluxDBClient(
            url="http://influxdb:8086",
            token="token",
            org="holmium",
            username="test",
            password="password"
        )

        query_api = client.query_api()

        if len(identifiants_sites) > 1:
            query = f'from(bucket:"test") |> range(start: {localise_datetime(date_debut).isoformat()}, stop: {localise_datetime(date_fin).isoformat()}) |> filter(fn: (r) => r.id_site =~ /[{identifiants_sites[0]} - {identifiants_sites[-1]}]$/)'
        else:
            query = f'from(bucket:"test") |> range(start: {localise_datetime(date_debut).isoformat()}, stop: {localise_datetime(date_fin).isoformat()}) |> filter(fn: (r) => r.id_site == "{identifiants_sites[0]}")'


        print(query)
        for i in range(10):
            result = query_api.query(org="holmium", query=query)

        debut = time.time()
        result = query_api.query(org="holmium", query=query)
        fin = time.time()

        client.__del__()
        return fin - debut

    @classmethod
    def update_at_timestamp(self, timestamp: dt.datetime, model, identifiants_sites: [], *args, **kwargs):
        elements, _ = generation_pour_ajout_donnees(len(identifiants_sites), timestamp, timestamp + dt.timedelta(minutes=4), model, 0, False, 'questdb')
        temps = self.write(model, elements)
        return temps

    @classmethod
    def update_between_dates(self, date_debut: dt.datetime, date_fin: dt.datetime, model, identifiants_sites: [], *args, **kwargs):
        elements, _ = generation_pour_ajout_donnees(len(identifiants_sites), date_debut, date_fin, model, 0, False, 'questdb')
        temps = self.write(model, elements)
        return temps

    @classmethod
    def ajout_element_en_fin_de_courbe_de_charge(self, model, nombre_elements: int, nombre_courbes: int, *args, **kwargs):  # |> max()

        client = influxdb_client.InfluxDBClient(
            url="http://influxdb:8086",
            token="token",
            org="holmium",
            username="test",
            password="password"
        )

        query_api = client.query_api()
        liste_elements_a_inserer = []
        for i in range(nombre_courbes):

            query = f'from(bucket:"test") |> range(start: {localise_datetime(dt.datetime(1980, 1, 1)).isoformat()}, stop: {localise_datetime(dt.datetime(2077, 1, 1)).isoformat()}) |> filter(fn: (r) => r.id_site == "{i}") |> last(column: "valeur")'

            # print(query)

            result = query_api.query(org="holmium", query=query)

            print(list(result[-1])[0]['horodate'])
            derniere_date = dt.datetime.strptime(list(result[-1])[0]['horodate'][0:-6], '%Y-%m-%d %H:%M:%S')

            element, _ = generation_pour_ajout_donnees(1, derniere_date + dt.timedelta(minutes=5), derniere_date + dt.timedelta(minutes=5 * nombre_elements), model, i, False, 'influxdb')

            liste_elements_a_inserer.extend(element)


        print(liste_elements_a_inserer[0])
        client.__del__()
        temps = self.write(model, liste_elements_a_inserer, premiere_fois=False)

        return temps

    @classmethod
    def write(self, model, liste_a_ecrire: [], *args, **kwargs):

        client = influxdb_client.InfluxDBClient(
            url="http://influxdb:8086",
            token="token",
            org="holmium",
            username="test",
            password="password"
        )
        write_api = client.write_api(write_options=SYNCHRONOUS)
        ultra_dataframe = liste_a_ecrire[0]
        if len(liste_a_ecrire) > 1:
            for i in liste_a_ecrire[1:]:
                ultra_dataframe = pd.concat([ultra_dataframe, i], axis=0)
        # liste = []
        # for i in liste_a_ecrire:
        #     liste.append(influxdb_client.Point("test").tag("identifiant_flux", i['identifiant_flux']).field("id_site", i['id_site']).time(i['horodate']).field('date_reception_flux', str(i['date_reception_flux'])).field('dernier_flux', False).field('valeur', i['valeur']))
        print('début de l"écriture')
        debut = time.time()
        write_api.write(bucket="test", org="holmium", record=ultra_dataframe, data_frame_measurement_name='test', data_frame_tag_columns=["id_site", "horodate", "identifiant_flux", "dernier_flux", "valeur"], data_frame_timestamp_column="horodate")  # , data_frame_measurement_name='test'    , data_frame_tag_columns=['id_site', 'dernier_flux', 'identifiant_flux', 'date_reception_flux', 'horodate', 'valeur']   , data_frame_measurement_name='test'
        fin = time.time()
        print('fin de l"écriture')

        # _write_client.write("my-bucket", "my-org", record=_data_frame, data_frame_measurement_name='h2o_feet', data_frame_tag_columns=['location'])


        # query_api = client.query_api()
        #
        # query = f'from(bucket:"test") |> range(start: {localise_datetime(dt.datetime(2021, 1, 1)).isoformat()}, stop: {localise_datetime(dt.datetime.now()).isoformat()})'
        #
        # query = f'from(bucket:"test") |> range(start: {localise_datetime(dt.datetime(2021, 1, 1)).isoformat()}, stop: {localise_datetime(dt.datetime(2023, 9, 1)).isoformat()})   |> filter(fn: (r) => r.id_site =~ /[0 - 2]$/)'  # |> max(column: "_value")'
        #
        # print(query)
        #
        # result = query_api.query(org="holmium", query=query)
        #
        # # print(result)
        #
        # verif = []
        #
        # for i in result:
        #     verif.append(i)
        # print(f'nombre d"éléments en base = {len(verif)}\nverif = {verif[0]}\nverif2 = {list(verif[-1])[-1]}')  #\nverif2 = {list(verif[-1])[-2]}


        # client = DataFrameClient('influxdb',8086, 'test', 'password', "test")
        #
        # if kwargs['premiere_fois'] == True:
        #     client.create_database('test')
        #
        # ultra_dataframe = pd.DataFrame()
        # for i in liste_a_ecrire:
        #     ultra_dataframe.merge(i)
        # debut = time.time()
        # client.write_points(ultra_dataframe, 'test', protocol='line')
        # fin = time.time()

        client.__del__()
        return fin - debut
