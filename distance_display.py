
from direct.gui.DirectGui import DirectLabel
from panda3d.core import Vec3


class DistanceDisplay:

    def __init__(self, game):

        self.game = game

        self.left_title = DirectLabel(

            text="DISTANCES",

            scale=0.035,

            pos=(
                -1.38,
                0,
                -0.30
            ),

            text_fg=(
                1,
                1,
                1,
                1
            ),

            frameColor=(
                0,
                0,
                0,
                0
            ),

            relief=None
        )

        self.left_distance_label = DirectLabel(

            text="",

            scale=0.030,

            pos=(
                -1.38,
                0,
                -0.39
            ),

            text_fg=(
                1,
                1,
                1,
                1
            ),

            frameColor=(
                0,
                0,
                0,
                0
            ),

            relief=None,

            text_align=0
        )

        self.right_title = DirectLabel(

            text="DISTANCES",

            scale=0.035,

            pos=(
                1.15,
                0,
                -0.30
            ),

            text_fg=(
                1,
                1,
                1,
                1
            ),

            frameColor=(
                0,
                0,
                0,
                0
            ),

            relief=None
        )

        self.right_distance_label = DirectLabel(

            text="",

            scale=0.030,

            pos=(
                1.15,
                0,
                -0.39
            ),

            text_fg=(
                1,
                1,
                1,
                1
            ),

            frameColor=(
                0,
                0,
                0,
                0
            ),

            relief=None,

            text_align=0
        )

        self.game.taskMgr.add(

            self.update_distances,

            "UpdateDistanceDisplay"
        )
        self.update_display()

    def get_node(self, object):

        if hasattr(object, "get_pos"):

            return object

        if hasattr(object, "node"):

            node = object.node

            if hasattr(node, "get_pos"):

                return node

        return None

    def get_world_position(self, object):

        node = self.get_node(object)

        if node is None:

            return Vec3(0, 0, 0)

        try:

            return node.get_pos(
                self.game.render
            )

        except:

            try:

                return node.get_pos()

            except:

                return Vec3(0, 0, 0)

    def calculate_distance(
        self,
        agent,
        target
    ):

        agent_position = (
            self.get_world_position(agent)
        )

        target_position = (
            self.get_world_position(target)
        )

        distance = (
            agent_position
            - target_position
        ).length()

        return distance

    def update_display(self):

        left_lines = []

        for target in self.game.targets:

            distance = self.calculate_distance(
                self.game.warrior1,
                target
            )

            target_name = target.get_name()

            left_lines.append(

                f"{target_name:<8} "
                f"{distance:6.2f} units"
            )

        right_lines = []

        for target in self.game.targets:

            distance = self.calculate_distance(
                self.game.warrior2,
                target
            )

            target_name = target.get_name()

            right_lines.append(

                f"{target_name:<8} "
                f"{distance:6.2f} units"
            )

        self.left_distance_label["text"] = (
            "\n".join(left_lines)
        )

        self.right_distance_label["text"] = (
            "\n".join(right_lines)
        )

    def update_distances(self, task):

        self.update_display()

        return task.cont

    def destroy(self):

        self.left_title.destroy()

        self.left_distance_label.destroy()

        self.right_title.destroy()

        self.right_distance_label.destroy()