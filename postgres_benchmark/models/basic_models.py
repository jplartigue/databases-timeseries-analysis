from django.db import models

# class TimeseriesBasicAbstract(models.Model):
#     identifiant_flux = models.CharField(max_length=50)
#     date_reception_flux = models.DateTimeField()
#     dernier_flux = models.BooleanField()
#     valeur = models.FloatField()
#
#     id_site = models.BigIntegerField()
#     horodate = models.DateTimeField()
#
#     objects = CopyManager()
#     interface = InterfacePostgres
#
#     class Meta:
#         abstract = True
class TimeseriesAbstract(models.Model):
    id_site = models.BigIntegerField()
    horodate = models.DateTimeField()
    valeur = models.FloatField()

    class Meta:
        ordering = ['horodate', ]
        abstract = True


class TimeseriesBasic(TimeseriesAbstract):
    pass


class TimeseriesBasicHorodateIndex(TimeseriesAbstract):

    class Meta(TimeseriesAbstract.Meta):
        indexes = [models.Index(fields=['horodate']),]


class TimeseriesBasicSiteHorodateIndexes(TimeseriesAbstract):

    class Meta(TimeseriesAbstract.Meta):
        indexes = [models.Index(fields=['id_site', 'horodate']), ]

