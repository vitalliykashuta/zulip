# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('zerver', '0030_auto_20160727_0458'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContractGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('contract_hash', models.CharField(unique=True, max_length=40, db_index=True)),
                ('executor', models.ForeignKey(related_name='contract_owners', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('owners', models.ManyToManyField(related_name='contract_executors', to=settings.AUTH_USER_MODEL, blank=True)),
                ('stream', models.ForeignKey(blank=True, to='zerver.Stream', null=True)),
            ],
        ),
        migrations.AlterField(
            model_name='interviewgroup',
            name='respondent',
            field=models.ForeignKey(related_name='find_job', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
