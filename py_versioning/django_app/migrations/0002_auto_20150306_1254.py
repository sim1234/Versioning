# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_app', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='dbversion',
            old_name='json',
            new_name='json_db',
        ),
        migrations.RenameField(
            model_name='dbversion',
            old_name='name',
            new_name='version',
        ),
        migrations.AddField(
            model_name='fsversion',
            name='git_hash',
            field=models.CharField(default='-', max_length=255, verbose_name='Git hash data'),
            preserve_default=False,
        ),
    ]
