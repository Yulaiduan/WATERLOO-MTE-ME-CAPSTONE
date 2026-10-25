"""Validate and persist independent Kinefold component and immutable study presets.

Imported lazily by ProfileService for preset-* requests; python verify_presets.py
checks temporary stores. Inputs retain builder mm/deg/kg/N and solver/motor SI;
outputs are profiles/presets.json with atomic optimistic revisions. Existing
project-v3/library.json and export behavior are untouched. Unknown passive terms
are flagged placeholders; saving is allowed, composition requires explicit ideal
zero acknowledgment in the browser. No hardware or dynamics validation is claimed.
"""
from __future__ import annotations

import copy
from datetime import datetime, timezone
import json
import math
import re
import uuid

from profile_service import StorageError, MAX_BYTES, _encoded, _project
from dynamic_model import Model, R, defaults
from motor_model import Motor

SCHEMA = 'kinefold/preset-library-v1'
BUNDLE_SCHEMA = 'kinefold/preset-bundle-v1'
UNKNOWN_KEYS = ('rotorInertiaKgM2', 'coggingAmplitudeNm', 'coulombFrictionNm', 'viscousFrictionNms')
RATING_KEYS = ('peakShaftNm', 'maxShaftRpm', 'gearboxContinuousNm', 'gearboxPeakNm')
OPTIONAL = ('contactConfig', 'caseConfig', 'energyConfig', 'torqueTargetConfig')
# A validation shell only; never saved, composed, or substituted for user inputs.
_PARAMS = dict(L2=300, L3=300, ra=50, rb=25, rc=35, rd=35, re=25, rf=25, rw=200,
              alpha=0, phi0=0, te=100, tc=165, theta2=132.5, m1=8.75, m2=0, m3=0,
              m5=0, m6=0, g=9.81, beta=0, Fn=85.8375, Ft=0, Fz=85.8375, Fx=0,
              loadMode='weight', Tab0=0, Tcd0=0, Tef0=0, springEnabled=False,
              springK=8, hornR=62, Sv=100, rs=10, p0=330, nu=0, Su=9, springLaw='v4')
_BOUNDS = dict(L2=(1, 5000), L3=(1, 5000), rw=(1, 2000), alpha=(0, 45), phi0=(0, 30),
               te=(90, 270), tc=(90, 270), springK=(0, 1000), p0=(0, 100000),
               hornR=(.1, 2000), nu=(-360, 360), Su=(-2000, 2000), Sv=(-2000, 2000),
               rs=(0, 1000), m1=(0, 10000), g=(0, 100), beta=(0, 90))
_BOUNDS.update({k: (.1, 1000) for k in ('ra', 'rb', 'rc', 'rd', 're', 'rf')})
_BOUNDS.update({k: (0, 1000) for k in ('m2', 'm3', 'm5', 'm6')})
_BOUNDS.update({k: (-100000, 100000) for k in ('Fx', 'Fz', 'Fn', 'Ft')})
_BOUNDS.update({k: (0, 100000) for k in ('Tab0', 'Tcd0', 'Tef0')})


def _tree(value, depth=0):
    if depth > 16:
        raise StorageError('Preset nesting exceeds the storage limit.')
    if isinstance(value, dict):
        if len(value) > 200 or any(not isinstance(k, str) or k in ('__proto__', 'prototype', 'constructor') for k in value):
            raise StorageError('Unsafe or excessive preset fields.')
        for child in value.values():
            _tree(child, depth + 1)
    elif isinstance(value, list):
        if len(value) > 200:
            raise StorageError('Too many preset records.')
        for child in value:
            _tree(child, depth + 1)
    elif type(value) in (int, float):
        if not math.isfinite(value) or abs(value) > 1e12:
            raise StorageError('Preset numbers must be finite and bounded.')
    elif isinstance(value, str):
        if len(value.encode('utf-16-le', errors='surrogatepass')) // 2 > 2000:
            raise StorageError('Preset string exceeds the storage limit.')
    elif value is not None and type(value) is not bool:
        raise StorageError('Preset values must be plain JSON.')


def _keys(value, required, label, extra=()):
    if not isinstance(value, dict) or not set(required) <= set(value) or set(value) - set(required) - set(extra):
        raise StorageError('Unknown or missing ' + label + ' fields.')


def _id(value):
    if not isinstance(value, str) or not re.fullmatch(r'preset-[a-zA-Z0-9-]{1,100}', value):
        raise StorageError('Invalid preset identifier.')


def _timestamp(value):
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3}Z', value):
        raise StorageError('Preset timestamps must use canonical UTC ISO milliseconds.')
    try:
        result = datetime.fromisoformat(value.replace('Z', '+00:00'))
        return result.timestamp()
    except (ValueError, OverflowError) as error:
        raise StorageError('Invalid preset timestamp.') from error


def _shell(values):
    view = dict.fromkeys('labels dimensions belts path loads axes grid indices beltMarkers'.split(), True)
    view['projection'] = 'side'
    return dict(schema='kinefold/project-v3', id='design-validation-shell', name='Validation shell',
                createdAt='2026-01-01T00:00:00Z', updatedAt='2026-01-01T00:00:00Z',
                params=copy.deepcopy(_PARAMS), view=view, **values)


def _params(params):
    value = _shell(dict(solverConfig=defaults()))
    value['params'] = params
    _project(value)
    for key, (lo, hi) in _BOUNDS.items():
        if not lo <= params[key] <= hi:
            raise StorageError(key + ' is outside its supported input range.')
    for a, b, length in (('ra', 'rb', 'L2'), ('rc', 'rd', 'L2'), ('re', 'rf', 'L3')):
        if params[a] + params[b] >= params[length]:
            raise StorageError('Pulley pitch circles overlap or touch.')
    if params['springEnabled']:
        # Reuse the exact standard-library finite-idler geometry, without creating
        # a dynamic model or imposing its positive-mass/monotone-heave restrictions.
        geometry = Model.__new__(Model)
        geometry.p = params
        geometry.lo, geometry.hi = params['te'] * R, params['tc'] * R
        geometry.route = geometry.exit_route()
        geometry.geometry(math.pi / 2, reference=True)
        for q in geometry.candidates(geometry.lo, geometry.hi):
            geometry.geometry(q)


def validate_sweep(value):
    _keys(value, ('maxJointSpeedRadS', 'jointAccelerationRadS2', 'samples'), 'sweep')
    speed, acceleration, samples = (value[k] for k in ('maxJointSpeedRadS', 'jointAccelerationRadS2', 'samples'))
    if type(speed) not in (int, float) or not math.isfinite(speed) or not 0 < speed <= 100 or type(acceleration) not in (int, float) or not math.isfinite(acceleration) or abs(acceleration) > 1000 or type(samples) not in (int, float) or not math.isfinite(samples) or samples != int(samples) or not 11 <= samples <= 101 or samples % 2 != 1:
        raise StorageError('Invalid finite speed/acceleration/odd sample sweep.')
    return copy.deepcopy(value)


def validate_record(record):
    _tree(record)
    _keys(record, ('id', 'kind', 'name', 'version', 'createdAt', 'updatedAt', 'values'), 'preset')
    _id(record['id'])
    name, version = record['name'], record['version']
    if not isinstance(name, str) or not name.strip() or len(name.encode('utf-16-le', errors='surrogatepass')) // 2 > 80 or any(ord(c) < 32 for c in name):
        raise StorageError('Preset name must contain 1–80 readable characters.')
    if type(version) not in (int, float) or not math.isfinite(version) or version != int(version) or not 1 <= version <= 2**53 - 1:
        raise StorageError('Preset version must be a positive safe integer.')
    if _timestamp(record['updatedAt']) < _timestamp(record['createdAt']):
        raise StorageError('Preset updated time precedes creation.')
    kind, v = record['kind'], record['values']
    if kind == 'suspension':
        _keys(v, ('params',), 'suspension values')
        _params(v['params'])
    elif kind == 'input':
        _keys(v, ('solverConfig',), 'input values', OPTIONAL)
        _project(_shell(v))
    elif kind == 'actuator':
        _keys(v, ('motorConfig', 'ratings', 'unknownFields', 'idealizeUnknowns', 'catalog'), 'actuator values')
        if v['motorConfig'] is None:
            raise StorageError('Explicit motorConfig must be a full configuration object.')
        Motor.resolve(v['motorConfig'])
        if v['motorConfig']['enabled'] is not True:
            raise StorageError('An actuator preset must contain an enabled motor model.')
        _keys(v['ratings'], RATING_KEYS, 'actuator ratings')
        for key, n in v['ratings'].items():
            if n is not None and (type(n) not in (int, float) or not math.isfinite(n) or n < 0 or (key == 'maxShaftRpm' and n == 0)):
                raise StorageError('Invalid actuator rating ' + key + '.')
        unknown = v['unknownFields']
        if not isinstance(unknown, list) or any(not isinstance(k, str) or k not in UNKNOWN_KEYS for k in unknown) or len(set(unknown)) != len(unknown):
            raise StorageError('Unknown passive fields must be distinct documented motor keys.')
        if type(v['idealizeUnknowns']) is not bool or any(v['motorConfig'][k] != 0 for k in unknown):
            raise StorageError('Unknown passive terms require zero placeholders and an explicit idealization flag.')
        _keys(v['catalog'], ('motorId', 'gearboxId', 'notes'), 'catalog')
        if any(not isinstance(x, str) for x in v['catalog'].values()):
            raise StorageError('Catalog provenance must contain strings.')
    elif kind == 'study':
        _keys(v, ('suspension', 'input', 'actuators', 'sweep'), 'study values')
        for key in ('suspension', 'input'):
            if validate_record(v[key])['kind'] != key:
                raise StorageError('Study requires a ' + key + ' snapshot.')
        if not isinstance(v['actuators'], list) or not 1 <= len(v['actuators']) <= 40:
            raise StorageError('Study requires 1–40 actuator snapshots.')
        for item in v['actuators']:
            if validate_record(item)['kind'] != 'actuator':
                raise StorageError('Study actuator snapshots cannot contain other kinds.')
        if len({r['id'] for r in v['actuators']}) != len(v['actuators']):
            raise StorageError('Study actuators must have distinct identifiers.')
        validate_sweep(v['sweep'])
    else:
        raise StorageError('Unknown preset kind.')
    return copy.deepcopy(record)


def validate_library(value):
    _tree(value)
    _keys(value, ('schema', 'revision', 'presets'), 'preset library')
    revision = value['revision']
    if value['schema'] != SCHEMA or type(revision) not in (int, float) or not math.isfinite(revision) or revision != int(revision) or not 0 <= revision <= 2**53 - 1 or not isinstance(value['presets'], list) or len(value['presets']) > 200:
        raise StorageError('Invalid preset library metadata.')
    records = [validate_record(r) for r in value['presets']]
    if len({r['id'] for r in records}) != len(records):
        raise StorageError('Duplicate preset identifiers.')
    return dict(schema=SCHEMA, revision=revision, presets=records)


def validate_bundle(value):
    _tree(value)
    _keys(value, ('schema', 'presets'), 'preset bundle')
    if value['schema'] != BUNDLE_SCHEMA:
        raise StorageError('Unsupported preset bundle.')
    return dict(schema=BUNDLE_SCHEMA, presets=validate_library(dict(schema=SCHEMA, revision=0, presets=value['presets']))['presets'])


class PresetService:
    """Use ProfileService's atomic writer and enclosing lock, independent disk file."""

    def __init__(self, owner):
        self.owner = owner
        self.file = owner.profiles / 'presets.json'

    def read(self):
        self.owner._folder(self.owner.profiles)
        if self.file.is_symlink():
            raise StorageError('Preset library cannot be a symbolic link.', 422)
        if not self.file.exists():
            return dict(schema=SCHEMA, revision=0, presets=[])
        if self.file.stat().st_size > MAX_BYTES:
            raise StorageError('Preset library exceeds 32 MiB.', 422)
        try:
            return validate_library(json.loads(self.file.read_text(encoding='utf-8')))
        except (ValueError, TypeError, KeyError, RecursionError) as error:
            raise StorageError('Preset library could not be read; original file retained: ' + str(error), 422) from error

    def handle(self, request):
        action = request.get('action')
        allowed = {'preset-list': (), 'preset-save': ('record',), 'preset-remove': ('id',), 'preset-import': ('bundle',)}
        if action not in allowed:
            raise StorageError('Unknown preset storage action.')
        _keys(request, ('action',) if action == 'preset-list' else ('action', 'expectedRevision', *allowed[action]), 'preset request')
        state = self.read()
        if action == 'preset-list':
            return dict(ok=True, **state)
        revision = request['expectedRevision']
        if type(revision) not in (int, float) or revision != state['revision'] or type(revision) is bool:
            raise StorageError('Presets changed in another tab. Reload before saving; your current edit was not written.', 409)
        if action == 'preset-save':
            record = validate_record(request['record'])
            old = next((r for r in state['presets'] if r['id'] == record['id']), None)
            if old:
                if old['kind'] == 'study':
                    raise StorageError('Saved studies are immutable; save a new study copy.', 409)
                if record['kind'] != old['kind'] or record['version'] != old['version'] + 1 or record['createdAt'] != old['createdAt']:
                    raise StorageError('Preset version or identity changed. Reload before saving.', 409)
            elif record['version'] != 1:
                raise StorageError('A new preset must start at version 1.')
            state['presets'] = [r for r in state['presets'] if r['id'] != record['id']] + [record]
        elif action == 'preset-remove':
            _id(request['id'])
            if not any(r['id'] == request['id'] for r in state['presets']):
                raise StorageError('Preset is no longer in this library.', 404)
            state['presets'] = [r for r in state['presets'] if r['id'] != request['id']]
        else:
            imported = validate_bundle(request['bundle'])['presets']
            now = datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
            for record in imported:
                record.update(id='preset-' + str(uuid.uuid4()), version=1, createdAt=now, updatedAt=now)
            state['presets'].extend(imported)
        state['revision'] += 1
        state = validate_library(state)
        self.owner._write(self.file, _encoded(state))
        return dict(ok=True, **state)
