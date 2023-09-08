# databases-timeseries-analysis

l'outil de test "automatique" de base de données du point de vue des timeseries !

les bases de données disponibles sont:\
-postgresql\
-timescale\
-mongodb\
-influxdb\
-questdb

pour utiliser l'outil il faut écrire le scénario de tests que vous voulez faire subir aux bases de données dans le script "lancement_des_tests.py" qui se trouve dans le dossier benchmark_app_for_databases/scripts.

LE FICHIER DE LANCEMENT DES TESTS:

le script présent dans ce fichier peut être découpé en 3 parties.\
1) le dictionnaire des bases de données
2) les variables de population
3) le scénario

LE DICTIONNAIRE DES BASES DE DONNÉES:

le dictionnaire des bases de données est là pour indiquer au programme les bases de données disponibles et les configurations à utiliser (s'il y en a plusieurs disponibles pour la base de données).
Dans sa forme exaustive il ressemble à cela:
````
_dict = {
        "postgres": [TimeSerieElementNonPartitionne, TimeSerieElementDoubleIndexationHorodateNonPartitionne,
                     TimeSerieElementDoubleIndexationSiteNonPartitionne, TimeSerieElementTripleIndexationNonPartitionne,
                     TimeSerieElement, TimeSerieElementIndexationHorodate, TimeSerieElementDoubleIndexationSite,
                     TimeSerieElementTripleIndexation],
        "mongo": [TimeSerieElementMongo, TimeSerieElementMongoIndexHorodate, TimeSerieElementMongoIndexSite,TimeSerieElementMongoIndexHorodateSite],
        "timescale": [TimeSerieElementTimescale],
        'questdb': [TimeSerieElementQuestdb, TimeserieElementQuestdbPartition, TimeSerieElementQuestdbIndexSite, TimeSerieElementQuestdbIndexSitePartition]
        'influxdb': [TimeserieElementInflux]

    }
````
les clés correspondent au nom du host de la base de données et les éléments des listes associées correspondent aux models associés à la base de données correspondante.\
ces models sont définis dans les fichiers "models" (celui de [postgres_benchmark](postgres_benchmark) pour les models de postgres ou celui de [benchmark_app_for_databases](benchmark_app_for_databases) pour les autres).\
tous les éléments présents dans le dictionnaire seront utilisés par le programme, si vous ne voulez pas tester certaines bases ou configurations il faudra modifier ce dictionnaire (j'ai préféré me concentrer sur l'intégration des bases de données en priorité au détriment de la configuration du fichier de scénarios).

LES VARIABLES DE POPULATION:

````
    date_depart_population = dt.datetime(2020, 1, 1)
    date_fin_population = dt.datetime(2023, 7, 31)
    population_base = 10
    ecart_aleatoire = 100
````
ces variables sont utilisées par la fonction ``insertion_sans_saturer_la_ram``. cette fonction sert à remplir la base de données avec des courbes de charge. vous n'avez pas besoin de la modifier dans un cadre utilisateur.

 pour en revenir aux variables, les variables date de départ et de fin de population vont définir les limites temporelles des courbes de charge qui seront injectées en base avant les tests.\
la variable "population_base" indique le nombre de courbes de charge qui seront injectées en base avant le début des tests.\
la variables "ecart_aleatoire" sert à introduire de l'aléatoire sur les dates de départ et de fin des courbes de charge. elle indique le nombre de jours d'écart qu'il peut y avoir entre les dates de début et de fin des courbes de charge qui ont été spécifiées et les dates de départ et de fin réelles.

si on récapitule, avec l'exemple présenté plus haut, les base de données testées seront remplies avec 10 courbes de charge
qui apparaitront aléatoirement et indépendament les unes des autres entre le 1/1/2020 et le 9/6/2020 et se finissent aléatoirement et indépendament les unes des autres entre le 20/04/2023 et le 31/07/2023.

LE SCÉNARIO:

la partie que je désigne par scénario est la partie "boucle":
````
        for database, models in _dict.items():
            insertion_sans_saturer_la_ram(database, population_base, models, date_depart_population, date_fin_population, 0, True, ecart_aleatoire)

            print('ecriture un element')
            liste_performances.extend(
                benchmark(database, models, 1, 'element', 'ecriture', dt.datetime(2021, 1, 1), dt.datetime(2023, 1, 1), population_base))

````
dans cet exemple le scénario est assez simple car il consiste à écrire un "élément" (comprenez un point d'une courbe de charge).\
l'écriture du scénario consite donc à appeler la fonction "benchmark" et à récupérer son résultat dans la liste "liste_performances".

cependant pour écrire votre scénario il nous faut faire un point sur la fonction "benchmark".

LA FONCTION BENCHMARK:

````
benchmark(base: str, models: list, nombre_elements: int, type_element: str, operation: str, date_depart_operation: dt.datetime, date_fin_operation: dt.datetime, remplissage_prealable: int, nombre_courbes: int=1)
````
la fonction "benchmark" s'utilise avec 8 paramètres obligatoires et 1 paramètre à usage spécial (dans le sens de "qui ne sert que dans un seul cas").
1) base qui permet de renseigner la base de données à tester (il faut renseigner ce champ avec la variable "database" créée par la boucle)
2) models qui renseigne la liste des models associés à la base (il faut renseigner ce champ avec la variable "models" créée par la boucle)
3) nombre_elements qui renseigne le nombre le nombre d'éléments concernés par le test. per exemple pour écrire 10 courbes de charge il faut renseigner ce paramètre à 10.
4) type_element qui renseigne le type d'élément concerné par le test. seuls choix possibles: "courbe" et "element" pour désigner respectivement les courbes de charge ou les points des courbes de charge.
5) operation qui permet de renseigner l'opération à effectuer ("ecriture", "lecture", "update" et "insertion avec update"). insertion avec update sert à insérer des données sur une période où l'on a à la fois de l'update et de l'ajout de points à une courbe de charge, dans ce cas les paramètres "type_element" et "nombre_elements" sont ignorés mais doivent être renseignés.
6) date_depart_operation définit la date à laquelle débute l'opération. par exemple, dans le cas d'une opération de lecture de courbes de charge, la requête envoyée à la base de données spécifiera que l'on veul les données qui se trouvent entre cette date et la date_fin_operation. date_debut_operation est prioritaire pour les opérations à une date. par exemple pour l'opération de lecture sur un élément le programme ira demander l'élément à la date de début et ignorera la date de fin.
7) date_fin_operation sert à désigner la date à laquelle l'opération s'achève. (pour plus de précisions voir la définition du paramètre 6)
8) remplissage_prealable qui permet de dire au programme combien de courbes de charge sont déjà présentes dans la base (il faut le renseigner avec la variable "population_base")
9) (optionnel) nombre_courbes sert à renseigner le nombre de courbes concernées par l'opération d'écriture d'élément(s).

LES OPÉRATIONS:

je vais détailler les opérations un peu plus en détail dans cette partie.

l'opération "lecture" va tenter de lire les données du nombre défini de courbes de charge (ou d'éléments) entre les dates spécifiées (à la date spécifiée par "date_debut_operation").\
l'opération "ecriture" va tenter d'écrire des données dans la base. si le type est "courbe" alors le programme va créer une courbe de charge qui commence et se termine EXACTEMENT aux dates spécifiées pour le test puis l'injecter en base. dans le cas d'un type "element", le programme va récupérer la date du dernier élément des courbes de charge qui sont déjà présentes en base (en fonction du nombre de courbes spécifiées par le paramètre "nombre_courbes") et va ajouter le nombre spécifié d'éléments à la fin de la courbe de charge.\
l'opération "update" va tenter de mettre à jour le nombre requis de courbes entre les dates spécifiées. dans le cas où le type renseigné soit "element", le programme va mettre à jour l'élément repéré par la date de début d'opération pour x courbes (x étant le nombre spécifié par le champ "nombre_elements").\
enfin l'opération "insertion avec update" va créer un morceau de courbe de charge suivant les dates spécifiées et tenter de l'écrire sur une courbe qui existe déjà (ici c'est à l'utilisateur de ne pas se planter dans les dates sinon le test sera pas celui escompté)

une dernière chose importante pour ne pas avoir de mauvaises surprises:\
les variables "taille_ram" et "limites_courbes_en_ram", qui se trouvent dans le fichier "benchmark", doivent être réglées en fonction de votre RAM.\
je recommande par expérience de ne pas dépasser 10 si vous disposez de 16 Go de RAM.

PARTIE TECHNIQUE:

en termes d'architecture l'exécution se déroule comme suit:\
le script "lancement_des_tests" va dérouler les tests définis par l'utilisateur en faisant appel à la fonction "benchmark".\
cette fonction est chargée de déterminer le type de test à mener et donc quelle méthode appeler.\
les méthodes appelées en fonction de l'opération sont définies dans le fichier "interfaces_bases_de_donnees" et sont associées aux models en définissant le champ "interface" de ce dernier et en y associant la bonne interface.\
le fichier [generation_donnes.py](generation_donnes.py) abrite, lui les fonctions de génération de données que sont "generation_donnees" et "generation_pour_ajout_donnees". le sigleton ne permetant plus d'utiliser la même fonction pour populer une base et pour ajouter de nouyvelles données qui pourraient être en dehors de la période temporelle désignée lors du remplissage de la base.\


POINT POSTGRES:

les models et migrations de postgresql sont stockés à part dans l'application/dossier [postgres_benchmark](postgres_benchmark) car pour pouvoir mettre en place le partitionning il a fallu recourir à la bibliothèque django-postgres-extra qui fait ses propres migrations via la commande "pgmakemigrations" et il faut en plus ajouter les partitions à la main dans les migrations comme suit:
````
PostgresAddRangePartition(
            model_name="TimeSerieElement",
            name="2021_jan",
            from_values="2021-01-01 00:00:00+01:00",
            to_values="2022-01-01 00:00:00+01:00",
        ),
````
il faut ajouter les partitions comme celle-ci dans la liste des opérations des migrations à la main.\
l'application des migration se fait par contre normalement en faisant appel à la fonction "migrate" de django.

