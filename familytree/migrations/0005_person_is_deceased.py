# Generated migration for is_deceased field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('familytree', '0004_person_media'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='is_deceased',
            field=models.BooleanField(default=False, help_text='Marquer comme décédé même sans date'),
        ),
    ]
