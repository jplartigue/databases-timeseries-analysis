from django.db import models
from timescale.db.models.fields import TimescaleDateTimeField
from timescale.db.models.managers import TimescaleManager
from djongo import models as mod
from postgres_copy import CopyManager
from benchmark_app_for_databases.interfaces_bases_de_donnees import InterfaceTimescale, InterfaceMongo, \
    InterfaceQuestdb, Interfaceinfluxdb


class TimescaleModel(models.Model):
    """
    A helper class for using Timescale within Django, has the TimescaleManager and
    TimescaleDateTimeField already present. This is an abstract class it should
    be inheritted by another class for use.
    """
    horodate = TimescaleDateTimeField(interval="1 month", db_index=True, primary_key=True)

    objects = TimescaleManager()
    object_copy = CopyManager()
    interface = InterfaceTimescale
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
    interface = InterfaceMongo



class TimeSerieElementMongoIndexHorodate(models.Model):
    interface = InterfaceMongo

class TimeSerieElementMongoIndexSite(models.Model):
    interface = InterfaceMongo


class TimeSerieElementMongoIndexHorodateSite(models.Model):
    interface = InterfaceMongo


class TimeSerieElementQuestdb(models.Model):
    name = "timeserieelementquestdb"
    interface = InterfaceQuestdb

class TimeserieElementQuestdbPartition(models.Model):
    name = "timeserieelementpartitionnementquestdb"
    interface = InterfaceQuestdb

class TimeSerieElementQuestdbIndexSite(models.Model):
    name = "timeserieelementquestdbindexsite"
    interface = InterfaceQuestdb

class TimeSerieElementQuestdbIndexSitePartition(models.Model):
    name = "timeserieelementquestdbindexsitepartition"
    interface = InterfaceQuestdb

class TimeserieElementInflux(models.Model):
    name = 'timeserieelementinflux'
    interface = Interfaceinfluxdb