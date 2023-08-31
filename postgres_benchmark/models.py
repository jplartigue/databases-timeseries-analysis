from django.contrib.postgres.indexes import BrinIndex
from django.db import models
from postgres_copy import CopyManager
from psqlextra.models import PostgresPartitionedModel
from psqlextra.types import PostgresPartitioningMethod



#
# # Create your models here.
class TimeseriesCommon(PostgresPartitionedModel):
    identifiant_flux = models.CharField(max_length=50)
    date_reception_flux = models.DateTimeField()
    dernier_flux = models.BooleanField()
    valeur = models.FloatField()

    id_site = models.BigIntegerField()
    horodate = models.DateTimeField()

    objects = CopyManager()

    class Meta:
        abstract = True


class TimeSerieElement(TimeseriesCommon):
    class PartitioningMeta:
        method = PostgresPartitioningMethod.RANGE
        key = ["horodate"]


class TimeSerieElementIndexationHorodate(TimeseriesCommon):


    class PartitioningMeta:
        method = PostgresPartitioningMethod.RANGE
        key = ["horodate"]


    class Meta:
        ordering = ['horodate',]
        indexes = [
            BrinIndex(
                fields=('horodate',),
                pages_per_range=12
            )
        ]

class TimeSerieElementDoubleIndexationSite(TimeseriesCommon):
    class Meta:
        ordering = ['horodate',]
        indexes = [
            BrinIndex(
                fields=('id_site',),
                pages_per_range=12
            )
        ]
    class PartitioningMeta:
        method = PostgresPartitioningMethod.RANGE
        key = ["horodate"]



class TimeSerieElementTripleIndexation(TimeseriesCommon):
    class Meta:
        ordering = ['horodate',]
        indexes = [
            BrinIndex(
                fields=('horodate', 'id_site'),
                pages_per_range=12
            )
        ]
    class PartitioningMeta:
        method = PostgresPartitioningMethod.RANGE
        key = ["horodate"]





class TimeseriesCommonNonPartitionne(models.Model):
    identifiant_flux = models.CharField(max_length=50)
    date_reception_flux = models.DateTimeField()
    dernier_flux = models.BooleanField()
    valeur = models.FloatField()

    id_site = models.BigIntegerField()
    horodate = models.DateTimeField()

    objects = CopyManager()


    class Meta:
        abstract = True

class TimeSerieElementNonPartitionne(TimeseriesCommonNonPartitionne):
    pass

class TimeSerieElementDoubleIndexationHorodateNonPartitionne(TimeseriesCommonNonPartitionne):

    class Meta:
        ordering = ['horodate',]
        indexes = [
            BrinIndex(
                fields=('horodate',),
                pages_per_range=24
            )
        ]




class TimeSerieElementDoubleIndexationSiteNonPartitionne(TimeseriesCommonNonPartitionne):
    class Meta:
        ordering = ['horodate',]
        indexes = [
            BrinIndex(
                fields=('id_site',),
                pages_per_range=24
            )
        ]


class TimeSerieElementTripleIndexationNonPartitionne(TimeseriesCommonNonPartitionne):
    class Meta:
        ordering = ['horodate',]
        indexes = [
            BrinIndex(
                fields=('horodate', 'id_site'),
                pages_per_range=24
            )
        ]


