"""Conceptual 12 m electric bus. Requires cadquery 2.8 and vtk 9.6.
Run: python build_electric_bus.py [output_directory]
Units: mm. Geometry and packaging are illustrative, not production validated.
"""
import math, sys, json
from pathlib import Path
import cadquery as cq
import vtk
OUT=Path(sys.argv[1] if len(sys.argv)>1 else __file__).resolve()
if OUT.suffix: OUT=OUT.parent
OUT.mkdir(parents=True,exist_ok=True)
V=cq.Vector
parts=[]
blue=(.04,.46,.58); white=(.88,.92,.93); dark=(.035,.06,.08)
glass=(.10,.22,.29); silver=(.60,.65,.68); orange=(.95,.42,.10)
def box(x,y,z,a,b,c):return cq.Solid.makeBox(a,b,c,V(x,y,z))
def cyl(r,h,p,d):return cq.Solid.makeCylinder(r,h,V(*p),V(*d))
def add(n,s,c):
    assert s.isValid(),n
    parts.append((n,s,c))
L,W,H=12000,2550,3300
axles=[-3500,2500]
# Floor height 550; envelope includes roof battery fairing.
floor=box(-6000,-1230,490,12000,2460,60)
for x in axles:
    for y in [-1230,680]:
        floor=floor.cut(box(x-550,y,480,1100,550,80))
        # Interior wheel housings cover the wheel openings.
        well=box(x-550,y,550,1100,550,530).cut(box(x-530,y+20,540,1060,510,520))
        add(f'Wheel_housing_{x}_{y}',well,silver)
add('Floor',floor,silver)
for y in [-790,690]:add('Chassis_rail_'+str(y),box(-5700,y,330,11300,100,160),dark)
for i,x in enumerate(range(-5400,5600,1000)):add(f'Crossmember_{i}',box(x,-1120,390,80,2240,80),silver)
for side,y in [('Right',-1275),('Left',1235)]:
    panel=box(-6000,y,550,12000,40,1050)
    for x in axles:panel=panel.cut(cyl(535,150,(x,y-50,510),(0,1,0)))
    doors=[(-5100,1150),(400,1250)] if side=='Right' else []
    for x,w in doors:panel=panel.cut(box(x,y-5,540,w,60,1070))
    add(side+'_lower_body',panel,blue)
    add(side+'_window_header',box(-6000,y,2620,12000,40,360),white)
    # Narrow pillars and individual glazing bays.
    for i in range(10):
        x=-5880+i*1180
        overlaps=any(x<d+w and x+1100>d for d,w in doors)
        if not overlaps:
            add(f'{side}_window_{i}',box(x,y+10,1610,1100,18,1000),glass)
            add(f'{side}_pillar_{i}',box(x-40,y,1600,40,40,1020),white)
    if side=='Right':
        for j,(x,w) in enumerate(doors):
            for k in range(2):
                a=x+k*w/2
                add(f'Door_{j}_leaf_{k}',box(a,y+5,570,w/2-8,30,2020),dark)
                add(f'Door_{j}_glass_{k}',box(a+35,y,1120,w/2-78,8,1410),glass)
            add(f'Door_{j}_step',box(x,-1265,510,w,280,35),silver)
add('Roof_panel',box(-6000,-1275,2980,12000,2550,70),white)
# Front at negative X.
add('Front_lower_mask',box(-6000,-1235,600,55,2470,900),blue)
add('Front_windscreen',box(-5995,-1180,1530,25,2360,1320),glass)
add('Front_brow',box(-6025,-1275,2850,70,2550,130),dark)
add('Destination_display',box(-6030,-850,2890,10,1700,90),glass)
add('Rear_lower_mask',box(5945,-1235,600,55,2470,1100),blue)
add('Rear_window',box(5960,-1100,1770,25,2200,1000),glass)
add('Rear_top',box(5945,-1235,2770,55,2470,210),white)
for end,x in [('Front',-6050),('Rear',6000)]:
    add(end+'_bumper',box(x,-1220,560,50,2440,150),dark)
    for j,y in enumerate([-1060,860]):
        add(f'{end}_light_{j}',box(x-5,y,920,65,200,120),(.98,.92,.64) if end=='Front' else (.85,.06,.04))
# Tyres and rims, visible wheels plus paired inner rear tyres.
for i,x in enumerate(axles):
    add(f'Axle_{i}',cyl(85,2040,(x,-1020,510),(0,1,0)),dark)
    positions=[-1240,960] if i==0 else [-1240,-960,680,960]
    for j,y in enumerate(positions):
        tyre=cyl(510,280,(x,y,510),(0,1,0)).cut(cyl(285,280,(x,y,510),(0,1,0)))
        add(f'Tyre_{i}_{j}',tyre,dark)
        add(f'Rim_{i}_{j}',cyl(282,260,(x,y+10,510),(0,1,0)),silver)
        add(f'Hub_{i}_{j}',cyl(125,284,(x,y-2,510),(0,1,0)),dark)
    for y in [-730,570]:add(f'Air_suspension_{i}_{y}',cyl(130,240,(x,y,660),(0,0,1)),dark)
add('Rear_drive_motor',cyl(190,540,(2500,-270,600),(0,1,0)),orange)
add('Inverter',box(3100,-450,570,600,900,240),silver)
# Interior seats: six left pairs and four right pairs, plus rear bench.
for side,y,rows in [('Left',250,[-2600,-1700,-800,100,1000,4000]),('Right',-1150,[-2600,-1700,-800,4000])]:
    for r,x in enumerate(rows):
        for j in range(2):
            sy=y+j*470
            add(f'Seat_{side}_{r}_{j}_base',box(x,sy,930,430,430,95),(.13,.36,.47))
            add(f'Seat_{side}_{r}_{j}_back',box(x+350,sy,1015,80,430,660),(.13,.36,.47))
            add(f'Seat_{side}_{r}_{j}_leg',box(x+170,sy+150,550,70,100,380),silver)
for j in range(5):
    y=-1170+j*470
    add(f'Rear_bench_{j}',box(5210,y,1050,580,440,100),blue)
    add(f'Rear_back_{j}',box(5710,y,1150,80,440,650),blue)
add('Driver_seat',box(-5100,650,900,500,480,110),dark)
add('Driver_back',box(-4680,650,1000,80,480,700),dark)
add('Dashboard',box(-5770,450,1050,620,760,240),dark)
steer=cyl(210,35,(-5310,870,1380),(1,0,1)).cut(cyl(175,35,(-5310,870,1380),(1,0,1)))
add('Steering_wheel',steer,dark)
for i,x in enumerate([-3050,-300,2050]):
    add(f'Handrail_{i}',cyl(17,2040,(x,300,550),(0,0,1)),orange)
add('Overhead_rail',cyl(17,8500,(-4000,300,2520),(1,0,0)),orange)
# Six battery packaging envelopes: nominal capacity label only, no cell design.
add('Roof_battery_tray',box(-2100,-1020,3050,4200,2040,40),dark)
for i in range(3):
    for j in range(2):
        add(f'Battery_envelope_{i}_{j}',box(-2000+i*1350,-950+j*970,3090,1250,900,210),silver)
add('HVAC_envelope',box(3200,-800,3050,1700,1600,250),white)
for i in range(10):add(f'HVAC_vent_{i}',box(3320+i*140,-600,3300,40,1200,8),dark)
for j,y in enumerate([-1495,1275]):
    add(f'Mirror_arm_{j}',box(-5700,min(y,-1275) if j==0 else 1275,2200,35,220,35),dark)
    add(f'Mirror_{j}',box(-5730,y,1900,85,75,420),dark)
add('Charge_port',box(4600,-1285,1100,300,15,300),dark)

ass=cq.Assembly(name='Electric_city_bus_12m_CONCEPT_mm')
for n,s,c in parts:ass.add(s,name=n,color=cq.Color(*c))
path=OUT/'electric_bus_12m.step';ass.export(str(path))
loaded=cq.importers.importStep(str(path));solids=loaded.solids().vals()
assert all(s.isValid() for s in solids)
b=loaded.val().BoundingBox()
report={'units':'mm','nominal_body_mm':[12000,2550,3300],'wheelbase_mm':6000,'front_overhang_mm':2500,'rear_overhang_mm':3500,'passenger_seats':25,'driver_seats':1,'battery_envelopes':6,'solids':len(solids),'all_solids_valid':True,'step_reimport_passed':True,'step_bytes':path.stat().st_size}
(OUT/'electric_bus_validation.json').write_text(json.dumps(report,indent=2))
ren=vtk.vtkRenderer();ren.SetBackground(.94,.96,.98)
for n,s,c in parts:
    vs,ts=s.tessellate(5,.15);points=vtk.vtkPoints();cells=vtk.vtkCellArray()
    for v in vs:points.InsertNextPoint(v.x,v.y,v.z)
    for t in ts:
        cells.InsertNextCell(3)
        for idx in t:cells.InsertCellPoint(idx)
    poly=vtk.vtkPolyData();poly.SetPoints(points);poly.SetPolys(cells)
    normals=vtk.vtkPolyDataNormals();normals.SetInputData(poly);normals.SetFeatureAngle(45);normals.Update()
    mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(normals.GetOutputPort())
    actor=vtk.vtkActor();actor.SetMapper(mapper);actor.GetProperty().SetColor(*c)
    if 'window' in n.lower() or 'windscreen' in n.lower() or '_glass_' in n:actor.GetProperty().SetOpacity(.62)
    ren.AddActor(actor)
win=vtk.vtkRenderWindow();win.SetOffScreenRendering(1);win.SetSize(1800,1000);win.AddRenderer(ren)
cam=ren.GetActiveCamera();cam.SetPosition(-14000,-19000,10500);cam.SetFocalPoint(0,0,1500);cam.SetViewUp(0,0,1);cam.ParallelProjectionOn();ren.ResetCamera();cam.Zoom(1.12)
win.Render();grab=vtk.vtkWindowToImageFilter();grab.SetInput(win);grab.Update()
writer=vtk.vtkPNGWriter();writer.SetFileName(str(OUT/'electric_bus_preview.png'));writer.SetInputConnection(grab.GetOutputPort());writer.Write()
print(json.dumps(report))
