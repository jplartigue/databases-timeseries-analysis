import random
from django.apps import apps

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db import connections
from psycopg2.extras import execute_values

from data_generator import DataFaker
from utils.localtime import localised_year_interval


class Command(BaseCommand):
    help = 'Load historical timeseries in postgres database'

    def add_arguments(self, parser):
        parser.add_argument('--number_of_sites', type=int, help='The number of sites to create')
        parser.add_argument('--table', type=str, help='The name of the table to use (default is all)')

    def handle(self, *args, **kwargs):
        number_of_sites = kwargs['number_of_sites']
        table_name = kwargs['table'] or None
        # Get the model class based on the table name
        app_models = list(apps.get_app_config('postgres_benchmark').get_models())
        try:
            if table_name is not None:
                app_models = [apps.get_model(f'postgres_benchmark.{table_name}')]
        except LookupError:
            self.stderr.write(self.style.ERROR(f"Table '{table_name}' does not exist. Using default 'Site' table."))

        data_faker = DataFaker(*localised_year_interval([2021, 2023]))

        for i in range(number_of_sites):
            df = data_faker.generate_fake_dataframe(size=random.randint(12*8760, 12*3*8760))
            columns_str = f"({', '.join(df.columns)})"

            for model in app_models:
                with connections['postgres'].cursor() as cursor:
                    # Define the INSERT statement
                    insert_query = f"INSERT INTO {'postgres_benchmark_' + model.__name__} {columns_str} VALUES %s"

                    # Insert the data
                    execute_values(cursor, insert_query, df.values)

                self.stdout.write(self.style.SUCCESS(f'Site n°{i} model {model} successfully created'))
        self.stdout.write(self.style.SUCCESS(f'Creation ended'))


