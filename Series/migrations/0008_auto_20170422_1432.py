# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-04-22 13:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Series', '0007_auto_20170422_1317'),
    ]

    operations = [
        migrations.AlterField(
            model_name='episode',
            name='magnet_link',
            field=models.CharField(default=b'', max_length=1000),
        ),
    ]