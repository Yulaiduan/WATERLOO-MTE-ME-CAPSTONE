"""Reproduce analytical quintic/block-clearance screening against a passive trace.

Run: python analyze_profile.py after python jon_single_leg_descent.py in this app.
Inputs: prior passive trace and explicit 0.1m wheel/step, 0.5m/s assumptions.
Outputs: ignored results/ PNG/PDF and numerical provenance/checks in SI units.
Limits: geometry and target screening, not new controlled dynamics or hardware.
"""
from pathlib import Path
import hashlib
import json
import os
import platform

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'results/2026-10-19-descent-profile'
OUT.mkdir(parents=True, exist_ok=True)
os.environ.setdefault('MPLCONFIGDIR', str(OUT / '.mpl-cache'))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ASSETS = OUT / 'assets'
ASSETS.mkdir(parents=True,exist_ok=True)
TRACE = ROOT / 'results/2026-10-18-jon-single-leg-descent/fixed-v05-b0/history.csv'
R, H, V, L = .1, .1, .5, .3
E0 = 2 * L * np.sin(np.deg2rad(135))


def blend(u):
    return u**3 * (10 + u * (-15 + 6*u))


def target(t, duration):
    u = np.clip(t / duration, 0, 1)
    d = H * blend(u)
    speed = H / duration * 30*u**2*(1-u)**2
    accel = H / duration**2 * 60*u*(1-u)*(1-2*u)
    return d, speed, accel


def duration_bound(u):
    # For h <= R: horizontal clearance needed for every requested drop.
    # T*u >= sqrt(2*R*d - d*d)/V, from circle/corner nonpenetration.
    d = H * blend(u)
    return np.sqrt(2*R*d - d*d) / (V*u)


def maximum_bound(count):
    u = np.linspace(1e-8, 1, count)
    index = int(np.argmax(duration_bound(u)))
    lo, hi = u[index-1], u[index+1]
    # Golden-section maximization around the maximum located by a full grid.
    ratio = (np.sqrt(5)-1)/2
    c, d = hi-ratio*(hi-lo), lo+ratio*(hi-lo)
    for _ in range(90):
        if duration_bound(c) > duration_bound(d):
            hi, d = d, c
            c = hi-ratio*(hi-lo)
        else:
            lo, c = c, d
            d = lo+ratio*(hi-lo)
    point = (lo+hi)/2
    return float(duration_bound(point)), float(point)


def main():
    history = np.genfromtxt(TRACE, delimiter=',', names=True)
    reltime = history['time_s'] - history['edge_time_s']
    landing = int(np.flatnonzero((history['floor_load_N'] > 1) & (reltime > -.1))[0])
    tmin, ucrit = maximum_bound(100001)
    check_tmin, _ = maximum_bound(20001)
    assert abs(tmin-check_tmin) < 1e-11
    assert abs(reltime[landing]-.2055) < 1e-8

    targets = []
    for duration in [.1, .2, .3, .4]:
        t = np.linspace(0, duration, 100001)
        drop, speed, acceleration = target(t, duration)
        q = np.pi - np.arcsin((E0+drop)/(2*L))
        jac = 2*L*np.cos(q)
        qdot = speed/jac
        qddot = (acceleration + 2*L*np.sin(q)*qdot**2)/jac
        targets.append(dict(duration_s=duration,
            peak_speed_mps=1.875*H/duration,
            peak_acceleration_mps2=10/np.sqrt(3)*H/duration**2,
            peak_jerk_mps3=60*H/duration**3,
            peak_joint_speed_radps=float(np.max(np.abs(qdot))),
            peak_joint_acceleration_radps2=float(np.max(np.abs(qddot))),
            clears_block_geometrically=bool(duration >= tmin)))

    # Independent signed-distance check of an example feasible command.
    t = np.linspace(0, R/V, 100001)
    drop, _, _ = target(t, .4)
    radial_clearance = np.sqrt((V*t)**2+(R-drop)**2)-R
    assert radial_clearance.min() > -1e-12
    drop_fast, _, _ = target(t, .2)
    radial_clearance_fast = np.sqrt((V*t)**2+(R-drop_fast)**2)-R
    assert radial_clearance_fast.min() < -.01

    results = dict(status='analytical screening; no new dynamics or hardware results',
        inputs=dict(wheel_radius_m=R, block_height_m=H, forward_speed_mps=V,
                    link_length_m=L, initial_hip_angle_deg=135,
                    fixed_hip=True, edge_start_time_s=0, quintic_rest_to_rest=True),
        corner_clearance_duration_bound_s=tmin, critical_normalized_time=ucrit,
        corner_clearance_bound_grid_refinement_difference_s=abs(tmin-check_tmin),
        passive_trace=dict(edge_to_floor_s=float(reltime[landing]),
            precontact_downward_speed_mps=float(-history['wheel_vz_mps'][landing-1]),
            sha256=hashlib.sha256(TRACE.read_bytes()).hexdigest(), path=str(TRACE.relative_to(ROOT))),
        targets=targets,
        example_at_100ms=dict(fast_quintic_drop_m=.05,
            maximum_collision_free_drop_m=float(R-np.sqrt(R*R-(V*.1)**2))),
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        versions=dict(python=platform.python_version(), numpy=np.__version__, matplotlib=matplotlib.__version__))
    (OUT/'results.json').write_text(json.dumps(results, indent=2)+'\n')

    plt.rcParams.update({'font.family':'DejaVu Sans', 'font.size':10,
                         'axes.spines.top':False, 'axes.spines.right':False})
    fig, axes = plt.subplots(2, 2, figsize=(12, 8.3), layout='constrained')
    fig.suptitle('A smooth descent must also clear the block', fontsize=19, weight='bold')
    fig.get_layout_engine().set(rect=(0, .055, 1, .94))
    ax = axes[0, 0]
    # Spatial view: wheel-centre exclusion boundary, not a terrain height command.
    x = np.linspace(0, R, 1001)
    limit = R-np.sqrt(np.maximum(0, R*R-x*x))
    ax.fill_between(x*1000, limit*1000, H*1000, color='#e6e8eb')
    ax.plot(x*1000, limit*1000, color='#394956', lw=2.5, label='Corner clearance boundary')
    ax.scatter([50], [50], marker='x', s=100, color='#bd4439', zorder=5)
    ax.scatter([50], [1000*(R-np.sqrt(R*R-.05**2))], s=40, color='#394956', zorder=5)
    ax.annotate('0.20 s command:\n50 mm drop at x = 50 mm', xy=(50,50),
                xytext=(8,72), fontsize=9, arrowprops={'arrowstyle':'->','color':'#bd4439'})
    ax.text(46, 90, 'Wheel overlaps block', color='#696f75', fontsize=9)
    ax.set(xlabel='Wheel-centre distance past edge (mm)', ylabel='Downward wheel travel (mm)',
           title='1   Circular wheel rounds the sharp corner', xlim=(0,105), ylim=(105,-5))
    ax.legend(loc='upper left', fontsize=8)

    t = np.linspace(0, .45, 2001)
    colors = ['#bd4439', '#007e83']
    labels = ['Quintic 0.20 s: overlaps block', 'Quintic 0.40 s: clears block only']
    ax = axes[0, 1]
    tc = np.linspace(0, R/V, 1001)
    ax.plot(tc*1000, 1000*(R-np.sqrt(np.maximum(0, R*R-(V*tc)**2))),
            '--', color='#394956', lw=1.5, label='Corner clearance boundary')
    for duration, color, label in zip([.2,.4], colors, labels):
        drop, _, _ = target(t, duration)
        ax.plot(t*1000, drop*1000, color=color, lw=2, label=label)
    use = (reltime >= 0) & (reltime <= .45)
    ax.plot(reltime[use]*1000, 1000*(history['wheel_z_m'][0]-history['wheel_z_m'][use]),
            color='#8d63ae', lw=2, label='Retained passive simulation')
    ax.set(xlabel='Time after wheel centre passes edge (ms)', ylabel='Downward wheel travel (mm)',
           title='2   Smooth curves and passive motion differ', xlim=(0,450), ylim=(-3,110))
    ax.legend(fontsize=8, loc='lower right')

    ax = axes[1, 0]
    for duration, color in zip([.2,.4], colors):
        _, speed, _ = target(t, duration)
        ax.plot(t*1000, speed, color=color, lw=2, label=f'Quintic {duration:.2f} s')
    # Stop at first loaded floor sample; subsequent impact response is excluded.
    use = (reltime >= 0) & (np.arange(len(reltime)) < landing)
    ax.plot(reltime[use]*1000, history['extension_speed_mps'][use], color='#8d63ae', lw=2,
            label='Passive simulation, before landing')
    ax.scatter(reltime[landing-1]*1000, history['extension_speed_mps'][landing-1],
               color='#8d63ae', s=35, zorder=5)
    ax.set(xlabel='Time after wheel centre passes edge (ms)', ylabel='Downward speed (m/s)',
           title='3   Landing speed needs explicit control', xlim=(0,450), ylim=(-.05,2.7))
    ax.legend(fontsize=8)

    ax = axes[1, 1]
    duration = np.linspace(.1,.5,1001)
    ax.axvspan(.1,tmin,color='#f6dedb',alpha=.8)
    ax.plot(duration*1000, 10/np.sqrt(3)*H/duration**2, color='#007e83', lw=2)
    ax.axvline(tmin*1000, color='#394956', ls='--')
    ax.annotate(f'{tmin*1000:.1f} ms\ngeometry bound for this quintic', xy=(tmin*1000,10),
                xytext=(285,41), fontsize=9, arrowprops={'arrowstyle':'->'})
    ax.text(112, 12, 'Curve intersects block', fontsize=9, color='#a84337')
    ax.set(xlabel='Command duration (ms)', ylabel='Peak target acceleration (m/s²)',
           title='4   More time reduces acceleration demand', xlim=(100,500), ylim=(0,62))
    for ax in axes.flat:
        ax.grid(alpha=.18)
    fig.text(.015,.015,'100 mm wheel radius and step; 0.5 m/s forward motion; held hip. '
             'Analytical curves are screening targets, not simulated controllers.\n'
             'Passive trace: October 18 V4 spring study with assumed moving masses; no suspension motor.',
             fontsize=9, color='#555e66')
    for path in [OUT/'descent-profile-feasibility.png', ASSETS/'descent-profile-feasibility.png']:
        fig.savefig(path, dpi=180, facecolor='white')
    fig.savefig(OUT/'descent-profile-feasibility.pdf', facecolor='white')
    plt.close(fig)
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
