# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('zerver', '0027_auto_20160726_0913'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interviewgroup',
            name='interviewers',
            field=models.ManyToManyField(related_name='hire', null=True, to=settings.AUTH_USER_MODEL, blank=True),
        ),
        migrations.AlterField(
            model_name='interviewgroup',
            name='respondent',
            field=models.ForeignKey(related_name='find', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
