from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0095_alter_affiliation_field_color_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='gloss',
            name='hamnosys',
            field=models.TextField(blank=True, null=True, verbose_name='HamNoSys'),
        ),
    ]