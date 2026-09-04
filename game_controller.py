
from direct.gui.DirectGui import DirectButton

from main import ArcherArena


class GameController:

    def __init__(
        self,
        game
    ):

        self.game = game

        self.started = False
        self.game.game_stopped = True
        self.game.agents_can_shoot = False

        self.game.ignore(
            "space"
        )

        self.create_play_button(
            "PLAY"
        )

        print()
        print(
            "=============================================="
        )

        print(
            "GAME READY"
        )

        print(
            "Click PLAY to start."
        )

        print(
            "=============================================="
        )

    def create_play_button(
        self,
        text
    ):

        self.play_button = DirectButton(

            text=text,

            scale=0.055,

            pos=(
                -1.5,
                2,
                0.88
            ),

            frameColor=(
                0.03,
                0.18,
                0.08,
                0.95
            ),

            text_fg=(
                1,
                1,
                1,
                1
            ),

            relief=1,

            command=self.start_game
        )

    def start_game(
        self
    ):

        print()
        print(
            "=============================================="
        )

        if self.started:

            print(
                "PLAY AGAIN PRESSED"
            )

            self.game.scoreboard.set_left_score(
                0
            )

            self.game.scoreboard.set_right_score(
                0
            )

            self.game.event_log.clear_all()

            self.game.timer.reset()

        else:

            print(
                "PLAY PRESSED"
            )

        print(
            "STARTING NEW ROUND"
        )

        print(
            "=============================================="
        )

        self.game.game_stopped = False

        self.game.agents_can_shoot = True

        self.started = True

        self.game.accept(
            "space",
            self.game.test_shoot
        )

        self.play_button.destroy()

        print(
            "GAME RUNNING"
        )

    def show_play_again(
        self
    ):

        self.create_play_button(
            "PLAY AGAIN"
        )

if __name__ == "__main__":

    game = ArcherArena()

    controller = GameController(
        game
    )

    game.controller = controller

    game.run()