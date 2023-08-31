


class BenchmarkRouter:

    models_postgres = {'TimeSerieElementNonPartitionne', 'TimeSerieElementDoubleIndexationHorodateNonPartitionne',
                     'TimeSerieElementDoubleIndexationSiteNonPartitionne', 'TimeSerieElementTripleIndexationNonPartitionne',
                     'TimeSerieElement', 'TimeSerieElementIndexationHorodate', 'TimeSerieElementDoubleIndexationSite',
                     'TimeSerieElementTripleIndexation', 'timeserieelementnonpartitionne', 'timeserieelementdoubleindexationhorodatenonpartitionne',
                     'timeserieelementdoubleindexationsitenonpartitionne', 'timeserieelementtripleindexationnonpartitionne',
                     'timeserieelement', 'timeserieelementindexationhorodate', 'timeserieelementdoubleindexationsite',
                     'timeserieelementtripleindexation'}
    models_timescale = {'TimeSerieElementTimescale', 'timeserieelementtimescale'}
    models_mongo = {'TimeSerieElementMongo', 'timeserieelementmongo'}
    models_questdb = {'TimeSerieElementQuestdb', 'timeserieelementquestdb'}



    def db_for_read(self, model, **hints):
        # print(f'MODELE DANS LE ROUTEUR POUR READ={model.__name__}')
        if str(model.__name__) in self.models_postgres:
            # print('postgres')
            return "postgres"
        elif str(model.__name__) in self.models_timescale:
            # print('timescale')
            return "timescale"
        elif str(model.__name__) in self.models_mongo:
            # print('mongo')
            return "mongo"
        elif str(model.__name__) in self.models_questdb:
            # print('questdb')
            return "questdb"
        else:
            return None
    def db_for_write(self, model, **hints):
        # print(f'MODELE DANS LE ROUTEUR POUR WRITE={model.__name__}')
        if str(model.__name__) in self.models_postgres:
            # print('postgres, je te choisis !')
            return "postgres"
        elif str(model.__name__) in self.models_timescale:
            # print('Timescale, je te choisis !')
            return "timescale"
        elif str(model.__name__) in self.models_mongo:
            # print('mongo, je te choisis !')
            return "mongo"
        elif str(model.__name__) in self.models_questdb:
            # print('questdb, je te choisis !')
            return "questdb"
        else:
            return None
    def allow_relation(self, obj1, obj2, **hints):

        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if str(model_name) in self.models_postgres and db == 'postgres':
            # print(f'{model_name} accepté pour {db}')
            return True
        if str(model_name) in self.models_timescale and db == 'timescale':
            # print(f'{model_name} accepté pour {db}')
            return True
        if str(model_name) in self.models_questdb and db == 'questdb':
            # print(f'{model_name} accepté pour {db}')
            return "questdb"
        else:
            # print(f'{model_name} refusé')
            return False