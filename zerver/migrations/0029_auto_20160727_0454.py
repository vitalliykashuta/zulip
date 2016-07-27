# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('zerver', '0028_auto_20160727_0453'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interviewgroup',
            name='interviewers',
            field=models.ManyToManyField(related_name='hire', to=settings.AUTH_USER_MODEL, blank=True),
        ),
    ]
