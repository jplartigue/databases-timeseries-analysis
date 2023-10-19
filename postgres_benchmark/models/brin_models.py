from django.contrib.postgres.indexes import BrinIndex

from postgres_benchmark.models.basic_models import TimeseriesAbstract
from django.db import models


class TimeseriesBrin128(TimeseriesAbstract):
    class Meta:
        indexes = [
            models.Index(fields=['id_site', 'horodate']),
            BrinIndex(fields=['horodate'], autosummarize=True), # page_per_range = 128 par défaut
        ]


class TimeseriesBrin64(TimeseriesAbstract):
    class Meta:
        indexes = [
            models.Index(fields=['id_site', 'horodate']),
            BrinIndex(fields=['horodate'], autosummarize=True, pages_per_range=64),
        ]


class TimeseriesBrin32(TimeseriesAbstract):
    class Meta:
        indexes = [
            models.Index(fields=['id_site', 'horodate']),
            BrinIndex(fields=['horodate'], autosummarize=True, pages_per_range=32),
        ]

