


class BenchmarkRouter:

    models_postgres = {'timeserieelement', 'timeserieelementdoubleindexationhorodate', 'timeserieelementdoubleindexationsite', 'timeserieelementtripleindexation'}
    models_timescale = {'timeserieelementtimescale'}
    models_mongo = {'timeserieelementmongo'}



    def db_for_read(self, model, **hints):

        if model.__name__ in self.models_postgres:
            return "postgres"
        elif model.__name__ in self.models_timescale:
            return "timescale"
        elif model.__name__ in self.models_mongo:
            return "mongo"
        else:
            return None
    def db_for_write(self, model, **hints):
        print(model.__name__)
        if model.__name__ in self.models_postgres:
            return "postgres"
        elif model.__name__ in self.models_timescale:
            return "timescale"
        elif model.__name__ in self.models_mongo:
            return "mongo"
        else:
            return None
    def allow_relation(self, obj1, obj2, **hints):

        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # if "benchmark_app_for_databases" == app_label:
        #     print(app_label)
        #     print(model_name)
        #     print(db)
        if db == "mongo" or db == 'default':
            return False
        else:
            if model_name in self.models_postgres and db == 'postgres':
                # print(f'db={db}\napplabel={app_label}\nmodel_name={model_name}')
                return True
            if model_name in self.models_timescale and db == 'timescale':
                return True
        return False