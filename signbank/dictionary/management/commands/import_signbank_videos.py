"""Import SignBank MP4 videos by matching 5-digit prefix to Gloss.alternative_id."""

import os
import re
import shutil
from django.core.management.base import BaseCommand
from signbank.dictionary.models import Dataset, Gloss
from signbank.video.models import GlossVideo
from signbank.settings.server_specific import WRITABLE_FOLDER, GLOSS_VIDEO_DIRECTORY


# Matches filenames like 00007.sgb.mp4  →  groups: (id='00007', variant='sgb')
VIDEO_RE = re.compile(r'^(\d{5})\.(\w+)\.(mp4|m4v|mov|webm)$', re.IGNORECASE)


def _target_dir(dataset_acronym, idgloss):
    two_letter = idgloss[:2].upper() if idgloss else 'XX'
    return os.path.join(WRITABLE_FOLDER, GLOSS_VIDEO_DIRECTORY, dataset_acronym, two_letter)


def _target_filename(idgloss, gloss_id, variant, extension):
    if variant:
        return f'{idgloss}-{gloss_id}_{variant}.{extension.lower()}'
    return f'{idgloss}-{gloss_id}.{extension.lower()}'


class Command(BaseCommand):
    help = 'Import MP4 videos from a folder by matching 00007.sgb.mp4 → Gloss.alternative_id=7.'

    def add_arguments(self, parser):
        parser.add_argument('videos_folder', help='Path to folder containing the .mp4 files')
        parser.add_argument('--dataset', default=None,
                            help='Dataset acronym (default: first dataset in DB)')
        parser.add_argument('--dry-run', action='store_true',
                            help='Show matches without copying files or writing DB records')
        parser.add_argument('--limit', type=int, default=0,
                            help='Stop after N files (0 = no limit)')

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        limit = options['limit']
        folder = os.path.expanduser(options['videos_folder'])

        dataset = (
            Dataset.objects.get(acronym=options['dataset'])
            if options['dataset']
            else Dataset.objects.first()
        )
        self.stdout.write(f'Dataset: {dataset.name} ({dataset.acronym})')
        self.stdout.write(f'Videos folder: {folder}')

        # Build a lookup: alternative_id (str) → Gloss
        gloss_map = {
            g.alternative_id: g
            for g in Gloss.objects.filter(lemma__dataset=dataset)
            .exclude(alternative_id__isnull=True)
            .exclude(alternative_id='')
        }
        self.stdout.write(f'Glosses with alternative_id: {len(gloss_map)}')

        copied = skipped_exists = skipped_no_gloss = errors = 0
        processed = 0

        filenames = sorted(f for f in os.listdir(folder) if VIDEO_RE.match(f))
        self.stdout.write(f'Video files found: {len(filenames)}')

        for filename in filenames:
            m = VIDEO_RE.match(filename)
            if not m:
                continue

            raw_id, variant, ext = m.group(1), m.group(2), m.group(3)
            ilex_id = str(int(raw_id))   # strip leading zeros for matching

            gloss = gloss_map.get(ilex_id)
            if not gloss:
                skipped_no_gloss += 1
                continue

            idgloss = gloss.idgloss or str(gloss.id)
            target_dir = _target_dir(dataset.acronym, idgloss)
            target_name = _target_filename(idgloss, gloss.id, variant, ext)
            target_rel = os.path.join(GLOSS_VIDEO_DIRECTORY, dataset.acronym,
                                      idgloss[:2].upper() if idgloss else 'XX',
                                      target_name)

            # Skip if DB record already exists for this gloss+path
            if GlossVideo.objects.filter(gloss=gloss, videofile=target_rel).exists():
                skipped_exists += 1
                continue

            if dry_run:
                self.stdout.write(f'  {filename}  →  {target_rel}  (gloss #{gloss.id} {idgloss})')
                copied += 1
            else:
                try:
                    os.makedirs(target_dir, exist_ok=True)
                    src = os.path.join(folder, filename)
                    dst = os.path.join(target_dir, target_name)
                    shutil.copy2(src, dst)

                    # Determine version: 0 for first video, increment for extras
                    existing_count = GlossVideo.objects.filter(gloss=gloss).count()
                    GlossVideo.objects.create(
                        gloss=gloss,
                        videofile=target_rel,
                        version=existing_count,
                    )
                    copied += 1
                except Exception as exc:
                    self.stderr.write(f'  ERROR {filename}: {exc}')
                    errors += 1

            processed += 1
            if processed % 500 == 0:
                self.stdout.write(
                    f'  ... {processed} processed | {copied} copied | '
                    f'{skipped_no_gloss} no-gloss | {errors} errors'
                )
            if limit and processed >= limit:
                break

        action = 'Would copy' if dry_run else 'Copied'
        self.stdout.write(
            f'\nDone — {action}: {copied}  |  skipped (no gloss match): {skipped_no_gloss}'
            f'  |  skipped (already exists): {skipped_exists}  |  errors: {errors}'
        )
