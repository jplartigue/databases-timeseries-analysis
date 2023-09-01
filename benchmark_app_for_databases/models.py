from django.contrib.postgres.indexes import BrinIndex
from django.db import models
from timescale.db.models.fields import TimescaleDateTimeField
from timescale.db.models.managers import TimescaleManager
from djongo import models as mod
from postgres_copy import CopyManager
from psqlextra.types import PostgresPartitioningMethod
from psqlextra.models import PostgresPartitionedModel
# from influxable.measurement import Measurement, attributes, serializers






class TimescaleModel(models.Model):
    """
    A helper class for using Timescale within Django, has the TimescaleManager and
    TimescaleDateTimeField already present. This is an abstract class it should
    be inheritted by another class for use.
    """
    horodate = TimescaleDateTimeField(interval="1 month", db_index=True, primary_key=True)

    objects = TimescaleManager()
    object_copy = CopyManager()
    class Meta:
        abstract = True

class TimeSerieElementTimescale(TimescaleModel):
    id_site = models.BigIntegerField(db_index=True)
    identifiant_flux = models.CharField(max_length=50)
    date_reception_flux = models.DateTimeField()
    dernier_flux = models.BooleanField()
    valeur = models.FloatField()

    class Meta:
        app_label = 'benchmark_app_for_databases'
        ordering = ("horodate",)

# class TimeSerieElementTimescaleDoubleIndexationSite(TimescaleModel):
#     id_site = models.BigIntegerField(db_index=True)
#     identifiant_flux = models.CharField(max_length=50)
#     date_reception_flux = models.DateTimeField()
#     dernier_flux = models.BooleanField()
#     valeur = models.FloatField()
#
#     class Meta:
#         app_label = 'benchmark_app_for_databases'
#         ordering = ("horodate",)


class TimeSerieElementMongo(mod.Model):
    id_site = mod.BigIntegerField()
    identifiant_flux = mod.CharField(max_length=50)
    horodate = mod.DateTimeField()
    date_reception_flux = mod.DateTimeField()
    dernier_flux = mod.BooleanField()
    valeur = mod.FloatField()
    objects = mod.DjongoManager()

    class Meta:
        _use_db = 'mongo'
        ordering = ("horodate",)
        app_label = 'benchmark_app_for_databases'

class TimeSerieElementMongoIndexHorodate(models.Model):
    id_site = mod.BigIntegerField()
    identifiant_flux = mod.CharField(max_length=50)
    horodate = mod.DateTimeField()
    date_reception_flux = mod.DateTimeField()
    dernier_flux = mod.BooleanField()
    valeur = mod.FloatField()
    objects = mod.DjongoManager()

    class Meta:
        _use_db = 'mongo'
        ordering = ("horodate",)
        app_label = 'benchmark_app_for_databases'

class TimeSerieElementMongoIndexSite(models.Model):
    id_site = mod.BigIntegerField()
    identifiant_flux = mod.CharField(max_length=50)
    horodate = mod.DateTimeField()
    date_reception_flux = mod.DateTimeField()
    dernier_flux = mod.BooleanField()
    valeur = mod.FloatField()
    objects = mod.DjongoManager()

    class Meta:
        _use_db = 'mongo'
        ordering = ("horodate",)
        app_label = 'benchmark_app_for_databases'

class TimeSerieElementMongoIndexHorodateSite(models.Model):
    id_site = mod.BigIntegerField()
    identifiant_flux = mod.CharField(max_length=50)
    horodate = mod.DateTimeField()
    date_reception_flux = mod.DateTimeField()
    dernier_flux = mod.BooleanField()
    valeur = mod.FloatField()
    objects = mod.DjongoManager()

    class Meta:
        _use_db = 'mongo'
        ordering = ("horodate",)
        app_label = 'benchmark_app_for_databases'

class TimeSerieElementQuestdb(models.Model):
    name = "timeserieelementquestdb"

class TimeserieElementQuestdbPartition(models.Model):
    name = "timeserieelementpartitionnementquestdb"

class TimeSerieElementQuestdbIndexSite(models.Model):
    name = "timeserieelementquestdbindexsite"

class TimeSerieElementQuestdbIndexSitePartition(models.Model):
    name = "timeserieelementquestdbindexsitepartition"

# class TimeserieElementInflux(Measurement):
#     id_site = attributes.IntegerFieldAttribute()
#     identifiant_flux = attributes.StringFieldAttribute()
#     horodate = attributes.DateTimeFieldAttribute()
#     date_reception_flux = attributes.DateTimeFieldAttribute()
#     dernier_flux = attributes.BooleanFieldAttribute()
#     valeur = attributes.FloatFieldAttribute()
#
#     parser_class = serializers.MeasurementPointSerializer