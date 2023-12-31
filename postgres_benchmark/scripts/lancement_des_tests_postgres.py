import pandas as pd
from django.db.models import Max
from pymongo import MongoClient

from benchmark import benchmark
from postgres_benchmark.models import *
import datetime as dt

from utils.localtime import localise_date


def run():
    # qs = TimeSerieElement.objects.values('id_site').annotate(max_horodate=Max('horodate')).values('id_site', 'max_horodate')
    flag = 0
    _dict = {
        "postgres": [TimeSerieElement]  #, TimeSerieElementDoubleIndexationHorodate],
                     # TimeSerieElementDoubleIndexationSite, TimeSerieElementTripleIndexation],
        # "timescale": [TimeSerieElementTimescale],
        # "mongo": [TimeSerieElementMongo]
    }

    liste_performances = []
    try:

        for database, models in _dict.items():
            # print('ecriture un element')
            # liste_performances.extend(benchmark(database, models, 1, 'element', 'ecriture', dt.datetime(2021, 1, 1), dt.datetime(2023, 1, 1), 1, [dt.datetime(2023, 1, 1), dt.datetime(2023, 1, 1)], [dt.datetime(2023, 7, 1), dt.datetime(2023, 7, 28)]))
            print('ecriture un element')
            liste_performances.extend(benchmark(database, models, 1, 'element', 'ecriture', dt.datetime(2021, 1, 1), dt.datetime(2023, 1, 1), 10, [dt.datetime(2021, 1, 1), dt.datetime(2022, 1, 1)], [dt.datetime(2023, 1, 1), dt.datetime(2023, 7, 28)]))

            print('update un element')
            liste_performances.extend(
                benchmark(database, models, 1, 'element', 'update', dt.datetime(2022, 2, 1, 0, 0), dt.datetime(2022, 2, 1, 0, 4),
                          10, [dt.datetime(2021, 1, 1), dt.datetime(2022, 1, 1)],
                          [dt.datetime(2023, 1, 1), dt.datetime(2023, 7, 28)]))

            print('ecriture une courbe')

            liste_performances.extend(
                benchmark(database, models, 1, 'courbe', 'ecriture', dt.datetime(2021, 1, 1), dt.datetime(2023, 1, 1),
                          10, [dt.datetime(2021, 1, 1), dt.datetime(2022, 1, 1)],
                          [dt.datetime(2023, 1, 1), dt.datetime(2023, 7, 28)]))

            print('insertion avec update une courbe')

            liste_performances.extend(
                benchmark(database, models, 1, 'courbe', 'insertion avec update', dt.datetime(2023, 1, 1), dt.datetime(2023, 1, 1),
                          10, [dt.datetime(2021, 1, 1), dt.datetime(2022, 1, 1)],
                          [dt.datetime(2023, 1, 1), dt.datetime(2023, 7, 28)]))
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
            #tests en lecture

            print('lecture un element')

            liste_performances.extend(
                benchmark(database, models, 1, 'element', 'lecture', localise_date(dt.datetime(2021, 1, 1, 0, 0)),
                          localise_date(dt.datetime(2021, 1, 1, 0, 4)),
                          10, [dt.datetime(2021, 1, 1), dt.datetime(2022, 1, 1)],
                          [dt.datetime(2023, 1, 1), dt.datetime(2023, 7, 28)]))

            print('lecture une courbe')

            liste_performances.extend(
                benchmark(database, models, 1, 'courbe', 'lecture', dt.datetime(2021, 1, 1),
                          dt.datetime(2023, 7, 28),
                          10, [dt.datetime(2021, 1, 1), dt.datetime(2022, 1, 1)],
                          [dt.datetime(2023, 1, 1), dt.datetime(2023, 7, 28)]))

            # print('lecture 100 courbe')
            #
            # liste_performances.extend(
            #     benchmark(database, models, 100, 'courbe', 'lecture', dt.datetime(2022, 2, 1),
            #               dt.datetime(2023, 2, 1),
            #               100, [dt.datetime(2021, 1, 1), dt.datetime(2022, 1, 1)],
            #               [dt.datetime(2023, 1, 1), dt.datetime(2023, 7, 28)]))

            # print('lecture 1000 courbe')

            # liste_performances.extend(
            #     benchmark(database, models, 1000, 'courbe', 'lecture', dt.datetime(2022, 2, 1),
            #               dt.datetime(2023, 2, 1),
            #               1000, [dt.datetime(2021, 1, 1), dt.datetime(2022, 1, 1)],
            #               [dt.datetime(2023, 1, 1), dt.datetime(2023, 7, 28)]))
        print(f'liste_performances={liste_performances}')

        resultats_ecriture = pd.DataFrame(liste_performances)
        resultats_ecriture.to_csv('resultats.csv')
        flag = 1
    finally:
        if flag == 0:
            for k, i in _dict.items():
                for j in i:
                    if k == 'mongo':
                        client = MongoClient("mongo", 27017)
                        db = client.mongo
                        collection = db.TimeSerieElementMongo
                        collection.remove({})
                    else:
                        j.objects.all().delete()
