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
l'application des migration se fait par contre normalement en faisant appel à la fonction "migrate" de django.\
les migrations sont appliquées automatiquement 10 secondes après le lancement du conteneur "outil_test".

INTERFACES:

les interfaces comportent toutes les 6 méthodes suivantes:
- read_at_timestamp
- read_between_dates
- update_at_timestamp
- update_between_dates
- ajout_element_en_fin_de_courbe_de_charge
- write

READ_AT_TIMESTAMP:

cette méthode a été pensée pour la lecture d'éléments/points uniques de courbes de charge et sera donc appelée si l'opération porte sur la lecture de points.\
la signature de cette méthode est la suivante:
````
read_at_timestamp(self, timestamp: dt.datetime, model, identifiants_sites: [str], *args, **kwargs)
````
le paramètre "timestamp" permet de déterminer la date à laquelle la lecture doit être menée.\
le paramètre model sert pour l'utilisation de l'ORM de django avec postgres et timescale et la configuration à utiliser pour les autres bases de données.\
le paramètre identifiants_sites est la liste des identifiants des sites sur lesquels la lecture s'effectuera. sa taille est égale au "nombre_elements" passé en paramètre de la fonction "benchmark". si le nombre d'éléments est de 5 par exemple, alors cette liste contiendra les identifiants 0, 1, 2, 3, 4.\
donc si cette fonction est appelée pour lire plusieurs points, elle va chercher à lire le point sur chaque courbe qui correspond au timestamp fourni. la limite de cette méthode est donc que l'on ne peux pas demander à lire plus de points qu'il n'y a de courbes de charge en base. elle a été conçue pour lire très peu de points comparé à la taille de la base de données et donc obtenir des informations sur les accès sur des éléments individuels.

READ_BETWEEN_DATES:

cette méthode a été créée pour lire des courbes de charge ou des portions entières de ces dernières et est appelée si l'opération de lecture porte sur un élément de type "courbe".\
sa signature est la suivante:
````
read_between_dates(self, date_debut: dt.datetime, date_fin: dt.datetime, model, identifiants_sites: [str], *args, **kwargs)
````
les paramètres "date_debut" et "date_fin" sont les bornes temporelles de lectures des données.\
"model" sert à la même chose que pour la fonction précédente.\
idem pour le paramètre "identifiants_sites".\
cette méthode va donc chercher à récupérer les points qui ont leurs "horodates" entre les dates fournies pour les courbes de charge dont l'identifiant du site est contenu dans la liste.

UPDATE_AT_TIMESTAMP:

cette méthode a été créée pour mettre à jour un nombre limité de points. elle est donc appelée si l'opération update porte sur le type d'élément "element".\
sa signature est identique à celle de la fonction "read_at_timestamp":
````
update_at_timestamp(self, timestamp: dt.datetime, model, identifiants_sites: [str], *args, **kwargs)
````
son pricipe de fonctionnement et identique à celui de "read_at_timestamp" à la différence que cette méthode ne va pas lire mais mettre à jour le champ "valeur" des points qui correspondent aux critères en y injectant la valeur "42".

UPDATE_BETWEEN_DATES:

cette fonction est très proche de "read_between_dates" dans sa forme et son fonctionnement et est appelée si l'opération de mise à jour porte sur le type d'élément "courbe".\
sa signature est la suivante:
````
update_between_dates(self, date_debut: dt.datetime, date_fin: dt.datetime, model, identifiants_sites: [str], *args, **kwargs)
````
les paramètres sont les mêmes que pour "read_between_dates" et le fonctionnement aussi. encore une fois à la différence que cette fonction ne va pas lire les valeurs mais mettre à jour leurs champs "valeur" avec la valeur "42".

AJOUT_ELEMENT_EN_FIN_DE_COURBE_DE_CHARGE:

cette fonction est prévue pour être utilisée pour l'écriture d'un nombre restreint d'éléments et sera appelée si le test porte sur une écriture de type "element".\
sa signature est la suivante:
````
ajout_element_en_fin_de_courbe_de_charge(self, model, nombre_elements: int, nombre_courbes: int, *args, **kwargs)
````
le paramètre "model" sert une fois de plus à savoir à quelle configuration on a affaire et pour le cas de postgres et timescale à utiliser l'ORM de django.\
le paramètre "nombre_elements" correspond au nombre d'éléments renseigné lors de l'appel à la fonction "benchmark" et sert à définir le nombre d'éléments à ajouter en fin de courbe.\
le paramètre "nombre_courbes" correspond au nombre de courbes qui seront concernées. de base ce paramètre est égal à 1.\
avec ces quelques paramètres, la méthode va chercher à ajouter le nombre d'éléments renseigné à chaque courbe dans la limite du nombre de courbes renseigné. par exemple, avec un nombre d'éléments égal à 3 et un nombre de courbes égal à 8, la méthode va ajouter 3 nouveaux éléments à la fin des 8 premières courbes de charge (les courbes avec 0, 1, 2, 3, 4, 5, 6 et 7 comme "id_site").\
si aucune date n'est utilisée c'est à cause de l'aléatoire mensionné dans la partie utilisateur de la documentation. en effet "ajout_element_en_fin_de_courbe_de_charge" va récupérer la date du dernier élément des courbes de charge concernées pour déterminer les dates auquelles les éléments doivent être ajoutés pour chaque courbe de charge. les éléments sont créés en faisant appel à la fonction "generation_pour_ajout_donnees" et insérés via la dernière méthode implémentée pour les interfaces "write".

WRITE:

cette méthode est utilisée pour toutes les opérations d'écriture. elle est appelée par la méthode décrite précédement si le test consiste en une opération d'écriture sur un ou plusieurs éléments/points. elle est aussi appelée directement lors des opérations de population des bases de données et d'écriture de courbes de charge.\
sa signature est la suivante:
````
write(self, model, liste_a_ecrire: [], *args, **kwargs)
````
le paramètre "model" est identique aux autres vus jusqu'ici.\
le paramètre "liste_a_ecrire" contient les éléments à écrire. le type n'est pas unique mais dépend de la base de données concernée:
- pour postgres et timescale ce paramètre contient une liste de nom de fichiers au format csv (les explications sont données au chapitre suivant)
- pour mongodb ce paramètre contient une liste de dictionnaires (chacun d'entre eux représentant un point de courbe de charge)
- pour influxdb et questdb ce sera une liste des pandas_dataframes (chaque pandas_dataframe correspond à une courbe de charge)

COMMUNICATION AVEC LES DIFFÉRENTES BASES DE DONNÉES:

POSTGRES ET TIMESCALE:

toutes les bases de données ne sont pas accessibles via l'ORM de django, aussi certaines informations doivent être données si d'avanture vous souhaitez modifier les comportements des interfaces.\
pour postgres et timescale, le programme passe par l'ORM django + une librairie qui s'appelle django-postgres-copy, qui permet d'insérer des courbes de charge bien plus vite qu'avec la fonction "bulk_create" de django en écrivant les courbes de cvharge dans des fichiers au format csv et en injectant ces fichiers dans les bases de données via la fonction "from_csv". ces fichiers temporaires sont effacés par la méthode write des bases de données concernées en faisant appel à la bibliothèque "os".

MONGODB:

pour mogodb, j'utilise pymongo. il était possible de passer par l'ORM django en utilisant la bibliothèque djongo, mais cette dernière semble avoir été abandonnée et ne fonctionne plus (en plus de cela, il était impossible de faire de l'indexation avec djongo à moind de payer 15€ par mois pour avoir accès à djongoCS... alors qu'il est possible de faire de l'indexation avec pymongo gratuitement).\
pour communiquer avec mogodb en utilisant pymongo il faut définir un client, la base, et la collection que l'on va utiliser comme ceci:
````
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
````
pour lire dans la base de données il suffit d'itérer (manuellement ou via la fonction list()) sur le résultat de la méthode find() de la collection.\
par exemple:
````
liste = list(collection.find({"id_site": {'$in': identifiants_sites}, "horodate": timestamp.astimezone(ZoneInfo("UTC"))}))
````
avec cette ligne on récupère les points qui ont une horodate égale à la variable "timestamp" et dont l'"id_site" est compris dans la liste "identifiants_sites".\
l'équivalent sql serait la requête suivante:\
```SELECT * FROM nom_collection WHERE horodate=timestamp AND id_site IN liste;```

pour insérer des données dans la base et créer un index il est possible de se baser sur cet exemple:
````
collection.create_index('horodate', unique=False)
collection.insert_many(liste_a_ecrire)
````
il faut avoir défini collection. la première ligne créée un index sur la colonne "horodate" en spécifiant que la valeur de ce champ n'est pas unique. la deuxième ligne, c'est la version pymongo du bulk_create, il faut lui donner une liste de dictionnaires représentant les points.

enfin pour les opérations d'update:
````
collection.update({'id_site': {'$in': identifiants_sites}, 'horodate': {'$gte': date_debut, '$lte': date_fin}}, {'$set': {'valeur': 42}}, upsert=False)
````
les champs précédés par un $ sont des fonctions de la base de données mongo.\
la traduction de cette ligne en sql donnerait cette requête:\
``UPDATE table_associée_au_model SET valeur=42 WHERE horodate >= date_debut AND horodate <= date_fin AND id_site IN liste;``

QUESTDB:

pour commmuniquer avec questdb, j'utilise deux techniques. une pour la création des tables et les requêtes et une autre pour l'insertion de données.

pour insérer les données je procède de cette manière (attention c'est un exemple simplifié):
````
        with Sender('questdb', 9009) as sender:
            ultra_dataframe = liste_a_ecrire[0]
            for i in liste_a_ecrire[1:]:
                ultra_dataframe = pd.concat([ultra_dataframe, i], axis=0)
            debut = time.time()
            sender.dataframe(
                    ultra_dataframe,
                    table_name=model().name,  # Table name to insert into.
                    symbols=['id_site'],
                    at='date_reception_flux')
            fin = time.time()
````
j'utilise Sender de "questdb.ingres" qui fait partie de la bibliothèque "questdb" en lui définissant le hostname et le port de la base de données.\
ensuite je crée une grande pandas_dataframe qui contient toutes les données des pandas_dataframe reçues via le paramètre "liste_a_ecrire" et tout insérer en une fois.\
finalement j'utilise la méthode "dataframe()" qui permet d'injecter des pandas_dataframe directement dans questdb en spécifiant le nom de la table à utiliser, la colonne qui sert de symbol (j'aborderai cela avec la création des tables) et la colonne qui sert de timestamp.\
!attention! la colonne qui sert de timestamp est en quelque sorte consommée et sa valeur en base est égale à "None" quand on fait un requête en lecture. c'est pour cela que j'utilise la colone "date_reception_flux" (qui est un clone de la colonne "horodate", elle contient exactement les mêmes données) pour pouvoir extraire les données de la colonne "horodate" avec "ajout_element_en_fin_de_courbe_de_charge".

pour les autres requêtes j'utilise "psycopg2" comme suit:
````
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

````
il faut créer une connection en passant les paramètres spécifiés par la variable "conn_str". avec cette connexion on crée un curseur et on fait appel à la méthode "execute()" pour exécuter des requêtes en pur sql.\
je profite de ce bout de code pour parler du partitioning et de la création d'index.

le partitioning par périodes de temps est le seul permis pour l'instant avec questdb. il faut donc lui renseigner une colonne qui contient un élément de type TIMESTAMP qui est un type spécifique à questdb (c'est un epoch time en ns) et on peut spécifier le partitionnement par YEAR, MONTH, WEEK, DAY, et HOUR. la fonction "timestamp()" appelée avant le partition by sert à spécifier la colonne qui sert au partitionning.

avec questdb, l'indexation n'est supportée que pour les données de type SYMBOL qui sont définis dans la documentation de quesdb comme étant des strings ayant un nombre fini de combinaisons possibles (des sortes de labels mais dans les faits il n'y a pas de vérification en dehors du fait que ce sont des strings et j'utilise la colonne id_site en tant que symbol pour m'en servir d'index).

INFLUXDB:

pour communiquer avec influxdb j'utilise la bibliothèque "influxdb-client". il existait une autre solution nommée influxable mais cette dernière est incompatible avec la version de python que j'utilise car depuis quelques versions, les imports comportants des "-" sont interdits. or influxable en utilise plusieurs ce qui résulte en une erreur quand on essaye de l'importer.\
avec cette bibliothèque il faut définir un client puis l'api que l'on souhaite utiliser selon que l'on souhaite faire une requête, insérer des éléments ou effacer des éléments.\
l'exemple suivant montre une instanciation du client et des trois APIs différentes:
````
client = influxdb_client.InfluxDBClient(
            url="http://influxdb:8086",
            token="token",
            org="holmium",
            username="test",
            password="password"
        )
write_api = client.write_api(write_options=SYNCHRONOUS)
query_api = client.query_api()
delete_api = client.delete_api()
````

pour insérer des données dans la base de données il faut se baser sur l'exemple suivant:
````
write_api.write(bucket="test", org="holmium", record=ultra_dataframe, data_frame_measurement_name='test', data_frame_tag_columns=["id_site", "horodate", "identifiant_flux", "dernier_flux", "valeur"], data_frame_timestamp_column="horodate")
````
dans cet exemple j'utilise la méthode "write()" de la "write_api" pour envoyer mes données dans le bucket "test" (car influxdb ne crée pas des bases de données mais des buckets même si côté utilisateur cette différence est imperceptible), je spécifie l'organisation (c'est le type d'authentification utilisée par influxdb), ensuite le record qui n'est autre que les données que je souhaite mettre en base (à noter que j'insère directement les pandas_dataframe mais selon la documentation il est possible d'insérer des listes de dictionnaires).
l'argument "data_frame_measurement_name" est spécifique au fait d'utiliser des pandas_dataframe et qui correspond au nom de la table.\
"data_frame_tag_columns" permet de spécifier les colonnes qui serviront de tags (selon la documentation tag est le nom donné aux champs indexés et en théorie rien ne les distingue des champs normaux en dehors de ça. en pratique si vous requêtez un champ qui n'est pas un tag sa valeur ne sera pas renvoyée voire la colonne n'apparaît même pas.).\
l'argument "data_frame_timestamp_column" permet de spécifier quelle colonne servira à l'indexation temporelle.

maintenant que la base contient des données, nous allons voir comment les requêter.\
pour ce faire nous allons étudier l'exemple suivant:
````
query = f'from(bucket:"test") |> range(start: {localise_datetime(date_debut).isoformat()}, stop: {localise_datetime(date_fin).isoformat()}) |> filter(fn: (r) => r.id_site =~ /[{identifiants_sites[0]} - {identifiants_sites[-1]}]$/)'
result = query_api.query(org="holmium", query=query)
````
il faut donc utiliser la méthode "query()" en spécifiant l'organisation via le paramètre "org" et la requête via le paramètre "query".\
à noter que la requête n'est pas du tout une requête sql standard car influx utilise ses propres codes.\
les requêtes utilisées dans l'application sont relativemant simples.\
tout commence en spécifiant le bucket et la période sur laquelle porte la requête:
````
from(bucket:"test") |> range(start: {localise_datetime(date_debut).isoformat()}, stop: {localise_datetime(date_fin).isoformat()})
````
ici je spécifie que la requête porte sur le bucket "test" et sur la période qui va de la "date_debut" à la "date_fin".\
ensuite viens l'équivalent de la clause WHERE:
````
|> filter(fn: (r) => r.id_site =~ /[{identifiants_sites[0]} - {identifiants_sites[-1]}]$/)
````
les deux premiers caractères servent à "faire continuer la requête" si je puis dire en transférant le résultat précédent à la fonction suivante (ici filter()). ce qui se passe dans le filter ici est un équivalent à un\
`WHERE id_site BETWEEN identifiant_site[0] AND identifiant_site[-1]`\
enfin on peut chainer les fonctions. ici un exemple qui récupère la dernière entrée d'une courbe de charge (du moins si elle finit avant l'année 2077):
````
f'from(bucket:"test") |> range(start: {localise_datetime(dt.datetime(1980, 1, 1)).isoformat()}, stop: {localise_datetime(dt.datetime(2077, 1, 1)).isoformat()}) |> filter(fn: (r) => r.id_site == "{i}") |> last(column: "valeur")'
````
!attention! c'est contre-intuitif mais la colonne passée en argument de la fonction "last()" est la colonne utilisée pour vérifier qu'il y a bien une valeur stockée (et donc que la ligne est bien valide/non-vide selon influxdb).\
donc en écrivant `last(column: "valeur")` je spécifie que last doit regarder la dernière ligne dont le champ "valeur" n'est pas vide.

