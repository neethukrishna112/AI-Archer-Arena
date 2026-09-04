
from direct.gui.DirectGui import (
    DirectFrame,
    DirectLabel,
)


class ScoreBoard:

    def __init__(
        self,
        game
    ):

        self.game = game

        self.left_score = 0
        self.right_score = 0

        self.left_panel = DirectFrame(
            frameColor=(
                0.025,
                0.035,
                0.055,
                0.92
            ),
            frameSize=(
                -0.36,
                0.36,
                -0.105,
                0.105
            ),
            pos=(
                -1.0,
                0,
                0.88
            ),
            relief=1
        )

        self.left_title = DirectLabel(
            text="AGENT 1",
            text_scale=0.047,
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
            pos=(
                -0.16,
                0,
                0.035
            ),
            parent=self.left_panel
        )

        self.left_score_label = DirectLabel(
            text="0",
            text_scale=0.060,
            text_fg=(
                1,
                0.75,
                0.15,
                1
            ),
            frameColor=(
                0,
                0,
                0,
                0
            ),
            pos=(
                0.14,
                0,
                0.035
            ),
            parent=self.left_panel
        )

        self.left_score_text = DirectLabel(
            text="SCORE",
            text_scale=0.030,
            text_fg=(
                0.65,
                0.70,
                0.78,
                1
            ),
            frameColor=(
                0,
                0,
                0,
                0
            ),
            pos=(
                0.14,
                0,
                -0.040
            ),
            parent=self.left_panel
        )

        self.right_panel = DirectFrame(
            frameColor=(
                0.025,
                0.035,
                0.055,
                0.92
            ),
            frameSize=(
                -0.36,
                0.36,
                -0.105,
                0.105
            ),
            pos=(
                1.0,
                0,
                0.88
            ),
            relief=1
        )

        self.right_title = DirectLabel(
            text="AGENT 2",
            text_scale=0.047,
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
            pos=(
                0.16,
                0,
                0.035
            ),
            parent=self.right_panel
        )

        self.right_score_label = DirectLabel(
            text="0",
            text_scale=0.060,
            text_fg=(
                1,
                0.75,
                0.15,
                1
            ),
            frameColor=(
                0,
                0,
                0,
                0
            ),
            pos=(
                -0.14,
                0,
                0.035
            ),
            parent=self.right_panel
        )

        self.right_score_text = DirectLabel(
            text="SCORE",
            text_scale=0.030,
            text_fg=(
                0.65,
                0.70,
                0.78,
                1
            ),
            frameColor=(
                0,
                0,
                0,
                0
            ),
            pos=(
                -0.14,
                0,
                -0.040
            ),
            parent=self.right_panel
        )

    def add_left_score(
        self,
        points=1
    ):

        self.left_score += points

        self.left_score_label["text"] = str(
            self.left_score
        )

    def add_right_score(
        self,
        points=1
    ):

        self.right_score += points

        self.right_score_label["text"] = str(
            self.right_score
        )

    def set_left_score(
        self,
        score
    ):

        self.left_score = score

        self.left_score_label["text"] = str(
            self.left_score
        )

    def set_right_score(
        self,
        score
    ):

        self.right_score = score

        self.right_score_label["text"] = str(
            self.right_score
        )

    def get_left_score(
        self
    ):

        return self.left_score

    def get_right_score(
        self
    ):

        return self.right_score