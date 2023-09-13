import datetime as dt
import gc
import os
import time
from zoneinfo import ZoneInfo
import pymongo
import pandas as pd
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
    def ajout_element_en_fin_de_courbe_de_charge(self, model, nombre_elements: int, nombre_courbes: int, *args, **kwargs):
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
            derniere_entree = model.objects.filter(id_site=i).latest("horodate").horodate
            elements_a_inserer, _ = generation_pour_ajout_donnees(1, derniere_entree + dt.timedelta(minutes=5),
                                                       derniere_entree + dt.timedelta(minutes=5 * nombre_elements),
                                                       model, i, False, 'timescale')
            liste.extend(elements_a_inserer)
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
            model.object_copy.from_csv(i)
            fin = time.time()
            temps = temps + (fin - debut)
            os.remove(i)
        return temps


class InterfaceMongo(InterfaceQueryDb):

    @classmethod
    def read_at_timestamp(self, timestamp: dt.datetime, model, identifiants_sites: [int], *args, **kwargs):
        client = MongoClient("mongo", 27017)
        db = client.mongo
        match model.__name__:
            case "TimeSerieElementMongo":
                collection = db.TimeSerieElementMongo
            case "TimeSerieElementMongoIndexHorodate":
                collection = db.TimeSerieElementMongoIndexHorodate
            case "TimeSerieElementMongoIndexSite":
                collection = db.TimeSerieElementMongoIndexSite
            case _:
                collection = db.TimeSerieElementMongoIndexHorodateSite

        for i in range(10):
            _ = list(collection.find(
                {"id_site": {'$in': identifiants_sites}, "horodate": timestamp.astimezone(ZoneInfo("UTC"))}))

        debut = time.time()
        _ = list(collection.find(
            {"id_site": {'$in': identifiants_sites}, "horodate": timestamp.astimezone(ZoneInfo("UTC"))}))
        fin = time.time()
        return fin - debut

    @classmethod
    def read_between_dates(self, date_debut: dt.datetime, date_fin: dt.datetime, model, identifiants_sites: [int],
                           *args, **kwargs):
        client = MongoClient("mongo", 27017)
        db = client.mongo
        match model.__name__:
            case "TimeSerieElementMongo":
                collection = db.TimeSerieElementMongo
            case "TimeSerieElementMongoIndexHorodate":
                collection = db.TimeSerieElementMongoIndexHorodate
            case "TimeSerieElementMongoIndexSite":
                collection = db.TimeSerieElementMongoIndexSite
            case _:
                collection = db.TimeSerieElementMongoIndexHorodateSite

        for i in range(10):
            _ = list(collection.find({"id_site": {'$in': identifiants_sites},
                                      "horodate": {'$lte': date_debut.astimezone(ZoneInfo("UTC")),
                                                   '$gte': date_fin.astimezone(ZoneInfo("UTC"))}}))
        debut = time.time()
        _ = list(collection.find({"id_site": {'$in': identifiants_sites},
                                  "horodate": {'$lte': date_debut.astimezone(ZoneInfo("UTC")),
                                               '$gte': date_fin.astimezone(ZoneInfo("UTC"))}}))
        fin = time.time()
        return fin - debut

    @classmethod
    def update_at_timestamp(self, timestamp: dt.datetime, model, identifiants_sites: [int], *args, **kwargs):
        client = MongoClient("mongo", 27017)
        db = client.mongo
        match model.__name__:
            case "TimeSerieElementMongo":
                collection = db.TimeSerieElementMongo
            case "TimeSerieElementMongoIndexHorodate":
                collection = db.TimeSerieElementMongoIndexHorodate
            case "TimeSerieElementMongoIndexSite":
                collection = db.TimeSerieElementMongoIndexSite
            case _:
                collection = db.TimeSerieElementMongoIndexHorodateSite
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
        match model.__name__:
            case "TimeSerieElementMongo":
                collection = db.TimeSerieElementMongo
            case "TimeSerieElementMongoIndexHorodate":
                collection = db.TimeSerieElementMongoIndexHorodate
            case "TimeSerieElementMongoIndexSite":
                collection = db.TimeSerieElementMongoIndexSite
            case _:
                collection = db.TimeSerieElementMongoIndexHorodateSite
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
        match model.__name__:
            case "TimeSerieElementMongo":
                collection = db.TimeSerieElementMongo
            case "TimeSerieElementMongoIndexHorodate":
                collection = db.TimeSerieElementMongoIndexHorodate
            case "TimeSerieElementMongoIndexSite":
                collection = db.TimeSerieElementMongoIndexSite
            case _:
                collection = db.TimeSerieElementMongoIndexHorodateSite
        print(f'liste des collections {db.list_collection_names()}')
        liste_elements_a_inserer = []
        for i in range(nombre_courbes):
            derniere_entree = dt.datetime(1981, 4, 2)
            for k in collection.find({"id_site": f'{i}'}).sort([('horodate', pymongo.DESCENDING),]).limit(1):

                if derniere_entree < k['horodate']:
                    derniere_entree = k['horodate']
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

            with connection.cursor() as cur:
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
                fin = time.time()
        return fin - debut

    @classmethod
    def read_between_dates(self, date_debut: dt.datetime, date_fin: dt.datetime, model, identifiants_sites: [str],
                           *args, **kwargs):
        conn_str = 'user=admin password=quest host=questdb port=8812 dbname=qdb'
        with pg.connect(conn_str) as connection:

            with connection.cursor() as cur:
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

            with connection.cursor() as cur:
                timestamp = int(timestamp.timestamp() * 1000000)

                liste = '('
                for i in identifiants_sites:
                    liste = liste + f"'{i}',"
                liste = liste[0:-1] + ')'

                debut = time.time()
                cur.execute(f"UPDATE {model().name} SET valeur=42 WHERE horodate = {timestamp} AND id_site IN {liste};")
                fin = time.time()
        return fin - debut

    @classmethod
    def update_between_dates(self, date_debut: dt.datetime, date_fin: dt.datetime, model, identifiants_sites: [str],
                             *args, **kwargs):
        conn_str = 'user=admin password=quest host=questdb port=8812 dbname=qdb'
        with pg.connect(conn_str) as connection:

            with connection.cursor() as cur:
                date_debut = int(date_debut.timestamp() * 1000000)
                date_fin = int(date_fin.timestamp() * 1000000)

                liste = '('
                for i in identifiants_sites:
                    liste = liste + f"'{i}',"
                liste = liste[0:-1] + ')'

                debut = time.time()
                cur.execute(f"UPDATE {model().name} SET valeur=42 WHERE horodate >= {date_debut} AND horodate <= {date_fin} AND id_site IN {liste};")
                records = cur.fetchall()
                fin = time.time()
                del records

        gc.collect()
        return fin - debut

    @classmethod
    def ajout_element_en_fin_de_courbe_de_charge(self, model, nombre_elements: int, nombre_courbes: int, *args, **kwargs):

        liste_elements_a_inserer = []
        conn_str = 'user=admin password=quest host=questdb port=8812 dbname=qdb'
        with pg.connect(conn_str) as connection:

            with connection.cursor() as cur:
                liste = '('
                for i in range(nombre_courbes):
                    liste = liste + f"'{i}',"
                liste = liste[0:-1] + ')'

                cur.execute(f"SELECT MAX(horodate) FROM {model().name} WHERE id_site IN {liste} GROUP BY id_site;")
                records = cur.fetchall()

                site = 0
                for i in records:
                    elements_a_inserer, _ = generation_pour_ajout_donnees(1, i[0] + dt.timedelta(minutes=5),
                                                                          i[0] + dt.timedelta(minutes=5 * nombre_elements),
                                                                          model, 0, False, 'questdb')
                    liste_elements_a_inserer.extend(elements_a_inserer)
                    site += 1


        del records
        temps = self.write(model, liste_elements_a_inserer)

        gc.collect()
        return temps

    @classmethod
    def write(self, model, liste_a_ecrire: [], *args, **kwargs):

        conn_str = 'user=admin password=quest host=questdb port=8812 dbname=qdb'
        with pg.connect(conn_str) as connection:

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
            if len(liste_a_ecrire) > 1:
                for i in liste_a_ecrire[1:]:
                    ultra_dataframe = pd.concat([ultra_dataframe, i], axis=0)
                debut = time.time()
                sender.dataframe(
                    ultra_dataframe,
                    table_name=model().name,
                    symbols=['id_site'],
                    at='date_reception_flux')
                fin = time.time()
            else:
                debut = time.time()
                sender.dataframe(
                    ultra_dataframe,
                    table_name=model().name,
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
            password="password",
            timeout=100_000
        )

        query_api = client.query_api()

        if len(identifiants_sites) > 1:
            query = f'from(bucket:"test") |> range(start: {localise_datetime(timestamp).isoformat()}, stop: {localise_datetime(timestamp + dt.timedelta(minutes=4)).isoformat()}) |> filter(fn: (r) => r.id_site =~ /[{identifiants_sites[0]} - {identifiants_sites[-1]}]$/)'
        else:
            query = f'from(bucket:"test") |> range(start: {localise_datetime(timestamp).isoformat()}, stop: {localise_datetime(timestamp + dt.timedelta(minutes=4)).isoformat()}) |> filter(fn: (r) => r.id_site == "{identifiants_sites[0]}")'

        for i in range(10):
            result = query_api.query(org="holmium", query=query)

        debut = time.time()
        result = query_api.query(org="holmium", query=query)
        fin = time.time()

        client.__del__()
        return fin - debut

    @classmethod
    def read_between_dates(self, date_debut: dt.datetime, date_fin: dt.datetime, model, identifiants_sites: [], *args,
                           **kwargs):
        client = influxdb_client.InfluxDBClient(
            url="http://influxdb:8086",
            token="token",
            org="holmium",
            username="test",
            password="password",
            timeout=100_000
        )

        query_api = client.query_api()

        if len(identifiants_sites) > 1:
            query = f'from(bucket:"test") |> range(start: {localise_datetime(date_debut).isoformat()}, stop: {localise_datetime(date_fin).isoformat()}) |> filter(fn: (r) => r.id_site =~ /[{identifiants_sites[0]} - {identifiants_sites[-1]}]$/)'
        else:
            query = f'from(bucket:"test") |> range(start: {localise_datetime(date_debut).isoformat()}, stop: {localise_datetime(date_fin).isoformat()}) |> filter(fn: (r) => r.id_site == "{identifiants_sites[0]}")'
        for i in range(3):
            result = query_api.query(org="holmium", query=query)

        debut = time.time()
        result = query_api.query(org="holmium", query=query)
        fin = time.time()

        client.__del__()
        return fin - debut

    @classmethod
    def update_at_timestamp(self, timestamp: dt.datetime, model, identifiants_sites: [], *args, **kwargs):
        elements, _ = generation_pour_ajout_donnees(len(identifiants_sites), timestamp,
                                                    timestamp + dt.timedelta(minutes=4), model, 0, False, 'questdb')
        temps = self.write(model, elements)
        return temps

    @classmethod
    def update_between_dates(self, date_debut: dt.datetime, date_fin: dt.datetime, model, identifiants_sites: [], *args,
                             **kwargs):
        elements, _ = generation_pour_ajout_donnees(len(identifiants_sites), date_debut, date_fin, model, 0, False,
                                                    'questdb')
        temps = self.write(model, elements)
        return temps

    @classmethod
    def ajout_element_en_fin_de_courbe_de_charge(self, model, nombre_elements: int, nombre_courbes: int, *args, **kwargs):

        client = influxdb_client.InfluxDBClient(
            url="http://influxdb:8086",
            token="token",
            org="holmium",
            username="test",
            password="password",
            timeout=100_000
        )

        query_api = client.query_api()
        liste_elements_a_inserer = []
        for i in range(nombre_courbes):
            query = f'from(bucket:"test") |> range(start: {localise_datetime(dt.datetime(1980, 1, 1)).isoformat()}, ' \
                    f'stop: {localise_datetime(dt.datetime(2077, 1, 1)).isoformat()}) |> filter(fn: (r) => r.id_site ' \
                    f'== "{i}") |> last(column: "valeur")'
            result = query_api.query(org="holmium", query=query)
            derniere_date = dt.datetime.strptime(list(result[-1])[0]['horodate'][0:-6], '%Y-%m-%d %H:%M:%S')
            element, _ = generation_pour_ajout_donnees(1, derniere_date + dt.timedelta(minutes=5),
                                                       derniere_date + dt.timedelta(minutes=5 * nombre_elements), model,
                                                       i, False, 'influxdb')
            liste_elements_a_inserer.extend(element)
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
            password="password",
            timeout=100_000_000
        )
        write_api = client.write_api(write_options=SYNCHRONOUS)
        ultra_dataframe = liste_a_ecrire[0]
        if len(liste_a_ecrire) > 1:
            for i in liste_a_ecrire[1:]:
                ultra_dataframe = pd.concat([ultra_dataframe, i], axis=0)
        debut = time.time()
        write_api.write(bucket="test", org="holmium", record=ultra_dataframe, data_frame_measurement_name='test',
                        data_frame_tag_columns=["id_site", "horodate", "identifiant_flux", "dernier_flux", "valeur"],
                        data_frame_timestamp_column="horodate")
        fin = time.time()
        client.__del__()
        return fin - debut
