# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('zerver', '0026_interviewgroup'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='interviewgroup',
            name='huddle',
        ),
        migrations.AddField(
            model_name='interviewgroup',
            name='stream',
            field=models.ForeignKey(blank=True, to='zerver.Stream', null=True),
        ),
    ]
