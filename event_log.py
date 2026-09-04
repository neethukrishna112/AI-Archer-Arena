
from direct.gui.DirectGui import (
    DirectFrame,
    DirectLabel,
)


class EventLog:

    def __init__(
        self,
        game
    ):

        self.game = game

        self.left_events = []
        self.right_events = []

        self.max_events = 5

        self.left_panel = DirectFrame(

            frameColor=(
                0.025,
                0.035,
                0.055,
                0.45
            ),

            frameSize=(
                -0.48,
                0.37,
                -0.105,
                0.105
            ),

            pos=(
                -1.72,
                0,
                0.88
            ),

            relief=1
        )

        self.left_title = DirectLabel(

            text="EVENT LOG",

            text_scale=0.032,

            text_fg=(
                1.0,
                1.0,
                1.0,
                1
            ),

            frameColor=(
                0,
                0,
                0,
                0
            ),

            pos=(
                0,
                0,
                0.070
            ),

            parent=self.left_panel
        )

        self.left_event_label = DirectLabel(

            text="Waiting for agent...",

            text_scale=0.03,

            text_fg=(
                1.0,
                0.2,
                0.2,
                1
            ),

            frameColor=(
                0,
                0,
                0,
                0
            ),

            text_align=0,

            text_wordwrap=18,

            pos=(
                -0.19,
                0,
                0.040
            ),

            parent=self.left_panel
        )

        self.right_panel = DirectFrame(

            frameColor=(
                0.025,
                0.035,
                0.055,
                0.45
            ),

            frameSize=(
                -0.37,
                0.48,
                -0.105,
                0.105
            ),

            pos=(
                1.72,
                0,
                0.88
            ),

            relief=1
        )

        self.right_title = DirectLabel(

            text="EVENT LOG",

            text_scale=0.032,

            text_fg=(
                1.0,
                1.0,
                1.0,
                1
            ),

            frameColor=(
                0,
                0,
                0,
                0
            ),

            pos=(
                0,
                0,
                0.070
            ),

            parent=self.right_panel
        )

        self.right_event_label = DirectLabel(

            text="Waiting for agent...",

            text_scale=0.03,

            text_fg=(
                1.0,
                0.2,
                0.2,
                1
            ),

            frameColor=(
                0,
                0,
                0,
                0
            ),

            text_align=0,

            text_wordwrap=18,

            pos=(
                -0.23,
                4,
                0.040
            ),

            parent=self.right_panel
        )

    def add_left_event(
        self,
        message
    ):

        self.left_events.append(
            str(message)
        )

        if len(self.left_events) > self.max_events:

            self.left_events.pop(0)

        self.left_event_label["text"] = (
            "\n".join(
                self.left_events
            )
        )

    def add_right_event(
        self,
        message
    ):

        self.right_events.append(
            str(message)
        )

        if len(self.right_events) > self.max_events:

            self.right_events.pop(0)

        self.right_event_label["text"] = (
            "\n".join(
                self.right_events
            )
        )

    def add_event(
        self,
        side,
        message
    ):

        if side == "LEFT":

            self.add_left_event(
                message
            )

        else:

            self.add_right_event(
                message
            )

    def clear_left(
        self
    ):

        self.left_events = []

        self.left_event_label["text"] = (
            "Waiting for agent..."
        )

    def clear_right(
        self
    ):

        self.right_events = []

        self.right_event_label["text"] = (
            "Waiting for agent..."
        )

    def clear_all(
        self
    ):

        self.clear_left()
        self.clear_right()

    def destroy(
        self
    ):

        if not self.left_panel.is_empty():

            self.left_panel.destroy()

        if not self.right_panel.is_empty():

            self.right_panel.destroy()