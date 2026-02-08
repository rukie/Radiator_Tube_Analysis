import cadquery as cq
from cadquery.vis import show
import math

from pathlib import Path


# -----------------------------

# Tube parameters

# -----------------------------

L = 120.0                # tube length (Z)

outer_overall = 24.0     # overall width of obround in X (end-to-end)

outer_diameter = 8.0     # overall height in Y (also diameter of rounded ends)

wall = 0.6               # wall thickness


# -----------------------------

# Turbulator parameters

# -----------------------------

group_spacing = 10.0         # spacing between turbulator groups along Z

angle_deg = 35.0             # defines diagonal slope dx/dz = tan(angle)

top_offset = 0.5 * group_spacing


pads_per_group = 4           # "4 little squares" per diagonal

pad_size = 1.3               # square pad footprint size (X and Z)

pad_height = 0.7             # protrusion inward (Y)

embed = 0.15                 # sink into wall for strong union


# How much of the *inner flat width* the diagonal chain should consume (0..1)

flat_width_coverage = 0.85


end_margin = 5.0             # keep turbulators away from tube ends


# -----------------------------

# Validation / derived dims

# -----------------------------

if outer_overall <= outer_diameter:

    raise ValueError(
        "outer_overall must be > outer_diameter for a valid obround.")


inner_overall = outer_overall - 2.0 * wall

inner_diameter = outer_diameter - 2.0 * wall


if inner_overall <= inner_diameter or inner_diameter <= 0:

    raise ValueError("Wall too thick; inner obround invalid.")


inner_flat_span = inner_overall - inner_diameter

if inner_flat_span <= 0:

    raise ValueError(
        "Inner flat span is non-positive; cannot place pads on flat sections.")


# Keep some safety margin from the curved ends

x_margin = max(0.5 * pad_size, 0.3)

usable_flat_span = max(0.0, inner_flat_span - 2.0 * x_margin)

if usable_flat_span <= 0:

    raise ValueError(
        "Pads too large for the available flat span; reduce pad_size or wall.")


# Desired total X span of the stepped diagonal chain

target_x_span = usable_flat_span * float(flat_width_coverage)

# avoid degenerately small span
target_x_span = max(target_x_span, 2.0 * pad_size)


angle_rad = math.radians(angle_deg)

tan_a = math.tan(angle_rad)

if abs(tan_a) < 1e-6:

    raise ValueError(
        "angle_deg too close to 0; cannot form diagonal chain across width.")


# For pads_per_group pads, there are (N-1) intervals.

# Choose step_dz so that total dx across the chain ~ target_x_span.

intervals = pads_per_group - 1

total_dz = target_x_span / abs(tan_a)

step_dz = total_dz / intervals

step_dx = tan_a * step_dz  # signed slope based on angle sign


# -----------------------------

# Build obround tube shell

# -----------------------------

outer = cq.Workplane("XY").slot2D(outer_overall, outer_diameter).extrude(L)

inner_void = cq.Workplane("XY").slot2D(
    inner_overall, inner_diameter).extrude(L)

tube = outer.cut(inner_void)


# -----------------------------

# Turbulator group: 4 stepped square pads

# -----------------------------

def make_pad(xc: float, yc: float, zc: float) -> cq.Solid:

    return (

        cq.Workplane("XY")

        .box(pad_size, pad_height, pad_size, centered=True)

        .translate((xc, yc, zc))

        .val()

    )


def make_turbulator_group(z_center: float, top: bool) -> cq.Solid:
    """

    Creates one 'diagonal turbulator' as 4 square pads arranged along a diagonal

    across the inner flat width.

    """

    # inner flat walls are at y = +/- inner_diameter/2

    y_wall = (inner_diameter / 2.0) if top else -(inner_diameter / 2.0)

    # inward direction:

    # top wall inward is -Y, bottom wall inward is +Y

    inward_sign = -1.0 if top else +1.0

    y_center = y_wall + inward_sign * (-pad_height / 2.0 + embed)

    # Center the chain at x=0, z=z_center, stepping along diagonal

    solids = []

    mid = (pads_per_group - 1) / 2.0

    for i in range(pads_per_group):

        local_x = (i - mid) * step_dx

        local_z = z_center + (i - mid) * step_dz

        # clip: ensure pads stay inside tube length margins

        if local_z < end_margin or local_z > (L - end_margin):

            continue

        # clip in X to flat region margin (keep pads off rounded ends)

        if abs(local_x) > (usable_flat_span / 2.0):

            continue

        solids.append(make_pad(local_x, y_center, local_z))

    # union pads into one solid group

    grp = solids[0]

    for s in solids[1:]:

        grp = grp.fuse(s)

    return grp


def z_positions(offset: float) -> list[float]:

    z0 = end_margin + offset

    zmax = L - end_margin

    if z0 > zmax:

        return []

    n = int(math.floor((zmax - z0) / group_spacing)) + 1

    return [z0 + i * group_spacing for i in range(n)]


# Place groups
for z in z_positions(0.0):

    tube = tube.union(make_turbulator_group(z, top=False))


for z in z_positions(top_offset):

    tube = tube.union(make_turbulator_group(z, top=True))


# -----------------------------

# Export STEP

# -----------------------------


out_file = Path(__file__).with_name("radiator_tube_with_turbulators.stl")

cq.exporters.export(
    tube,
    str(out_file),
    exportType="STL",
    tolerance=0.05,     # controls facet resolution
    angularTolerance=0.1
)


print(f"Exported: {out_file}")

#show(tube)

bbox = (
    cq.Workplane("XY")
    .box(
        inner_overall * 1.2,
        inner_diameter * 1.2,
        L * 1.2,
        centered=True
    )
)

fluid = bbox.cut(tube)

show(fluid)