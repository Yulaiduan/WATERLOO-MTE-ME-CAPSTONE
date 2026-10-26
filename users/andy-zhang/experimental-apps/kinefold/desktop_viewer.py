"""Display captured native Pymunk results in an independent Tk desktop window.

Invocation: app .venv Python desktop_viewer.py --request-stdin (service-owned
JSON envelope); --self-test adds a short genuine Tk playback/control smoke test.
Inputs are validated builder mm/deg/kg/N parameters, seconds/SI run controls and
optional terrain-contact contactConfig.
Outputs a visible Canvas, pause/scrub/replay controls, ignored readiness JSON and
logs. Pymunk integrates first; this is prerecorded results playback, not live
integration. Actual chassis frames drive an explicitly ideal condensed linkage.
Prescribed mode illustrates a wheel-height input. Terrain-contact mode renders
the actual collision mesh and integrated chassis/wheel bodies, with an ideal
condensed massless linkage. Neither mode establishes all-body/hardware fidelity.
The finite-idler cable follows captured pose/chassis and drives an illustrative
linear compression assembly. Its packaging dimensions do not alter either law.
"""
from __future__ import annotations

import argparse
import bisect
import json
import math
import os
from pathlib import Path
import sys
import time

from dynamic_model import Model, R
from dynamics import simulate

ROOT = Path(__file__).resolve().parent
BACKGROUND = '#f6f5ee'
INK = '#263c34'
SAGE = '#557b64'
GOLD = '#bb8b3c'
BLUE = '#527e98'


def is_contact(result):
    """Identify only the explicit contact result contract, without heuristics."""
    return result.get('schema') in ('kinefold/contact-v1','kinefold/contact-v2') and result.get('scope', {}).get('mode') == 'terrain-contact'


def simulate_snapshot(snapshot):
    """Dispatch the captured payload to its fixed genuine Pymunk backend."""
    request = {'engine': 'pymunk', 'params': snapshot['params'], 'runConfig': snapshot['runConfig'], **({'motorConfig':snapshot['motorConfig']} if 'motorConfig' in snapshot else {})}
    if (snapshot.get('contactConfig') or {}).get('mode') == 'terrain-contact':
        from contact_dynamics import simulate_contact
        return simulate_contact({**request, 'contactConfig': snapshot['contactConfig'], **({'caseConfig':snapshot['caseConfig']} if 'caseConfig' in snapshot else {})})
    return simulate(request)


def contact_mesh(result, frame):
    """Return actual translated collision polygons/base in world x/z mm.

    The frame's supplied collision vertices are authoritative. The infinite
    base's retained segment uses its returned offset; wheel Cx, wheel height
    and the prescribed-input function never enter this reconstruction.
    """
    if not is_contact(result):
        raise ValueError('Actual contact mesh requires a terrain-contact result.')
    offset = frame['terrainOffsetMm']
    polygons = [[(point[0], point[2]) for point in polygon]
                for polygon in frame['terrainPolygonsMm']]
    base = [(point[0] + offset[0], point[2] + offset[2])
            for point in result['terrain']['baseSegmentMm']]
    return polygons, base


def index_endpoint(point, radius, angle_degrees):
    """World x/z rim endpoint; returned angles start at −x, positive toward +z."""
    angle = math.radians(angle_degrees)
    return (point[0] - radius * math.cos(angle), point[2] + radius * math.sin(angle))


def spring_drawing(model, frame):
    """Exact captured-frame cable route plus a 1:1 compression assembly, mm.

    Reconstruct from returned theta2 and actual chassis translation, never the
    builder's initial pose. Illustrative seats, wire and clearance are drawing
    dimensions only; no new stiffness, inertia or package specification is used.
    """
    p = model.p
    if not p['springEnabled']:
        return dict(enabled=False, law='Spring disabled')
    z = model.spring(frame['theta2'] * R)
    A = frame.get('actualA', frame['A'])
    def world(v):
        x, height = model.rotate(v)
        return [A[0] - x, 0, A[2] + height]
    angle = math.pi / 2 - model.route['applied']
    outgoing = (p['Su'] + p['rs'] * math.cos(angle), p['Sv'] + p['rs'] * math.sin(angle))
    direction = (math.cos(model.route['applied']), -math.sin(model.route['applied']))
    psi = math.atan2(z['Q'][1] - p['Sv'], z['Q'][0] - p['Su'])
    arc = [world((p['Su'] + p['rs'] * math.cos(psi - z['wrap'] * i / 64),
                  p['Sv'] + p['rs'] * math.sin(psi - z['wrap'] * i / 64))) for i in range(65)] if p['rs'] else []
    delta = z['payout'] - model.reference_payout
    # Reuse exact route extrema, stable across all frames of this captured model.
    if not hasattr(model, '_spring_illustration_envelope'):
        payouts = [model.geometry(q)['payout'] for q in model.candidates(model.lo, model.hi)]
        model._spring_illustration_envelope = (min(payouts), max(payouts))
    minimum, maximum = model._spring_illustration_envelope
    length = 80 + maximum - z['payout']
    if not length > 0:
        raise ValueError('Pose exceeds illustrative compression assembly travel.')
    def along(distance, normal=0):
        return world((outgoing[0] + direction[0] * distance - direction[1] * normal,
                      outgoing[1] + direction[1] * distance + direction[0] * normal))
    fixed = along(125)
    moving = along(125 + length)
    fixed_bar = [along(125, -20), along(125, 20)]
    moving_bar = [along(125 + length, -20), along(125 + length, 20)]
    wire = [along(125 + 6 + (length - 12) * i / 168,
                  14 * math.sin(i / 168 * 14 * math.pi)) for i in range(169)]
    rails = [[along(125, n) for n in (-18, 18)],
             [along(125 + 80 + maximum - minimum, n) for n in (-18, 18)]]
    return dict(enabled=True, law='Ideal constant cable force' if p['springLaw'] == 'constant' else 'V4 linear coil',
                A=A, D=world(z['D']), Q=world(z['Q']), S=world((p['Su'], p['Sv'])),
                out=world(outgoing), remote=moving, fixedSeat=fixed, movingSeat=moving,
                fixedBar=fixed_bar, movingBar=moving_bar, wire=wire, rails=rails,
                assemblyPoints=fixed_bar + moving_bar + wire + rails[0] + rails[1],
                lengthMm=length, compressionMm=z['payout'] - minimum, strokeMm=maximum - minimum,
                arc=arc, forceN=z['force'], torqueNm=z['torque'], payoutMm=z['payout'],
                deltaMm=delta)


def floor_height(model, row, x, applied=True):
    """Spatial height in mm at world x; +x left, translated toward -x.

    The instantaneous wheel Cx is the spatial anchor, including finite ramps,
    initial delay and duplicate-time exact event sides. Baseline derives from
    returned wheel height rather than an invented ground offset.
    """
    config = model.c
    effective_t = row['t'] + (x - row['CxMm']) / config['inputSpeedMmS']
    side = 'left' if row.get('eventSide') == 'before' else 'right'
    height = model.input(effective_t, side)['applied' if applied else 'requested'] * 1000
    base = row['wheelZMm'] - model.p['rw'] - row['appliedInputMm']
    return base + height


def floor_points(model, row, x_min, x_max, applied=True):
    """Bounded exact corner samples plus smooth ramp samples, world mm pairs."""
    c = model.c
    speed = c['inputSpeedMmS']
    period = (c['inputPlateauMm'] + c['inputGapMm']) / speed
    high = c['inputPlateauMm'] / speed
    rise = c['inputRiseMm'] / speed
    lo = row['t'] + (x_min - row['CxMm']) / speed
    hi = row['t'] + (x_max - row['CxMm']) / speed
    samples = [(x_min, floor_height(model, row, x_min, applied)),
               (x_max, floor_height(model, row, x_max, applied))]
    first = max(0, math.floor((lo - c['inputDelayS']) / period) - 1)
    last = max(0, math.ceil((hi - c['inputDelayS']) / period) + 1)
    # UI complexity remains bounded even for otherwise-valid very short waves.
    if last - first > 1200:
        raise ValueError('Spatial profile is too dense for native playback (over 1200 visible cycles). Increase plateau/gap lengths or reduce the geometry span.')
    base = row['wheelZMm'] - model.p['rw'] - row['appliedInputMm']
    for cycle in range(first, last + 1):
        start = c['inputDelayS'] + cycle * period
        for offset in (0, high):
            event = start + offset
            x = row['CxMm'] + speed * (event - row['t'])
            if x_min < x < x_max:
                if not applied or rise == 0:
                    values = (0, c['inputHeightMm']) if offset == 0 else (c['inputHeightMm'], 0)
                    samples.extend((x, base + value) for value in values)
                else:
                    samples.append((x, base))
        if applied and rise > 0:
            for offset in (0, high - rise):
                for i in range(25):
                    event = start + offset + rise * i / 24
                    x = row['CxMm'] + speed * (event - row['t'])
                    if x_min < x < x_max:
                        samples.append((x, floor_height(model, row, x, applied)))
    return sorted(samples, key=lambda point: point[0])


def parent_alive(pid):
    """Read parent liveness without sending a Windows signal to another process."""
    if os.name == 'nt':
        import ctypes
        from ctypes import wintypes
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
        kernel.OpenProcess.restype = wintypes.HANDLE
        kernel.WaitForSingleObject.argtypes = (wintypes.HANDLE, wintypes.DWORD)
        kernel.CloseHandle.argtypes = (wintypes.HANDLE,)
        handle = kernel.OpenProcess(0x00100000, False, pid)
        if not handle:
            return False
        try:
            return kernel.WaitForSingleObject(handle, 0) == 258
        finally:
            kernel.CloseHandle(handle)
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


class StateWriter:
    def __init__(self, token):
        self.token = token
        self.path = ROOT / '.preview' / 'viewer-state.json'
        self.path.parent.mkdir(exist_ok=True)

    def write(self, **state):
        data = dict(token=self.token, **state)
        temporary = self.path.with_suffix('.tmp')
        temporary.write_text(json.dumps(data, allow_nan=False), encoding='utf-8')
        try:
            temporary.replace(self.path)
        except PermissionError:
            pass  # A status reader may briefly hold the old Windows file.


class PlaybackWindow:
    def __init__(self, result, name, writer, parent_pid, self_test=False):
        import tkinter as tk
        from tkinter import ttk
        self.tk, self.ttk = tk, ttk
        self.result, self.name, self.writer = result, name, writer
        self.parent_pid = parent_pid
        self.contact = is_contact(result)
        if self.contact:
            from contact_dynamics import validate_contact_request
            self.model = validate_contact_request({key: result[key] for key in ('engine', 'params', 'runConfig', 'contactConfig', 'caseConfig') if key in result})
        else:
            self.model = Model(result['params'], result['runConfig'])
        self.rows, self.frames = result['rows'], result['frames']
        self.times = [row['t'] for row in self.rows]
        self.index, self.playing = 0, True
        self.anchor = time.monotonic()
        self.anchor_t = self.times[0]
        self.last_report = 0
        self.self_test = self_test
        self.root = tk.Tk()
        self.root.title('Kinefold · Pymunk ' + ('terrain contact' if self.contact else 'prescribed input') + ' playback')
        self.root.geometry('1120x820')
        self.root.minsize(850, 640)
        self.root.configure(bg=BACKGROUND)
        self.root.protocol('WM_DELETE_WINDOW', self.close)
        style = ttk.Style(self.root)
        style.theme_use('clam')
        style.configure('TFrame', background=BACKGROUND)
        style.configure('TLabel', background=BACKGROUND, foreground=INK, font=('Segoe UI', 10))
        style.configure('TButton', font=('Segoe UI', 10), padding=(14, 7))
        header = ttk.Frame(self.root, padding=(24, 16, 24, 8))
        header.pack(fill='x')
        ttk.Label(header, text='KINEFOLD  /  NATIVE PYMUNK', foreground=SAGE,
                  font=('Segoe UI', 10, 'bold')).pack(anchor='w')
        ttk.Label(header, text='Terrain contact · results playback' if self.contact else 'Prescribed input · results playback', font=('Segoe UI', 23, 'bold')).pack(anchor='w')
        ttk.Label(header, text=name, font=('Segoe UI', 11)).pack(anchor='w', pady=(3, 6))
        ttk.Label(header, text=('Actual Pymunk chassis and free wheel · unilateral terrain collision · ideal massless linkage' if self.contact else
                               'Actual Pymunk chassis frames · ideal condensed linkage reconstruction · prescribed wheel input'),
                  wraplength=1040).pack(anchor='w')
        ttk.Label(header, text=('Integrated before playback. Returned world collision mesh and actual free-wheel spin; links are not separate rigid bodies.' if self.contact else
                               'Integrated before playback. No tire collision/contact or separate rigid link bodies.'),
                  foreground='#68736b').pack(anchor='w', pady=(3, 0))
        self.canvas = tk.Canvas(self.root, bg='#fdfcf7', highlightthickness=1,
                                highlightbackground='#dce0d5', height=430)
        self.canvas.pack(fill='both', expand=True, padx=24, pady=12)
        self.canvas.bind('<Configure>', lambda event: self.draw())
        controls = ttk.Frame(self.root, padding=(24, 0, 24, 0))
        controls.pack(fill='x')
        self.play_button = ttk.Button(controls, text='Pause', command=self.toggle)
        self.play_button.pack(side='left')
        ttk.Button(controls, text='Replay', command=self.replay).pack(side='left', padx=(8, 16))
        self.clock = ttk.Label(controls, font=('Segoe UI', 11, 'bold'))
        self.clock.pack(side='left')
        ttk.Label(controls, text='1× playback · +x ←  +z ↑', foreground=SAGE).pack(side='right')
        self.scrub = tk.Scale(self.root, from_=0, to=len(self.frames) - 1, orient='horizontal',
                              showvalue=False, resolution=1, command=self.seek, bg=BACKGROUND,
                              highlightthickness=0, troughcolor='#d9e0d3', activebackground=SAGE)
        self.scrub.pack(fill='x', padx=24, pady=(8, 4))
        self.readout = ttk.Label(self.root, font=('Segoe UI', 10), wraplength=1050)
        self.readout.pack(fill='x', padx=24, pady=(0, 6))
        ttk.Label(self.root, text=('Solid sage: actual collision terrain   ·   gold points: reported contacts   ·   terrain stationary for jump/landing; translates → (−x) for terrain stability' if self.contact else
                                 'Solid sage: applied profile   ·   dashed amber: requested sharp square   ·   floor moves → (−x) at the study speed'),
                  wraplength=1040).pack(fill='x', padx=24, pady=(0, 5))
        contact_config = result.get('contactConfig', {})
        scope_text = (f'Quarter model · chassis x/pitch locked · wheel m₆ {self.model.p["m6"]:g} kg · μ {contact_config["friction"]:g} · restitution {contact_config["restitution"]:g} · drive {contact_config["drive"]}'
                      if self.contact else 'Quarter model · chassis horizontal position and pitch locked · schematic chassis marker · no guide rods drawn')
        ttk.Label(self.root, text=scope_text,
                  foreground='#68736b', wraplength=1040).pack(fill='x', padx=24, pady=(0, 15))
        self._bounds()
        self.draw()
        self.root.after(30, self.tick)
        self.root.after(500, self.check_parent)
        if self_test:
            self.root.after(400, self.exercise)

    def _bounds(self):
        keys = ('actualA', 'B', 'actualC') if self.contact else ('A', 'B', 'C')
        points = [frame[key] for frame in self.frames for key in keys]
        for frame in self.frames:
            spring = spring_drawing(self.model, frame)
            if spring['enabled']:
                points.extend([spring['D'], spring['S'], *spring['assemblyPoints']])
        radius = self.model.p['rw']
        xs = [point[0] for point in points]
        zs = [point[2] for point in points]
        width = max(900, max(xs) - min(xs) + 2 * radius + 300)
        center = (min(xs) + max(xs)) / 2
        self.bounds = (center - width / 2, center + width / 2,
                       min(-90, min(zs) - radius - 50), max(zs) + 225)
        # Check the draw budget before entering Tk callbacks. Never replace a
        # dense sharp square with a misleading interpolated/aliased waveform.
        if self.contact:
            # Inspect returned terrain only. Contact runs have no wheel-height law.
            terrain_z = [point[2] for polygon in self.result['terrain']['polygonsMm'] for point in polygon]
            terrain_z += [point[2] for point in self.result['terrain']['baseSegmentMm']]
            self.bounds = (self.bounds[0], self.bounds[1], min(self.bounds[2], min(terrain_z) - 50),
                           max(self.bounds[3], max(terrain_z) + 50))
            contact_mesh(self.result, self.frames[0])
        else:
            floor_points(self.model, self.rows[0], self.bounds[0], self.bounds[1])

    def project(self, x, z):
        x0, x1, z0, z1 = self.bounds
        width, height = max(1, self.canvas.winfo_width()), max(1, self.canvas.winfo_height())
        scale = min((width - 80) / (x1 - x0), (height - 60) / (z1 - z0))
        return (width / 2 - (x - (x0 + x1) / 2) * scale,
                height / 2 - (z - (z0 + z1) / 2) * scale)

    def line(self, points, **kwargs):
        coords = [value for x, z in points for value in self.project(x, z)]
        if len(coords) >= 4:
            self.canvas.create_line(*coords, **kwargs)

    def circle(self, point, radius, **kwargs):
        x, z = point[0], point[2]
        a, b = self.project(x - radius, z + radius), self.project(x + radius, z - radius)
        self.canvas.create_oval(*a, *b, **kwargs)

    def draw(self):
        if not hasattr(self, 'bounds'):
            return
        canvas, p = self.canvas, self.model.p
        canvas.delete('all')
        row, frame = self.rows[self.index], self.frames[self.index]
        x0, x1, z0, z1 = self.bounds
        # World-calibrated understated grid, never a vertical guide constraint.
        for x in range(math.ceil(x0 / 100) * 100, math.floor(x1 / 100) * 100 + 1, 100):
            self.line([(x, z0), (x, z1)], fill='#eef0e8')
        for z in range(math.ceil(z0 / 100) * 100, math.floor(z1 / 100) * 100 + 1, 100):
            self.line([(x0, z), (x1, z)], fill='#eef0e8')
        if self.contact:
            polygons, base = contact_mesh(self.result, frame)
            for polygon in polygons:
                coords = [value for x, z in polygon for value in self.project(x, z)]
                canvas.create_polygon(*coords, fill='#e4eadd', outline=SAGE, width=2)
            self.line(base, fill=SAGE, width=3)
        else:
            applied = floor_points(self.model, row, x0, x1)
            polygon = applied + [(x1, z0), (x0, z0)]
            coords = [value for x, z in polygon for value in self.project(x, z)]
            canvas.create_polygon(*coords, fill='#e4eadd', outline='')
            self.line(floor_points(self.model, row, x0, x1, False), fill=GOLD, width=2, dash=(5, 4))
            self.line(applied, fill=SAGE, width=3)
        A, B, C = (frame['actualA'], frame['B'], frame['actualC']) if self.contact else (frame['A'], frame['B'], frame['C'])
        self.line([(A[0], A[2]), (B[0], B[2])], fill=INK, width=9, capstyle='round')
        self.line([(B[0], B[2]), (C[0], C[2])], fill=BLUE, width=8, capstyle='round')
        self.circle(C, p['rw'], outline=INK, width=3, fill='#faf9f0')
        # Match the builder's index gauge after mounting-pitch rotation.
        angle = frame['wheelAngle'] if self.contact else frame['wheelAngle'] - p['alpha']
        self.line([(C[0], C[2]), index_endpoint(C, p['rw'], angle)], fill='#8b9b8d', width=2)
        for point, pulleys in ((A, ('a', 'c')), (B, ('b', 'd', 'e')), (C, ('f',))):
            for radius in sorted({p['r' + key] for key in pulleys}, reverse=True):
                self.circle(point, radius, outline=SAGE, width=2, fill='#e9eee2')
            if self.contact:
                for key in pulleys:
                    self.line([(point[0], point[2]), index_endpoint(point, p['r' + key], frame['indexAnglesDeg'][key] - p['alpha'])],
                              fill=GOLD if key in ('c', 'd', 'e') else BLUE, width=2)
            self.circle(point, 5, fill=INK, outline='')
        spring = spring_drawing(self.model, frame)
        if spring['enabled']:
            pair = lambda point: (point[0], point[2])
            self.line([pair(spring[key]) for key in ('A', 'D')], fill=GOLD, width=3)
            self.line([pair(spring[key]) for key in ('D', 'Q')], fill=GOLD, width=2)
            self.line([pair(point) for point in spring['arc']], fill=GOLD, width=3)
            self.circle(spring['S'], p['rs'], outline=GOLD, width=1)
            self.line([pair(spring[key]) for key in ('out', 'remote')], fill=GOLD, width=1.4)
            for index in (0, 1):
                self.line([pair(spring['rails'][0][index]), pair(spring['rails'][1][index])],
                          fill='#d9c8a8', width=1)
            self.line([pair(point) for point in spring['fixedBar']], fill=GOLD, width=3,
                      tags=('spring-fixed-seat',))
            self.line([pair(point) for point in spring['movingBar']], fill=GOLD, width=3,
                      tags=('spring-moving-seat',))
            self.line([pair(point) for point in spring['wire']], fill=GOLD, width=1.3,
                      tags=('spring-compression-body',))
        if self.contact:
            for point in frame['contactPointsMm']:
                self.circle(point, 4, fill=GOLD, outline=INK)
        if self.contact and self.result.get('caseConfig',{}).get('undersideOffsetMm') is not None:
            offset=self.result['caseConfig']['undersideOffsetMm']
            underside=[A[0],0,A[2]-offset]
            self.line([(A[0],A[2]),(underside[0],underside[2])],fill='#ad6054',dash=(3,3))
            self.circle(underside,5,outline='#ad6054',width=2)
        ax, az = self.project(A[0], A[2])
        canvas.create_rectangle(ax - 54, az - 23, ax + 54, az - 7, fill=SAGE, outline=INK)
        canvas.create_text(ax, az - 35, text=f'Chassis m₁ · {p["m1"]:g} kg', fill=INK, font=('Segoe UI', 10, 'bold'))
        for key, point, offset in (('A', A, (17, 10)), ('B', B, (17, -12)), ('C', C, (16, 17))):
            px, py = self.project(point[0], point[2])
            canvas.create_text(px + offset[0], py + offset[1], text=key, fill=INK, font=('Segoe UI', 10, 'bold'))
        canvas.create_text(17, 17, anchor='nw', text='WORLD x–z  /  100 mm grid', fill='#68736b', font=('Segoe UI', 9))
        canvas.create_text(17, 37, anchor='nw', text='Actual chassis / wheel bodies + ideal linkage' if self.contact else 'Actual chassis body + ideal linkage', fill=INK, font=('Segoe UI', 10))
        canvas.create_text(17, 58, anchor='nw', text=(f'{spring["law"]} · Fₛ {spring["forceN"]:.2f} N · τₛ {spring["torqueNm"]:.2f} N·m' if spring['enabled'] else 'Spring disabled · no spring force'), fill=GOLD, font=('Segoe UI', 10))
        if spring['enabled']:
            canvas.create_text(17, 79, anchor='nw', text=f'Compression spring · illustrative size · 1:1 cable stroke · ΔL₉₀ {spring["deltaMm"]:.2f} mm', fill='#68736b', font=('Segoe UI', 9))
        canvas.create_text(17, canvas.winfo_height() - 17, anchor='sw', text='← +x     +z ↑     +y toward you', fill=SAGE, font=('Segoe UI', 10, 'bold'))
        event = ' · ' + row['eventSide'] + ' exact jump' if row.get('eventSide') else ''
        self.clock.configure(text=f'{row["t"]:.3f} / {self.times[-1]:.3f} s  ·  frame {self.index + 1}/{len(self.frames)}{event}')
        if self.contact:
            slip = f'{frame["slipMmS"]:.2f} mm/s' if frame.get('slipMmS') is not None else '— / no sampled contact'
            self.readout.configure(text=f'Chassis z {A[2]:.3f} mm   ·   wheel z {C[2]:.3f} mm   ·   θ₂ {frame["theta2"]:.3f}°   ·   actual spin {frame["wheelAngle"]:.2f}°   ·   normal / tangent {frame["contactNormalForceN"]:.2f} / {frame["contactTangentialForceN"]:.2f} N   ·   slip {slip}   ·   gap / penetration {frame["gapMm"]:.3f} / {frame["penetrationMm"]:.3f} mm   ·   phase {row.get("controllerPhase","terrain")}')
        else:
            self.readout.configure(text=f'Chassis z {row["chassisZMm"]:.3f} mm   ·   Δz {row["chassisZMm"] - self.rows[0]["chassisZMm"]:+.3f} mm   ·   θ₂ {row["theta2"]:.3f}°   ·   requested / applied {row["requestedInputMm"]:.1f} / {row["appliedInputMm"]:.1f} mm   ·   input reaction {row["inputReactionN"]:.2f} N')

    def report(self):
        row = self.rows[self.index]
        self.writer.write(state='ready', name=self.name, frameIndex=self.index,
                          frameCount=len(self.frames), playing=self.playing, t=row['t'],
                          eventSide=row.get('eventSide'), designHash=self.result['designHash'],
                          engine='pymunk', playback='prerecorded-results',
                          mode='terrain-contact' if self.contact else 'prescribed-input',
                          termination=self.result['diagnostics']['termination'],
                          selfTestPassed=getattr(self, 'self_test_passed', False))

    def toggle(self):
        if not self.playing and self.index == len(self.frames) - 1:
            self.replay()
            return
        self.playing = not self.playing
        self.anchor, self.anchor_t = time.monotonic(), self.times[self.index]
        self.play_button.configure(text='Pause' if self.playing else 'Play')
        self.report()

    def replay(self):
        self.index, self.playing = 0, True
        self.anchor, self.anchor_t = time.monotonic(), self.times[0]
        self.scrub.set(0)
        self.play_button.configure(text='Pause')
        self.draw()
        self.report()

    def seek(self, value):
        index = int(float(value))
        if index != self.index:
            self.index, self.playing = index, False
            self.play_button.configure(text='Play')
            self.draw()
            self.report()

    def tick(self):
        if self.playing:
            target = self.anchor_t + time.monotonic() - self.anchor
            self.index = min(len(self.frames) - 1, max(0, bisect.bisect_right(self.times, target) - 1))
            # Scale command is asynchronous; equality in seek avoids pausing playback.
            self.scrub.set(self.index)
            if self.index == len(self.frames) - 1:
                self.playing = False
                self.play_button.configure(text='Play')
            self.draw()
        if time.monotonic() - self.last_report > .2:
            self.report()
            self.last_report = time.monotonic()
        self.root.after(30, self.tick)

    def check_parent(self):
        if not parent_alive(self.parent_pid):
            self.close()
        else:
            self.root.after(500, self.check_parent)

    def exercise(self):
        try:
            assert self.index > 0, 'Playback failed to advance.'
            self.toggle()
            assert not self.playing
            self.seek(len(self.frames) - 1)
            assert self.index == len(self.frames) - 1 and not self.playing
            self.replay()
            assert self.index == 0 and self.playing
            self.self_test_passed = True
            self.report()
            self.root.after(500, self.close)
        except AssertionError as error:
            self.writer.write(state='error', error='Native self-test: ' + str(error))
            self.root.destroy()
            raise

    def close(self):
        self.writer.write(state='closed', name=self.name, selfTestPassed=getattr(self, 'self_test_passed', False))
        self.root.destroy()

    def run(self):
        self.root.update_idletasks()
        self.report()
        self.root.mainloop()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--request-stdin', action='store_true', required=True)
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    writer = None
    try:
        envelope = json.loads(sys.stdin.buffer.read(128 * 1024 + 1))
        if not isinstance(envelope, dict) or set(envelope) != {'request', 'token', 'parentPid'}:
            raise ValueError('Invalid service envelope.')
        if not isinstance(envelope['token'], str) or not isinstance(envelope['parentPid'], int):
            raise ValueError('Invalid service ownership.')
        from viewer_service import ViewerService
        snapshot = ViewerService._validate(envelope['request'])
        if snapshot is None:
            raise ValueError('Native child requires an open snapshot.')
        writer = StateWriter(envelope['token'])
        writer.write(state='starting', name=snapshot['name'])
        result = simulate_snapshot(snapshot)
        window = PlaybackWindow(result, snapshot['name'], writer, envelope['parentPid'], args.self_test)
        window.run()
        return 0
    except Exception as error:
        if writer is not None:
            writer.write(state='error', error=str(error))
        print('Native playback failed: ' + str(error), file=sys.stderr, flush=True)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
