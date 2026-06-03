from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0100_headerconfig_branding'),
    ]

    operations = [
        migrations.AddField(
            model_name='headerconfig',
            name='logo',
            field=models.FileField(
                blank=True,
                null=True,
                upload_to='branding/',
                help_text='Upload a logo image (SVG, PNG, etc.) shown in the header. Replaces the built-in theme icon.',
            ),
        ),
    ]
