"""Render CAMEL mass/COM, spring and energy sensitivities for preliminary design.

Run: python database/code_prototypes/plot_parameter_relationships.py --output DIR
Inputs: retained spring_fits.csv, slopes.csv and range_cases.csv; declared seed
  assumptions below in kg, m, radians, N, N m, W and Wh. Plot units are explicit.
Dependencies: Python 3.11+, NumPy 2.4.6, Matplotlib 3.10.7 (plotting environment).
Outputs: three PNG/SVG figures, curve samples CSV and provenance/checks JSON in DIR.
Limitations: quasi-static mechanics and constant-speed energy accounting only;
  no terrain rollout, measured correlation, hardware rating or global optimum.
  The fixed-spring preload minimum uses uniform angle weighting, not a mission.
"""

import argparse
import csv
import hashlib
import json
import platform
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

G, L, RS, RW = 9.81, .240, .050, .175
MU, ML, MW = .350, .350, .900
MOVING = 4*(MU+ML+MW)
B, T = .700, .600
THETA = np.deg2rad(np.linspace(25, 75, 1001))
T0 = np.deg2rad(50)
ASSIST, MARGIN = .90, .10
NAVY, BLUE, TEAL, AMBER, GRAY = "#152C43", "#2168AE", "#008373", "#A65E12", "#526374"


def gravity(gross, angle=THETA):
    support = G*((np.asarray(gross)-MOVING)/4 + .75*MU + .25*ML)
    return 2*L*support*np.sin(angle)


def spring_fit(gross, radius=RS):
    demand = gravity(gross)
    design = np.column_stack((np.ones(len(THETA)), THETA-T0))
    a, b = np.linalg.lstsq(design, demand, rcond=None)[0]
    preload = ASSIST*(a+b*(THETA[0]-T0))/radius
    rate = ASSIST*b/radius**2/1000
    return float(a), float(b), preload, rate


def spring_force(preload, rate, radius=RS, angle=THETA):
    return preload + rate*1000*radius*(angle-THETA[0])


def energy(gross, power, speed=1.0, crr=.015):
    return (crr*np.asarray(gross)*G/.75+np.asarray(power)/speed)/3.6


def drive_torque(gross, slope):
    a = np.deg2rad(slope)
    return np.asarray(gross)*G*(np.sin(a)+.02*np.cos(a))*RW/2


def layout_com(drop_mm, payload_height=.400):
    hip = RW+2*L*np.cos(T0)
    upper = RW+1.5*L*np.cos(T0)
    lower = RW+.5*L*np.cos(T0)
    return (18.6*(hip-np.asarray(drop_mm)/1000)+7.5*payload_height
            +4*(MU*upper+ML*lower+MW*RW))/32.5*1000


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    record = root/"docs/benchmarks/2026-10-02-requirement-parameter-screen"
    sources = [record/name for name in ("spring_fits.csv", "slopes.csv", "range_cases.csv")]
    samples, checks = [], {}

    # Reproduce retained values before extending the same analytical models.
    for source in sources:
        with source.open(newline="") as f:
            rows = list(csv.DictReader(f))
        errors = []
        for row in rows:
            row = {k: float(v) for k, v in row.items()}
            if source.name == "spring_fits.csv" and row["fitted_assist_fraction"] == ASSIST:
                a, b, f0, k = spring_fit(row["gross_kg"])
                errors += [abs(f0-row["preload_at_25_deg_N"]),
                           abs(k-row["spring_rate_N_per_mm"])]
            elif source.name == "slopes.csv":
                errors += [abs(drive_torque(row["gross_kg"], row["slope_deg"])
                               -row["side_wheel_equivalent_torque_Nm"])]
            elif source.name == "range_cases.csv":
                errors += [abs(energy(row["gross_mass_kg"],row["auxiliaries_and_suspension_W"],
                                      row["speed_mps"],row["Crr"])
                               -row["consumption_Wh_per_km"])]
        assert max(errors) < 1e-10, source
        checks[source.name] = {"rows_read":len(rows), "scalar_comparisons":len(errors),
                               "max_absolute_error_in_column_units":float(max(errors))}

    plt.rcParams.update({"font.family":"DejaVu Sans", "font.size":10,
        "axes.labelcolor":NAVY, "text.color":NAVY, "xtick.color":GRAY,
        "ytick.color":GRAY, "axes.edgecolor":"#BCC6CE", "svg.fonttype":"none",
        "svg.hashsalt":"camel-parameter-relationships-2026-10-03"})
    args.output.mkdir(parents=True,exist_ok=True)

    def canvas(title, subtitle):
        fig, axes = plt.subplots(2,2,figsize=(13.5,10.2))
        fig.subplots_adjust(left=.08,right=.97,top=.84,bottom=.175,wspace=.24,hspace=.47)
        fig.text(.08,.953,title,fontsize=22,weight="bold")
        fig.text(.08,.912,subtitle,fontsize=11,color=GRAY)
        for ax in axes.flat:
            ax.spines[["top","right"]].set_visible(False)
            ax.grid(axis="y",color="#E3E9EE",linewidth=.8)
            ax.set_axisbelow(True)
        return fig, axes.flat

    def curve(ax, panel, series, x, y, xu, yu, color=BLUE, **kwargs):
        x, y = np.asarray(x), np.asarray(y)
        ax.plot(x,y,color=color,lw=2.3,label=series,**kwargs)
        samples.extend({"panel":panel,"series":series,"x":float(a),"x_unit":xu,
                        "y":float(b),"y_unit":yu} for a,b in zip(x,y))

    def label(ax, xy, text, offset=(8,10), color=BLUE, align="left"):
        ax.scatter(*xy,color=color,s=34,zorder=5)
        ax.annotate(text,xy,xytext=offset,textcoords="offset points",ha=align,
                    fontsize=9.5,color=color,
                    bbox=dict(facecolor="white",edgecolor="none",pad=1.4),zorder=6)

    def finish(fig, name, lines):
        for i,line in enumerate(lines):
            fig.text(.08,.094-i*.025,line,fontsize=9.2,color=GRAY)
        for ext in ("png","svg"):
            fig.savefig(args.output/f"{name}.{ext}",dpi=150,facecolor="white",
                        metadata={"Date":None} if ext=="svg" else {})
        plt.close(fig)

    # Figure 1: mass, component placement, and operational support-plane COM.
    fig, (ax1,ax2,ax3,ax4) = canvas("Mass and COM: inputs that change slope capability",
        "CAMEL 6-DOF-B  •  Calculated sensitivities  •  240 mm links; 700 mm wheelbase; 600 mm track")
    assembly = np.linspace(12,28.6,121)
    for ratio,color in [(0,TEAL),(.3,BLUE)]:
        gross = (1+ratio)*(assembly+MOVING)
        curve(ax1,"mass-knee",f"Payload = {ratio:.1f} × empty robot",assembly,
              gravity(gross,T0)/2,"kg","N m",color)
    ax1.set_title("A. Chassis assembly mass → knee holding torque",loc="left",fontsize=11)
    ax1.set(xlabel="Chassis assembly mass, excluding payload (kg)",
            ylabel="Unassisted relative-knee torque (N m)",xlim=(12,29),ylim=(0,21))
    ax1.axvline(28.6,color=AMBER,ls="--",lw=1.2)
    ax1.text(28.1,1,"Empty mass <35 kg\nrequires assembly <28.6 kg",
             ha="right",fontsize=8.5,color=AMBER)
    label(ax1,(18.6,float(gravity(32.5,T0)/2)),"18.6 kg seed: 12.40 N m")
    ax1.legend(loc="upper left",frameon=False,fontsize=9)

    drops = np.linspace(60,220,121)
    for hp,color in [(.3,TEAL),(.4,BLUE),(.5,AMBER)]:
        curve(ax2,"component-com",f"Payload COM {hp*1000:.0f} mm above ground",drops,
              layout_com(drops,hp),"mm","mm",color)
    ax2.set_title("B. Lower chassis contents → lower combined COM",loc="left",fontsize=11)
    ax2.set(xlabel="Chassis assembly COM below hip plane (mm)",
            ylabel="Loaded COM above level ground (mm)",xlim=(60,220),ylim=(255,425))
    label(ax2,(120,float(layout_com(120))),f"120 mm drop: {layout_com(120):.1f} mm COM",(7,10))
    ax2.legend(loc="lower left",frameon=False,fontsize=8.5)

    heights = np.linspace(250,500,121)
    traction_ceiling = float(np.rad2deg(np.arctan(.8-.02)))
    for offset,name,color in [(0,"Fore/aft; centered COM",BLUE),(.035,"Fore/aft; 35 mm adverse offset",TEAL)]:
        limit = np.minimum(np.rad2deg(np.arctan(((.5-MARGIN)*B-offset)/(heights/1000))),traction_ceiling)
        curve(ax3,"com-slope",name,heights,limit,"mm","deg",color)
    ax3.axhline(35,color=AMBER,ls="--",lw=1.2)
    ax3.text(496,35.45,"35° design test",color=AMBER,ha="right",fontsize=9)
    ax3.text(255,39.7,f"Traction ceiling ≈{traction_ceiling:.1f}° at assumed μ = 0.8",fontsize=9,color=GRAY)
    ax3.set_title("C. COM height → static slope screening limit",loc="left",fontsize=11)
    ax3.set(xlabel="COM height normal to support plane (mm)",ylabel="Screening slope limit (degrees)",
            xlim=(250,500),ylim=(23,42))
    ax3.legend(loc="lower left",frameon=False,fontsize=9)

    offsets = np.linspace(-60,60,121)
    for extent,name,color in [(B,"Fore/aft offset; 700 mm wheelbase",BLUE),
                               (T,"Lateral offset; 600 mm track",TEAL)]:
        bound = ((.5-MARGIN)*extent-np.abs(offsets)/1000)/np.tan(np.deg2rad(35))*1000
        curve(ax4,"offset-com",name,offsets,bound,"mm","mm",color)
    hlong = (.4*B-.035)/np.tan(np.deg2rad(35))*1000
    hside = (.4*T-.030)/np.tan(np.deg2rad(35))*1000
    label(ax4,(35,hlong),f"±35 mm → {hlong:.0f} mm",(-8,13),align="right")
    label(ax4,(30,hside),f"±30 mm → {hside:.0f} mm",(-8,-22),color=TEAL,align="right")
    ax4.set_title("D. COM offset reduces the height budget at 35°",loc="left",fontsize=11)
    ax4.set(xlabel="COM offset from contact-footprint center (mm)",
            ylabel="Maximum normal COM height (mm)",xlim=(-60,60),ylim=(230,430))
    ax4.legend(loc="upper right",frameon=False,fontsize=8.5)
    finish(fig,"mass-com-relationships",[
        "A: level, symmetric support at 50°. B: 18.6 kg assembly + 7.5 kg payload + 6.4 kg moving parts; masses fixed while relocating COM.",
        "C–D: assumed 10% footprint margin; C is fore/aft travel at μ = 0.8 and Crr = 0.02. D protects both directions along the selected axis.",
        "Use actual terrain-frame COM for C–D; active levelling changes it. Geometry/drive limits, contact loss and dynamics remain untested.  •  2026-10-03"])

    # Figure 2: distinguish retuned spring designs from preload adjustment at fixed k.
    a,b,f0,k = spring_fit(32.5)
    empty_fit = spring_fit(25)
    fig,(ax1,ax2,ax3,ax4) = canvas("Spring assistance: force, preload and drum size",
        "Level static support  •  25–75° hip travel  •  90% of a linear gravity-torque fit  •  All spring forces are per leg")
    degrees=np.rad2deg(THETA)
    curve(ax1,"angle-force","Loaded gravity-equivalent force",degrees,gravity(32.5)/RS,"deg","N",GRAY,ls="--")
    for mass,color in [(25,TEAL),(32.5,BLUE)]:
        aa,bb,ff,kk=spring_fit(mass)
        curve(ax1,"angle-force",f"{mass:g} kg gross; retuned k = {kk:.2f} N/mm",degrees,
              spring_force(ff,kk),"deg","N",color)
    label(ax1,(50,float(spring_force(f0,k,angle=T0))),"432 N at ride pose",(-12,12),align="right")
    ax1.set_title("A. Force rises through the hip travel",loc="left",fontsize=11)
    ax1.set(xlabel="Hip angle from chassis downward vertical (degrees)",ylabel="Spring / equivalent force (N)",
            xlim=(25,75),ylim=(120,740))
    ax1.legend(loc="upper left",frameon=False,fontsize=8.5)

    preloads=np.linspace(100,420,161)
    preload_minima={}
    for mass,color in [(25,TEAL),(32.5,BLUE)]:
        demand=gravity(mass)
        forces=spring_force(preloads[:,None],k)
        rms=np.sqrt(np.mean(((demand[None,:]-RS*forces)/2)**2,axis=1))
        optimum=float(np.mean(demand/RS-k*1000*RS*(THETA-THETA[0])))
        optimum_rms=float(np.sqrt(np.mean(((demand-RS*spring_force(optimum,k))/2)**2)))
        no_reverse=float(np.min(demand/RS-k*1000*RS*(THETA-THETA[0])))
        preload_minima[str(mass)]={"preload_N":optimum,"rms_knee_Nm":optimum_rms,
            "max_preload_without_opposing_spring_N":no_reverse,
            "minimum_RMS_preload_if_nonnegative_residual_required_N":min(optimum,no_reverse)}
        assert np.min(demand-RS*spring_force(no_reverse,k)) >= -1e-10
        assert np.min(demand-RS*spring_force(no_reverse+1,k)) < 0
        # Independent convex objective check at the analytical stationary point.
        for shift in [-20,20]:
            shifted=np.mean(((demand-RS*spring_force(optimum+shift,k))/2)**2)
            assert shifted > optimum_rms**2
        curve(ax2,"preload-rms",f"{mass:g} kg gross; same {k:.2f} N/mm spring",preloads,rms,"N","N m",color)
        label(ax2,(optimum,optimum_rms),f"{optimum:.0f} N minimum",(0,16),color,align="center")
    ax2.axvline(f0,color=GRAY,lw=1,ls="--")
    ax2.text(f0-5,6.2,"272 N starting preload",rotation=90,ha="right",va="top",fontsize=8.5,color=GRAY)
    ax2.text(310,6.1,"To avoid opposing the spring\nin the loaded case:\npreload ≤274 N",fontsize=8.5,color=GRAY,
             bbox=dict(facecolor="white",edgecolor="none",pad=2))
    ax2.set_title("B. Best preload changes with payload",loc="left",fontsize=11)
    ax2.set(xlabel="Installed preload at 25° (N)",ylabel="RMS relative-knee torque over 25–75° (N m)",
            xlim=(100,420),ylim=(0,8))
    ax2.legend(loc="upper left",frameon=False,fontsize=8.5)

    radii=np.linspace(40,60,81)
    for mass,color in [(25,TEAL),(32.5,BLUE)]:
        _,_,_,rates=spring_fit(mass,radii/1000)
        curve(ax3,"drum-rate",f"{mass:g} kg gross",radii,rates,"mm","N/mm",color)
    label(ax3,(50,k),f"50 mm drum: {k:.2f} N/mm",(10,10))
    ax3.set_title("C. Larger drum → lower required spring rate",loc="left",fontsize=11)
    ax3.set(xlabel="Effective spring-drum radius (mm)",ylabel="Retuned spring rate (N/mm)",
            xlim=(40,60),ylim=(3,13))
    ax3.legend(loc="upper right",frameon=False)
    _,_,pre,rate=spring_fit(32.5,radii/1000)
    peak=spring_force(pre,rate,radii/1000,THETA[-1])
    curve(ax4,"drum-force","Tension at 75° stop",radii,peak,"mm","N",BLUE)
    curve(ax4,"drum-force","Preload at 25° stop",radii,pre,"mm","N",TEAL)
    label(ax4,(50,float(spring_force(f0,k,angle=THETA[-1]))),"593 N",(9,9))
    label(ax4,(50,f0),"272 N",(9,9),TEAL)
    ax4.set_title("D. Larger drum → less force, more spring travel",loc="left",fontsize=11)
    ax4.set(xlabel="Effective spring-drum radius (mm)",ylabel="Spring force at 32.5 kg gross (N)",
            xlim=(40,60),ylim=(100,850))
    ax4.legend(loc="upper right",frameon=False,fontsize=9)
    ax4.text(41,135,"40 → 60 mm radius: travel rises 34.9 → 52.4 mm",fontsize=9,color=GRAY)
    finish(fig,"spring-relationships",[
        "A, C, D compare separately retuned spring designs. B varies preload only, holding stiffness at 7.349 N/mm and drum radius at 50 mm.",
        "B minimizes angle-averaged torque squared; the motor may need to oppose the spring. It does not optimize battery range or an obstacle trajectory.",
        "Knee torque assumes relative knee = −2 × hip angle. No uneven loading, airborne wheel, dynamics, friction or spring hysteresis.  •  2026-10-03"])

    # Figure 3: electrical range and slope propulsion need their own budgets.
    fig,(ax1,ax2,ax3,ax4)=canvas("Range and slope: power, mass, traction and drive torque",
        "Conditional screening  •  15 km target  •  1 m/s cruise  •  75% drivetrain efficiency  •  80% usable battery energy")
    for power,color in [(30,TEAL),(50,BLUE),(100,AMBER)]:
        capacity=15*energy(1.3*(assembly+MOVING),power)/.8
        curve(ax1,"mass-battery",f"Auxiliary + suspension = {power} W",assembly,capacity,"kg","Wh",color)
    label(ax1,(18.6,float(15*energy(32.5,50)/.8)),"294 Wh at the seed",(8,10))
    ax1.axvline(28.6,color=GRAY,ls="--",lw=1)
    ax1.set_title("A. Chassis mass → nominal battery for 15 km",loc="left",fontsize=11)
    ax1.set(xlabel="Chassis assembly mass, excluding payload (kg)",ylabel="Required nominal battery capacity (Wh)",
            xlim=(12,29),ylim=(100,670))
    ax1.legend(loc="upper left",frameon=False,fontsize=8.5)

    powers=np.linspace(20,150,131)
    power_budgets={}
    for capacity,color in [(400,TEAL),(600,BLUE)]:
        distance=.8*capacity/energy(32.5,powers)
        curve(ax2,"power-range",f"{capacity} Wh nominal battery",powers,distance,"W","km",color)
        budget=float(3.6*.8*capacity/15-.015*32.5*G/.75)
        power_budgets[str(capacity)]=budget
        label(ax2,(budget,15),f"{budget:.1f} W",(0,-24),color,align="center")
    ax2.axhline(15,color=AMBER,ls="--",lw=1.2)
    ax2.text(148,16.4,"15 km requirement",ha="right",fontsize=9,color=AMBER)
    ax2.set_title("B. Electrical overhead strongly affects range",loc="left",fontsize=11)
    ax2.set(xlabel="Auxiliary + suspension electrical power (W)",ylabel="Predicted flat cruising range (km)",
            xlim=(20,150),ylim=(0,70))
    ax2.legend(loc="upper right",frameon=False,fontsize=9)

    slopes=np.linspace(0,40,161)
    for mass,color in [(32.5,BLUE),(45.5,AMBER)]:
        curve(ax3,"slope-drive",f"{mass:g} kg gross"+(" (boundary)" if mass==45.5 else ""),slopes,
              drive_torque(mass,slopes),"deg","N m",color)
        label(ax3,(35,float(drive_torque(mass,35))),f"{drive_torque(mass,35):.2f} N m",(-7,12),color,align="right")
    ax3.axvline(35,color=GRAY,ls="--",lw=1)
    ax3.set_title("C. Grade and gross mass set drive-torque demand",loc="left",fontsize=11)
    ax3.set(xlabel="Slope angle (degrees)",ylabel="Summed wheel-equivalent torque per side (N m)",
            xlim=(0,40),ylim=(0,30))
    ax3.legend(loc="upper left",frameon=False,fontsize=9)

    friction=np.linspace(.3,1,141)
    limits=np.rad2deg(np.arctan(friction-.02))
    curve(ax4,"friction-slope","Ideal all-wheel traction bound",friction,limits,"dimensionless","deg",BLUE)
    required_mu=float(np.tan(np.deg2rad(35))+.02)
    label(ax4,(required_mu,35),f"35° needs μ ≥ {required_mu:.3f}",(-10,16),align="right")
    ax4.axhline(35,color=AMBER,ls="--",lw=1.2)
    ax4.set_title("D. More spring force cannot replace tire traction",loc="left",fontsize=11)
    ax4.set(xlabel="Assumed tire / surface friction coefficient, μ",ylabel="Traction-limited grade (degrees)",
            xlim=(.3,1),ylim=(10,48))
    finish(fig,"range-drive-relationships",[
        "A–B: flat straight cruise, Crr = 0.015; battery mass must already fit the assembly budget. B holds gross mass at 32.5 kg for both batteries.",
        "C–D: Crr = 0.02, 175 mm wheel radius, sufficient contact/load sharing assumed. Side totals are not motor-shaft or per-wheel ratings.",
        "45.5 kg is the 35 kg empty-mass boundary plus 30% payload; the actual empty requirement is strictly <35 kg. No dynamic/range proof.  •  2026-10-03"])

    # Solve contact-force/moment balance separately at the plotted COM boundaries.
    statics_error=[]
    for extent,offset in [(B,0),(B,-.035),(T,0),(T,-.030)]:
        angle=np.deg2rad(35)
        normal=32.5*G*np.cos(angle)
        height=((.5-MARGIN)*extent-abs(offset))/np.tan(angle)
        # Contact lever arms relative to COM; the traction sum acts h below COM.
        system=np.array([[1,1],[extent/2-offset,-extent/2-offset]])
        up,down=np.linalg.solve(system,[normal,-height*32.5*G*np.sin(angle)])
        statics_error += [abs(up/normal-MARGIN),abs(down/normal-(1-MARGIN))]
    assert max(statics_error)<1e-10
    assert abs(float(layout_com(120)-layout_com(160))-18.6/32.5*40)<1e-10
    with (args.output/"parameter-relationships.csv").open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(samples[0])); writer.writeheader(); writer.writerows(samples)
    details={
        "evidence":"derived analytical sensitivity; not measured correlations or trained response models",
        "python":platform.python_version(),"numpy":np.__version__,"matplotlib":matplotlib.__version__,
        "script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "source_sha256":{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
        "checks":checks,"COM_boundary_normal_load_fraction_max_error":max(statics_error),
        "curve_samples":len(samples),
        "seed":{"link_m":L,"wheel_radius_m":RW,"spring_drum_m":RS,"chassis_kg":18.6,
                "payload_kg":7.5,"moving_kg":MOVING,"gross_kg":32.5,"spring_rate_N_per_mm":k,
                "preload_N":f0,"loaded_level_COM_mm":float(layout_com(120))},
        "chassis_upper_bound_exclusive_kg":35-MOVING,
        "fixed_rate_preload_minima":preload_minima,
        "equal_empty_loaded_weight_fixed_rate_preload_N":float(np.mean([v["preload_N"] for v in preload_minima.values()])),
        "lowering_18_6kg_assembly_40mm_lowers_loaded_COM_mm":18.6/32.5*40,
        "35deg_COM_bounds_mm":{"centered_fore_aft":.4*B/np.tan(np.deg2rad(35))*1000,
             "fore_aft_offset_35mm":hlong,"centered_lateral":.4*T/np.tan(np.deg2rad(35))*1000,
             "lateral_offset_30mm":hside},
        "auxiliary_suspension_power_limit_for_15km_W":power_budgets,
        "nominal_battery_Wh_per_additional_chassis_kg_at_30pct_payload":15/.8*.015*1.3*G/.75/3.6,
        "nominal_battery_Wh_per_extra_10W_at_1mps":15/.8*10/3.6,
        "extra_used_Wh_for_0_5kg_per_wheel_over_15km_at_Crr_0_02":15*.02*2*G/.75/3.6,
        "required_mu_at_35deg_Crr_0_02":required_mu,
        "limitations":["uniform 1001-angle spring objective; no time trajectory",
          "10% static stability margin is an assumption",
          "range excludes turns, aerodynamics, elevation and transient contact losses",
          "COM in CAD level pose must be transformed for actual slope/levelling posture",
          "spring fit does not determine damping, wheel-contact dynamics or motor rating"]}
    (args.output/"parameter-relationships.json").write_text(json.dumps(details,indent=2)+"\n")
    print(json.dumps(details,indent=2))


if __name__=="__main__":
    main()
