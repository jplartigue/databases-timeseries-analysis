# Generated by Django 4.2.2 on 2023-09-06 07:13

from django.db import migrations, models
import timescale.db.models.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TimeserieElementInflux',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='TimeSerieElementMongo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_site', models.BigIntegerField()),
                ('identifiant_flux', models.CharField(max_length=50)),
                ('horodate', models.DateTimeField()),
                ('date_reception_flux', models.DateTimeField()),
                ('dernier_flux', models.BooleanField()),
                ('valeur', models.FloatField()),
            ],
            options={
                'ordering': ('horodate',),
            },
        ),
        migrations.CreateModel(
            name='TimeSerieElementMongoIndexHorodate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_site', models.BigIntegerField()),
                ('identifiant_flux', models.CharField(max_length=50)),
                ('horodate', models.DateTimeField()),
                ('date_reception_flux', models.DateTimeField()),
                ('dernier_flux', models.BooleanField()),
                ('valeur', models.FloatField()),
            ],
            options={
                'ordering': ('horodate',),
            },
        ),
        migrations.CreateModel(
            name='TimeSerieElementMongoIndexHorodateSite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_site', models.BigIntegerField()),
                ('identifiant_flux', models.CharField(max_length=50)),
                ('horodate', models.DateTimeField()),
                ('date_reception_flux', models.DateTimeField()),
                ('dernier_flux', models.BooleanField()),
                ('valeur', models.FloatField()),
            ],
            options={
                'ordering': ('horodate',),
            },
        ),
        migrations.CreateModel(
            name='TimeSerieElementMongoIndexSite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_site', models.BigIntegerField()),
                ('identifiant_flux', models.CharField(max_length=50)),
                ('horodate', models.DateTimeField()),
                ('date_reception_flux', models.DateTimeField()),
                ('dernier_flux', models.BooleanField()),
                ('valeur', models.FloatField()),
            ],
            options={
                'ordering': ('horodate',),
            },
        ),
        migrations.CreateModel(
            name='TimeSerieElementQuestdb',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='TimeSerieElementQuestdbIndexSite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='TimeSerieElementQuestdbIndexSitePartition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='TimeserieElementQuestdbPartition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='TimeSerieElementTimescale',
            fields=[
                ('horodate', timescale.db.models.fields.TimescaleDateTimeField(db_index=True, interval='1 month', primary_key=True, serialize=False)),
                ('id_site', models.BigIntegerField(db_index=True)),
                ('identifiant_flux', models.CharField(max_length=50)),
                ('date_reception_flux', models.DateTimeField()),
                ('dernier_flux', models.BooleanField()),
                ('valeur', models.FloatField()),
            ],
            options={
                'ordering': ('horodate',),
            },
        ),
    ]