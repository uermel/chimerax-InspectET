import numpy as np
from typing import List, Tuple


def get_axes_model(session, size: Tuple[float, float, float], z_offset=0):
    # Axes from https://www.cgl.ucsf.edu/chimera/docs/UsersGuide/bild.html
    from chimerax.bild.bild import _BildFile

    b = _BildFile(session, "dummy")
    # Global X
    b.color_command(".color red".split())
    b.arrow_command(f".arrow {-size[0]} 0 0 {size[0]} 0 0 80 240 0.9".split())
    b.color_command(".color red".split())
    b.transparency_command(".transparency 0.5".split())
    b.arrow_command(f".arrow {-size[0]} 0 {z_offset} {size[0]} 0 {z_offset} 80 240 0.9".split())

    # Global Y
    b.color_command(".color yellow".split())
    b.transparency_command(".transparency 0".split())
    b.arrow_command(f".arrow 0 {-size[1]} 0 0 {size[1]} 0 80 240 0.9".split())
    b.color_command(".color yellow".split())
    b.transparency_command(".transparency 0.5".split())
    b.arrow_command(f".arrow 0 {-size[1]} {z_offset} 0 {size[1]} {z_offset} 80 240 0.9".split())

    # Global Z
    b.color_command(".color blue".split())
    b.transparency_command(".transparency 0".split())
    b.arrow_command(f".arrow 0 0 {-size[2]} 0 0 {size[2]} 80 240 0.9".split())

    # Electron Beam
    b.color_command(".color green".split())
    b.arrow_command(f".arrow 0 0 {size[2] + 1000} 0 0 {size[2] + 500} 160 600 0.9".split())

    from chimerax.atomic import AtomicShapeDrawing
    from chimerax.core.models import Model

    d = AtomicShapeDrawing("shapes")
    d.add_shapes(b.shapes)
    m = Model("axes", session)
    m.add_drawing(d)

    return m


def get_box_model(
    session,
    size: Tuple[float, float, float],
    name: str = "volume",
    color: str = "cyan",
    transparency: float = 0.5,
    offset=(0, 0, 0),
):
    from chimerax.bild.bild import _BildFile

    b = _BildFile(session, "dummy")
    # Box
    b.color_command(f".color {color}".split())
    b.transparency_command(f".transparency {transparency}".split())
    b.box_command(f".box {offset[0]} {offset[0]} {offset[0]} {size[0]} {size[1]} {size[2]}".split())

    # Origin
    b.color_command(".color red".split())
    b.sphere_command(f".sphere 0 0 0 300".split())

    from chimerax.atomic import AtomicShapeDrawing
    from chimerax.core.models import Model

    d = AtomicShapeDrawing("shapes")
    d.add_shapes(b.shapes)
    m = Model(name, session)
    m.add_drawing(d)

    return m


def create_alignment_objects(
    session,
    alignment,
    params,
    vol_file: str = None,
    ts_file: str = None,
):

    axes_size = (
        1 * alignment.volume_dimension["x"],
        1 * alignment.volume_dimension["y"],
        2 * alignment.volume_dimension["z"],
    )
    z_offset = -4 * alignment.volume_dimension["z"] + 1000

    if session.inspectet.axes_model is not None and not session.inspectet.axes_model.deleted:
        session.inspectet.axes_model.delete()
        session.inspectet.axes_model = None

    axes = get_axes_model(session, axes_size, z_offset)
    session.models.add([axes])
    session.inspectet.axes_model = axes

    if session.inspectet.volume_model is not None and not session.inspectet.volume_model.deleted:
        session.inspectet.volume_model.delete()
        session.inspectet.volume_model = None

    if vol_file:
        from chimerax.open_command.cmd import cmd_open

        models = cmd_open(session, [vol_file], "", log=True)
        session.inspectet.volume_model = models[0]
        session.inspectet.volume_model.data.set_origin((0, 0, 0))

        vol_size = (alignment.volume_dimension["x"], alignment.volume_dimension["y"], alignment.volume_dimension["z"])
        print("vol size", vol_size)
        from chimerax.geometry import rotation, translation

        ico = session.inspectet.initial_coord_order
        pos = (
            rotation((0, 1, 0), params.tilt_angle)
            * session.inspectet.additional_rotation
            * translation((-vol_size[ico[0]] / 2, -vol_size[ico[1]] / 2, -vol_size[ico[2]] / 2))
        )

        session.inspectet.volume_model.position = pos

        from chimerax.core.commands import run

        run(
            session,
            f"volume #{models[0].id_string} style surface region all showOutlineBox true capFaces false",
            log=True,
        )

    else:
        vol_size = (alignment.volume_dimension["x"], alignment.volume_dimension["y"], alignment.volume_dimension["z"])
        vol = get_box_model(session, vol_size)
        session.models.add([vol])
        session.inspectet.volume_model = vol

        from chimerax.geometry import rotation, translation

        pos = (
            rotation((0, 1, 0), params.tilt_angle)
            * session.inspectet.additional_rotation
            * translation((-vol_size[0] / 2, -vol_size[1] / 2, -vol_size[2] / 2))
        )
        vol.position = pos

    if session.inspectet.raw_tiltseries is not None and not session.inspectet.raw_tiltseries.deleted:
        session.inspectet.raw_tiltseries.delete()
        session.inspectet.raw_tiltseries = None

    if session.inspectet.aligned_tiltseries is not None and not session.inspectet.aligned_tiltseries.deleted:
        session.inspectet.aligned_tiltseries.delete()
        session.inspectet.aligned_tiltseries = None

    from chimerax.core.models import Model

    raw_tiltseries = Model("raw tiltseries", session)
    session.models.add([raw_tiltseries])
    session.inspectet.raw_tiltseries = raw_tiltseries

    ali_tiltseries = Model("aligned tiltseries", session)
    session.models.add([ali_tiltseries])
    session.inspectet.aligned_tiltseries = ali_tiltseries

    if ts_file:
        from chimerax.open_command.cmd import cmd_open

        models = cmd_open(session, [ts_file], "", log=True)
        ts = models[0]
        mat = ts.data.matrix()

        for z in range(mat.shape[0]):
            data = mat[z, :, :]
            data = np.expand_dims(data, axis=0)

            from chimerax.map_data import ArrayGridData
            from chimerax.map import volume_from_grid_data

            im_data = ArrayGridData(data, origin=(0, 0, 0), step=ts.data.step)
            im = volume_from_grid_data(im_data, session, style="image", open_model=False)
            im.name = f"aligned image {z}"
            ali_tiltseries.add([im])
            im.display = False

            im_size = im.data.ijk_to_xyz((im.data.size[0], im.data.size[1], 5))

            fake_im = get_box_model(session, im_size, name="raw_image", color="grey", transparency=0.9)
            fake_im.name = f"raw image {z}"
            raw_tiltseries.add([fake_im])
            fake_im.display = False

            # General Alignment
            pos = translation((-im_size[0] / 2, -im_size[1] / 2, z_offset))
            im.position = pos

            pos2 = translation((0, 0, z_offset))
            fake_im.position = pos2

            from chimerax.core.commands import run

            run(
                session,
                f"volume #{im.id_string} style image colorMode l8 color white",
                log=True,
            )

        # Per image alignment
        for psap in alignment.per_section_alignment_parameters:
            im = ali_tiltseries.child_models()[psap.z_index]

            im_size = im.data.ijk_to_xyz((im.data.size[0], im.data.size[1], 0))
            pos = translation((-im_size[0] / 2, -im_size[1] / 2, z_offset))
            print("shifts: ", (-psap.x_offset * im.data.step[0], -psap.y_offset * im.data.step[1], 0))
            off = translation((-psap.x_offset * im.data.step[0], -psap.y_offset * im.data.step[1], 0))
            rot = rotation((0, 0, 1), -psap.tilt_axis_rotation)

            im.position = rot * off * pos
            im.display = False

        ts.delete()

    else:
        max_z = max([psap.z_index for psap in alignment.per_section_alignment_parameters])

        for z in range(max_z + 1):
            im_size = (alignment.volume_dimension["x"], alignment.volume_dimension["y"], 20)
            im = get_box_model(session, im_size, name="aligned_image", color="cyan")
            ali_tiltseries.add([im])
            im.display = False

            im_size = (alignment.volume_dimension["x"], alignment.volume_dimension["y"], 19)
            im2 = get_box_model(session, im_size, name="raw_image", color="grey", transparency=0.5, offset=(0, 0, 1))
            raw_tiltseries.add([im2])
            im2.display = False

            from chimerax.geometry import translation

            pos = translation((-im_size[0] / 2, -im_size[0] / 2, z_offset))
            im.position = pos

            pos2 = translation((0, 0, z_offset))
            im2.position = pos2

        for psap in alignment.per_section_alignment_parameters:
            im = ali_tiltseries.child_models()[psap.z_index]

            im_size = (alignment.volume_dimension["x"], alignment.volume_dimension["y"], 20)
            pos = translation((-im_size[0] / 2, -im_size[1] / 2, z_offset))
            off = translation((-psap.x_offset, -psap.y_offset, 0))
            rot = rotation((0, 0, 1), -psap.tilt_axis_rotation)

            im.position = rot * off * pos
            im.display = False


def apply_alignment(session, alignment, params):

    from chimerax.geometry import rotation, translation

    vol = session.inspectet.volume_model
    vol_size = (alignment.volume_dimension["x"], alignment.volume_dimension["y"], alignment.volume_dimension["z"])
    ico = session.inspectet.initial_coord_order
    vol.position = (
        rotation((0, 1, 0), params.tilt_angle)
        * session.inspectet.additional_rotation
        * translation((-vol_size[ico[0]] / 2, -vol_size[ico[1]] / 2, -vol_size[ico[2]] / 2))
    )

    ali_ts = session.inspectet.aligned_tiltseries
    raw_ts = session.inspectet.raw_tiltseries

    for idx, (ali_im, raw_im) in enumerate(zip(ali_ts.child_models(), raw_ts.child_models())):
        if idx == params.z_index:
            ali_im.display = True
            raw_im.display = True
        else:
            ali_im.display = False
            raw_im.display = False
