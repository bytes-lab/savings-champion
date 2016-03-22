# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def truncate_table(apps, schema_editor):
    ConciergeUserPool = apps.get_model("concierge", "ConciergeUserPool")

    ConciergeUserPool.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('concierge', '0003_adviserqueue__claim_time'),
    ]

    operations = [

        migrations.RunPython(truncate_table),

        migrations.AlterUniqueTogether(
            name='conciergeuserpool',
            unique_together=set([('user', 'term')]),
        ),
    ]
