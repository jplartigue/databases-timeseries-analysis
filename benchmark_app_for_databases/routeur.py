from django.apps import apps


class BenchmarkRouter:

    models_postgres = list(apps.get_app_config('postgres_benchmark').get_models())
    models_timescale = {'TimeSerieElementTimescale', 'timeserieelementtimescale', 'TimeSerieElementTimescaleDoubleIndexationSite', 'timeserieelementtimescaledoubleindexationsite'}
    models_mongo = {'TimeSerieElementMongo', 'timeserieelementmongo'}
    models_questdb = {'TimeSerieElementQuestdb', 'timeserieelementquestdb'}


    def db_for_read(self, model, **hints):
        # print(f'MODELE DANS LE ROUTEUR POUR READ={model.__name__}')
        if model in self.models_postgres:
            return "postgres"
        elif str(model.__name__) in self.models_timescale:
            return "timescale"
        else:
            return None

    def db_for_write(self, model, **hints):
        if model in self.models_postgres:
            return "postgres"
        elif str(model.__name__) in self.models_timescale:
            return "timescale"
        else:
            return None
    def allow_relation(self, obj1, obj2, **hints):

        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == "postgres_benchmark" and db == 'postgres':
            return True
        if str(model_name) in self.models_timescale and db == 'timescale':
            return True
        else:
            return False