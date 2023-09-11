from benchmark_app_for_databases.interfaces_bases_de_donnees import *
from generation_donnes import generation_donnees
from utils.localtime import localise_date


def insertion_sans_saturer_la_ram(base: str, nombre_sites: int, models: list,
                                  date_debut: dt.datetime,
                                  date_fin: dt.datetime,
                                  identifiant_max: int, population: bool, rand_days: int):
    limite_courbes_en_ram = 10
    temps = 0.0
    les_temps = []
    date_debut = localise_datetime(date_debut)
    date_fin = localise_datetime(date_fin)
    identifiant_original = identifiant_max
    if base == "postgres" or base == "timescale":
        export = True
    else:
        export = False
    print(f'models={models}')
    for current_model in models:
        print(f'base={base}')
        if population:
            identifiant_max = 0
        else:
            identifiant_max = identifiant_original
        current = 0
        while current != nombre_sites:
            print(f'current={current}\nnombre_sites={nombre_sites}')

            liste_elements, identifiant_max = generation_donnees(min(limite_courbes_en_ram, nombre_sites-current),
                                                                 date_debut, date_fin, current_model, identifiant_max, export, base, rand_days)
            print("paré pour insertion en base")
            temps = current_model.interface.write(current_model, liste_elements)
            print("insertion réussie")
            liste_elements.clear()
            current += min(limite_courbes_en_ram, nombre_sites - current)


        les_temps.append(temps)
    return les_temps, identifiant_max

def fonction_lecture(date_depart_operation: dt.datetime, date_fin_operation: dt.datetime, type_element: str, models: list, taille_ram: int, nombre_elements: int, base: str):
    if type_element == "element":
        taille_ram = taille_ram * 2522880
    liste_des_temps_et_models = [[], []]
    for current_model in models:
        liste_complette_a_requeter = []
        for i in range(0, nombre_elements):
            liste_complette_a_requeter.append(i)
        temps = 0.0
        while len(liste_complette_a_requeter) != 0:
            liste_a_requeter = liste_complette_a_requeter[0:taille_ram]
            liste_complette_a_requeter = liste_complette_a_requeter[taille_ram:]
            if type_element == "element":
                temps = current_model.interface.read_at_timestamp(date_depart_operation, current_model, liste_a_requeter)
            else:
                temps = current_model.interface.read_between_dates(date_depart_operation, date_fin_operation, current_model, liste_a_requeter)
        liste_des_temps_et_models[0].append(temps)
        liste_des_temps_et_models[1].append(current_model)
    return liste_des_temps_et_models

def benchmark(base: str, models: list, nombre_elements: int,
              type_element: str, operation: str,
              date_depart_operation: dt.datetime,
              date_fin_operation: dt.datetime,
              remplissage_prealable: int,
              nombre_courbes: int=1):
    resultat_test = []
    taille_ram = 10
    identifiant_max = remplissage_prealable
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
            les_temps, identifiant_max = insertion_sans_saturer_la_ram(base, nombre_elements, models, date_depart_operation, date_fin_operation, identifiant_max, False, 0)
            for idx, temp in enumerate(les_temps):
                resultat_test.append([base, temp, f"ecriture de {nombre_elements} element de type {type_element}", models[idx].__name__])
        elif type_element == 'element':


            for current_model in models:

                temps = current_model.interface.ajout_element_en_fin_de_courbe_de_charge(current_model, nombre_elements, nombre_courbes)

                resultat_test.append([base, temps, f"ecriture de {nombre_elements} element de type {type_element}", current_model.__name__])
        else:
            raise ValueError("ce type d'élément n'est pas reconnu. choix possibles: 'element' ou 'courbe'.")
    elif operation == "update":
        if type_element == 'element':
            for current_model in models:
                liste_elements_a_update = []
                for i in range(nombre_elements):
                    liste_elements_a_update.append(i)
                temps = current_model.interface.update_at_timestamp(date_depart_operation, current_model, liste_elements_a_update)
                resultat_test.append([base, temps, f"update de {nombre_elements} element de type {type_element}", current_model.__name__])
        elif type_element == 'courbe':
            for current_model in models:
                liste_elements_a_update = []
                for i in range(nombre_elements):
                    liste_elements_a_update.append(i)
                temps = current_model.interface.update_between_dates(date_depart_operation, date_fin_operation, current_model, liste_elements_a_update)
                resultat_test.append([base, temps, f"update de {nombre_elements} element de type {type_element}", current_model.__name__])
        else:
            raise ValueError("ce type d'élément n'est pas reconnu. choix possibles: 'element' ou 'courbe'.")
    elif operation == "insertion avec update":
        for i in models:
            if base == "postgres" or base == 'timescale':
                elements_a_inserer = generation_pour_ajout_donnees(nombre_elements, date_depart_operation,
                                                                   date_fin_operation, i, identifiant_max, True, base)
            else:
                elements_a_inserer = generation_pour_ajout_donnees(nombre_elements, date_depart_operation, date_fin_operation, i, identifiant_max, False, base)
            i.interface.write(i, elements_a_inserer)
        temps, identifiant_max = insertion_sans_saturer_la_ram(base, nombre_elements, models, date_depart_operation, date_fin_operation, 0, False, 0)
        for current_model in range(len(models)):
            resultat_test.append([base, temps[current_model], f"update de {nombre_elements} element de type {type_element}", models[current_model].__name__])
    else:
        raise ValueError("ce type d'opération n'est pas reconnu. choix possibles: 'lecture', 'update', 'insertion avec update' ou 'ecriture'.")

    return resultat_test
