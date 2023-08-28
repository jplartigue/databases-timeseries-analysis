import time
from zoneinfo import ZoneInfo
import datetime as dt
import os

from pymongo import MongoClient

from benchmark_app_for_databases.interfaces_bases_de_donnees import InterfacePostgres, InterfaceMongo, \
    InterfaceTimescale
from generation_donnes import generation_donnees


def insertion_sans_saturer_la_ram(base: str, nombre_sites: int, models: list,
                                  date_debut: dt.datetime | list,
                                  date_fin: dt.datetime | list,
                                  identifiant_max: int, population: bool):
    limite_courbes_en_ram = 10
    temps = 0.0
    les_temps = []
    identifiant_original = identifiant_max
    if base == "postgres":  # or base == "timescale":
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
                                                                 date_debut, date_fin, j, identifiant_max, export, base)
            print("paré pour insertion en base")
            if export:
                print(f'utilisation de la fonction spécifique à postgres avec {j.__name__} et {base}')
                if base == 'postgres':
                    temps = InterfacePostgres.write(j, liste_elements)
                else:
                    temps = InterfaceTimescale.write(j, liste_elements)
                print(f'il y a actuellement {j.objects.using(base).count()} objets en base')
            elif base == 'mongo':



                temps = InterfaceMongo.write(j, liste_elements)
            else:

                temps = InterfaceTimescale.write(j, liste_elements)
                print(f'il y a actuellement {j.objects.using(base).count()} objets en base')
            print("insertion réussie")
            liste_elements.clear()
            current += min(limite_courbes_en_ram, nombre_sites - current)


        les_temps.append(temps)
    return les_temps, identifiant_max

def fonction_lecture(date_depart_operation: dt.datetime, date_fin_operation: dt.datetime, type_element: str, models: list, taille_ram: int, nombre_elements: int, base: str):
    if type_element == "element":
        taille_ram = taille_ram * 2522880
    liste_des_temps_et_models = [[], []]
    for j in models:
        liste_complette_a_requeter = []
        for i in range(0, nombre_elements):
            liste_complette_a_requeter.append(i)
        temps = 0.0
        while len(liste_complette_a_requeter) != 0:
            liste_a_requeter = liste_complette_a_requeter[0:taille_ram]
            liste_complette_a_requeter = liste_complette_a_requeter[taille_ram:]
            if type_element == "element":
                if base == "mongo":
                    temps = InterfaceMongo.read_at_timestamp(date_depart_operation, j, liste_a_requeter)
                elif base == 'postgres':
                    temps = InterfacePostgres.read_at_timestamp(date_depart_operation, j, liste_a_requeter)
                else:
                    temps = InterfaceTimescale.read_at_timestamp(date_depart_operation, j, liste_a_requeter)
            else:

                if base == 'mongo':
                    temps = InterfaceMongo.read_between_dates(date_depart_operation, date_fin_operation, j, liste_a_requeter)

                elif base == 'timescale':
                    temps = InterfaceTimescale.read_between_dates(date_depart_operation, date_fin_operation, j, liste_a_requeter)
                else:
                    temps = InterfacePostgres.read_between_dates(date_depart_operation, date_fin_operation, j, liste_a_requeter)
        liste_des_temps_et_models[0].append(temps)
        liste_des_temps_et_models[1].append(j)
    return liste_des_temps_et_models

def benchmark(base: str, models: list, nombre_elements: int, type_element: str, operation: str, date_depart_operation: dt.datetime, date_fin_operation: dt.datetime, remplissage_prealable: int, dates_depart: list, dates_fin: list, nombre_courbes: int=1):
    identifiant_max = 0
    resultat_test = []
    date_depart_operation = date_depart_operation.astimezone(ZoneInfo('UTC'))
    date_fin_operation = date_fin_operation.astimezone(ZoneInfo('UTC'))
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

                if base == 'postgres':
                    temps = InterfacePostgres.ajout_element_en_fin_de_courbe_de_charge(j, nombre_elements, nombre_courbes)
                elif base == 'timescale':
                    temps = InterfaceTimescale.ajout_element_en_fin_de_courbe_de_charge(j, nombre_elements, nombre_courbes)
                elif base == 'mongo':
                    temps = InterfaceMongo.ajout_element_en_fin_de_courbe_de_charge(j, nombre_elements, nombre_courbes, date_fin=dates_fin[0])
                else:
                    raise ValueError('base inconnue')

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
                if base == 'postgres':
                    temps = InterfacePostgres.update_at_timestamp(date_depart_operation, j, liste_elements_a_update)
                elif base == 'timescale':
                    temps = InterfaceTimescale.update_at_timestamp(date_depart_operation, j, liste_elements_a_update)
                else:
                    temps = InterfaceMongo.update_at_timestamp(date_depart_operation, j, liste_elements_a_update)
                resultat_test.append([base, temps, f"update de {nombre_elements} element de type {type_element}", j.__name__])
        elif type_element == 'courbe':
            for j in models:
                liste_elements_a_update = []
                for i in range(nombre_elements):
                    liste_elements_a_update.append(i)
                if base == 'postgres':
                    temps = InterfacePostgres.update_between_dates(date_depart_operation, date_fin_operation, j, liste_elements_a_update)
                elif base == 'timescale':
                    temps = InterfaceTimescale.update_between_dates(date_depart_operation, date_fin_operation, j, liste_elements_a_update)
                else:
                    temps = InterfaceMongo.update_between_dates(date_depart_operation, date_fin_operation, j, liste_elements_a_update)
                resultat_test.append([base, temps, f"update de {nombre_elements} element de type {type_element}", j.__name__])
        else:
            raise ValueError("ce type d'élément n'est pas reconnu. choix possibles: 'element' ou 'courbe'.")
    elif operation == "insertion avec update":
        temps, identifiant_max = insertion_sans_saturer_la_ram(base, nombre_elements, models, date_depart_operation, date_fin_operation, identifiant_max, False)
        for j in range(len(models)):
            resultat_test.append([base, temps[j], f"update de {nombre_elements} element de type {type_element}", models[j].__name__])
    else:
        raise ValueError("ce type d'opération n'est pas reconnu. choix possibles: 'lecture', 'update', 'insertion avec update' ou 'ecriture'.")




    for i in models:
        if base == 'mongo':
            client = MongoClient("mongo", 27017)
            db = client.mongo
            collection = db.TimeSerieElementMongo
            print(f'grand nettoyage lancé pour {i.__name__}')
            collection.remove({})
            print(f'grand nettoyage terminé pour {i.__name__}')
        else:
            print(f'grand nettoyage lancé pour {i.__name__}')
            i.objects.using(base).all().delete()
            print(f'grand nettoyage terminé pour {i.__name__}')
    return resultat_test
