# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-04-11 17:16
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Series', '0019_auto_20170411_1815'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='magnet',
            options={'ordering': ['-seeds_number']},
        ),
    ]
