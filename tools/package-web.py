#!/usr/bin/env python3
"""Package only deployable plugin/theme files, never the local site or credentials."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import json
import re

DUPLICATE = re.compile(r' \d+(\.[A-Za-z0-9]+)?$')  # Finder copies: 'pdf 2.mjs', 'LICENSE 3'

root = Path(__file__).resolve().parents[1]
version = json.loads((root / 'package.json').read_text())['version']
out = root / 'dist'
out.mkdir(exist_ok=True)
theme = root / 'wordpress/themes/flexagon'
for required in ('assets/app.js', 'assets/app.css', 'assets/katex/katex.min.css', 'assets/pdfjs/pdf.mjs', 'assets/pdfjs/pdf.worker.mjs'):
    if not (theme / required).is_file():
        raise SystemExit('Run npm run build:web before packaging.')
for kind, folder in (('plugin', root / 'wordpress/plugins/flexagon'), ('theme', theme)):
    metadata = folder / ('flexagon.php' if kind == 'plugin' else 'style.css')
    match = re.search(r'^\s*(?:\*\s*)?Version:\s*(\S+)', metadata.read_text(), re.M)
    package_version = match.group(1) if match else version
    archive = out / f'flexagon-{kind}-{package_version}.zip'
    with ZipFile(archive, 'w', ZIP_DEFLATED) as package:
        for file in sorted(folder.rglob('*')):
            relative = file.relative_to(folder)
            if not file.is_file() or relative.parts[0] == 'src' or file.name.startswith('.') or file.suffix == '.md':
                continue
            if DUPLICATE.search(file.name):
                raise SystemExit(f'Stray duplicate file in {kind}: {relative}. Delete it and run npm run build:web.')
            if kind == 'plugin' and file.suffix != '.php':
                continue
            package.write(file, Path('flexagon') / relative)
    with ZipFile(archive) as package:
        assert package.testzip() is None
        assert all('.local' not in name and 'wp-config' not in name for name in package.namelist())
    print(archive)
