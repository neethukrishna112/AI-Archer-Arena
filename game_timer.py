from direct.showbase.ShowBaseGlobal import globalClock
from direct.gui.DirectGui import (
    DirectFrame,
    DirectLabel,
)

from panda3d.core import (
    TextNode,
)


class GameTimer:

    def __init__(
        self,
        game,
        duration=60
    ):

        self.game = game

        self.duration = float(duration)

        self.remaining_time = float(duration)

        self.running = False

        self.finished = False

        self.panel = DirectFrame(

            frameColor=(
                0.015,
                0.025,
                0.045,
                0.90
            ),

            frameSize=(
                -0.18,
                0.18,
                -0.075,
                0.075
            ),

            pos=(
                0,
                0,
                0.88
            )
        )

        self.title = DirectLabel(

            parent=self.panel,

            text="BATTLE TIME",

            text_scale=0.045,

            text_fg=(
                1.0,
                1.0,
                1.0,
                2
            ),

            text_align=TextNode.ACenter,

            relief=None,

            pos=(
                0,
                0,
                0.025
            )
        )

        self.time_label = DirectLabel(

            parent=self.panel,

            text=self.format_time(
                self.remaining_time
            ),

            text_scale=0.075,

            text_fg=(
                1,
                1,
                1,
                1
            ),

            text_align=TextNode.ACenter,

            relief=None,

            pos=(
                0,
                0,
                -0.045
            )
        )

        self.game.taskMgr.add(
            self.wait_for_game_start,
            "WaitForGameStart"
        )

    def wait_for_game_start(
        self,
        task
    ):

        if getattr(
            self.game,
            "agents_can_shoot",
            False
        ):

            self.start()

            return task.done

        return task.cont

    def format_time(
        self,
        seconds
    ):

        seconds = max(
            0,
            int(seconds)
        )

        minutes = seconds // 60

        seconds = seconds % 60

        return (
            f"{minutes:02d}:{seconds:02d}"
        )

    def start(
        self
    ):

        if self.running:

            return

        if self.finished:

            return

        self.running = True

        self.task = (
            self.game.taskMgr.add(
                self.update,
                "GameTimerTask"
            )
        )

        print()
        print(
            "=============================================="
        )

        print(
            "BATTLE TIMER STARTED"
        )

        print(
            "DURATION:",
            int(self.duration),
            "SECONDS"
        )

        print(
            "=============================================="
        )

    def update(
        self,
        task
    ):

        if not self.running:

            return task.done

        dt = globalClock.getDt()

        self.remaining_time -= dt

        if self.remaining_time <= 0:

            self.remaining_time = 0

            self.game.stop_game()

            self.time_label["text"] = (
                self.format_time(
                    self.remaining_time
                )
            )

            self.running = False

            self.finished = True

            print()
            print(
                "=============================================="
            )

            print(
                "TIME UP"
            )

            print(
                "BATTLE TIMER FINISHED"
            )

            print(
                "=============================================="
            )

            return task.done

        self.time_label["text"] = (
            self.format_time(
                self.remaining_time
            )
        )

        if self.remaining_time <= 10:

            self.time_label["text_scale"] = 0.085

            self.time_label["text_fg"] = (
                1.0,
                0.25,
                0.25,
                1
            )

        else:

            self.time_label["text_scale"] = 0.075

            self.time_label["text_fg"] = (
                1.0,
                1.0,
                1.0,
                1
            )

        return task.cont

    def pause(
        self
    ):

        self.running = False

    def resume(
        self
    ):

        if self.finished:

            return

        self.running = True

    def reset(
        self,
        duration=None
    ):

        if duration is not None:

            self.duration = float(
                duration
            )

        if hasattr(
            self,
            "task"
        ):

            try:

                self.game.taskMgr.remove(
                    self.task
                )

            except:

                pass

            self.task = None

        self.remaining_time = (
            self.duration
        )

        self.running = False

        self.finished = False

        self.time_label["text"] = (
            self.format_time(
                self.remaining_time
            )
        )

        self.time_label["text_scale"] = 0.075

        self.time_label["text_fg"] = (
            1.0,
            1.0,
            1.0,
            1
        )

        self.start()

    def is_running(
        self
    ):

        return self.running

    def is_finished(
        self
    ):

        return self.finished

    def get_remaining_time(
        self
    ):

        return self.remaining_time