import datetime as dt

from psqlextra.partitioning import PostgresPartitioningManager, PostgresPartitioningConfig, \
    PostgresTimePartitionSize, PostgresTimePartitioningStrategy

from postgres_benchmark.models.partitionned_models import TimeseriesMonthPartition, TimeseriesYearPartition
from utils.localtime import localise_date

manager = PostgresPartitioningManager([
    PostgresPartitioningConfig(
        model=TimeseriesMonthPartition,
        strategy=PostgresTimePartitioningStrategy(
            start_datetime=localise_date(dt.datetime(2021, 1, 1)),
            size=PostgresTimePartitionSize(months=1),
            count=6*12,
            # max_age=relativedelta(months=36),
        )),
     PostgresPartitioningConfig(
        model=TimeseriesYearPartition,
        strategy=PostgresTimePartitioningStrategy(
            start_datetime=localise_date(dt.datetime(2021, 1, 1)),
            size=PostgresTimePartitionSize(months=12),
            count=6,
                # max_age=relativedelta(months=36),
        )),

])
