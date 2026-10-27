#!/usr/bin/env python3
"""Flatten a Bambu Studio preset ("inherits": a BBL system preset) into one self-contained
JSON for the command-line slicer, which refuses user presets whose inherited compatibility it cannot resolve
("process not compatible with printer").  usage: flatten_preset.py <profiles/BBL dir> <preset.json> <out.json>"""
import json, os, sys

prof, src, out = sys.argv[1:4]
index = {}
for kind in ('machine', 'process', 'filament'):
    for f in os.listdir(os.path.join(prof, kind)):
        if f.endswith('.json'):
            try:
                d = json.load(open(os.path.join(prof, kind, f)))
            except Exception:
                continue
            index[d.get('name', f[:-5])] = d


def resolve(d):
    base = resolve(index[d['inherits']]) if d.get('inherits') in index else {}
    if d.get('inherits') and d['inherits'] not in index:
        sys.exit(f"preset {d['inherits']!r} not found under {prof}")
    m = dict(base)
    m.update(d)
    return m


d = resolve(json.load(open(src)))
d.pop('inherits', None)
d['from'] = 'system'
json.dump(d, open(out, 'w'), indent=1)
print(out, len(d), 'keys', d.get('compatible_printers', '')[:2] if isinstance(d.get('compatible_printers'), list) else '')
