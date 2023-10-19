from benchmark_app_for_databases.interfaces_bases_de_donnees import *
from data_generator import generate_fake_dataframe


def insertion_sans_saturer_la_ram(base: str, nombre_sites: int, models: list,
                                  date_debut: dt.datetime,
                                  date_fin: dt.datetime,
                                  identifiant_max: int, population: bool, rand_days: int):
    """
    cette fonction est pensée pour permettre de créer et insérer lescourbes de charge dans les bases de données tout en
    évitant de saturer la mémoire vive. pour modifier le nombre de courbes de charge à manipuler à chaque fois il faut
    modifier la valeur affectée à la variable limite_courbes_en_ram à la main.
    :param base: le nom de la base concernée
    :param nombre_sites: le nombre de courbes à créer en tout
    :param models: les models à utiliser
    :param date_debut: la date du premier élément de chaque courbe de charge
    :param date_fin: la date du dernier élément de chaque courbe de charge
    :param identifiant_max: l'identifiant de site maximum qui se trouve en base
    :param population: un booléen pour spécifier si la création se déroule dans le cadre de la phase de remplissag de la base de données ou dans le cadre d'un test
    :param rand_days: le nombre de jours d'écart tolérés avec les dates de départ et de fin des courbes de charge
    :return: la liste des temps totaux pris par les insertions dans l'ordre des models et l'identifiant maximum en base
    """
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
    for current_model in models:
        if population:
            identifiant_max = 0
        else:
            identifiant_max = identifiant_original
        current = 0
        while current != nombre_sites:
            if population:
                liste_elements, identifiant_max = generate_fake_dataframe(min(limite_courbes_en_ram, nombre_sites - current),
                                                                          date_debut, date_fin, current_model,
                                                                          export, base, rand_days)
            else:
                liste_elements, identifiant_max = generation_pour_ajout_donnees(min(limite_courbes_en_ram,
                                                                                    nombre_sites - current),
                                                                                date_debut, date_fin, current_model,
                                                                                identifiant_max, export, base)
            temps = current_model.interface.write(current_model, liste_elements)
            liste_elements.clear()
            current += min(limite_courbes_en_ram, nombre_sites - current)

        les_temps.append(temps)
    return les_temps, identifiant_max


def fonction_lecture(date_depart_operation: dt.datetime, date_fin_operation: dt.datetime, type_element: str,
                     models: list, taille_ram: int, nombre_elements: int):
    """
    cette fonction est prévue pour lire les données des bases de données sans saturer la mémoire vive
    :param date_depart_operation: la date du plus ancient point qui sera requêté
    :param date_fin_operation: la date du point le plus récent qui sera requêté
    :param type_element: le type d'élément demandé (element pour demander des points et courbe pour demander des courbes)
    :param models: les models à utiliser
    :param taille_ram: le nombre de courbes qui peuvent tenir en mémoire vive (penser à prévoir quand-même une marge de 1 Go minimum)
    :param nombre_elements: le nombre de points ou de courbes de charge à requêter
    :return:
    """
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
                temps = current_model.interface.read_at_timestamp(date_depart_operation, current_model,
                                                                  liste_a_requeter)
            else:
                temps = current_model.interface.read_between_dates(date_depart_operation, date_fin_operation,
                                                                   current_model, liste_a_requeter)
        liste_des_temps_et_models[0].append(temps)
        liste_des_temps_et_models[1].append(current_model)
    return liste_des_temps_et_models


def benchmark(base: str, models: list, nombre_elements: int,
              type_element: str, operation: str,
              date_depart_operation: dt.datetime,
              date_fin_operation: dt.datetime,
              remplissage_prealable: int,
              nombre_courbes: int = 1):
    """
    c'est la fonction qui va appeler les fonctions adaptées au test demandé par l'utilisateur.
    :param base: la base à tester
    :param models: les models ratachés à la base
    :param nombre_elements: le nombre de points ou de courbe de charge concernés par le test
    :param type_element: le type d'élément concerné par le test ("element" pour demander un point de courbe de charge ou "courbe" pour des courbes de charge)
    :param operation: le type de test/opération à effectuer ("ecriture", "lecture", "update" ou "insertion avec update")
    :param date_depart_operation: la date de départ de l'opération
    :param date_fin_operation: la date de fin de l'opération
    :param remplissage_prealable: int pour indiquer combien de courbes se trouvent déjà en base
    :param nombre_courbes: paramètre qui ne sert que dans le cas d'un test d'écriture de points et sert à donner le nombre de courbe concernées par le test
    :return: une liste dont chaque élément représente le rapport portant sur un test
    """
    resultat_test = []
    taille_ram = 10
    identifiant_max = remplissage_prealable
    if operation == 'lecture':
        if type_element != "courbe" and type_element != "element" or nombre_elements > remplissage_prealable:
            raise ValueError(
                "ce type d'élément n'est pas reconnu ou vous avez demander à lire plus d'éléments qu'il n'y en as en "
                "base. choix possibles: 'element' ou 'courbe'.")
        temps_et_models = fonction_lecture(date_depart_operation, date_fin_operation, type_element, models, taille_ram,
                                           nombre_elements)
        flag = 0
        for i in temps_et_models[0]:
            resultat_test.append([base, i, f"lecture de {nombre_elements} element de type {type_element}",
                                  temps_et_models[1][flag].__name__])
            flag += 1

    elif operation == 'ecriture':
        if type_element == 'courbe':
            les_temps, identifiant_max = insertion_sans_saturer_la_ram(base, nombre_elements, models,
                                                                       date_depart_operation, date_fin_operation,
                                                                       identifiant_max, False, 0)
            for idx, temp in enumerate(les_temps):
                resultat_test.append(
                    [base, temp, f"ecriture de {nombre_elements} element de type {type_element}", models[idx].__name__])
        elif type_element == 'element':

            for current_model in models:
                temps = current_model.interface.ajout_element_en_fin_de_courbe_de_charge(current_model, nombre_elements,
                                                                                         nombre_courbes)

                resultat_test.append([base, temps,
                                      f"ecriture de {nombre_elements} element de type {type_element} sur {nombre_courbes} courbes",
                                      current_model.__name__])
        else:
            raise ValueError("ce type d'élément n'est pas reconnu. choix possibles: 'element' ou 'courbe'.")
    elif operation == "update":
        if type_element == 'element':
            for current_model in models:
                liste_elements_a_update = []
                for i in range(nombre_elements):
                    liste_elements_a_update.append(i)
                temps = current_model.interface.update_at_timestamp(date_depart_operation, current_model,
                                                                    liste_elements_a_update)
                resultat_test.append([base, temps, f"update de {nombre_elements} element de type {type_element}",
                                      current_model.__name__])
        elif type_element == 'courbe':
            for current_model in models:
                liste_elements_a_update = []
                for i in range(nombre_elements):
                    liste_elements_a_update.append(i)
                temps = current_model.interface.update_between_dates(date_depart_operation, date_fin_operation,
                                                                     current_model, liste_elements_a_update)
                resultat_test.append([base, temps, f"update de {nombre_elements} element de type {type_element}",
                                      current_model.__name__])
        else:
            raise ValueError("ce type d'élément n'est pas reconnu. choix possibles: 'element' ou 'courbe'.")
    elif operation == "insertion avec update":
        for i in models:
            if base == "postgres" or base == 'timescale':
                elements_a_inserer = generation_pour_ajout_donnees(nombre_elements, date_depart_operation,
                                                                   date_fin_operation, i, identifiant_max, True, base)
            else:
                elements_a_inserer = generation_pour_ajout_donnees(nombre_elements, date_depart_operation,
                                                                   date_fin_operation, i, identifiant_max, False, base)
            i.interface.write(i, elements_a_inserer)
        temps, identifiant_max = insertion_sans_saturer_la_ram(base, nombre_elements, models, date_depart_operation,
                                                               date_fin_operation, 0, False, 0)
        for current_model in range(len(models)):
            resultat_test.append(
                [base, temps[current_model], f"update de {nombre_elements} element de type {type_element}",
                 models[current_model].__name__])
    else:
        raise ValueError(
            "ce type d'opération n'est pas reconnu. choix possibles: 'lecture', 'update', 'insertion avec update' ou "
            "'ecriture'.")

    return resultat_test
