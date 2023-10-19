# databases_timeseries_analysis

Commandes pour inspecter la BDD postgres
`./manage.py dbshell --database postgres`
- <b>\dt+</b> : liste toutes les tables
- <b>\d <i>TABLE_NAME</i></b> : liste les colonnes et les tables annexes créées pour les index 


Voir la taille d'une table : \
`
SELECT pg_size_pretty(pg_total_relation_size('TABLE_NAME'));
`