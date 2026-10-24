"""Preserve reviewed unused assets locally; default copies, --move removes public copies."""

import argparse
from datetime import date, datetime
import hashlib
import json
from pathlib import Path
import shutil
from zoneinfo import ZoneInfo

from check_site import ROOT, audit


def checksum(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('paths', nargs='+', type=Path, help='Explicit reviewed asset paths')
    parser.add_argument('--date', type=date.fromisoformat)
    parser.add_argument('--note', required=True, help='Why these files are being archived')
    parser.add_argument('--move', action='store_true', help='Remove public files only after verified copies exist')
    args = parser.parse_args()
    report = audit(ROOT)
    if report['errors']:
        raise SystemExit('Fix site-check errors before archiving assets.')
    assets = {a['path']: a for a in report['assets']}
    day = str(args.date or datetime.now(ZoneInfo('Asia/Tokyo')).date())
    folder = ROOT / '・Site archive' / day
    manifest_path = folder / 'manifest.json'
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else []
    pending = []
    # Validate the whole requested set before changing any public files.
    for value in args.paths:
        path = (ROOT / value).resolve()
        if not path.is_relative_to(ROOT):
            raise SystemExit(f'Not inside website: {value}')
        relative = str(path.relative_to(ROOT))
        item = assets.get(relative)
        if not item or item['referencedBy']:
            raise SystemExit(f'Not an unused media asset: {value}')
        target = folder / relative
        if target.exists() and checksum(target) != item['sha256']:
            raise SystemExit(f'Archive collision; keep existing history: {target}')
        pending.append((path, target, item))
    for path, target, item in pending:
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            shutil.copy2(path, target)
        if checksum(target) != item['sha256']:
            raise SystemExit(f'Archive verification failed: {target}')
        manifest.append({'originalPath': item['path'], 'bytes': item['bytes'],
                         'sha256': item['sha256'], 'archivedOn': day,
                         'operation': 'move' if args.move else 'copy', 'note': args.note})
        # Persist the recovery record before removing the verified public copy.
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
        if args.move:
            path.unlink()
        print(('MOVED ' if args.move else 'COPIED ') + item['path'])


if __name__ == '__main__':
    main()
