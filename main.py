
from direct.showbase.ShowBaseGlobal import globalClock
from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    AmbientLight,
    DirectionalLight,
    PointLight,
    Vec4,
    Material,
    Filename,
    TextureStage,
    CullFaceAttrib,
    TransparencyAttrib,
    AnimControlCollection,
    autoBind,
    Point3,
    Geom,
    GeomNode,
    GeomTriangles,
    GeomVertexData,
    GeomVertexFormat,
    GeomVertexWriter,
)

import panda3d.core as p3d
import simplepbr
import os
import random
import math

from projectile import LightProjectile
from target import GlowingTarget
from agent import ArcherAgent
from scoreboard import ScoreBoard
from event_log import EventLog
from game_timer import GameTimer
from distance_display import DistanceDisplay


class ArcherArena(ShowBase):

    def __init__(self):
        super().__init__()

        self.set_background_color(0.02, 0.035, 0.06)

        self.disableMouse()

        self.camera.set_pos(0, -45, 7)

        self.camera.look_at(0, 0, 3)

        self.ground = self.loader.loadModel("models/box")

        self.ground.reparentTo(self.render)

        self.ground_scale_x = 68
        self.ground_scale_y = 33

        self.ground.set_scale(
            self.ground_scale_x,
            self.ground_scale_y,
            0.5
        )

        self.ground_z = -0.5

        self.ground.set_pos(
            -self.ground_scale_x / 2.0,
            -self.ground_scale_y / 2.0,
            self.ground_z
        )

        self.ground.set_color(
            0.15,
            0.45,
            0.15,
            1
        )

        self.ground.clear_texture()

        ground_mat = p3d.Material()

        ground_mat.set_base_color(
            Vec4(
                0.15,
                0.45,
                0.15,
                1
            )
        )

        self.ground.set_material(
            ground_mat
        )

        self.left_wall = self.loader.loadModel(
            "models/box"
        )

        self.left_wall.reparentTo(
            self.render
        )

        self.left_wall.set_scale(
            0.5,
            self.ground_scale_y,
            8.0
        )

        self.left_wall.set_pos(
            -self.ground_scale_x / 2.0,
            -self.ground_scale_y / 2.0,
            7.5
        )

        self.left_wall.set_color(
            0.25,
            0.03,
            0.04,
            1
        )

        self.right_wall = self.loader.loadModel(
            "models/box"
        )

        self.right_wall.reparentTo(
            self.render
        )

        self.right_wall.set_scale(
            0.5,
            self.ground_scale_y,
            8.0
        )

        self.right_wall.set_pos(
            self.ground_scale_x / 2.0,
            -self.ground_scale_y / 2.0,
            7.5
        )

        self.right_wall.set_color(
            0.10,
            0.12,
            0.16,
            1
        )

        ambient = AmbientLight(
            "ambient"
        )

        ambient.set_color(
            Vec4(
                0.7,
                0.7,
                0.7,
                1
            )
        )

        ambient_node = (
            self.render.attach_new_node(
                ambient
            )
        )

        self.render.set_light(
            ambient_node
        )

        sun = DirectionalLight(
            "sun"
        )

        sun.set_color(
            Vec4(
                1,
                1,
                1,
                1
            )
        )

        sun_node = (
            self.render.attach_new_node(
                sun
            )
        )

        sun_node.set_hpr(
         -45,
         -45,
         0
        )

        self.render.set_light(
         sun_node
        )

        self.sun_node = sun_node

        self.sun_angle = -45.0

        self.sun_direction = 1.0

        self.taskMgr.add(
          self.animate_sun_light,
          "AnimateSunLight"
        )

        print()
        print(
            "Initializing SimplePBR..."
        )

        simplepbr.init()

        print(
            "SimplePBR initialized successfully."
        )

        self.create_warriors()

        self.create_targets()

        self.scoreboard = ScoreBoard(
            self
        )

        self.event_log = EventLog(
          self
        )

        self.timer = GameTimer(
          self,
          60
        )
        self.game_stopped = False

        self.agent1 = ArcherAgent(
            self,
            "Agent 1",
            self.warrior1,
            self.targets,
            "LEFT"
        )

        self.agent2 = ArcherAgent(
            self,
            "Agent 2",
            self.warrior2,
            self.targets,
            "RIGHT"
        )

        self.distance_display = DistanceDisplay(
           self
        )

        self.projectiles = []

        self.taskMgr.add(
            self.update_projectiles,
            "ProjectileUpdateTask"
        )

        self.accept(
            "space",
            self.test_shoot
        )

        self.is_dragging = False

        self.last_mouse_y = 0.0

        self.accept(
            "mouse1",
            self.start_drag
        )

        self.accept(
            "mouse1-up",
            self.stop_drag
        )

        self.taskMgr.add(
            self.drag_update_task,
            "DragUpdateTask"
        )

    def animate_sun_light(
        self,
        task
    ):

        dt = globalClock.getDt()

        self.sun_angle += (
            25.0
            * self.sun_direction
            * dt
        )

        if self.sun_angle >= 60.0:

            self.sun_angle = 60.0

            self.sun_direction = -1.0

        elif self.sun_angle <= -60.0:

            self.sun_angle = -60.0

            self.sun_direction = 1.0

        self.sun_node.set_hpr(
            self.sun_angle,
            -65,
            0
        )

        return task.cont

    def create_warriors(self):

        warrior_model_path = (
            "assets/warriors/"
            "warrior_with_bow_fixed.glb"
        )

        print()
        print(
            "=============================================="
        )

        print(
            "Loading NEW animated warrior:"
        )

        print(
            warrior_model_path
        )

        print(
            "=============================================="
        )

        if not os.path.exists(
            warrior_model_path
        ):

            print(
                "ERROR: New warrior GLB not found!"
            )

            self.warrior1 = (
                self.create_placeholder_warrior(
                    "Warrior1",
                    -8,
                    0.9,
                    0.2,
                    0.2
                )
            )

            self.warrior2 = (
                self.create_placeholder_warrior(
                    "Warrior2",
                    8,
                    0.2,
                    0.3,
                    0.9
                )
            )

            return

        print()
        print(
            "----------------------------------------------"
        )

        print(
            "Loading Warrior 1..."
        )

        print(
            "----------------------------------------------"
        )

        infile = (
            p3d.Filename.from_os_specific(
                os.path.abspath(
                    warrior_model_path
                )
            )
        )

        p3d.get_model_path().prepend_directory(
            infile.get_dirname()
        )

        self.warrior1 = (
            self.loader.loadModel(
                infile,
                noCache=True
            )
        )

        print(
            "Warrior 1 empty:",
            self.warrior1.isEmpty()
        )

        if self.warrior1.isEmpty():

            print(
                "ERROR: Warrior 1 could not be loaded."
            )

            self.warrior1 = (
                self.create_placeholder_warrior(
                    "Warrior1",
                    -8,
                    0.9,
                    0.2,
                    0.2
                )
            )

        else:

            self.warrior1.reparentTo(
                self.render
            )

            self.warrior1.set_scale(
                4.5
            )

            self.warrior1.set_pos(
                -11,
                0,
                0
            )

            self.warrior1.set_hpr(
                90,
                0,
                0
            )

            self.warrior1.clear_transparency()

            self.warrior1.set_transparency(
                TransparencyAttrib.M_none
            )

            self.warrior1.set_attrib(
                CullFaceAttrib.make(
                    CullFaceAttrib.MCullNone
                )
            )

            self.warrior1.clear_color_scale()

            self.warrior1.show()

            dress_parts = (
                self.warrior1.find_all_matches(
                    "**/Body"
                )
            )

            for part in dress_parts:

                part.set_color_scale(
                    0.45,
                    0.05,
                    0.08,
                    1.0
                )

            print(
                "Warrior 1 bounds:",
                self.warrior1.get_tight_bounds()
            )

            character_nodes = (
                self.warrior1.find_all_matches(
                    "**/+Character"
                )
            )

            print(
                "Warrior 1 Character nodes:",
                character_nodes.get_num_paths()
            )

            self.warrior1_anims = (
                AnimControlCollection()
            )

            autoBind(
                self.warrior1.node(),
                self.warrior1_anims,
                ~0
            )

            print(
                "Warrior 1 animations:",
                self.warrior1_anims.get_num_anims()
            )

            for i in range(
                self.warrior1_anims.get_num_anims()
            ):

                anim = (
                    self.warrior1_anims.get_anim(i)
                )

                print(
                    "  Animation",
                    i,
                    ":",
                    anim
                )

            self.warrior1_animation = None

            for i in range(
                self.warrior1_anims.get_num_anims()
            ):

                anim = (
                    self.warrior1_anims.get_anim(i)
                )

                if (
                    anim.get_name()
                    == "ArmatureAction.006"
                ):

                    self.warrior1_animation = anim

                    break

            if (
                self.warrior1_animation
                is not None
            ):

                self.warrior1_animation.play()

                print(
                    "Warrior 1 animation started:"
                )

                print(
                    "ArmatureAction.006"
                )

            else:

                print(
                    "WARNING: Warrior 1 animation "
                    "ArmatureAction.006 not found."
                )

        print()
        print(
            "----------------------------------------------"
        )

        print(
            "Loading Warrior 2..."
        )

        print(
            "----------------------------------------------"
        )

        self.warrior2 = (
            self.loader.loadModel(
                infile,
                noCache=True
            )
        )

        print(
            "Warrior 2 empty:",
            self.warrior2.isEmpty()
        )

        if self.warrior2.isEmpty():

            print(
                "ERROR: Warrior 2 could not be loaded."
            )

            self.warrior2 = (
                self.create_placeholder_warrior(
                    "Warrior2",
                    8,
                    0.2,
                    0.3,
                    0.9
                )
            )

        else:

            self.warrior2.reparentTo(
                self.render
            )

            self.warrior2.set_scale(
                4.5
            )

            self.warrior2.set_pos(
                11,
                0,
                0
            )

            self.warrior2.set_hpr(
                -90,
                0,
                0
            )

            self.warrior2.clear_transparency()

            self.warrior2.set_transparency(
                TransparencyAttrib.M_none
            )

            self.warrior2.set_attrib(
                CullFaceAttrib.make(
                    CullFaceAttrib.MCullNone
                )
            )

            self.warrior2.clear_color_scale()

            self.warrior2.show()

            print(
                "Warrior 2 bounds:",
                self.warrior2.get_tight_bounds()
            )

            character_nodes = (
                self.warrior2.find_all_matches(
                    "**/+Character"
                )
            )

            print(
                "Warrior 2 Character nodes:",
                character_nodes.get_num_paths()
            )

            self.warrior2_anims = (
                AnimControlCollection()
            )

            autoBind(
                self.warrior2.node(),
                self.warrior2_anims,
                ~0
            )

            print(
                "Warrior 2 animations:",
                self.warrior2_anims.get_num_anims()
            )

            for i in range(
                self.warrior2_anims.get_num_anims()
            ):

                anim = (
                    self.warrior2_anims.get_anim(i)
                )

                print(
                    "  Animation",
                    i,
                    ":",
                    anim
                )

            self.warrior2_animation = None

            for i in range(
                self.warrior2_anims.get_num_anims()
            ):

                anim = (
                    self.warrior2_anims.get_anim(i)
                )

                if (
                    anim.get_name()
                    == "ArmatureAction.006"
                ):

                    self.warrior2_animation = anim

                    break

            if (
                self.warrior2_animation
                is not None
            ):

                self.warrior2_animation.play()

                print(
                    "Warrior 2 animation started:"
                )

                print(
                    "ArmatureAction.006"
                )

            else:

                print(
                    "WARNING: Warrior 2 animation "
                    "ArmatureAction.006 not found."
                )

        print()
        print(
            "=============================================="
        )

        print(
            "WARRIOR LOADING COMPLETE"
        )

        print(
            "=============================================="
        )

        print(
            "Warrior 1:",
            self.warrior1
        )

        print(
            "Warrior 2:",
            self.warrior2
        )

        print()

    def apply_original_textures(
        self,
        model
    ):

        print()
        print(
            "----------------------------------------------"
        )

        print(
            "Checking warrior textures..."
        )

        print(
            "----------------------------------------------"
        )

        texture_folder = os.path.abspath(
            "assets/warriors"
        )

        geom_nodes = (
            model.find_all_matches(
                "**/+GeomNode"
            )
        )

        print(
            "Geometry nodes:",
            geom_nodes.get_num_paths()
        )

        texture_files = [
            "_01.png",
            "_02.png",
            "_03.png",
            "_04.png",
            "_05.png",
            "_06.png",
            "_07.png",
            "_08.png",
            "_09.png",
            "_10.png",
            "_11.png",
            "_12.png",
            "_13.png",
            "_14.png",
            "_15.png",
            "_16.png",
            "_17.png",
            "_18.png",
            "_19.png",
            "_20.png",
            "_21.png",
            "_22.png",
        ]

        print()
        print(
            "Checking texture files:"
        )

        for texture_file in texture_files:

            full_path = os.path.join(
                texture_folder,
                texture_file
            )

            if os.path.exists(
                full_path
            ):

                print(
                    "FOUND:",
                    texture_file
                )

            else:

                print(
                    "MISSING:",
                    texture_file
                )

        print()
        print(
            "----------------------------------------------"
        )

        print(
            "GLB materials/textures are being preserved."
        )

        print(
            "----------------------------------------------"
        )

        print()

    def create_placeholder_warrior(
        self,
        name,
        x,
        r,
        g,
        b
    ):

        warrior = (
            self.render.attach_new_node(
                name
            )
        )

        warrior.set_pos(
            x,
            0,
            self.ground_z + 0.5
        )

        body = self.loader.loadModel(
            "models/box"
        )

        body.reparentTo(
            warrior
        )

        body.set_scale(
            1.0,
            0.5,
            1.5
        )

        body.set_pos(
            0,
            0,
            2.0
        )

        body.set_color(
            r,
            g,
            b,
            1
        )

        head = self.loader.loadModel(
            "models/box"
        )

        head.reparentTo(
            warrior
        )

        head.set_scale(
            0.6,
            0.6,
            0.6
        )

        head.set_pos(
            0,
            0,
            4.2
        )

        head.set_color(
            0.9,
            0.6,
            0.4,
            1
        )

        leg1 = self.loader.loadModel(
            "models/box"
        )

        leg1.reparentTo(
            warrior
        )

        leg1.set_scale(
            0.3,
            0.3,
            1.0
        )

        leg1.set_pos(
            -0.45,
            0,
            0.5
        )

        leg1.set_color(
            0.1,
            0.1,
            0.1,
            1
        )

        leg2 = self.loader.loadModel(
            "models/box"
        )

        leg2.reparentTo(
            warrior
        )

        leg2.set_scale(
            0.3,
            0.3,
            1.0
        )

        leg2.set_pos(
            0.45,
            0,
            0.5
        )

        leg2.set_color(
            0.1,
            0.1,
            0.1,
            1
        )

        return warrior

    def create_targets(self):

        self.target_bronze = GlowingTarget(
            self,
            "Bronze",
            (
                -4.5,
                5.0,
                self.ground_z + 10.5
            ),
            (
                0.38,
    0.14,
    0.055
            ),
            10
        )

        self.target_silver = GlowingTarget(
            self,
            "Silver",
            (
                -1.5,
                6.0,
                self.ground_z + 12.0
            ),
            (
                 0.32,
                 0.38,
                 0.45
            ),
            20
        )

        self.target_gold = GlowingTarget(
            self,
            "Gold",
            (
                1.5,
                5.0,
                self.ground_z + 11.5
            ),
            (
                0.55,
                0.30,
                0.035
            ),
            30
        )

        self.target_diamond = GlowingTarget(
            self,
            "Diamond",
            (
                4.5,
                6.5,
                self.ground_z + 12.5
            ),
            (
                0.08,
                0.20,
                0.55
            ),
            50
        )

        self.targets = [
            self.target_bronze,
            self.target_silver,
            self.target_gold,
            self.target_diamond,
        ]

        print()
        print(
            "=============================================="
        )

        print(
            "4 GLOWING TARGETS CREATED"
        )

        print(
            "=============================================="
        )

        print(
            "Bronze  : HIGH"
        )

        print(
            "Silver  : HIGH"
        )

        print(
            "Gold    : HIGH"
        )

        print(
            "Diamond : HIGH"
        )

        print(
            "=============================================="
        )

    def start_drag(
        self
    ):

        if self.mouseWatcherNode.hasMouse():

            self.is_dragging = True

            self.last_mouse_y = (
                self.mouseWatcherNode.getMouseY()
            )

    def stop_drag(
        self
    ):

        self.is_dragging = False

    def drag_update_task(
        self,
        task
    ):

        if (
            self.is_dragging
            and self.mouseWatcherNode.hasMouse()
        ):

            current_mouse_y = (
                self.mouseWatcherNode.getMouseY()
            )

            delta_y = (
                current_mouse_y
                - self.last_mouse_y
            )

            movement_speed = 10.0

            self.ground_z += (
                delta_y
                * movement_speed
            )

            if self.ground_z > 4.0:

                self.ground_z = 4.0

            elif self.ground_z < -5.0:

                self.ground_z = -5.0

            self.update_arena_positions()

            self.last_mouse_y = (
                current_mouse_y
            )

        return task.cont

    def update_arena_positions(
        self
    ):

        self.ground.set_pos(
            -self.ground_scale_x / 2.0,
            -self.ground_scale_y / 2.0,
            self.ground_z
        )

        self.place_model_on_ground(
            self.warrior1
        )

        self.place_model_on_ground(
            self.warrior2
        )

    def place_model_on_ground(
        self,
        model
    ):

        bounds = (
            model.get_tight_bounds()
        )

        if bounds is None:

            print(
                "WARNING: Could not calculate model bounds."
            )

            return

        min_point = bounds[0]

        current_bottom_z = (
            min_point.get_z()
        )

        desired_bottom_z = (
            self.ground_z
            + 0.5
            + 0.05
        )

        correction = (
            desired_bottom_z
            - current_bottom_z
        )

        model.set_z(
            model.get_z()
            + correction
        )

    def fire_light_projectile(
       self,
       warrior,
       target,
       side="LEFT"
    ):
        if self.game_stopped:
            return


        
        start_position = (
           self.get_bow_position(
             warrior
        )
        )

        miss_radius = 1.0

        def handle_hit(
           hit_target,
           was_hit
        ):
            if self.game_stopped:
                return

            target_name = (
               hit_target.get_name()
            )

            target_points = {
               "Bronze": 10,
                "Silver": 20,
                "Gold": 30,
                "Diamond": 50
            }

            points = target_points.get(
              target_name,
              0
            )

            if was_hit:

               self.event_log.add_event(
                  side,
                  "HIT "
                  + target_name
                  + " +"
                  + str(points)
                )

               if side == "LEFT":

                   self.scoreboard.add_left_score(
                      points
                    )

                   print(
                      "Agent 1 HIT",
                      target_name,
                      "and gained",
                      points,
                      "points"
                    )

               else:

                   self.scoreboard.add_right_score(
                       points
                    )

                   print(
                       "Agent 2 HIT",
                        target_name,
                        "and gained",
                        points,
                        "points"
                    )

               hit_target.choose_new_destination()

            else:

               self.event_log.add_event(
                   side,
                   "MISS " + target_name
                )

               if side == "LEFT":

                  print(
                    "Agent 1 MISSED",
                    target_name
                 )

               else:

                   print(
                    "Agent 2 MISSED",
                    target_name
                )

        projectile = LightProjectile(
          self,
          start_position,
          target,
          speed=22.0,
          on_hit=handle_hit,
          miss_radius=miss_radius,
          agent_name=(
              "Agent 1"
              if side == "LEFT"
              else "Agent 2"
          )
        )

        if projectile.active:

           self.projectiles.append(
             projectile
         )

    def trigger_warrior_shot(
        self,
        warrior,
        target,
        side
    ):

        animation = None

        if warrior is self.warrior1:

            animation = getattr(
                self,
                "warrior1_animation",
                None
            )

        elif warrior is self.warrior2:

            animation = getattr(
                self,
                "warrior2_animation",
                None
            )

        if (
            animation is not None
            and not animation.isPlaying()
        ):

            animation.play()

        self.taskMgr.doMethodLater(
            0.60,
            self.release_agent_shot,
            "ReleaseAgentShotTask_" + side,
            extraArgs=[
                warrior,
                target,
                side
            ],
            appendTask=False
        )

    def release_agent_shot(
        self,
        warrior,
        target,
        side
    ):  

        if self.game_stopped:
            return

        self.fire_light_projectile(
            warrior,
            target,
            side
        )

    def update_projectiles(
        self,
        task
    ):

        dt = globalClock.getDt()

        active_projectiles = []

        for projectile in self.projectiles:

            if projectile.update(
                dt
            ):

                active_projectiles.append(
                    projectile
                )

        self.projectiles = (
            active_projectiles
        )

        return task.cont

    def get_bow_position(
        self,
        warrior
    ):

        minimum, maximum = (
            warrior.get_tight_bounds()
        )

        x = (
            minimum.x
            + maximum.x
        ) / 2.0

        y = minimum.y

        z = (
            minimum.z
            + (
                maximum.z
                - minimum.z
            )
            * 0.72
        )

        position = Point3(
            x,
            y,
            z
        )

        print(
            "PROJECTILE START POSITION:",
            position
        )

        return position

    def test_shoot(
        self
    ):

        print()
        print(
            "=============================================="
        )

        print(
            "SPACE PRESSED - SHOOT"
        )

        print(
            "=============================================="
        )

        if (
            hasattr(
                self,
                "warrior1_animation"
            )
            and self.warrior1_animation
            is not None
        ):

            self.warrior1_animation.play()

        if (
            hasattr(
                self,
                "warrior2_animation"
            )
            and self.warrior2_animation
            is not None
        ):

            self.warrior2_animation.play()

        self.taskMgr.doMethodLater(
            0.60,
            self.release_space_shot,
            "ReleaseSpaceShotTask"
        )

    def release_space_shot(
        self,
        task
    ):

        print(
            "Bow and arrow reached release timing."
        )

        self.fire_light_projectile(
            self.warrior1,
            self.target_gold,
            "LEFT"
        )

        self.fire_light_projectile(
            self.warrior2,
            self.target_diamond,
            "RIGHT"
        )

        print(
            "Light projectiles released."
        )

        return None

    def stop_game(
        self
    ):

        if getattr(
            self,
            "game_stopped",
            False
        ):

            return

        self.game_stopped = True

        self.agents_can_shoot = False

        self.is_dragging = False

        print()
        print(
            "=============================================="
        )

        print(
            "GAME STOPPED - TIME UP"
        )

        print(
            "FINAL SCORE"
        )

        print(
            "=============================================="
        )

        if hasattr(
            self,
            "controller"
        ):

            self.controller.show_play_again()

    def reset_game(
        self
    ):

        print()
        print(
            "=============================================="
        )

        print(
            "RESETTING GAME"
        )

        print(
            "=============================================="
        )

        self.game_stopped = True

        self.agents_can_shoot = False

        for projectile in self.projectiles:

            try:

                projectile.remove()

            except:

                try:

                    projectile.node.remove_node()

                except:

                    pass

        self.projectiles = []

        self.scoreboard.left_score = 0
        self.scoreboard.right_score = 0

        if hasattr(
            self.scoreboard,
            "update_display"
        ):

            self.scoreboard.update_display()

        if hasattr(
            self.event_log,
            "clear_events"
        ):

            self.event_log.clear_events()

        self.warrior1.set_pos(
            -11,
            0,
            0
        )

        self.warrior1.set_hpr(
            90,
            0,
            0
        )

        self.warrior2.set_pos(
            11,
            0,
            0
        )

        self.warrior2.set_hpr(
            -90,
            0,
            0
        )

        self.ground_z = -0.5

        self.ground.set_pos(
            -self.ground_scale_x / 2.0,
            -self.ground_scale_y / 2.0,
            self.ground_z
        )

        for target in self.targets:

            try:

                target.choose_new_destination()

            except:

                pass

        if hasattr(
            self.timer,
            "reset"
        ):

            self.timer.reset()

        elif hasattr(
            self.timer,
            "time_left"
        ):

            self.timer.time_left = 60

        self.is_dragging = False

        print(
            "GAME RESET COMPLETE"
        )

if __name__ == "__main__":

    game = ArcherArena()

    game.run()