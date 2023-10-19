from django.contrib.postgres.indexes import BrinIndex
from psqlextra.models import PostgresPartitionedModel
from psqlextra.types import PostgresPartitioningMethod

from postgres_benchmark.models.basic_models import TimeseriesAbstract
from django.db import models


class TimeseriesMonthPartition(PostgresPartitionedModel, TimeseriesAbstract, ):
    indexes = [
        models.Index(fields=['id_site', 'horodate']),
    ]

    class PartitioningMeta:
        method = PostgresPartitioningMethod.RANGE
        key = ["horodate"]


class TimeseriesYearPartition(PostgresPartitionedModel, TimeseriesAbstract, ):
    indexes = [
        models.Index(fields=['id_site', 'horodate']),
    ]

    class PartitioningMeta:
        method = PostgresPartitioningMethod.RANGE
        key = ["horodate"]
