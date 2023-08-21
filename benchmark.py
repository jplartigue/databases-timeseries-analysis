import time
from itertools import islice
from zoneinfo import ZoneInfo
import numpy as np
import datetime as dt
import os

from pymongo import MongoClient

from benchmark_app_for_databases.models import TimeSerieElementMongo
from generation_donnes import generation_donnees


def insertion_sans_saturer_la_ram(base: str, nombre_sites: int, models: list,
                                  date_debut: dt.datetime | list,
                                  date_fin: dt.datetime | list,
                                  identifiant_max: int, population: bool):
    limite_courbes_en_ram = 10
    temps = 0.0
    les_temps = []
    identifiant_original = identifiant_max
    if base == "postgres":  #or base == "timescale":
        export = True
    else:
        export = False
    # export = False
    print(f'models={models}')
    for j in models:
        print(f'base={base}')
        if population:
            identifiant_max = 0
        else:
            identifiant_max = identifiant_original
        current = 0
        while current != nombre_sites:
            print(f'current={current}\nnombre_sites={nombre_sites}')
            liste_elements, identifiant_max = generation_donnees(min(limite_courbes_en_ram, nombre_sites-current),
                                                                 date_debut, date_fin, j, identifiant_max, export)
            print("paré pour insertion en base")
            if export:
                print(f'utilisation de la fonction spécifique à postgres avec {j.__name__} et {base}')
                for i in liste_elements:
                    debut = time.time()
                    j.objects.using(base).from_csv(i, using=base)
                    fin = time.time()
                    temps = temps + (fin - debut)
                    os.remove(i)
                    print('destruction du fichier temporaire')
            else:
                # for i in liste_elements:
                #     print(f'{i.valeur}')
                #     debut = time.time()
                #     # i.objects.using(base).save()
                #     i.save()
                #     fin = time.time()
                #     temps = temps + (fin - debut)

                # for i in liste_elements:
                #     print(f'on insère dans {base}')
                #     j.objects.using(base).create(i)

                debut = time.time()
                j.objects.using(base).bulk_create(liste_elements, batch_size=200000)  #, batch_size=2000
                fin = time.time()

                # client = MongoClient("mongo", 27017)
                # db = client.mongo
                # collection = db.TimeSerieElementMongo
                # debut = time.time()
                # collection.insert_many(liste_elements)
                # fin = time.time()
                temps = temps + (fin - debut)
                # print(f'nombre de documents injectés: {collection.count_documents({})}')
            print("insertion réussie")
            current += min(limite_courbes_en_ram, nombre_sites - current)
            print(f'il y a actuellement {j.objects.using(base).count()} objets en base')

        les_temps.append(temps)
    return les_temps, identifiant_max

def fonction_lecture(date_depart_operation: dt.datetime, date_fin_operation: dt.datetime, type_element: str, models: list, taille_ram: int, nombre_elements: int, base: str):
    if type_element == "element":
        taille_ram = taille_ram * 2522880
    liste_des_temps_et_models = [[], []]
    for j in models:
        liste_complette_a_requeter = range(0, nombre_elements)
        temps = 0.0
        while len(liste_complette_a_requeter) != 0:
            liste_a_requeter = liste_complette_a_requeter[0:taille_ram]
            liste_complette_a_requeter = liste_complette_a_requeter[taille_ram:]
            debut = time.time()
            if type_element == "element":
                # if base == "mongo":
                #     client = MongoClient("mongo", 27017)
                #     db = client.mongo
                #     collection = db.TimeSerieElementMongo
                #     debut = time.time()
                #     collection.find({"id_site": {'$in': liste_a_requeter}, "horodate": {'$lte': date_fin_operation.astimezone(ZoneInfo("UTC")), '$gte': date_depart_operation.astimezone(ZoneInfo("UTC"))}})
                _ = list(j.objects.using(base).filter(id_site__in=liste_a_requeter,
                                                      horodate__gte=date_depart_operation,
                                                      horodate__lte=date_fin_operation))
            else:
                _ = list(j.objects.using(base).filter(id_site__in=liste_a_requeter,
                                                      horodate__gte=date_depart_operation,
                                                      horodate__lte=date_fin_operation))
            fin = time.time()
            temps = temps + (fin - debut)
        liste_des_temps_et_models[0].append(temps)
        liste_des_temps_et_models[1].append(j)
    return liste_des_temps_et_models

def benchmark(base: str, models: list, nombre_elements: int, type_element: str, operation: str, date_depart_operation: dt.datetime, date_fin_operation: dt.datetime, remplissage_prealable: int, dates_depart: list, dates_fin: list):
    identifiant_max = 0
    resultat_test = []
    taille_ram = 10
    _, identifiant_max = insertion_sans_saturer_la_ram(base, remplissage_prealable, models, dates_depart, dates_fin, identifiant_max, True)
    if operation == 'lecture':
        if type_element != "courbe" and type_element != "element" or nombre_elements > remplissage_prealable:
            raise ValueError("ce type d'élément n'est pas reconnu ou vous avez demander à lire plus d'éléments qu'il n'y en as en base. choix possibles: 'element' ou 'courbe'.")
        temps_et_models = fonction_lecture(date_depart_operation, date_fin_operation, type_element, models, taille_ram,
                                           nombre_elements, base)
        flag = 0
        for i in temps_et_models[0]:
            resultat_test.append([base, i, f"lecture de {nombre_elements} element de type {type_element}", temps_et_models[1][flag].__name__])
            flag += 1

    elif operation == 'ecriture':
        if type_element == 'courbe':
            les_temps, identifiant_max = insertion_sans_saturer_la_ram(base, nombre_elements, models, date_depart_operation, date_fin_operation, identifiant_max, False)
            for idx, temp in enumerate(les_temps):
                resultat_test.append([base, temp, f"ecriture de {nombre_elements} element de type {type_element}", models[idx].__name__])
        elif type_element == 'element':


            for j in models:

                liste_elements_a_inserer = []
                for i in range(nombre_elements):
                    derniere_entree = j.objects.using(base).filter(id_site=i).latest("horodate").horodate
                    if base == 'postgres' or base == 'timescale':
                        element_a_inserer, _ = generation_donnees(nombre_elements, derniere_entree + dt.timedelta(minutes=5), derniere_entree + dt.timedelta(minutes=6), j, i, True)
                    else:
                        element_a_inserer, _ = generation_donnees(nombre_elements, derniere_entree + dt.timedelta(minutes=5), derniere_entree + dt.timedelta(minutes=6), j, i, False)
                    liste_elements_a_inserer.append(element_a_inserer)


                temps = 0.0
                if base == 'postgres' or base == 'timescale':
                    for i in range(nombre_elements):
                        debut = time.time()
                        j.objects.using(base).from_csv(f'tmp/df_{i}.csv', using=base)
                        fin = time.time()
                        temps = temps+(fin-debut)
                        os.remove(f'tmp/df_{i}.csv')
                else:

                    debut = time.time()
                    j.objects.using(base).bulk_create(liste_elements_a_inserer, )
                    fin = time.time()
                    temps = fin - debut

                resultat_test.append([base, temps, f"ecriture de {nombre_elements} element de type {type_element}", j.__name__])
        else:
            raise ValueError("ce type d'élément n'est pas reconnu. choix possibles: 'element' ou 'courbe'.")
    elif operation == "update":
        if type_element == 'element':
            for j in models:
                liste_elements_a_update = []
                for i in range(nombre_elements):
                    liste_elements_a_update.append(i)
                # print(f'les éléments qui seront demandés sont {liste_elements_a_update}')

                if nombre_elements < 2:
                    element = j.objects.using(base).filter(id_site__in=liste_elements_a_update).latest("horodate")
                    element.valeur = 12
                    debut = time.time()
                    element.save()
                    fin = time.time()
                else:
                    debut = time.time()
                    j.objects.using(base).filter(id_site__in=liste_elements_a_update).latest("horodate").update(valeur=12)
                    fin = time.time()
                resultat_test = [base, fin - debut, f"update de {nombre_elements} element de type {type_element}", j.__name__]
        elif type_element == 'courbe':
            for j in models:
                liste_elements_a_update = []
                for i in range(nombre_elements):
                    liste_elements_a_update.append(identifiant_max)
                    identifiant_max -= 1
                debut = time.time()
                j.objects.using(base).filter(id_site__in=liste_elements_a_update).update(valeur=12)
                fin = time.time()
                resultat_test = [base, fin - debut, f"update de {nombre_elements} element de type {type_element}", j.__name__]
        else:
            raise ValueError("ce type d'élément n'est pas reconnu. choix possibles: 'element' ou 'courbe'.")
    elif operation == "insertion avec update":

        _, identifiant_max = insertion_sans_saturer_la_ram(base, nombre_elements, models, dates_depart[0] or dates_depart, dates_fin[0] or dates_fin, identifiant_max, False)
        identifiant_max -= nombre_elements
        temps, identifiant_max = insertion_sans_saturer_la_ram(base, nombre_elements, models, date_depart_operation, date_fin_operation, identifiant_max, False)
        for j in range(len(models)):
            resultat_test = [base, temps[j], f"update de {nombre_elements} element de type {type_element}", models[j].__name__]
    else:
        raise ValueError("ce type d'opération n'est pas reconnu. choix possibles: 'lecture', 'update', 'insertion avec update' ou 'ecriture'.")
    for i in models:
        print(f'grand nettoyage lancé pour {i.__name__}')
        i.objects.using(base).all().delete()
        print(f'grand nettoyage terminé pour {i.__name__}')
    return resultat_test
