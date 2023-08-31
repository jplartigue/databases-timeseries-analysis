# Generated by Django 4.2.2 on 2023-08-25 07:24

import django.contrib.postgres.indexes
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('postgres_benchmark', '0003_auto_20230824_1550'),
    ]

    operations = [
        migrations.CreateModel(
            name='TimeSerieElementNonPartitionne',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifiant_flux', models.CharField(max_length=50)),
                ('date_reception_flux', models.DateTimeField()),
                ('dernier_flux', models.BooleanField()),
                ('valeur', models.FloatField()),
                ('id_site', models.BigIntegerField()),
                ('horodate', models.DateTimeField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TimeSerieElementTripleIndexationNonPartitionne',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifiant_flux', models.CharField(max_length=50)),
                ('date_reception_flux', models.DateTimeField()),
                ('dernier_flux', models.BooleanField()),
                ('valeur', models.FloatField()),
                ('id_site', models.BigIntegerField()),
                ('horodate', models.DateTimeField()),
            ],
            options={
                'ordering': ['horodate'],
                'indexes': [django.contrib.postgres.indexes.BrinIndex(fields=['horodate', 'id_site'], name='postgres_be_horodat_4b8eb7_brin', pages_per_range=24)],
            },
        ),
        migrations.CreateModel(
            name='TimeSerieElementDoubleIndexationSiteNonPartitionne',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifiant_flux', models.CharField(max_length=50)),
                ('date_reception_flux', models.DateTimeField()),
                ('dernier_flux', models.BooleanField()),
                ('valeur', models.FloatField()),
                ('id_site', models.BigIntegerField()),
                ('horodate', models.DateTimeField()),
            ],
            options={
                'ordering': ['horodate'],
                'indexes': [django.contrib.postgres.indexes.BrinIndex(fields=['id_site'], name='postgres_be_id_site_b67e1a_brin', pages_per_range=24)],
            },
        ),
        migrations.CreateModel(
            name='TimeSerieElementDoubleIndexationHorodateNonPartitionne',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifiant_flux', models.CharField(max_length=50)),
                ('date_reception_flux', models.DateTimeField()),
                ('dernier_flux', models.BooleanField()),
                ('valeur', models.FloatField()),
                ('id_site', models.BigIntegerField()),
                ('horodate', models.DateTimeField()),
            ],
            options={
                'ordering': ['horodate'],
                'indexes': [django.contrib.postgres.indexes.BrinIndex(fields=['horodate'], name='postgres_be_horodat_2c92e3_brin', pages_per_range=24)],
            },
        ),
    ]