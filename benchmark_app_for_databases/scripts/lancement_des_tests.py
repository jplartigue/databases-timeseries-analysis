import gc

import pandas as pd
from pymongo import MongoClient

from benchmark import benchmark
from benchmark_app_for_databases.models import *
import datetime as dt

from postgres_benchmark.models import *
from utils.localtime import localise_date



def run():
    _dict = {
        # "postgres": [TimeSerieElementNonPartitionne, TimeSerieElementDoubleIndexationHorodateNonPartitionne,
        #              TimeSerieElementDoubleIndexationSiteNonPartitionne, TimeSerieElementTripleIndexationNonPartitionne,
        #              TimeSerieElement, TimeSerieElementIndexationHorodate, TimeSerieElementDoubleIndexationSite,
        #              TimeSerieElementTripleIndexation],
        # "mongo": [TimeSerieElementMongo, TimeSerieElementMongoIndexHorodate, TimeSerieElementMongoIndexSite,TimeSerieElementMongoIndexHorodateSite],
        # "timescale": [TimeSerieElementTimescale, TimeSerieElementTimescaleDoubleIndexationSite, TimeSerieElementQuestdbIndexSite, TimeSerieElementQuestdbIndexSitePartition],
        # 'questdb': [TimeSerieElementQuestdb, TimeserieElementQuestdbPartition, TimeSerieElementQuestdbIndexSite, TimeSerieElementQuestdbIndexSitePartition]
        'influxdb': [TimeserieElementInflux]

    }

    liste_performances = []
    flag = 0
    # gc.set_debug(gc.DEBUG_STATS)  # gc.DEBUG_COLLECTABLE  gc.DEBUG_STATS gc.DEBUG_LEAK

    print(f'le ramasse miettes est: {gc.isenabled()}')

    for database, models in _dict.items():
        print('ecriture un element')
        liste_performances.extend(benchmark(database, models, 1, 'courbe', 'lecture', dt.datetime(2023, 6, 2), dt.datetime(2023, 6, 3), 1, [dt.datetime(2023, 6, 1), dt.datetime(2023, 6, 1)], [dt.datetime(2023, 7, 1), dt.datetime(2023, 7, 28)]))
        # print('ecriture un element')
        # liste_performances.extend(
        #     benchmark(database, models, 1, 'element', 'ecriture', dt.datetime(2021, 1, 1), dt.datetime(2023, 1, 1), 10,
        #               [dt.datetime(2022, 1, 1), dt.datetime(2022, 1, 1)],
        #               [dt.datetime(2023, 1, 1), dt.datetime(2023, 7, 28)]))
        #
        # print('update un element')
        # liste_performances.extend(
        #     benchmark(database, models, 1, 'element', 'update', dt.datetime(2022, 2, 1, 0, 0),
        #               dt.datetime(2022, 2, 1, 0, 4),
        #               10, [dt.datetime(2021, 1, 1), dt.datetime(2022, 1, 1)],
        #               [dt.datetime(2023, 1, 1), dt.datetime(2023, 7, 28)]))
        #
        # print('ecriture une courbe')
        #
        # liste_performances.extend(
        #     benchmark(database, models, 1, 'courbe', 'ecriture', dt.datetime(2021, 1, 1), dt.datetime(2023, 1, 1),
        #               10, [dt.datetime(2021, 1, 1), dt.datetime(2022, 1, 1)],
        #               [dt.datetime(2023, 1, 1), dt.datetime(2023, 7, 28)]))
        #
        # print('insertion avec update une courbe')
        #
        # liste_performances.extend(
        #     benchmark(database, models, 1, 'courbe', 'insertion avec update', dt.datetime(2023, 7, 1),
        #               dt.datetime(2023, 8, 1),
        #               10, [dt.datetime(2021, 1, 1), dt.datetime(2022, 1, 1)],
        #               [dt.datetime(2023, 7, 28), dt.datetime(2023, 7, 28)]))
        #
        # # print('ecriture 100 courbes')
        # #
        # # liste_performances.extend(
        # #     benchmark(database, models, 100, 'courbe', 'ecriture', dt.datetime(2021, 1, 1, 0, 0),
        # #               dt.datetime(2022, 1, 1, 0, 4),
        # #               10, [dt.datetime(2021, 1, 1), dt.datetime(2022, 1, 1)],
        # #               [dt.datetime(2023, 1, 1), dt.datetime(2023, 7, 28)]))
        #
        # # print('ecriture 1000 courbes')
        #
        # # liste_performances.extend(
        # #     benchmark(database, models, 1000, 'courbe', 'ecriture', dt.datetime(2021, 1, 1, 0, 0),
        # #               dt.datetime(2022, 1, 1, 0, 4),
        # #               10, [dt.datetime(2021, 1, 1), dt.datetime(2022, 1, 1)],
        # #               [dt.datetime(2023, 1, 1), dt.datetime(2023, 7, 28)]))
        #
        # # tests en lecture
        #
        # print('lecture un element')
        #
        # liste_performances.extend(
        #     benchmark(database, models, 1, 'element', 'lecture', localise_date(dt.datetime(2022, 2, 1, 0, 0)),
        #               localise_date(dt.datetime(2022, 1, 1, 0, 7)),
        #               10, [dt.datetime(2021, 1, 1), dt.datetime(2022, 1, 1)],
        #               [dt.datetime(2023, 1, 1), dt.datetime(2023, 7, 28)]))
        #
        # print('lecture une courbe')
        #
        # liste_performances.extend(
        #     benchmark(database, models, 1, 'courbe', 'lecture', dt.datetime(2021, 1, 1),
        #               dt.datetime(2023, 7, 28),
        #               10, [dt.datetime(2021, 1, 1), dt.datetime(2022, 1, 1)],
        #               [dt.datetime(2023, 1, 1), dt.datetime(2023, 7, 28)]))
        #
        # # print('lecture 100 courbe')
        # #
        # # liste_performances.extend(
        # #     benchmark(database, models, 100, 'courbe', 'lecture', dt.datetime(2022, 2, 1),
        # #               dt.datetime(2023, 2, 1),
        # #               100, [dt.datetime(2021, 1, 1), dt.datetime(2022, 1, 1)],
        # #               [dt.datetime(2023, 1, 1), dt.datetime(2023, 7, 28)]))
        #
        # # print('lecture 1000 courbe')
        #
        # # liste_performances.extend(
        # #     benchmark(database, models, 1000, 'courbe', 'lecture', dt.datetime(2022, 2, 1),
        # #               dt.datetime(2023, 2, 1),
        # #               1000, [dt.datetime(2021, 1, 1), dt.datetime(2022, 1, 1)],
        # #               [dt.datetime(2023, 1, 1), dt.datetime(2023, 7, 28)]))
    print(f'liste_performances={liste_performances}')

    resultats_ecriture = pd.DataFrame(liste_performances)
    resultats_ecriture.to_csv(f'resultats_{dt.datetime.now()}.csv')
    gc.collect()

    # try:
    #     for database, models in _dict.items():
    #         # print('ecriture un element')
    #         # liste_performances.extend(benchmark(database, models, 1, 'element', 'ecriture', dt.datetime(2021, 1, 1), dt.datetime(2023, 1, 1), 1, [dt.datetime(2023, 6, 1), dt.datetime(2023, 6, 1)], [dt.datetime(2023, 7, 1), dt.datetime(2023, 7, 28)]))
    #         print('ecriture un element')
    #         liste_performances.extend(benchmark(database, models, 1, 'element', 'ecriture', dt.datetime(2021, 1, 1), dt.datetime(2023, 1, 1), 10, [dt.datetime(2021, 1, 1), dt.datetime(2022, 1, 1)], [dt.datetime(2023, 1, 1), dt.datetime(2023, 7, 28)]))
    #
    #         print('update un element')
    #         liste_performances.extend(
    #             benchmark(database, models, 1, 'element', 'update', dt.datetime(2022, 2, 1, 0, 0), dt.datetime(2022, 2, 1, 0, 4),
    #                       10, [dt.datetime(2021, 1, 1), dt.datetime(2022, 1, 1)],
    #                       [dt.datetime(2023, 1, 1), dt.datetime(2023, 7, 28)]))
    #
    #         print('ecriture une courbe')
    #
    #         liste_performances.extend(
    #             benchmark(database, models, 1, 'courbe', 'ecriture', dt.datetime(2021, 1, 1), dt.datetime(2023, 1, 1),
    #                       10, [dt.datetime(2021, 1, 1), dt.datetime(2022, 1, 1)],
    #                       [dt.datetime(2023, 1, 1), dt.datetime(2023, 7, 28)]))
    #
    #         print('insertion avec update une courbe')
    #
    #         liste_performances.extend(
    #             benchmark(database, models, 1, 'courbe', 'insertion avec update', dt.datetime(2023, 1, 1), dt.datetime(2023, 1, 1),
    #                       10, [dt.datetime(2021, 1, 1), dt.datetime(2022, 1, 1)],
    #                       [dt.datetime(2023, 1, 1), dt.datetime(2023, 7, 28)]))
    #         #
    #         # # print('ecriture 100 courbes')
    #         # #
    #         # # liste_performances.extend(
    #         # #     benchmark(database, models, 100, 'courbe', 'ecriture', dt.datetime(2021, 1, 1, 0, 0),
    #         # #               dt.datetime(2022, 1, 1, 0, 4),
    #         # #               10, [dt.datetime(2021, 1, 1), dt.datetime(2022, 1, 1)],
    #         # #               [dt.datetime(2023, 1, 1), dt.datetime(2023, 7, 28)]))
    #         #
    #         # # print('ecriture 1000 courbes')
    #         #
    #         # # liste_performances.extend(
    #         # #     benchmark(database, models, 1000, 'courbe', 'ecriture', dt.datetime(2021, 1, 1, 0, 0),
    #         # #               dt.datetime(2022, 1, 1, 0, 4),
    #         # #               10, [dt.datetime(2021, 1, 1), dt.datetime(2022, 1, 1)],
    #         # #               [dt.datetime(2023, 1, 1), dt.datetime(2023, 7, 28)]))
    #         #
    #         #tests en lecture
    #
    #         print('lecture un element')
    #
    #         liste_performances.extend(
    #             benchmark(database, models, 1, 'element', 'lecture', localise_date(dt.datetime(2021, 1, 1, 0, 0)),
    #                       localise_date(dt.datetime(2021, 1, 1, 0, 4)),
    #                       10, [dt.datetime(2021, 1, 1), dt.datetime(2022, 1, 1)],
    #                       [dt.datetime(2023, 1, 1), dt.datetime(2023, 7, 28)]))
    #
    #         print('lecture une courbe')
    #
    #         liste_performances.extend(
    #             benchmark(database, models, 1, 'courbe', 'lecture', dt.datetime(2021, 1, 1),
    #                       dt.datetime(2023, 7, 28),
    #                       10, [dt.datetime(2021, 1, 1), dt.datetime(2022, 1, 1)],
    #                       [dt.datetime(2023, 1, 1), dt.datetime(2023, 7, 28)]))
    #
    #         # print('lecture 100 courbe')
    #         #
    #         # liste_performances.extend(
    #         #     benchmark(database, models, 100, 'courbe', 'lecture', dt.datetime(2022, 2, 1),
    #         #               dt.datetime(2023, 2, 1),
    #         #               100, [dt.datetime(2021, 1, 1), dt.datetime(2022, 1, 1)],
    #         #               [dt.datetime(2023, 1, 1), dt.datetime(2023, 7, 28)]))
    #
    #         # print('lecture 1000 courbe')
    #
    #         # liste_performances.extend(
    #         #     benchmark(database, models, 1000, 'courbe', 'lecture', dt.datetime(2022, 2, 1),
    #         #               dt.datetime(2023, 2, 1),
    #         #               1000, [dt.datetime(2021, 1, 1), dt.datetime(2022, 1, 1)],
    #         #               [dt.datetime(2023, 1, 1), dt.datetime(2023, 7, 28)]))
    #     print(f'liste_performances={liste_performances}')
    #
    #     resultats_ecriture = pd.DataFrame(liste_performances)
    #     resultats_ecriture.to_csv('resultats.csv')
    #     flag = 1
    # finally:
    #
    #     if flag == 0:
    #         print("nettoyages d'urgence des bases de donees")
    #         for k, i in _dict.items():
    #             for j in i:
    #                 if k == 'mongo':
    #                     client = MongoClient("mongo", 27017)
    #                     db = client.mongo
    #                     collection = db.TimeSerieElementMongo
    #                     collection.remove({})
    #                 else:
    #                     j.objects.all().delete()
