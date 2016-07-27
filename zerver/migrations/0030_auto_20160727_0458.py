# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('zerver', '0029_auto_20160727_0454'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interviewgroup',
            name='job_post_hash',
            field=models.CharField(max_length=40, db_index=True),
        ),
        migrations.AlterUniqueTogether(
            name='interviewgroup',
            unique_together=set([('respondent', 'job_post_hash')]),
        ),
    ]
