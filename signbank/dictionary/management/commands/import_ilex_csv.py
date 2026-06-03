"""Import glosses from an iLex CSV export into Signbank."""

import csv
import re
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from signbank.dictionary.models import (
    Dataset, Gloss, LemmaIdgloss, LemmaIdglossTranslation,
    AnnotationIdglossTranslation, Language, Keyword, Translation,
)


def _clean_name(name):
    """Return the bare concept name without iLex phonetic suffixes.

    DEFINITIV_1A'bew'lok  →  DEFINITIV_1A
    SITZEN_1B'bew_phs:2   →  SITZEN_1B
    """
    return re.split(r"'", name)[0].strip()


def _lemma_base(annotation_name):
    """Strip variant letter to get a lemma key.

    DEFINITIV_1A  →  DEFINITIV_1
    DEFINITIV_2B  →  DEFINITIV_2
    """
    return re.sub(r'[A-Z]$', '', annotation_name).rstrip('_')


class Command(BaseCommand):
    help = 'Import glosses from an iLex CSV export (level-1 entries only).'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', help='Path to the iLex CSV file')
        parser.add_argument('--dataset', default=None,
                            help='Dataset acronym (default: first dataset in DB)')
        parser.add_argument('--dry-run', action='store_true',
                            help='Report what would be imported without writing')
        parser.add_argument('--limit', type=int, default=0,
                            help='Stop after N rows (0 = no limit, for testing)')

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        limit = options['limit']

        dataset = (
            Dataset.objects.get(acronym=options['dataset'])
            if options['dataset']
            else Dataset.objects.first()
        )
        language = dataset.default_language
        if not language:
            self.stderr.write('Dataset has no default language set.')
            return

        self.stdout.write(f'Dataset: {dataset.name} ({dataset.acronym})  language: {language}')

        admin_user = User.objects.filter(is_superuser=True).first()

        created = skipped = errors = 0

        with open(options['csv_file'], encoding='utf-8-sig') as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                name = row.get('name', '').strip()
                level = row.get('level', '').strip()
                ilex_id = row.get('id', '').strip()

                # Only import level-1 reviewed entries
                if level != '1':
                    continue
                if not name or 'UNGEPRÜFT' in name.upper():
                    continue
                if not ilex_id:
                    continue

                annotation_text = _clean_name(name)[:30]   # DB max_length=30
                lemma_text = _lemma_base(annotation_text)[:30]
                mouthing = row.get('mouth', '').strip()
                english = row.get('english', '').strip()
                hamnosys = row.get('hamnosys', '').strip()

                if dry_run:
                    self.stdout.write(
                        f'  Would create: [{ilex_id}] {annotation_text}'
                        + (f'  mouth={mouthing}' if mouthing else '')
                    )
                    created += 1
                    if limit and created >= limit:
                        break
                    continue

                # Skip if already imported (idempotent on alternative_id)
                if Gloss.objects.filter(alternative_id=ilex_id, lemma__dataset=dataset).exists():
                    skipped += 1
                    continue

                try:
                    # Lemma: reuse existing one with same text in this dataset
                    lemma_trans = LemmaIdglossTranslation.objects.filter(
                        text=lemma_text,
                        language=language,
                        lemma__dataset=dataset,
                    ).first()
                    if lemma_trans:
                        lemma = lemma_trans.lemma
                    else:
                        lemma = LemmaIdgloss.objects.create(dataset=dataset)
                        LemmaIdglossTranslation.objects.create(
                            lemma=lemma, language=language, text=lemma_text
                        )

                    gloss = Gloss.objects.create(
                        lemma=lemma,
                        alternative_id=ilex_id,
                        mouthing=mouthing,
                        hamnosys=hamnosys,
                    )
                    if admin_user:
                        gloss.creator.add(admin_user)

                    AnnotationIdglossTranslation.objects.create(
                        gloss=gloss,
                        language=language,
                        text=annotation_text,
                    )

                    # English keyword → Translation
                    if english:
                        for word in english.split(';'):
                            word = word.strip()
                            if word:
                                kw, _ = Keyword.objects.get_or_create(text=word[:100])
                                Translation.objects.get_or_create(
                                    gloss=gloss,
                                    language=language,
                                    translation=kw,
                                )

                    created += 1
                    if created % 500 == 0:
                        self.stdout.write(f'  ... {created} created, {skipped} skipped')

                except Exception as exc:
                    self.stderr.write(f'  ERROR row {ilex_id} ({annotation_text}): {exc}')
                    errors += 1

                if limit and (created + skipped) >= limit:
                    break

        action = 'Would create' if dry_run else 'Created'
        self.stdout.write(
            f'\nDone — {action}: {created}  |  skipped (already exists): {skipped}  |  errors: {errors}'
        )
