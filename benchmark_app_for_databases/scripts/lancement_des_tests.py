import datetime as dt
import pandas as pd
from pymongo import MongoClient
import psycopg2 as pg

import influxdb_client

from benchmark import benchmark, insertion_sans_saturer_la_ram
from benchmark_app_for_databases.models import TimeSerieElementMongo, TimeSerieElementMongoIndexSite, \
    TimeSerieElementMongoIndexHorodateSite, TimeSerieElementMongoIndexHorodate, TimeSerieElementTimescale, \
    TimeSerieElementQuestdb, TimeserieElementQuestdbPartition, TimeSerieElementQuestdbIndexSitePartition, \
    TimeSerieElementQuestdbIndexSite, TimeserieElementInflux
from postgres_benchmark.models import *
from utils.profile import ProfilerHandler

profiler = ProfilerHandler(print_our_code_only=True, sortby='cumtime', print_callers=True, print_callees=True,
                               output_file=f'./tmp/perf_report_{dt.datetime.now()}.txt',
                               output_table=f'./tmp/perf_table_{dt.datetime.now()}.csv')


def run():

    _dict = {
        # "postgres": [TimeSerieElementNonPartitionne, TimeSerieElementDoubleIndexationHorodateNonPartitionne,
        #              TimeSerieElementDoubleIndexationSiteNonPartitionne, TimeSerieElementTripleIndexationNonPartitionne,
        #              TimeSerieElement, TimeSerieElementIndexationHorodate, TimeSerieElementDoubleIndexationSite,
        #              TimeSerieElementTripleIndexation],
        # "mongo": [TimeSerieElementMongo, TimeSerieElementMongoIndexHorodate, TimeSerieElementMongoIndexSite, TimeSerieElementMongoIndexHorodateSite],
        # "timescale": [TimeSerieElementTimescale],
        # 'questdb': [TimeSerieElementQuestdb, TimeserieElementQuestdbPartition, TimeSerieElementQuestdbIndexSite, TimeSerieElementQuestdbIndexSitePartition],
        # 'influxdb': [TimeserieElementInflux]

    }

    liste_performances = []

    date_depart_population = dt.datetime(2021, 1, 1)
    date_fin_population = dt.datetime(2023, 7, 31)
    population_base = 10
    ecart_aleatoire = 10

    try:
        for database, models in _dict.items():
            insertion_sans_saturer_la_ram(database, population_base, models, date_depart_population, date_fin_population, 0, True, ecart_aleatoire)

            # kwargs = {
            #     'base': database,
            #     'models': models,
            #     'nombre_elements': 1,
            #     'type_element': 'element',
            #     'operation': 'ecriture',
            #     'date_depart_operation': dt.datetime(2023, 6, 2),
            #     'date_fin_operation': dt.datetime(2023, 7, 31),
            #     'remplissage_prealable': population_base,
            # }
            # perfs = profiler.profile_func(partial(benchmark, **kwargs))
            #
            # liste_performances.extend(perfs)
            print('ecriture un element')
            liste_performances.extend(
                benchmark(database, models, 1, 'element', 'ecriture', dt.datetime(2021, 1, 1), dt.datetime(2023, 1, 1), population_base, 5))

            print('update un element')
            liste_performances.extend(
                benchmark(database, models, 1, 'element', 'update', dt.datetime(2022, 2, 1, 0, 0),
                          dt.datetime(2022, 2, 1, 0, 4),
                          population_base))

            print('ecriture une courbe')

            liste_performances.extend(
                benchmark(database, models, 1, 'courbe', 'ecriture', dt.datetime(2021, 1, 1), dt.datetime(2023, 1, 1),
                          population_base))

            print('insertion avec update une courbe')

            liste_performances.extend(
                benchmark(database, models, 1, 'courbe', 'ecriture', dt.datetime(2023, 7, 1),
                          dt.datetime(2023, 8, 1),
                          population_base))

            # print('ecriture 100 courbes')
            #
            # liste_performances.extend(
            #     benchmark(database, models, 100, 'courbe', 'ecriture', dt.datetime(2021, 1, 1, 0, 0),
            #               dt.datetime(2022, 1, 1, 0, 4),
            #               population_base))

            # print('ecriture 1000 courbes')

            # liste_performances.extend(
            #     benchmark(database, models, 1000, 'courbe', 'ecriture', dt.datetime(2021, 1, 1, 0, 0),
            #               dt.datetime(2022, 1, 1, 0, 4),
            #               population_base))

            # tests en lecture

            print('lecture un element')

            liste_performances.extend(
                benchmark(database, models, 1, 'element', 'lecture', dt.datetime(2022, 2, 1, 0, 0,),
                          dt.datetime(2022, 1, 1, 0, 7),
                          population_base))

            print('lecture une courbe')

            liste_performances.extend(
                benchmark(database, models, 1, 'courbe', 'lecture', dt.datetime(2021, 1, 1),
                          dt.datetime(2023, 7, 28),
                          population_base))

            # print('lecture 100 courbe')
            #
            # liste_performances.extend(
            #     benchmark(database, models, 100, 'courbe', 'lecture', dt.datetime(2022, 2, 1),
            #               dt.datetime(2023, 2, 1),
            #               population_base))

            # print('lecture 1000 courbe')

            # liste_performances.extend(
            #     benchmark(database, models, 1000, 'courbe', 'lecture', dt.datetime(2022, 2, 1),
            #               dt.datetime(2023, 2, 1),
            #               population_base))
        print(f'liste_performances={liste_performances}')
        # profiler.gen_report()

        resultats_ecriture = pd.DataFrame(liste_performances)
        resultats_ecriture.to_csv(f'resultats_{population_base}_courbes_entre{date_depart_population}_et_{date_fin_population}_{dt.datetime.now()}.csv')

    finally:
        for k, i in _dict.items():
            for j in i:
                if k == 'mongo':
                    client = MongoClient("mongo", 27017)
                    db = client.mongo
                    if isinstance(j(), TimeSerieElementMongo):
                        collection = db.TimeSerieElementMongo
                    elif isinstance(j(), TimeSerieElementMongoIndexHorodate):
                        collection = db.TimeSerieElementMongoIndexHorodate
                    elif isinstance(j(), TimeSerieElementMongoIndexSite):
                        collection = db.TimeSerieElementMongoIndexSite
                    else:
                        collection = db.TimeSerieElementMongoIndexHorodateSite
                    print(f'grand nettoyage lancé pour {j.__name__}')
                    collection.remove({})
                    print(f'grand nettoyage terminé pour {j.__name__}')
                elif k == 'questdb':
                    print(f'grand nettoyage lancé pour {j.__name__}')
                    conn_str = 'user=admin password=quest host=questdb port=8812 dbname=qdb'
                    with pg.connect(conn_str) as connection:

                        with connection.cursor() as cur:
                            cur.execute(f'DROP TABLE {j().name};')


                    print(f'grand nettoyage terminé pour {j.__name__}')
                elif k == 'influxdb':

                    client = influxdb_client.InfluxDBClient(
                        url="http://influxdb:8086",
                        token="token",
                        org="holmium",
                        username="test",
                        password="password"
                    )

                    delete_api = client.delete_api()

                    delete_api.delete(dt.datetime(1980, 1, 1), dt.datetime(2077, 1, 1), '_measurement="test"', bucket="test")

                    client.__del__()
                else:
                    print(f'grand nettoyage lancé pour {j.__name__}')
                    j.objects.using(k).all().delete()
                    print(f'grand nettoyage terminé pour {j.__name__}')


