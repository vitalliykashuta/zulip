# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('zerver', '0025_realm_message_content_edit_limit'),
    ]

    operations = [
        migrations.CreateModel(
            name='InterviewGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('job_post_hash', models.CharField(unique=True, max_length=40, db_index=True)),
                ('huddle', models.ForeignKey(blank=True, to='zerver.Huddle', null=True)),
                ('interviewers', models.ManyToManyField(related_name='hire', to=settings.AUTH_USER_MODEL)),
                ('respondent', models.ForeignKey(related_name='find', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
