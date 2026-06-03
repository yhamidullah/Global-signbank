import django.db.models.deletion
from django.db import migrations, models
import signbank.dictionary.models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0096_gloss_hamnosys'),
    ]

    operations = [
        # Add NMA FieldChoice category choices (no DB change needed — these are Python constants
        # that feed the 'choices' argument; the migration just adds the FK columns below).

        migrations.AddField(
            model_name='gloss',
            name='nmaEyebrows',
            field=signbank.dictionary.models.FieldChoiceForeignKey(
                blank=True, null=True,
                field_choice_category='NmaEyebrows',
                limit_choices_to={'field': 'NmaEyebrows'},
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='nma_eyebrows',
                to='dictionary.fieldchoice',
                verbose_name='NMA Eyebrows',
            ),
        ),
        migrations.AddField(
            model_name='gloss',
            name='nmaEyelids',
            field=signbank.dictionary.models.FieldChoiceForeignKey(
                blank=True, null=True,
                field_choice_category='NmaEyelids',
                limit_choices_to={'field': 'NmaEyelids'},
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='nma_eyelids',
                to='dictionary.fieldchoice',
                verbose_name='NMA Eyelids',
            ),
        ),
        migrations.AddField(
            model_name='gloss',
            name='nmaGaze',
            field=signbank.dictionary.models.FieldChoiceForeignKey(
                blank=True, null=True,
                field_choice_category='NmaGaze',
                limit_choices_to={'field': 'NmaGaze'},
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='nma_gaze',
                to='dictionary.fieldchoice',
                verbose_name='NMA Gaze',
            ),
        ),
        migrations.AddField(
            model_name='gloss',
            name='nmaHead',
            field=signbank.dictionary.models.FieldChoiceForeignKey(
                blank=True, null=True,
                field_choice_category='NmaHead',
                limit_choices_to={'field': 'NmaHead'},
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='nma_head',
                to='dictionary.fieldchoice',
                verbose_name='NMA Head',
            ),
        ),
        migrations.AddField(
            model_name='gloss',
            name='nmaMouthGesture',
            field=signbank.dictionary.models.FieldChoiceForeignKey(
                blank=True, null=True,
                field_choice_category='NmaMouthGesture',
                limit_choices_to={'field': 'NmaMouthGesture'},
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='nma_mouth_gesture',
                to='dictionary.fieldchoice',
                verbose_name='NMA Mouth Gesture',
            ),
        ),
        migrations.AddField(
            model_name='gloss',
            name='nmaNmk',
            field=signbank.dictionary.models.FieldChoiceForeignKey(
                blank=True, null=True,
                field_choice_category='NmaNmk',
                limit_choices_to={'field': 'NmaNmk'},
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='nma_nmk',
                to='dictionary.fieldchoice',
                verbose_name='NMA Non-Manual Component',
            ),
        ),
        migrations.AddField(
            model_name='gloss',
            name='nmaNose',
            field=signbank.dictionary.models.FieldChoiceForeignKey(
                blank=True, null=True,
                field_choice_category='NmaNose',
                limit_choices_to={'field': 'NmaNose'},
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='nma_nose',
                to='dictionary.fieldchoice',
                verbose_name='NMA Nose',
            ),
        ),
        migrations.AddField(
            model_name='gloss',
            name='nmaTorso',
            field=signbank.dictionary.models.FieldChoiceForeignKey(
                blank=True, null=True,
                field_choice_category='NmaTorso',
                limit_choices_to={'field': 'NmaTorso'},
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='nma_torso',
                to='dictionary.fieldchoice',
                verbose_name='NMA Torso',
            ),
        ),
        migrations.AddField(
            model_name='gloss',
            name='nmaShoulders',
            field=signbank.dictionary.models.FieldChoiceForeignKey(
                blank=True, null=True,
                field_choice_category='NmaShoulders',
                limit_choices_to={'field': 'NmaShoulders'},
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='nma_shoulders',
                to='dictionary.fieldchoice',
                verbose_name='NMA Shoulders',
            ),
        ),
    ]
