from panda3d.core import (
    Point3,
    LineSegs,
    TransparencyAttrib,
    PointLight,
    Vec4,
)


class LightProjectile:

    def __init__(
        self,
        game,
        start_position,
        target,
        speed=22.0,
        on_hit=None,
        miss_radius=1.0,
        agent_name="Unknown Agent"
    ):

        self.game = game
        self.target = target
        self.speed = speed
        self.active = True
        self.on_hit = on_hit

        self.agent_name = agent_name

        self.miss_radius = miss_radius

        self.node = (
            game.render.attach_new_node(
                "LightArrow"
            )
        )

        self.node.set_pos(
            start_position
        )

        if self.target is not None:

            target_position = (
                self.target.get_pos()
            )

            self.aim_position = Point3(
                target_position.x,
                target_position.y,
                target_position.z
            )

        else:

            self.aim_position = Point3(
                start_position.x,
                start_position.y,
                start_position.z
            )

        arrow = LineSegs(
            "RedLightArrow"
        )

        arrow.set_thickness(
            3.5
        )

        arrow.set_color(
            1.0,
            0.05,
            0.02,
            1.0
        )

        arrow.move_to(
            0.0,
            -0.35,
            0.0
        )

        arrow.draw_to(
            0.0,
            0.45,
            0.0
        )

        arrow.move_to(
            0.0,
            0.45,
            0.0
        )

        arrow.draw_to(
            -0.13,
            0.25,
            0.0
        )

        arrow.move_to(
            0.0,
            0.45,
            0.0
        )

        arrow.draw_to(
            0.13,
            0.25,
            0.0
        )

        arrow_node = (
            arrow.create()
        )

        self.arrow = (
            self.node.attach_new_node(
                arrow_node
            )
        )

        self.arrow.set_light_off()

        glow = LineSegs(
            "RedLightArrowGlow"
        )

        glow.set_thickness(
            9.0
        )

        glow.set_color(
            1.0,
            0.0,
            0.0,
            0.22
        )

        glow.move_to(
            0.0,
            -0.28,
            0.0
        )

        glow.draw_to(
            0.0,
            0.42,
            0.0
        )

        glow.move_to(
            0.0,
            0.42,
            0.0
        )

        glow.draw_to(
            -0.17,
            0.22,
            0.0
        )

        glow.move_to(
            0.0,
            0.42,
            0.0
        )

        glow.draw_to(
            0.17,
            0.22,
            0.0
        )

        glow_node = (
            glow.create()
        )

        self.glow = (
            self.node.attach_new_node(
                glow_node
            )
        )

        self.glow.set_transparency(
            TransparencyAttrib.M_alpha
        )

        self.glow.set_depth_write(
            False
        )

        self.glow.set_bin(
            "fixed",
            10
        )

        self.glow.set_light_off()

        self.projectile_light = PointLight(
            "ProjectileLight"
        )

        self.projectile_light.set_color(
            Vec4(
                1.0,
                0.02,
                0.01,
                1.0
            )
        )

        self.projectile_light.set_attenuation(
            Point3(
                1.0,
                0.12,
                0.01
            )
        )

        self.projectile_light_node = (
            self.node.attach_new_node(
                self.projectile_light
            )
        )

        self.projectile_light_node.set_pos(
            0,
            0,
            0
        )

        self.game.render.set_light(
            self.projectile_light_node
        )

        direction = (
            self.aim_position
            - Point3(
                start_position.x,
                start_position.y,
                start_position.z
            )
        )

        if direction.length() > 0.001:

            self.node.look_at(
                Point3(
                    start_position.x
                    + direction.x,

                    start_position.y
                    + direction.y,

                    start_position.z
                    + direction.z
                )
            )

        print(
            "RED LIGHT ARROW CREATED"
        )

        print(
            "Agent:",
            self.agent_name
        )

        print(
            "Start:",
            start_position
        )

        if self.target is not None:

            print(
                "Target:",
                self.target.get_name()
            )

        print(
            "LOCKED AIM POSITION:",
            self.aim_position
        )

        print(
            "MISS RADIUS:",
            self.miss_radius
        )

    def update(
        self,
        dt
    ):

        if not self.active:

            return False

        if self.node.isEmpty():

            self.active = False

            return False

        current_pos = (
            self.node.get_pos()
        )

        direction = (
            self.aim_position
            - Point3(
                current_pos.x,
                current_pos.y,
                current_pos.z
            )
        )

        distance = (
            direction.length()
        )

        if distance < 0.15:

            hit = False
            target_distance = None
            current_target_position = None

            # Maximum movement allowed for the target
            # after the projectile has been fired.
            allowed_movement = 1.0

            if self.target is not None:

                current_target_position = (
                    self.target.get_pos()
                )

                # Calculate how far the target moved
                # from the original locked aim position.
                target_distance = (
                    current_target_position
                    - self.aim_position
                ).length()

                # HIT only if the target movement
                # is within the allowed movement.
                if target_distance <= allowed_movement:

                    hit = True

                else:

                    hit = False

            if hit:

                print(
                    "========================================"
                )

                print(
                    "PROJECTILE HIT"
                )

                print(
                    "Agent:",
                    self.agent_name
                )

                print(
                    "Target:",
                    self.target.get_name()
                )

                print(
                    "Original Aim:",
                    self.aim_position
                )

                print(
                    "Current Target:",
                    current_target_position
                )

                print(
                    "Target Movement:",
                    round(
                        target_distance,
                        3
                    )
                )

                print(
                    "Allowed Movement:",
                    allowed_movement
                )

                print(
                    "========================================"
                )

            else:

                print(
                    "========================================"
                )

                print(
                    "PROJECTILE MISS"
                )

                print(
                    "Agent:",
                    self.agent_name
                )

                if self.target is not None:

                    print(
                        "Target:",
                        self.target.get_name()
                    )

                    print(
                        "Original Aim:",
                        self.aim_position
                    )

                    print(
                        "Current Target:",
                        current_target_position
                    )

                    if target_distance is not None:

                        print(
                            "Target Movement:",
                            round(
                                target_distance,
                                3
                            )
                        )

                    print(
                        "Allowed Movement:",
                        allowed_movement
                    )

                print(
                    "========================================"
                )

            if self.on_hit is not None:

                self.on_hit(
                    self.target,
                    hit
                )

            self.remove()

            return False

        if distance > 0:

            direction.normalize()

        movement = (
            self.speed
            * dt
        )

        if movement > distance:

            movement = distance

        new_position = (
            Point3(
                current_pos.x,
                current_pos.y,
                current_pos.z
            )
            +
            direction
            *
            movement
        )

        self.node.set_pos(
            new_position
        )

        if direction.length() > 0.001:

            self.node.look_at(
                new_position
                + direction
            )

        return True

    def remove(
        self
    ):

        if not self.node.isEmpty():

            self.game.render.clear_light(
                self.projectile_light_node
            )

            self.node.remove_node()

        self.active = False