from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0098_glosslistconfig'),
    ]

    operations = [
        migrations.CreateModel(
            name='HeaderConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('theme', models.CharField(
                    choices=[('global', 'Global Signbank (default)'), ('uzh', 'UZH Computational Linguistics')],
                    default='global', max_length=20,
                )),
                ('site_title', models.CharField(
                    blank=True, max_length=100,
                    help_text='Override the main title shown in the header (leave blank for default).',
                )),
                ('institution_name', models.CharField(
                    blank=True, default='Universität Zürich', max_length=200,
                    help_text='Shown in the UZH theme institutional bar.',
                )),
                ('department_name', models.CharField(
                    blank=True, default='Institut für Computerlinguistik', max_length=200,
                    help_text='Shown in the UZH theme institutional bar.',
                )),
            ],
            options={
                'verbose_name': 'Header Theme Configuration',
                'verbose_name_plural': 'Header Theme Configuration',
            },
        ),
    ]
