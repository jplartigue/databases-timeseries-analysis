


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



    def db_for_read(self, model, **hints):
        print(f'MODELE DANS LE ROUTEUR POUR READ={model.__name__}')
        if str(model.__name__) in self.models_postgres:
            return "postgres"
        elif str(model.__name__) in self.models_timescale:
            return "timescale"
        elif str(model.__name__) in self.models_mongo:
            return "mongo"
        else:
            return None
    def db_for_write(self, model, **hints):
        # print(f'MODELE DANS LE ROUTEUR POUR WRITE={model.__name__}')
        if str(model.__name__) in self.models_postgres:
            return "postgres"
        elif str(model.__name__) in self.models_timescale:
            # print('Timescale, je te choisis !')
            return "timescale"
        elif str(model.__name__) in self.models_mongo:
            return "mongo"
        else:
            return None
    def allow_relation(self, obj1, obj2, **hints):

        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        print(f'base={db}')
        if str(model_name) in self.models_postgres and db == 'postgres':
            print(f'{model_name} accepté')
            return True
        if str(model_name) in self.models_timescale and db == 'timescale':
            print(f'{model_name} accepté')
            return True
        else:
            print(f'{model_name} refusé')
            return False