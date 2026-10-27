"""Preliminary sizing only. Standard Python, no external packages.
Run in this folder: python calculate_powertrain.py
"""
from pathlib import Path
import math, json, csv
P=Path(__file__).resolve().parent
m,g,r=18000,9.81,.51
Crr,rho,CdA=.008,1.2,6.0
ratio,eta_g,eta_m,eta_i=8.0,.95,.94,.98
Ppeak,Pcont,Tpeak,Tcont,nmax=300000,200000,3000,2000,4000
def loads(speed_kph,grade=0,accel=0):
    v=speed_kph/3.6; theta=math.atan(grade)
    roll=m*g*Crr*math.cos(theta)
    aero=.5*rho*CdA*v*v
    hill=m*g*math.sin(theta)
    force=roll+aero+hill+1.05*m*accel
    rpm=v/r*ratio*60/(2*math.pi)
    omega=rpm*2*math.pi/60
    return dict(speed_kph=speed_kph,grade_percent=100*grade,acceleration_m_s2=accel,
        force_N=force,wheel_torque_Nm=force*r,motor_torque_Nm=force*r/(ratio*eta_g),
        motor_power_kW=force*v/eta_g/1000,motor_rpm=rpm,
        available_peak_force_N=min(Tpeak,Ppeak/max(omega,1e-9))*ratio*eta_g/r,
        available_cont_force_N=min(Tcont,Pcont/max(omega,1e-9))*ratio*eta_g/r)
cases={'flat_80':loads(80),'grade15_20':loads(20,.15),'grade15_launch':loads(0,.15),
       'flat_accel_50':loads(50,0,.5)}
for name,case in cases.items():
    use_cont=name in ('flat_80','grade15_20')
    case['meets_assumed_requirement']=case['force_N'] <= case['available_cont_force_N' if use_cont else 'available_peak_force_N'] and case['motor_rpm']<=nmax
assert all(c['meets_assumed_requirement'] for c in cases.values())
cellAh,series,parallel=335,224,2
Vnom=3.2*series; Vmin=2.8*series; Vmax=3.65*series
E=Vnom*cellAh*parallel/1000
soc,soh=.8,.8
ranges={str(e):{'BOL_km':E*soc/e,'EOL80_km':E*soc*soh/e} for e in [1.3,1.5,1.8,2.0]}
aux=20000
peak_dc=(Ppeak/(eta_m*eta_i)+aux)/1000
cont_dc=(Pcont/(eta_m*eta_i)+aux)/1000
# Full peak traction requires approximately mu=0.40 for the assumed static rear load.
rear_static_kg=11500
mu_peak=cases['grade15_launch']['available_peak_force_N']/(rear_static_kg*g)
mu_grade=cases['grade15_launch']['force_N']/(rear_static_kg*g)
# Numerical time integration; flat road, ideal full battery and no thermal derating.
v,t=0.,0.;dt=.01
while v<50/3.6:
    road=loads(v*3.6)
    a=min(.8,(road['available_peak_force_N']-road['force_N'])/(1.05*m))
    assert a>0
    v+=a*dt;t+=dt
report={'status':'CONCEPT ONLY - assumed requirements, not validated hardware',
 'assumptions':{'gross_mass_kg':m,'effective_tyre_radius_m':r,'Crr':Crr,'CdA_m2':CdA,'air_density_kg_m3':rho,'rotating_mass_factor':1.05,'gear_efficiency':eta_g,'motor_efficiency':eta_m,'inverter_efficiency':eta_i,'auxiliaries_kW':20,'rear_static_load_kg':rear_static_kg},
 'motor_requirement':{'peak_kW':300,'continuous_kW':200,'peak_Nm':3000,'continuous_Nm':2000,'base_rpm':Pcont/Tcont*60/(2*math.pi),'max_rpm':nmax,'peak_duration_target_s':30},
 'transmission':{'primary_ratio':2,'final_ratio':4,'total_ratio':ratio,'peak_wheel_torque_Nm':Tpeak*ratio*eta_g,'peak_contact_force_N':Tpeak*ratio*eta_g/r,'speed_at_max_rpm_kph':nmax/ratio*2*math.pi*r/60*3.6,'vehicle_speed_limiter_kph':80},
 'cases':cases,'ideal_flat_0_50_s_with_acceleration_limit_0_8':t,
 'traction':{'minimum_mu_for_full_peak_static_rear':mu_peak,'minimum_mu_for_grade15_launch_static_rear':mu_grade,'note':'No load transfer model; traction control must limit torque on low friction.'},
 'battery_concept':{'chemistry':'LFP assumed','cell_nominal_V':3.2,'cell_capacity_Ah':cellAh,'series_cells':series,'parallel_strings':parallel,'cell_count':series*parallel,'nominal_V':Vnom,'minimum_design_V':Vmin,'maximum_V':Vmax,'nominal_Ah':cellAh*parallel,'nominal_kWh':E,'SOC_window_fraction':soc,'BOL_usable_kWh':E*soc,'EOL80_usable_kWh':E*soc*soh,'energy_per_km_assumptions_include_auxiliaries':True,'range_scenarios':ranges,'peak_DC_kW_including_aux':peak_dc,'continuous_DC_kW_including_aux':cont_dc,'peak_A_at_min_V':peak_dc*1000/Vmin,'continuous_A_at_min_V':cont_dc*1000/Vmin,'pack_current_target_cont_A':450,'pack_current_target_peak_A':600,'pack_mass_at_140_Wh_kg':E*1000/140,'pack_volume_at_200_Wh_L_m3':E/200,'six_enlarged_envelopes_mm':[1600,1000,280],'old_six_envelope_volume_m3':6*1.25*.9*.21,'new_envelope_volume_m3':6*1.6*1*.28},
 'thermal_estimates_kW':{'drive_losses_at_continuous':Pcont*(1/(eta_m*eta_i)-eta_g)/1000,'battery_heat_at_450A_assumed_40mOhm':450**2*.04/1000},
 'charge':{'DC_charger_target_kW':150,'ideal_SOC10_90_h_at_95percent_battery_charge_efficiency':E*.8/(150*.95),'note':'Ideal constant-power lower-bound planning estimate, no taper or temperature constraints.'}}
(P/'powertrain_calculations.json').write_text(json.dumps(report,indent=2),encoding='utf8')
with (P/'tractive_force_curve.csv').open('w',newline='',encoding='utf8') as f:
    fields=['speed_kph','motor_rpm','force_N','available_cont_force_N','available_peak_force_N']
    w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
    for speed in range(81):
        row=loads(speed);w.writerow({k:row[k] for k in fields})
print(json.dumps(report,indent=2))
