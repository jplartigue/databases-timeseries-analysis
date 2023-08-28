from psqlextra.partitioning import PostgresPartitioningManager, PostgresPartitioningConfig, \
    PostgresCurrentTimePartitioningStrategy, PostgresTimePartitionSize, PostgresTimePartitioningStrategy
import datetime as dt
from postgres_benchmark.models import *
from utils.localtime import localise_date

manager = PostgresPartitioningManager([
    # 3 partitions ahead, each partition is one year
    # partitions will be named `[table_name]_[year]`.
    PostgresPartitioningConfig(
        model=TimeSerieElement,
        strategy=PostgresTimePartitioningStrategy(
            start_datetime=localise_date(dt.datetime(2024, 1, 1)),
            size=PostgresTimePartitionSize(months=12),
            count=3,
            # max_age=relativedelta(months=36),
        )),
     PostgresPartitioningConfig(
        model=TimeSerieElementIndexationHorodate,
        strategy=PostgresTimePartitioningStrategy(
            start_datetime=localise_date(dt.datetime(2024, 1, 1)),
            size=PostgresTimePartitionSize(months=12),
            count=3,
                # max_age=relativedelta(months=36),
        )),

])
