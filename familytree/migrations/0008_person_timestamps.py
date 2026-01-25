# Generated migration for adding timestamps to Person model

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('familytree', '0007_proposedmodification'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='person',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
