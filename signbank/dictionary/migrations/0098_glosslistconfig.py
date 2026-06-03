from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0097_add_nma_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='GlossListConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('display_fields', models.JSONField(
                    default=list,
                    help_text='Ordered list of Gloss field names shown as extra columns in the search results.'
                )),
            ],
            options={
                'verbose_name': 'Gloss List Column Configuration',
                'verbose_name_plural': 'Gloss List Column Configuration',
            },
        ),
    ]
