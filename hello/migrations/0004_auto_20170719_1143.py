# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-07-19 15:43
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hello', '0003_auto_20170719_1140'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Quotes',
            new_name='Quote',
        ),
    ]
