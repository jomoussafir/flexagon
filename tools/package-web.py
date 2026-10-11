#!/usr/bin/env python3
"""Package only deployable plugin/theme files, never the local site or credentials."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import json

root = Path(__file__).resolve().parents[1]
version = json.loads((root / 'package.json').read_text())['version']
out = root / 'dist'
out.mkdir(exist_ok=True)
theme = root / 'wordpress/themes/le-probleme-du-jour'
for required in ('assets/app.js', 'assets/app.css', 'assets/katex/katex.min.css'):
    if not (theme / required).is_file():
        raise SystemExit('Run npm run build:web before packaging.')
for kind, folder in (('plugin', root / 'wordpress/plugins/le-probleme-du-jour'), ('theme', theme)):
    archive = out / f'le-probleme-du-jour-{kind}-{version}.zip'
    with ZipFile(archive, 'w', ZIP_DEFLATED) as package:
        for file in sorted(folder.rglob('*')):
            relative = file.relative_to(folder)
            if not file.is_file() or relative.parts[0] == 'src' or file.name.startswith('.') or file.suffix == '.md':
                continue
            if kind == 'plugin' and file.suffix != '.php':
                continue
            package.write(file, Path('le-probleme-du-jour') / relative)
    with ZipFile(archive) as package:
        assert package.testzip() is None
        assert all('.local' not in name and 'wp-config' not in name for name in package.namelist())
    print(archive)
