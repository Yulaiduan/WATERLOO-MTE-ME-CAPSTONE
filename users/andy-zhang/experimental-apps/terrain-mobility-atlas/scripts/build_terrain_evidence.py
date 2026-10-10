"""Retrieve a DEM transect and build labeled terrain evidence examples.

Run: python scripts/build_terrain_evidence.py from app root.
Inputs: cached/public USGS responses and chosen SI terrain envelopes (m, grades).
Outputs: data/terrain CSV/provenance and ignored artifacts/terrain-evidence plots.
Requires NumPy, SciPy, Matplotlib and requests; retrieval may use the network.
DEM scale and synthetic profiles do not establish wheel-scale surveyed terrain
or hardware performance. Original large inputs remain in the archive package.
"""
from pathlib import Path
import concurrent.futures
import csv
import hashlib
import json
import math

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import requests
from scipy.integrate import quad, cumulative_trapezoid

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data' / 'terrain'
OUT = ROOT / 'artifacts' / 'terrain-evidence'
RAW = DATA / 'sources'
for path in (DATA, OUT, RAW):
    path.mkdir(parents=True, exist_ok=True)
BASE = 'https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer'


def write_json(path, obj):
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def fetch_json(path, url, params):
    if path.exists():
        return json.loads(path.read_text(encoding='utf-8'))
    response = requests.get(url, params=params, timeout=45)
    response.raise_for_status()
    result = response.json()
    if 'error' in result:
        raise RuntimeError(result['error'])
    write_json(path, result)
    write_json(path.with_suffix('.request.json'), {'url': url, 'params': params, 'retrieved_client_date': '2026-10-02'})
    return result


def meridian_points(distances, lat0=38.60, lon0=-78.35):
    # WGS84 meridional arc, solved numerically, for a due-north transect.
    a, e2 = 6378137.0, 6.6943799901413165e-3
    phi0 = math.radians(lat0)
    def radius(phi):
        return a * (1 - e2) / (1 - e2 * math.sin(phi) ** 2) ** 1.5
    points = []
    for distance in distances:
        phi = phi0 + float(distance) / radius(phi0)
        for _ in range(3):
            arc = quad(radius, phi0, phi, epsabs=1e-7)[0]
            phi -= (arc - distance) / radius(phi)
        assert abs(quad(radius, phi0, phi)[0] - distance) < 1e-5
        points.append([lon0, math.degrees(phi)])
    return points


def retrieve_measured():
    distances = np.arange(1001, dtype=float)
    points = meridian_points(distances)
    service = fetch_json(RAW / 'usgs-service.json', BASE, {'f': 'json'})
    # Lock the identified 1 m source, rather than silently mixing resolutions.
    rule = {'mosaicMethod': 'esriMosaicLockRaster', 'lockRasterIds': [75304], 'mosaicOperation': 'MT_FIRST'}
    def batch(start):
        subset = points[start:start + 100]
        params = {'f': 'json', 'geometryType': 'esriGeometryMultipoint',
                  'geometry': json.dumps({'points': subset, 'spatialReference': {'wkid': 4326}}),
                  'mosaicRule': json.dumps(rule), 'returnFirstValueOnly': 'true',
                  'interpolation': 'RSP_BilinearInterpolation', 'outFields': '*',
                  'pixelSize': json.dumps({'x': 1, 'y': 1, 'spatialReference': {'wkid': 3857}})}
        result = fetch_json(RAW / f'usgs-samples-{start:04d}.json', BASE + '/getSamples', params)
        samples = result.get('samples', [])
        assert len(samples) == len(subset), (start, len(samples), len(subset))
        samples = sorted(samples, key=lambda s: s['locationId'])
        assert [s['locationId'] for s in samples] == list(range(len(subset)))
        for point, sample in zip(subset, samples):
            assert abs(sample['location']['x'] - point[0]) < 1e-7
            assert abs(sample['location']['y'] - point[1]) < 1e-7
            assert sample['rasterId'] == 75304
            assert sample['resolution'] == 1
        return samples
    starts = list(range(0, len(points), 100))
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        batches = list(executor.map(batch, starts))
    samples = [sample for batch_samples in batches for sample in batch_samples]
    heights = np.array([float(sample['value']) for sample in samples])
    assert np.isfinite(heights).all()
    assert heights.min() > -100
    attributes = samples[0]['attributes']
    relative = heights - heights[0]
    # Grade reported over 10 m baselines, not noisy one-pixel derivatives.
    grade = np.full(len(distances), np.nan)
    grade[5:-5] = 100 * (heights[10:] - heights[:-10]) / 10
    for length in (100, 1000):
        mask = distances <= length
        with (DATA / f'usgs-shenandoah-transect-{length}m.csv').open('w', newline='', encoding='utf-8') as stream:
            writer = csv.writer(stream)
            writer.writerow(['distance_m', 'longitude_deg', 'latitude_deg', 'elevation_navd88_m', 'relative_elevation_m', 'grade_10m_baseline_percent', 'provenance'])
            for index in np.where(mask)[0]:
                writer.writerow([distances[index], *points[index], heights[index], relative[index], '' if not np.isfinite(grade[index]) else grade[index], 'USGS_3DEP_1m_DEM_bilinear_sample'])
    summary = {'length_m': 1000, 'sample_count': len(samples), 'sample_interval_m': 1,
               'source_resolution_m': 1, 'net_elevation_change_m': float(relative[-1]),
               'elevation_range_m': float(np.ptp(heights)),
               'grade_10m_p05_percent': float(np.nanpercentile(grade, 5)),
               'grade_10m_p95_percent': float(np.nanpercentile(grade, 95))}
    provenance = {'evidence_type': 'observed_dem_derived_profile', 'retrieved_client_date': '2026-10-02',
                  'site': 'Shenandoah area, Virginia; illustrative northward off-road transect',
                  'start_wgs84': points[0], 'end_wgs84': points[-1], 'source_attributes': attributes,
                  'service_url': BASE, 'service_description': service['serviceDescription'],
                  'selection': 'LockRaster source 75304; bilinear samples of a 1 m bare-earth DEM',
                  'path_method': 'WGS84 meridional arc integrated numerically; due north, horizontal ground distance',
                  'vertical_accuracy_m': None, 'biome_classification': None,
                  'limitations': ['Not a surveyed trail or traversable route.', 'One site does not define a biome distribution.',
                                  'Source-specific vertical accuracy is not established here.',
                                  '1 m DEM cannot establish 50–300 mm roots, rock shapes, or suspension-scale RMS.',
                                  '100 m file is the first 100 m of the same 1 km transect.'], 'summary': summary}
    write_json(DATA / 'usgs-shenandoah-provenance.json', provenance)
    fig, axes = plt.subplots(3, 1, figsize=(12, 9), layout='constrained')
    axes[0].plot(distances, relative, color='#176c67', linewidth=1.8)
    axes[0].axvspan(0, 100, color='#eab76d', alpha=.22, label='100 m detail below')
    axes[0].set(title='Observed DEM profile · 1 km transect', xlabel='Horizontal distance (m)', ylabel='Elevation relative to start (m)')
    axes[0].legend()
    axes[1].plot(distances[:101], relative[:101], color='#176c67', linewidth=1.8)
    axes[1].set(title='Same transect · first 100 m', xlabel='Horizontal distance (m)', ylabel='Elevation relative to start (m)')
    axes[2].plot(distances, grade, color='#425f9c')
    axes[2].axhline(0, color='#888', linewidth=.8)
    axes[2].set(title='Grade calculated over a 10 m baseline', xlabel='Horizontal distance (m)', ylabel='Grade (%)')
    for axis in axes:
        axis.grid(alpha=.2)
    fig.suptitle('USGS 3DEP · VA_Shenandoah_2014 · source resolution 1 m\nDEM-derived terrain shape; centimetre-scale obstacles are unresolved', fontsize=13)
    fig.savefig(OUT / 'measured-transect.png', dpi=160)
    plt.close(fig)
    return summary


def generated_examples():
    catalog = json.loads((DATA / 'terrain-archetypes.json').read_text(encoding='utf-8'))
    presets = catalog['periodic_presets_from_chat']['presets']
    selected = [('Gravel', 3), ('Maintained trail', 8), ('Boreal forest', 10)]
    x = np.arange(0, 1000 + .005, .01)
    outputs = []
    fig, axes = plt.subplots(3, 3, figsize=(16, 10), layout='constrained')
    for row, (name, grade) in enumerate(selected):
        preset = next(p for p in presets if p['name'] == name)
        rms = preset['roughness_rms_mm'] / 1000
        wavelength = preset['roughness_wavelength_m']
        spacing = preset['obstacle_spacing_m']
        amplitude = math.sqrt(2) * rms
        # Roughness, grade, and obstacles remain separately exported.
        roughness = amplitude * np.sin(2 * np.pi * x / wavelength)
        baseline = grade / 100 * x
        obstacles = np.zeros_like(x)
        width = .30  # assumed FWHM; not specified by the source preset
        sigma = width / (2 * math.sqrt(2 * math.log(2)))
        positions = np.arange(spacing / 2, 1000, spacing)
        for position in positions:
            left = max(0, int((position - 4 * sigma) / .01))
            right = min(len(x), int((position + 4 * sigma) / .01) + 1)
            obstacles[left:right] += preset['obstacle_height_mm'] / 1000 * np.exp(-.5 * ((x[left:right] - position) / sigma) ** 2)
        total = baseline + roughness + obstacles
        slug = name.lower().replace(' ', '-')
        for length in (100, 1000):
            with (DATA / f'synthetic-{slug}-{length}m.csv').open('w', newline='', encoding='utf-8') as stream:
                writer = csv.writer(stream)
                writer.writerow(['distance_m', 'relative_elevation_m', 'grade_component_m', 'roughness_component_m', 'obstacle_component_m', 'provenance'])
                for i in range(int(length / .01) + 1):
                    writer.writerow([f'{x[i]:.2f}', f'{total[i]:.6f}', f'{baseline[i]:.6f}', f'{roughness[i]:.6f}', f'{obstacles[i]:.6f}', 'synthetic_chat_design_preset'])
        detail = {**preset, 'grade_percent': grade, 'grade_evidence': 'chosen baseline test point within source design envelope; not total instantaneous slope',
                  'obstacle_fwhm_m': width, 'width_evidence': 'added engineering assumption',
                  'generator': 'constant grade + sine roughness + equally spaced Gaussian obstacles',
                  'evidence_type': 'synthetic_engineering_cycle', 'sampling_m': .01,
                  'sine_peak_amplitude_mm': amplitude * 1000,
                  'realized_roughness_rms_mm_1km': float(np.std(roughness) * 1000),
                  'combined_residual_min_mm': float(np.min(roughness + obstacles) * 1000),
                  'combined_residual_max_mm': float(np.max(roughness + obstacles) * 1000),
                  'obstacle_count_1km': len(positions),
                  'cycle_count_100m': 100 / wavelength, 'cycle_count_1km': 1000 / wavelength,
                  'roughness_definition': 'RMS of the sine component about its mean; excludes grade and discrete obstacles',
                  'interpretation': 'Illustrative deterministic test; not a measured biome profile or inferred periodicity.'}
        write_json(DATA / f'synthetic-{slug}-provenance.json', detail)
        outputs.append(detail)
        axes[row, 0].plot(x[::10], total[::10], color='#176c67', linewidth=1)
        axes[row, 0].plot(x, baseline, '--', color='#bc763a', linewidth=1)
        axes[row, 0].set(title=f'{name} · 1 km · baseline grade {grade}%', xlabel='Distance (m)', ylabel='Total elevation (m)')
        mask = x <= 100
        residual = roughness + obstacles
        axes[row, 1].plot(x[mask], residual[mask] * 1000, color='#176c67', linewidth=.75)
        axes[row, 1].set(title='First 100 m · grade removed', xlabel='Distance (m)', ylabel='Height above grade (mm)')
        mask = x <= 5
        axes[row, 2].plot(x[mask], roughness[mask] * 1000, label='Roughness sine', color='#425f9c')
        axes[row, 2].plot(x[mask], obstacles[mask] * 1000, label='Obstacle layer', color='#bc763a')
        axes[row, 2].plot(x[mask], residual[mask] * 1000, label='Combined', color='#176c67', alpha=.65)
        axes[row, 2].set(title=f'5 m detail · RMS {rms*1000:g} mm · λ {wavelength:g} m', xlabel='Distance (m)', ylabel='Height above grade (mm)')
        axes[row, 2].legend(fontsize=8)
        for axis in axes[row]:
            axis.grid(alpha=.2)
    fig.suptitle('Generated engineering cycles from the chat presets\nGrade and obstacle width are added assumptions; all profiles are synthetic', fontsize=14)
    fig.savefig(OUT / 'synthetic-cycles.png', dpi=160)
    plt.close(fig)
    write_json(DATA / 'synthetic-example-summary.json', outputs)
    return outputs


def download_reference():
    # USFS reference cited by the original chat; retain its original bytes.
    url = 'https://www.fs.usda.gov/eng/pubs/pdfpubs/pdf11232804/pdf11232804dpi100.pdf'
    path = RAW / 'usfs-trail-design-guide.pdf'
    if not path.exists():
        response = requests.get(url, timeout=45)
        response.raise_for_status()
        assert response.content.startswith(b'%PDF')
        path.write_bytes(response.content)
    write_json(RAW / 'usfs-trail-design-guide.provenance.json', {'url': url, 'retrieved_client_date': '2026-10-02',
                                                            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})


def slope_cycle():
    x = np.arange(0, 1000 + .05, .1)
    phase = x % 100
    grade = np.full_like(x, .08)
    rise = (phase >= 40) & (phase < 45)
    plateau = (phase >= 45) & (phase < 65)
    fall = (phase >= 65) & (phase < 70)
    grade[rise] += .17 * .5 * (1 - np.cos(np.pi * (phase[rise] - 40) / 5))
    grade[plateau] = .25
    grade[fall] += .17 * .5 * (1 + np.cos(np.pi * (phase[fall] - 65) / 5))
    height = cumulative_trapezoid(grade, x, initial=0)
    assert abs(height[1000] - 12.25) < 1e-6
    assert abs(height[-1] - 122.5) < 1e-6
    for length in (100, 1000):
        with (DATA / f'synthetic-class3-slope-cycle-{length}m.csv').open('w', newline='', encoding='utf-8') as stream:
            writer = csv.writer(stream)
            writer.writerow(['distance_m', 'relative_elevation_m', 'baseline_grade_percent', 'provenance'])
            for i in range(int(length / .1) + 1):
                writer.writerow([f'{x[i]:.1f}', f'{height[i]:.6f}', f'{grade[i]*100:.6f}', 'synthetic_USFS_Class3_benchmark_cycle'])
    write_json(DATA / 'synthetic-class3-slope-cycle-provenance.json', {
        'evidence_type': 'synthetic_engineering_cycle', 'benchmark_source': 'usfs-trail-benchmarks.json',
        'published_constraints': {'target_grade_percent': [5, 15], 'short_pitch_max_percent': 25, 'max_pitch_density_percent': [15, 30]},
        'chosen_assumptions': {'cycle_length_m': 100, 'baseline_grade_percent': 8,
                               'maximum_grade_percent': 25, 'maximum_grade_plateau_m': 20,
                               'transition_length_m_each': 5, 'transition_shape': 'raised cosine'},
        'summary': {'mean_grade_percent': 12.25, 'ascent_per_cycle_m': 12.25, 'ascent_1km_m': 122.5,
                    'maximum_grade_fraction_percent': 20, 'repeats_1km': 10},
        'interpretation': 'The GRADE pattern repeats every 100 m; elevation accumulates without a reset. Segment lengths and periodicity are chosen assumptions, not observations.'})
    fig, axes = plt.subplots(3, 1, figsize=(12, 8), layout='constrained')
    axes[0].plot(x, height, color='#176c67')
    axes[0].set(title='1 km · ten grade cycles · total climb 122.5 m', ylabel='Elevation (m)', xlabel='Distance (m)')
    mask = x <= 100
    axes[1].plot(x[mask], height[mask], color='#176c67')
    axes[1].set(title='One 100 m cycle · climb 12.25 m', ylabel='Elevation (m)', xlabel='Distance (m)')
    axes[2].axhspan(5, 15, color='#176c67', alpha=.12, label='Published target grade: 5–15%')
    axes[2].axhline(25, color='#bc763a', linestyle='--', label='Published short-pitch maximum: 25%')
    axes[2].plot(x[mask], grade[mask]*100, color='#425f9c', label='Chosen grade cycle')
    axes[2].set(title='8% baseline · 20 m at 25% · two 5 m transitions', ylabel='Grade (%)', xlabel='Distance (m)', ylim=(0, 29))
    axes[2].legend(fontsize=9, loc='lower right')
    for axis in axes:
        axis.grid(alpha=.2)
    fig.suptitle('Synthetic slope test constrained by the cited USFS ATV Class 3 guideline\nCycle length, baseline and transition geometry are explicit engineering assumptions', fontsize=12)
    fig.savefig(OUT / 'slope-cycle.png', dpi=160)
    plt.close(fig)


if __name__ == '__main__':
    measured = retrieve_measured()
    generated = generated_examples()
    slope_cycle()
    download_reference()
    print(json.dumps({'measured': measured, 'synthetic_examples': [{k: p[k] for k in ('name', 'roughness_rms_mm', 'roughness_wavelength_m', 'sine_peak_amplitude_mm', 'obstacle_count_1km')} for p in generated]}, indent=2))
