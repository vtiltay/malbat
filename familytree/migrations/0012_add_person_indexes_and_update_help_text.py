# Generated manually for Person model timestamp improvements

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('familytree', '0011_alter_familychild_order_and_more'),
    ]

    operations = [
        # Update help text for timestamp fields
        migrations.AlterField(
            model_name='person',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, help_text='When this record was first created in the database', null=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, help_text='Last modification time (any change, including web app edits)'),
        ),
        migrations.AlterField(
            model_name='person',
            name='gramps_last_updated',
            field=models.DateTimeField(blank=True, help_text='Last update from Gramps synchronization', null=True),
        ),
        # Add indexes for better query performance
        migrations.AddIndex(
            model_name='person',
            index=models.Index(fields=['gramps_id'], name='familytree_gramps__idx'),
        ),
        migrations.AddIndex(
            model_name='person',
            index=models.Index(fields=['last_name', 'first_name'], name='familytree_name_idx'),
        ),
        migrations.AddIndex(
            model_name='person',
            index=models.Index(fields=['gramps_last_updated'], name='familytree_gramps_sync_idx'),
        ),
    ]
