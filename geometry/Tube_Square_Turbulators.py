import cadquery as cq
from cadquery.vis import show
import math
from pathlib import Path

# -----------------------------
# Tube parameters
# -----------------------------

L = 120.0
outer_overall = 24.0
outer_diameter = 8.0
wall = 0.6

# -----------------------------
# Turbulator parameters
# -----------------------------

group_spacing = 10.0
angle_deg = 35.0
top_offset = 0.5 * group_spacing

pads_per_group = 4
pad_size = 1.3
pad_height = 0.7
embed = 0.15

flat_width_coverage = 0.85
end_margin = 5.0

# -----------------------------
# Derived geometry
# -----------------------------

if outer_overall <= outer_diameter:
    raise ValueError("outer_overall must be > outer_diameter")

inner_overall = outer_overall - 2 * wall
inner_diameter = outer_diameter - 2 * wall

if inner_overall <= inner_diameter or inner_diameter <= 0:
    raise ValueError("Invalid inner geometry — wall too thick")

inner_flat_span = inner_overall - inner_diameter

x_margin = max(0.5 * pad_size, 0.3)
usable_flat_span = inner_flat_span - 2 * x_margin

if usable_flat_span <= 0:
    raise ValueError("Pads too large for flat span")

target_x_span = max(usable_flat_span * flat_width_coverage, 2 * pad_size)

angle_rad = math.radians(angle_deg)
tan_a = math.tan(angle_rad)

intervals = pads_per_group - 1
total_dz = target_x_span / abs(tan_a)
step_dz = total_dz / intervals
step_dx = tan_a * step_dz

# -----------------------------
# Base tube geometry
# -----------------------------

outer = cq.Workplane("XY").slot2D(outer_overall, outer_diameter).extrude(L)
inner_void = cq.Workplane("XY").slot2D(
    inner_overall, inner_diameter).extrude(L)

tube_shell = outer.cut(inner_void)

# -----------------------------
# Turbulator construction
# -----------------------------


def make_pad(xc, yc, zc):
    return (
        cq.Workplane("XY")
        .box(pad_size, pad_height, pad_size, centered=True)
        .translate((xc, yc, zc))
        .val()
    )


def make_turbulator_group(z_center, top):
    y_wall = (inner_diameter / 2) if top else -(inner_diameter / 2)
    inward_sign = -1 if top else 1

    y_center = y_wall + inward_sign * (-pad_height / 2 + embed)

    solids = []
    mid = (pads_per_group - 1) / 2

    for i in range(pads_per_group):
        local_x = (i - mid) * step_dx
        local_z = z_center + (i - mid) * step_dz

        if local_z < end_margin or local_z > (L - end_margin):
            continue
        if abs(local_x) > (usable_flat_span / 2):
            continue

        solids.append(make_pad(local_x, y_center, local_z))

    if not solids:
        return None

    grp = solids[0]
    for s in solids[1:]:
        grp = grp.fuse(s)

    return grp


def z_positions(offset):
    z0 = end_margin + offset
    zmax = L - end_margin
    if z0 > zmax:
        return []
    n = int(math.floor((zmax - z0) / group_spacing)) + 1
    return [z0 + i * group_spacing for i in range(n)]

# -----------------------------
# Build ALL turbulators as one solid
# -----------------------------


turbulators = None

for z in z_positions(0.0):
    g = make_turbulator_group(z, top=False)
    if g:
        turbulators = g if turbulators is None else turbulators.fuse(g)

for z in z_positions(top_offset):
    g = make_turbulator_group(z, top=True)
    if g:
        turbulators = g if turbulators is None else turbulators.fuse(g)

# -----------------------------
# Final solids
# -----------------------------

tube_metal = tube_shell.union(turbulators) if turbulators else tube_shell

fluid = inner_void.cut(turbulators) if turbulators else inner_void
fluid = fluid.clean()

# -----------------------------
# Export
# -----------------------------

tube_file = Path(__file__).with_name("tube_metal.stl")
fluid_file = Path(__file__).with_name("tube_fluid.stl")

cq.exporters.export(tube_metal, str(tube_file), exportType="STL")
cq.exporters.export(fluid, str(fluid_file), exportType="STL")

print("Exported:")
print(tube_file)
print(fluid_file)

# -----------------------------
# Visualization
# -----------------------------

show(fluid)
