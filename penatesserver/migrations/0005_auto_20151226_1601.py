# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-26 15:01
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import ldapdb.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('penatesserver', '0004_auto_20151214_1135'),
    ]

    operations = [
        migrations.CreateModel(
            name='RecoveryKey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kind', models.CharField(choices=[('filevault2', 'Filevault 2')], db_index=True, default='filevault2', max_length=255, verbose_name='kind')),
                ('serial_number', models.CharField(db_index=True, default=None, max_length=255, verbose_name='serial number')),
                ('recovery_key', models.TextField(blank=True, default='', verbose_name='recovery key')),
            ],
        ),
        migrations.CreateModel(
            name='WifiNetwork',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ssid', models.CharField(db_index=True, max_length=255, verbose_name='SSID')),
                ('hidden_network', models.BooleanField(default=False, verbose_name='hidden?')),
                ('encryption_type', models.CharField(blank=True, choices=[('WEP', 'WEP'), ('WPA', 'WPA'), ('Any', 'Any')], default=None, max_length=30, null=True, verbose_name='encryption type')),
                ('is_hotspot', models.BooleanField(default=False, verbose_name='hidden?')),
                ('password', models.CharField(blank=True, db_index=True, default=None, max_length=255, null=True, verbose_name='Password')),
            ],
        ),
        migrations.AlterField(
            model_name='djangouser',
            name='username',
            field=models.CharField(help_text='Required. Letters, digits and "/"/@/./+/-/_ only.', max_length=250, unique=True, validators=[django.core.validators.RegexValidator('^[/\\w.@+_\\-]+$', 'Enter a valid username. ', 'invalid')], verbose_name="nom d'utilisateur"),
        ),
        migrations.AlterField(
            model_name='host',
            name='fqdn',
            field=models.CharField(blank=True, db_index=True, default=None, help_text='hostname.admin.test.example.org', max_length=255, null=True, verbose_name='Host fqdn'),
        ),
    ]