import csv
import os
import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from signbank.settings.server_specific import DEFAULT_KEYWORDS_LANGUAGE
from signbank.dictionary.models import Dataset, Gloss
from signbank.abstract_machine import create_gloss
from signbank.zip_interface import unzip_video_files, import_video_file

User = get_user_model()


class _FakeRequest:
    """Minimal request substitute for functions that only need request.user."""
    def __init__(self, user):
        self.user = user


class Command(BaseCommand):
    help = ('Import glosses from a CSV file into an existing dataset, '
            'and optionally import videos from a zip archive. '
            'The dataset and all its languages must already exist in the database.\n\n'
            'Expected CSV columns (one per dataset language):\n'
            '  Dataset, Lemma ID Gloss (<lang>), Annotation ID Gloss (<lang>), Senses (<lang>)\n\n'
            'Expected zip structure:\n'
            '  <acronym>/<lang3char>/<annotation_text>.mp4')

    def add_arguments(self, parser):
        parser.add_argument('--dataset', required=True, metavar='ACRONYM',
                            help='Acronym of the target dataset (must already exist)')
        parser.add_argument('--csv', required=True, dest='csv_file', metavar='FILE',
                            help='Path to the CSV file with gloss data')
        parser.add_argument('--videos', required=False, dest='zip_file', metavar='FILE',
                            help='Path to a zip file containing videos (optional)')
        parser.add_argument('--user', required=True, metavar='USERNAME',
                            help='Username to record as gloss creator')
        parser.add_argument('--dry-run', action='store_true',
                            help='Validate and report what would happen without writing to the database')

    def handle(self, *args, **options):
        dataset_acronym = options['dataset']
        csv_path = options['csv_file']
        zip_path = options.get('zip_file')
        username = options['user']
        dry_run = options['dry_run']

        # ── Validate inputs ────────────────────────────────────────────────
        try:
            dataset = Dataset.objects.get(acronym=dataset_acronym)
        except Dataset.DoesNotExist:
            raise CommandError(f"Dataset '{dataset_acronym}' does not exist.")

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError(f"User '{username}' does not exist.")

        if not os.path.isfile(csv_path):
            raise CommandError(f"CSV file not found: {csv_path}")

        if zip_path and not os.path.isfile(zip_path):
            raise CommandError(f"Video zip file not found: {zip_path}")

        dataset_languages = list(dataset.translation_languages.all())
        if not dataset_languages:
            raise CommandError(
                f"Dataset '{dataset_acronym}' has no translation languages configured. "
                "Add languages to the dataset before importing."
            )

        # ── Build column ↔ value_dict key mappings ─────────────────────────
        # CSV column names use the human language name, e.g. "Annotation ID Gloss (English)"
        # create_gloss() expects keys like "annotation_id_gloss_en"
        lang_attr = 'name_' + DEFAULT_KEYWORDS_LANGUAGE['language_code_2char']
        lemma_col_map = {}
        annot_col_map = {}
        sense_col_map = {}
        for lang in dataset_languages:
            lang_name = getattr(lang, lang_attr)
            code = lang.language_code_2char
            lemma_col_map[f"Lemma ID Gloss ({lang_name})"] = f"lemma_id_gloss_{code}"
            annot_col_map[f"Annotation ID Gloss ({lang_name})"] = f"annotation_id_gloss_{code}"
            sense_col_map[f"Senses ({lang_name})"] = f"sense_{code}"

        required_cols = set(lemma_col_map) | set(annot_col_map)

        # ── Parse CSV ──────────────────────────────────────────────────────
        with open(csv_path, newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        if not rows:
            self.stdout.write(self.style.WARNING("CSV file is empty, nothing to import."))
            return

        missing_cols = required_cols - set(rows[0].keys())
        if missing_cols:
            raise CommandError(
                "CSV is missing required columns:\n  " + "\n  ".join(sorted(missing_cols))
            )

        self.stdout.write(f"Dataset : {dataset} ({dataset_acronym})")
        self.stdout.write(f"User    : {username}")
        self.stdout.write(f"Rows    : {len(rows)}")
        self.stdout.write(f"Dry run : {dry_run}")
        self.stdout.write("")

        # ── Create glosses ─────────────────────────────────────────────────
        default_lang = dataset_languages[0]
        created = skipped = errors = 0

        for row_nr, row in enumerate(rows, start=1):
            # Optional Dataset column must match if present
            row_dataset = row.get('Dataset', '').strip()
            if row_dataset and row_dataset != dataset_acronym:
                self.stdout.write(self.style.WARNING(
                    f"  Row {row_nr}: Dataset column is '{row_dataset}', expected '{dataset_acronym}' — skipping."
                ))
                skipped += 1
                continue

            # Build the value_dict create_gloss() expects
            value_dict = {}
            for col, key in lemma_col_map.items():
                value_dict[key] = row.get(col, '').strip()
            for col, key in annot_col_map.items():
                value_dict[key] = row.get(col, '').strip()
            for col, key in sense_col_map.items():
                value_dict[key] = row.get(col, '').strip()

            annotation_text = value_dict.get(f"annotation_id_gloss_{default_lang.language_code_2char}", '')
            if not annotation_text:
                self.stdout.write(self.style.WARNING(
                    f"  Row {row_nr}: empty Annotation ID Gloss — skipping."
                ))
                skipped += 1
                continue

            # Skip duplicates already in the database
            existing = Gloss.objects.filter(
                lemma__dataset=dataset,
                annotationidglosstranslation__text=annotation_text,
                annotationidglosstranslation__language=default_lang,
            ).first()
            if existing:
                self.stdout.write(self.style.WARNING(
                    f"  Row {row_nr}: '{annotation_text}' already exists (#{existing.pk}) — skipping."
                ))
                skipped += 1
                continue

            if dry_run:
                self.stdout.write(f"  Row {row_nr}: would create '{annotation_text}'")
                created += 1
                continue

            result = create_gloss(user, dataset, value_dict)
            if result['createstatus'] == 'Success':
                self.stdout.write(self.style.SUCCESS(
                    f"  Row {row_nr}: created '{annotation_text}' (#{result['glossid']})"
                ))
                created += 1
            else:
                self.stdout.write(self.style.ERROR(
                    f"  Row {row_nr}: failed to create '{annotation_text}' — {result.get('errors')}"
                ))
                errors += 1

        self.stdout.write("")
        self.stdout.write(
            f"Glosses — created: {created}, skipped: {skipped}, errors: {errors}"
        )

        if not zip_path:
            return
        if dry_run:
            self.stdout.write("(dry-run: video import skipped)")
            return

        # ── Import videos ──────────────────────────────────────────────────
        self.stdout.write("")
        self.stdout.write("Importing videos from zip…")

        tmp_dir = tempfile.mkdtemp(prefix='signbank_import_')
        try:
            # Pre-create the subdirectory tree unzip_video_files expects
            for lang in dataset_languages:
                os.makedirs(
                    os.path.join(tmp_dir, dataset_acronym, lang.language_code_3char),
                    exist_ok=True,
                )

            unzip_video_files(dataset, zip_path, tmp_dir)

            fake_request = _FakeRequest(user)
            vid_ok = vid_skip = vid_fail = 0

            for lang in dataset_languages:
                lang_dir = os.path.join(tmp_dir, dataset_acronym, lang.language_code_3char)
                if not os.path.isdir(lang_dir):
                    continue

                for filename in sorted(os.listdir(lang_dir)):
                    if not filename.lower().endswith('.mp4'):
                        continue

                    annotation_text, _ = os.path.splitext(filename)
                    gloss = Gloss.objects.filter(
                        lemma__dataset=dataset,
                        annotationidglosstranslation__text=annotation_text,
                        annotationidglosstranslation__language=lang,
                    ).first()

                    if not gloss:
                        self.stdout.write(self.style.WARNING(
                            f"  {filename}: no matching gloss found — skipping."
                        ))
                        vid_skip += 1
                        continue

                    video_file_path = os.path.join(lang_dir, filename)
                    status, err = import_video_file(fake_request, gloss, video_file_path)
                    if status == 'Success':
                        self.stdout.write(self.style.SUCCESS(
                            f"  {filename} → gloss #{gloss.pk}"
                        ))
                        vid_ok += 1
                    else:
                        self.stdout.write(self.style.ERROR(
                            f"  {filename}: import failed — {err}"
                        ))
                        vid_fail += 1
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

        self.stdout.write("")
        self.stdout.write(
            f"Videos  — imported: {vid_ok}, skipped: {vid_skip}, failed: {vid_fail}"
        )
