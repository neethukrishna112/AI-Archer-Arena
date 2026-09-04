
import random
import math

from direct.showbase.ShowBaseGlobal import globalClock
from panda3d.core import (
    CullFaceAttrib,
    Point3,
    PointLight,
    Material,
    Vec4,
    Geom,
    GeomNode,
    GeomVertexData,
    GeomVertexFormat,
    GeomVertexWriter,
    GeomVertexReader,
    GeomVertexRewriter,
    GeomTriangles,
)

def make_gem_material(
    color,
    metallic=0.65,
    roughness=0.22
):

    material = Material()

    material.set_base_color(
        Vec4(
            1.0,
            1.0,
            1.0,
            1.0
        )
    )

    material.set_emission(
        Vec4(
            color[0] * 0.08,
            color[1] * 0.08,
            color[2] * 0.08,
            1.0
        )
    )

    material.set_metallic(
        metallic
    )

    material.set_roughness(
        roughness
    )

    return material

def add_triangle(
    vertex_writer,
    normal_writer,
    triangle_writer,
    p1,
    p2,
    p3
):

    edge1 = (
        p2[0] - p1[0],
        p2[1] - p1[1],
        p2[2] - p1[2]
    )

    edge2 = (
        p3[0] - p1[0],
        p3[1] - p1[1],
        p3[2] - p1[2]
    )

    nx = (
        edge1[1] * edge2[2]
        - edge1[2] * edge2[1]
    )

    ny = (
        edge1[2] * edge2[0]
        - edge1[0] * edge2[2]
    )

    nz = (
        edge1[0] * edge2[1]
        - edge1[1] * edge2[0]
    )

    length = math.sqrt(
        nx * nx
        + ny * ny
        + nz * nz
    )

    if length == 0:

        length = 1.0

    nx /= length
    ny /= length
    nz /= length

    index = (
        vertex_writer.get_write_row()
    )

    vertex_writer.add_data3(
        p1[0],
        p1[1],
        p1[2]
    )

    normal_writer.add_data3(
        nx,
        ny,
        nz
    )

    vertex_writer.add_data3(
        p2[0],
        p2[1],
        p2[2]
    )

    normal_writer.add_data3(
        nx,
        ny,
        nz
    )

    vertex_writer.add_data3(
        p3[0],
        p3[1],
        p3[2]
    )

    normal_writer.add_data3(
        nx,
        ny,
        nz
    )

    triangle_writer.add_vertices(
        index,
        index + 1,
        index + 2
    )

def apply_gradient(
    vertex_data,
    name
):

    if name.lower() == "diamond":

        bottom_color = (
            0.02,
            0.12,
            0.55,
            1.0
        )

        top_color = (
            0.20,
            0.85,
            1.00,
            1.0
        )

    elif name.lower() == "gold":

        bottom_color = (
            0.55,
            0.18,
            0.01,
            1.0
        )

        top_color = (
            1.00,
            0.85,
            0.05,
            1.0
        )

    elif name.lower() == "silver":

        bottom_color = (
            0.25,
            0.32,
            0.45,
            1.0
        )

        top_color = (
            0.90,
            0.95,
            1.00,
            1.0
        )

    else:

        bottom_color = (
            0.45,
            0.08,
            0.01,
            1.0
        )

        top_color = (
            1.00,
            0.40,
            0.05,
            1.0
        )

    vertex_reader = GeomVertexReader(
        vertex_data,
        "vertex"
    )

    z_values = []

    while not vertex_reader.is_at_end():

        vertex = vertex_reader.get_data3()

        z_values.append(
            vertex[2]
        )

    if not z_values:

        return

    minimum_z = min(
        z_values
    )

    maximum_z = max(
        z_values
    )

    height = (
        maximum_z
        - minimum_z
    )

    if height == 0:

        height = 1.0

    color_rewriter = GeomVertexRewriter(
        vertex_data,
        "color"
    )

    vertex_reader = GeomVertexReader(
        vertex_data,
        "vertex"
    )

    while not vertex_reader.is_at_end():

        vertex = vertex_reader.get_data3()

        factor = (
            vertex[2]
            - minimum_z
        ) / height
        factor = max(
            0.0,
            min(
                1.0,
                factor
            )
        )

        red = (
            bottom_color[0]
            + (
                top_color[0]
                - bottom_color[0]
            )
            * factor
        )

        green = (
            bottom_color[1]
            + (
                top_color[1]
                - bottom_color[1]
            )
            * factor
        )

        blue = (
            bottom_color[2]
            + (
                top_color[2]
                - bottom_color[2]
            )
            * factor
        )

        color_rewriter.set_data4(
            red,
            green,
            blue,
            1.0
        )

def create_faceted_stone(
    game,
    name
):

    format = GeomVertexFormat.get_v3n3c4()

    vertex_data = GeomVertexData(
        name + "_Stone",
        format,
        Geom.UH_static
    )

    vertex_writer = GeomVertexWriter(
        vertex_data,
        "vertex"
    )

    normal_writer = GeomVertexWriter(
        vertex_data,
        "normal"
    )

    color_writer = GeomVertexWriter(
        vertex_data,
        "color"
    )

    triangles = GeomTriangles(
        Geom.UH_static
    )

    if name.lower() == "diamond":

        top = (
            0.0,
            0.0,
            1.35
        )

        bottom = (
            0.0,
            0.0,
            -1.35
        )

        ring = [

            (
                0.95,
                0.0,
                0.15
            ),

            (
                0.48,
                0.48,
                0.15
            ),

            (
                0.0,
                0.95,
                0.15
            ),

            (
                -0.48,
                0.48,
                0.15
            ),

            (
                -0.95,
                0.0,
                0.15
            ),

            (
                -0.48,
                -0.48,
                0.15
            ),

            (
                0.0,
                -0.95,
                0.15
            ),

            (
                0.48,
                -0.48,
                0.15
            )
        ]

        lower_ring = [

            (
                0.62,
                0.0,
                -0.35
            ),

            (
                0.31,
                0.31,
                -0.35
            ),

            (
                0.0,
                0.62,
                -0.35
            ),

            (
                -0.31,
                0.31,
                -0.35
            ),

            (
                -0.62,
                0.0,
                -0.35
            ),

            (
                -0.31,
                -0.31,
                -0.35
            ),

            (
                0.0,
                -0.62,
                -0.35
            ),

            (
                0.31,
                -0.31,
                -0.35
            )
        ]

        for i in range(8):

            next_i = (
                i + 1
            ) % 8

            add_triangle(
                vertex_writer,
                normal_writer,
                triangles,
                top,
                ring[i],
                ring[next_i]
            )

            add_triangle(
                vertex_writer,
                normal_writer,
                triangles,
                ring[i],
                lower_ring[i],
                lower_ring[next_i]
            )

            add_triangle(
                vertex_writer,
                normal_writer,
                triangles,
                ring[i],
                lower_ring[next_i],
                ring[next_i]
            )

            add_triangle(
                vertex_writer,
                normal_writer,
                triangles,
                bottom,
                lower_ring[next_i],
                lower_ring[i]
            )

    else:

        if name.lower() == "gold":

            top_z = 1.05
            middle_radius = 1.05
            lower_radius = 0.82
            bottom_z = -0.85

        elif name.lower() == "silver":

            top_z = 1.00
            middle_radius = 1.00
            lower_radius = 0.78
            bottom_z = -0.95

        else:
            top_z = 0.95
            middle_radius = 1.10
            lower_radius = 0.82
            bottom_z = -0.90

        top = (
            0.0,
            0.0,
            top_z
        )

        bottom = (
            0.0,
            0.0,
            bottom_z
        )

        ring = []

        lower_ring = []

        for i in range(8):

            angle = (
                math.pi * 2.0
                * i
                / 8.0
            )

            variation = random.uniform(
                0.90,
                1.10
            )

            x = (
                math.cos(angle)
                * middle_radius
                * variation
            )

            y = (
                math.sin(angle)
                * middle_radius
                * variation
            )

            z = random.uniform(
                -0.10,
                0.25
            )

            ring.append(
                (
                    x,
                    y,
                    z
                )
            )

            lower_variation = random.uniform(
                0.92,
                1.08
            )

            lx = (
                math.cos(angle)
                * lower_radius
                * lower_variation
            )

            ly = (
                math.sin(angle)
                * lower_radius
                * lower_variation
            )

            lower_ring.append(
                (
                    lx,
                    ly,
                    -0.40
                    + random.uniform(
                        -0.08,
                        0.08
                    )
                )
            )

        for i in range(8):

            next_i = (
                i + 1
            ) % 8
            add_triangle(
                vertex_writer,
                normal_writer,
                triangles,
                top,
                ring[i],
                ring[next_i]
            )
            add_triangle(
                vertex_writer,
                normal_writer,
                triangles,
                ring[i],
                lower_ring[i],
                lower_ring[next_i]
            )

            add_triangle(
                vertex_writer,
                normal_writer,
                triangles,
                ring[i],
                lower_ring[next_i],
                ring[next_i]
            )
            add_triangle(
                vertex_writer,
                normal_writer,
                triangles,
                bottom,
                lower_ring[next_i],
                lower_ring[i]
            )

    vertex_count = (
        vertex_data.get_num_rows()
    )

    for i in range(
        vertex_count
    ):

        color_writer.add_data4(
            1.0,
            1.0,
            1.0,
            1.0
        )

    apply_gradient(
        vertex_data,
        name
    )

    geom = Geom(
        vertex_data
    )

    geom.add_primitive(
        triangles
    )

    node = GeomNode(
        name + "_Stone"
    )

    node.add_geom(
        geom
    )

    stone = game.render.attach_new_node(
        node
    )

    return stone

class GlowingTarget:

    def __init__(
        self,
        game,
        name,
        position,
        base_color,
        points
    ):

        self.game = game
        self.name = name
        self.base_color = base_color

        self.points = points

        self.root = (
            game.render.attach_new_node(
                name
            )
        )

        self.root.set_pos(
            position[0],
            position[1],
            position[2]
        )

        self.root.set_tag(
            "target",
            name
        )

        self.cube = create_faceted_stone(
            game,
            name
        )

        self.cube.reparent_to(
            self.root
        )

        if name.lower() == "diamond":

            self.cube.set_scale(
                0.80,
                0.50,
                0.80
            )

        elif name.lower() == "gold":

            self.cube.set_scale(
                0.80,
                0.52,
                0.73
            )

        elif name.lower() == "silver":

            self.cube.set_scale(
                0.77,
                0.50,
                0.70
            )

        else:
            self.cube.set_scale(
                0.80,
                0.52,
                0.70
            )

        self.cube.set_hpr(
            0,
            0,
            0
        )

        self.cube.set_texture_off(
            1
        )

        if name.lower() == "diamond":

            target_color = (
                0.25,
                0.65,
                1.00
            )

            metallic = 0.15
            roughness = 0.15

        elif name.lower() == "gold":

            target_color = (
                1.00,
                0.68,
                0.08
            )

            metallic = 0.40
            roughness = 0.20

        elif name.lower() == "silver":

            target_color = (
                0.75,
                0.80,
                0.88
            )

            metallic = 0.45
            roughness = 0.18

        else:
            target_color = (
                0.85,
                0.38,
                0.10
            )

            metallic = 0.35
            roughness = 0.24

        self.cube.set_material(
            make_gem_material(
                target_color,
                metallic,
                roughness
            )
        )

        self.cube.set_color_scale(
            1.0,
            1.0,
            1.0,
            1.0
        )

        self.cube.set_two_sided(
            True
        )

        self.cube.set_attrib(
            CullFaceAttrib.make(
                CullFaceAttrib.MCullNone
            )
        )

        if name.lower() == "diamond":

            light_color = Vec4(
                0.30,
                0.80,
                1.00,
                1.0
            )

        elif name.lower() == "gold":

            light_color = Vec4(
                1.00,
                0.75,
                0.20,
                1.0
            )

        elif name.lower() == "silver":

            light_color = Vec4(
                0.75,
                0.85,
                1.00,
                1.0
            )

        else:
            light_color = Vec4(
                1.00,
                0.35,
                0.10,
                1.0
            )

        self.target_light = PointLight(
            name + "_Light"
        )

        self.target_light.set_color(
            light_color
        )

        self.target_light.set_attenuation(
            (
                1.0,
                0.025,
                0.001
            )
        )

        self.target_light_node = (
            self.root.attach_new_node(
                self.target_light
            )
        )
        self.target_light_node.set_pos(
            0.0,
            0.0,
            2.8
        )

        self.game.render.set_light(
            self.target_light_node
        )

        self.destination = Point3(
            position[0],
            position[1],
            position[2]
        )

        self.speed = random.uniform(
            0.8,
            1.5
        )

        self.choose_new_destination()

        game.taskMgr.add(
            self.update,
            "TargetMovement_" + name
        )

    def choose_new_destination(
        self
    ):

        self.destination = Point3(
            random.uniform(
                -6.0,
                6.0
            ),
            random.uniform(
                3.0,
                9.0
            ),
            self.game.ground_z
            + random.uniform(
                10.0,
                14.0
            )
        )

        self.speed = random.uniform(
            0.8,
            1.5
        )

    def update(
        self,
        task
    ):

        dt = globalClock.getDt()

        current_position = (
            self.root.get_pos()
        )

        direction = (
            self.destination
            - current_position
        )

        distance = direction.length()

        if distance < 0.15:

            self.choose_new_destination()

        else:

            direction.normalize()

            movement = (
                self.speed
                * dt
            )

            if movement > distance:

                movement = distance

            self.root.set_pos(
                current_position
                + direction
                * movement
            )

        return task.cont

    def get_pos(
        self
    ):

        return self.root.get_pos()

    def get_name(
        self
    ):

        return self.name

    def get_value(
        self
    ):

        return self.points

    def get_node(
        self
    ):

        return self.root

    def remove(
        self
    ):

        if not self.root.is_empty():
            if hasattr(
                self,
                "target_light_node"
            ):

                self.game.render.clear_light(
                    self.target_light_node
                )

                self.target_light_node.remove_node()

            self.root.remove_node()