from django.contrib.postgres.indexes import BrinIndex
from django.db import models
from timescale.db.models.fields import TimescaleDateTimeField
from timescale.db.models.managers import TimescaleManager
from djongo import models as mod
from postgres_copy import CopyManager



class TimeSerieElement(models.Model):
    id_site = models.BigIntegerField()
    identifiant_flux = models.CharField(max_length=50)
    horodate = models.DateTimeField()
    date_reception_flux = models.DateTimeField()
    dernier_flux = models.BooleanField()
    valeur = models.FloatField()
    objects = CopyManager()




class TimeSerieElementDoubleIndexationHorodate(models.Model):
    id_site = models.BigIntegerField()
    identifiant_flux = models.CharField(max_length=50)
    horodate = models.DateTimeField()
    date_reception_flux = models.DateTimeField()
    dernier_flux = models.BooleanField()
    valeur = models.FloatField()
    objects = CopyManager()

    class Meta:
        indexes = [
            BrinIndex(
                fields=('horodate',),
                pages_per_range=32
            )
        ]


class TimeSerieElementDoubleIndexationSite(models.Model):
    id_site = models.BigIntegerField()
    identifiant_flux = models.CharField(max_length=50)
    horodate = models.DateTimeField()
    date_reception_flux = models.DateTimeField()
    dernier_flux = models.BooleanField()
    valeur = models.FloatField()
    objects = CopyManager()

    class Meta:
        indexes = [
            BrinIndex(
                fields=('id_site',),
                pages_per_range=32
            )
        ]

class TimeSerieElementTripleIndexation(models.Model):
    id_site = models.BigIntegerField()
    identifiant_flux = models.CharField(max_length=50)
    horodate = models.DateTimeField()
    date_reception_flux = models.DateTimeField()
    dernier_flux = models.BooleanField()
    valeur = models.FloatField()
    objects = CopyManager()

    class Meta:
        indexes = [
            BrinIndex(
                fields=('horodate', 'id_site'),
                pages_per_range=32
            )
        ]

# class Meta:
#     db_index = ('id', 'dernier_flux')




class TimescaleModel(models.Model):
    """
    A helper class for using Timescale within Django, has the TimescaleManager and
    TimescaleDateTimeField already present. This is an abstract class it should
    be inheritted by another class for use.
    """
    horodate = TimescaleDateTimeField(interval="5 minutes")

    # objects = TimescaleManager()
    objects = CopyManager()

    class Meta:
        abstract = True
class TimeSerieElementTimescale(TimescaleModel):
    id_site = models.BigIntegerField()
    identifiant_flux = models.CharField(max_length=50)
    date_reception_flux = models.DateTimeField()
    dernier_flux = models.BooleanField()
    valeur = models.FloatField()


# class TimeSerieElementDoubleIndexationSiteTimescale(TimescaleModel):
#     id_site = models.IntegerField(db_index=True)
#     identifiant_flux = models.CharField(max_length=50)
#     date_reception_flux = models.DateTimeField()
#     dernier_flux = models.IntegerField()
#     valeur = models.FloatField()








class TimeSerieElementMongo(mod.Model):
    id_site = models.BigIntegerField()
    identifiant_flux = models.CharField(max_length=50)
    horodate = models.DateTimeField()
    date_reception_flux = models.DateTimeField()
    dernier_flux = models.BooleanField()
    valeur = models.FloatField()
    objects = mod.DjongoManager()




# class TimeSerieElementDoubleIndexationHorodateMongo(mod.Model):
#     id_site = models.IntegerField()
#     identifiant_flux = models.CharField(max_length=50)
#     horodate = models.DateTimeField(db_index=True)
#     date_reception_flux = models.DateTimeField()
#     dernier_flux = models.IntegerField()
#     valeur = models.FloatField()
#
#     class Meta:
#         indexes = [
#             TextIndex(fields=['horodate'])
#         ]
#
#
# class TimeSerieElementDoubleIndexationSiteMongo(mod.Model):
#     id_site = models.IntegerField(db_index=True)
#     identifiant_flux = models.CharField(max_length=50)
#     horodate = models.DateTimeField()
#     date_reception_flux = models.DateTimeField()
#     dernier_flux = models.IntegerField()
#     valeur = models.FloatField()
#
#     class Meta:
#         indexes = [
#             TextIndex(fields=['id_site'])
#         ]
#
# class TimeSerieElementTripleIndexationMongo(mod.Model):
#     id_site = models.IntegerField(db_index=True)
#     identifiant_flux = models.CharField(max_length=50)
#     horodate = models.DateTimeField(db_index=True)
#     date_reception_flux = models.DateTimeField()
#     dernier_flux = models.IntegerField()
#     valeur = models.FloatField()
#
#     class Meta:
#         indexes = [
#             TextIndex(fields=['horodate', 'id_site'])
#         ]