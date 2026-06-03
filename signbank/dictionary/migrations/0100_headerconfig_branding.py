from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0099_headerconfig'),
    ]

    operations = [
        migrations.AddField(
            model_name='headerconfig',
            name='favicon',
            field=models.FileField(
                blank=True, null=True, upload_to='branding/',
                help_text='Upload a .png or .ico file to replace the default browser tab icon.',
            ),
        ),
        migrations.AddField(
            model_name='headerconfig',
            name='color_primary',
            field=models.CharField(
                blank=True, default='', max_length=20,
                help_text='Main brand color (hex, e.g. #0028a5).',
            ),
        ),
        migrations.AddField(
            model_name='headerconfig',
            name='color_primary_text',
            field=models.CharField(
                blank=True, default='', max_length=20,
                help_text='Text/icon color on the primary-colored background (default: #ffffff).',
            ),
        ),
        migrations.AddField(
            model_name='headerconfig',
            name='color_accent',
            field=models.CharField(
                blank=True, default='', max_length=20,
                help_text='Accent color for hover states, borders, and dropdown tops.',
            ),
        ),
        migrations.AddField(
            model_name='headerconfig',
            name='color_inst_bar_bg',
            field=models.CharField(
                blank=True, default='', max_length=20,
                help_text='Institutional strip background color (UZH theme, default: #f0f2f7).',
            ),
        ),
    ]
