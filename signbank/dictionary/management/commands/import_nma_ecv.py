"""Import non-manual annotation (NMA) vocabulary from ECV text files into FieldChoice."""

import os
from django.core.management.base import BaseCommand
from signbank.dictionary.models import FieldChoice


# Maps each ECV filename to its FieldChoice category constant
ECV_FILE_MAP = [
    ('Augenbrauen.txt', FieldChoice.NMAEYEBROWS),
    ('Augenlider.txt', FieldChoice.NMAEYELIDS),
    ('Blick.txt',      FieldChoice.NMAGAZE),
    ('Kopf.txt',       FieldChoice.NMAHEAD),
    ('Mundform.txt',   FieldChoice.NMAMOUTHGESTURE),
    ('NMK.txt',        FieldChoice.NMANK),
    ('Nase.txt',       FieldChoice.NMANOSE),
    ('Rumpf.txt',      FieldChoice.NMATORSO),
    ('Schultern.txt',  FieldChoice.NMASHOULDERS),
]


def _next_machine_value(field_category):
    existing = FieldChoice.objects.filter(field=field_category).order_by('-machine_value').first()
    return (existing.machine_value + 1) if existing else 1


def _parse_ecv_file(filepath):
    """Yield (name,) tuples from a tab-separated ECV vocabulary file.

    Format per line: <order_id>\t<short_code>\t<DE description>\t<EN description>\t<false>
    The short_code (column 2) is used as the canonical name stored in FieldChoice.
    Lines where the short_code is '?' are skipped.
    """
    with open(filepath, encoding='utf-8') as fh:
        for line in fh:
            line = line.rstrip('\n')
            parts = line.split('\t')
            if len(parts) < 2:
                continue
            name = parts[1].strip()
            if not name or name == '?':
                continue
            yield name


class Command(BaseCommand):
    help = 'Import NMA ECV vocabulary files into FieldChoice entries.'

    def add_arguments(self, parser):
        parser.add_argument(
            'ecv_folder',
            help='Path to the folder containing the ECV .txt files (e.g. ~/Downloads/ECV)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Print what would be imported without writing to the database.',
        )

    def handle(self, *args, **options):
        folder = os.path.expanduser(options['ecv_folder'])
        dry_run = options['dry_run']

        for filename, field_category in ECV_FILE_MAP:
            filepath = os.path.join(folder, filename)
            if not os.path.exists(filepath):
                self.stderr.write(f'File not found, skipping: {filepath}')
                continue

            created_count = 0
            skipped_count = 0
            for name in _parse_ecv_file(filepath):
                exists = FieldChoice.objects.filter(field=field_category, name=name).exists()
                if exists:
                    skipped_count += 1
                    continue
                if not dry_run:
                    mv = _next_machine_value(field_category)
                    FieldChoice.objects.create(field=field_category, name=name, machine_value=mv)
                created_count += 1

            action = 'Would create' if dry_run else 'Created'
            self.stdout.write(
                f'{filename} [{field_category}]: {action} {created_count}, skipped {skipped_count} existing.'
            )
