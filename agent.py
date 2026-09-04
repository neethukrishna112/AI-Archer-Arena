
import math

from panda3d.core import Vec3
from direct.showbase.ShowBaseGlobal import globalClock


class ArcherAgent:

    def __init__(
        self,
        game,
        name,
        warrior,
        targets,
        side
    ):

        self.game = game
        self.name = name
        self.warrior = warrior
        self.targets = targets
        self.side = side

        self.target_values = {
            "Bronze": 10,
            "Silver": 20,
            "Gold": 30,
            "Diamond": 50
        }

        if self.side == "LEFT":

            self.policy_name = "RISK_HUNTER"

            self.risk_tolerance = 0.78

            self.value_weight = 1.25

            self.speed_weight = 0.12

            self.distance_penalty = 0.035

            self.opponent_pressure = 0.20

        else:

            self.policy_name = "TACTICAL_OPTIMIZER"

            self.risk_tolerance = 0.38

            self.value_weight = 1.00

            self.speed_weight = 0.30

            self.distance_penalty = 0.055

            self.opponent_pressure = 0.35

        self.state = "OBSERVE"

        self.current_target = None

        self.state_time = 0.0

        self.shoot_delay = 2.0

        self.aim_time = 0.0

        self.aim_duration = 0.8

        self.last_target_name = None

        self.last_decision_score = 0.0

        self.last_confidence = 0.0

        self.last_strategy = "INITIAL"

        self.recent_targets = []

        self.max_memory = 5

        self.observation_count = 0

        self.last_observed_score = None

        self.last_opponent_score = None

        self.target_attempts = {}

        self.target_hits = {}

        for target_name in self.target_values:

            self.target_attempts[target_name] = 0

            self.target_hits[target_name] = 0

        self.shots = 0

        self.hits = 0

        self.misses = 0

        self.total_decisions = 0

        self.total_decision_time = 0.0

        self.last_decision_start = 0.0
        self.pending_shots = []

        self.miss_distance_threshold = 1.0

        self.game.taskMgr.add(
            self.update,
            "AgentUpdate_" + name
        )

        print()
        print(
            "=================================================="
        )

        print(
            "AUTONOMOUS AGENT CREATED"
        )

        print(
            "Name:",
            self.name
        )

        print(
            "Side:",
            self.side
        )

        print(
            "Policy:",
            self.policy_name
        )

        print(
            "Risk tolerance:",
            round(
                self.risk_tolerance,
                2
            )
        )

        print(
            "=================================================="
        )

    def get_own_score(self):

        scoreboard = getattr(
            self.game,
            "scoreboard",
            None
        )

        if scoreboard is None:

            return 0

        if self.side == "LEFT":

            return scoreboard.get_left_score()

        return scoreboard.get_right_score()

    def get_opponent_score(self):

        scoreboard = getattr(
            self.game,
            "scoreboard",
            None
        )

        if scoreboard is None:

            return 0

        if self.side == "LEFT":

            return scoreboard.get_right_score()

        return scoreboard.get_left_score()

    def get_score_difference(self):

        own_score = self.get_own_score()

        opponent_score = self.get_opponent_score()

        return (
            own_score
            - opponent_score
        )

    def determine_strategy(self):

        difference = self.get_score_difference()

        if difference <= -30:

            return "COMEBACK"

        if difference < 0:

            return "PRESSURE"

        if difference >= 30:

            return "LEAD_CONTROL"

        return "BALANCED"

    def get_target_velocity(
        self,
        target
    ):

        try:

            current_position = target.get_pos()

            destination = target.destination

            direction = (
                destination
                - current_position
            )

            if direction.length() < 0.001:

                return Vec3(
                    0,
                    0,
                    0
                )

            direction.normalize()

            speed = getattr(
                target,
                "speed",
                0.0
            )

            return (
                direction
                * speed
            )

        except Exception:

            return Vec3(
                0,
                0,
                0
            )

    def predict_target_position(
        self,
        target,
        travel_time
    ):

        current_position = (
            target.get_pos()
        )

        velocity = (
            self.get_target_velocity(
                target
            )
        )

        predicted = (
            current_position
            + velocity
            * travel_time
        )

        return predicted

    def estimate_movement_difficulty(
        self,
        target
    ):

        velocity = (
            self.get_target_velocity(
                target
            )
        )

        speed = velocity.length()

        difficulty = (
            speed
            / 1.5
        )

        if difficulty < 0.0:

            difficulty = 0.0

        if difficulty > 1.0:

            difficulty = 1.0

        return difficulty

    def estimate_hit_probability(
        self,
        distance,
        target
    ):

        distance_factor = (
            1.0
            - (
                distance
                / 30.0
            )
        )

        if distance_factor < 0.0:

            distance_factor = 0.0

        if distance_factor > 1.0:

            distance_factor = 1.0

        movement_difficulty = (
            self.estimate_movement_difficulty(
                target
            )
        )

        movement_penalty = (
            movement_difficulty
            * 0.18
        )

        probability = (
            0.35
            + (
                distance_factor
                * 0.60
            )
            - movement_penalty
        )

        target_name = (
            target.get_name()
        )

        attempts = (
            self.target_attempts.get(
                target_name,
                0
            )
        )

        hits = (
            self.target_hits.get(
                target_name,
                0
            )
        )

        if attempts >= 3:

            learned_accuracy = (
                hits
                / attempts
            )

            probability = (
                probability
                * 0.70
                +
                learned_accuracy
                * 0.30
            )

        if probability < 0.25:

            probability = 0.25

        if probability > 0.95:

            probability = 0.95

        return probability

    def estimate_travel_time(
        self,
        distance
    ):

        projectile_speed = 22.0

        travel_time = (
            distance
            / projectile_speed
        )

        release_delay = 0.60

        return (
            travel_time
            + release_delay
        )

    def estimate_future_distance(
        self,
        warrior_position,
        target,
        travel_time
    ):

        predicted_position = (
            self.predict_target_position(
                target,
                travel_time
            )
        )

        return (
            predicted_position
            - warrior_position
        ).length()

    def calculate_aim_duration(
        self,
        distance
    ):

        minimum_aim = 0.35

        maximum_aim = 1.20

        distance_factor = (
            distance
            / 30.0
        )

        if distance_factor < 0.0:

            distance_factor = 0.0

        if distance_factor > 1.0:

            distance_factor = 1.0

        aim_duration = (
            minimum_aim
            +
            (
                distance_factor
                *
                (
                    maximum_aim
                    - minimum_aim
                )
            )
        )

        return aim_duration

    def calculate_shoot_delay(
        self,
        distance
    ):

        minimum_delay = 0.90

        maximum_delay = 2.00

        distance_factor = (
            distance
            / 30.0
        )

        if distance_factor < 0.0:

            distance_factor = 0.0

        if distance_factor > 1.0:

            distance_factor = 1.0

        delay = (
            minimum_delay
            +
            (
                distance_factor
                *
                (
                    maximum_delay
                    - minimum_delay
                )
            )
        )

        return delay

    def calculate_opponent_pressure(
        self,
        target_value
    ):

        difference = (
            self.get_score_difference()
        )

        if difference < 0:

            deficit = abs(
                difference
            )

            pressure = (
                deficit
                / 100.0
            )

            if pressure > 1.0:

                pressure = 1.0

            return (
                target_value
                * pressure
                * self.opponent_pressure
            )

        if difference > 0:

            return 0.0

        return 0.0

    def calculate_repeat_penalty(
        self,
        target_name
    ):

        if not self.recent_targets:

            return 0.0

        recent_count = (
            self.recent_targets.count(
                target_name
            )
        )

        return (
            recent_count
            * 1.5
        )

    def calculate_utility(
        self,
        target,
        distance
    ):

        target_name = (
            target.get_name()
        )

        target_value = (
            self.target_values.get(
                target_name,
                0
            )
        )

        initial_travel_time = (
            self.estimate_travel_time(
                distance
            )
        )

        warrior_position = (
            self.warrior.get_pos()
        )

        future_distance = (
            self.estimate_future_distance(
                warrior_position,
                target,
                initial_travel_time
            )
        )

        travel_time = (
            self.estimate_travel_time(
                future_distance
            )
        )

        hit_probability = (
            self.estimate_hit_probability(
                future_distance,
                target
            )
        )

        expected_reward = (
            target_value
            * hit_probability
        )

        movement_difficulty = (
            self.estimate_movement_difficulty(
                target
            )
        )

        opponent_pressure = (
            self.calculate_opponent_pressure(
                target_value
            )
        )

        repeat_penalty = (
            self.calculate_repeat_penalty(
                target_name
            )
        )

        strategy = (
            self.determine_strategy()
        )

        if strategy == "COMEBACK":

            value_multiplier = (
                self.value_weight
                + 0.25
            )

            risk_multiplier = (
                self.risk_tolerance
                + 0.15
            )

        elif strategy == "PRESSURE":

            value_multiplier = (
                self.value_weight
                + 0.10
            )

            risk_multiplier = (
                self.risk_tolerance
                + 0.08
            )

        elif strategy == "LEAD_CONTROL":

            value_multiplier = (
                self.value_weight
                - 0.05
            )

            risk_multiplier = (
                self.risk_tolerance
                - 0.12
            )

        else:

            value_multiplier = (
                self.value_weight
            )

            risk_multiplier = (
                self.risk_tolerance
            )

        risk_cost = (
            movement_difficulty
            * target_value
            * (
                1.0
                - risk_multiplier
            )
            * 0.45
        )

        time_cost = (
            travel_time
            * self.speed_weight
        )

        distance_cost = (
            future_distance
            * self.distance_penalty
        )

        aim_duration = (
            self.calculate_aim_duration(
                future_distance
            )
        )

        shoot_delay = (
            self.calculate_shoot_delay(
                future_distance
            )
        )

        action_time = (
            aim_duration
            + shoot_delay
            + travel_time
        )

        speed_bonus = (
            2.0
            / max(
                action_time,
                0.1
            )
        )

        utility = (

            expected_reward
            * value_multiplier

            + opponent_pressure

            + speed_bonus

            - risk_cost

            - time_cost

            - distance_cost

            - repeat_penalty
        )

        return (
            utility,
            target_value,
            hit_probability,
            travel_time,
            expected_reward,
            future_distance,
            movement_difficulty,
            opponent_pressure,
            risk_cost,
            strategy
        )

    def calculate_confidence(
        self,
        best_score,
        second_score
    ):

        if best_score <= 0:

            return 0.25

        difference = max(
            0.0,
            best_score - second_score
        )

        margin_confidence = (
            difference
            / max(abs(best_score), 1.0)
        )

        total_attempts = (
            self.hits
            + self.misses
        )

        if total_attempts > 0:

            success_rate = (
                self.hits
                / total_attempts
            )

            experience_factor = (
                0.75
                + (
                    success_rate
                    * 0.25
                )
            )

        else:

            experience_factor = 0.75

        confidence = (
            margin_confidence
            * experience_factor
        )

        confidence = max(
            0.05,
            min(
                confidence,
                0.98
            )
        )

        return confidence

    def observe(self):

        if not self.targets:

            return None

        self.observation_count += 1

        warrior_pos = (
            self.warrior.get_pos()
        )

        best_target = None

        best_score = None

        second_best_score = None

        best_details = None

        strategy = (
            self.determine_strategy()
        )

        own_score = (
            self.get_own_score()
        )

        opponent_score = (
            self.get_opponent_score()
        )

        print()

        print(
            "=================================================="
        )

        print(
            self.name,
            "WORLD ANALYSIS"
        )

        print(
            "Policy:",
            self.policy_name
        )

        print(
            "Strategy:",
            strategy
        )

        print(
            "Own score:",
            own_score
        )

        print(
            "Opponent score:",
            opponent_score
        )

        print(
            "Score difference:",
            self.get_score_difference()
        )

        print(
            "=================================================="
        )

        for target in self.targets:

            target_pos = (
                target.get_pos()
            )

            distance = (
                target_pos
                - warrior_pos
            ).length()

            (
                utility,
                target_value,
                hit_probability,
                travel_time,
                expected_reward,
                future_distance,
                movement_difficulty,
                opponent_pressure,
                risk_cost,
                target_strategy
            ) = self.calculate_utility(
                target,
                distance
            )

            aim_duration = (
                self.calculate_aim_duration(
                    future_distance
                )
            )

            shoot_delay = (
                self.calculate_shoot_delay(
                    future_distance
                )
            )

            print(
                self.name,
                "→",
                target.get_name(),
                "|",
                "Distance:",
                round(
                    distance,
                    2
                ),
                "|",
                "Value:",
                target_value,
                "|",
                "FutureDist:",
                round(
                    future_distance,
                    2
                ),
                "|",
                "Hit:",
                round(
                    hit_probability * 100,
                    1
                ),
                "%",
                "|",
                "ETA:",
                round(
                    travel_time,
                    2
                ),
                "|",
                "Aim:",
                round(
                    aim_duration,
                    2
                ),
                "|",
                "Delay:",
                round(
                    shoot_delay,
                    2
                ),
                "|",
                "MoveRisk:",
                round(
                    movement_difficulty,
                    2
                ),
                "|",
                "Expected:",
                round(
                    expected_reward,
                    2
                ),
                "|",
                "RiskCost:",
                round(
                    risk_cost,
                    2
                ),
                "|",
                "Utility:",
                round(
                    utility,
                    2
                )
            )

            if (
                best_score is None
                or utility > best_score
            ):

                if best_score is not None:

                    second_best_score = (
                        best_score
                    )

                best_score = (
                    utility
                )

                best_target = (
                    target
                )

                best_details = (
                    distance,
                    target_value,
                    hit_probability,
                    travel_time,
                    expected_reward,
                    future_distance,
                    movement_difficulty,
                    opponent_pressure,
                    risk_cost,
                    target_strategy
                )

            elif (
                second_best_score is None
                or utility > second_best_score
            ):

                second_best_score = (
                    utility
                )

        if best_target is not None:

            if second_best_score is None:

                second_best_score = 0.0

            confidence = (
                self.calculate_confidence(
                    best_score,
                    second_best_score
                )
            )

            (
                distance,
                target_value,
                hit_probability,
                travel_time,
                expected_reward,
                future_distance,
                movement_difficulty,
                opponent_pressure,
                risk_cost,
                target_strategy
            ) = best_details

            self.last_confidence = (
                confidence
            )

            self.last_decision_score = (
                best_score
            )

            self.last_strategy = (
                target_strategy
            )

            print()

            print(
                "**************** AI DECISION ****************"
            )

            print(
                "Agent:",
                self.name
            )

            print(
                "Strategy:",
                target_strategy
            )

            print(
                "Target:",
                best_target.get_name()
            )

            print(
                "Value:",
                target_value
            )

            print(
                "Current distance:",
                round(
                    distance,
                    2
                )
            )

            print(
                "Predicted distance:",
                round(
                    future_distance,
                    2
                )
            )

            print(
                "Estimated hit probability:",
                round(
                    hit_probability * 100,
                    1
                ),
                "%"
            )

            print(
                "Expected reward:",
                round(
                    expected_reward,
                    2
                )
            )

            print(
                "Aim duration:",
                round(
                    self.calculate_aim_duration(
                        future_distance
                    ),
                    2
                )
            )

            print(
                "Shoot recovery:",
                round(
                    self.calculate_shoot_delay(
                        future_distance
                    ),
                    2
                )
            )

            print(
                "Risk cost:",
                round(
                    risk_cost,
                    2
                )
            )

            print(
                "Decision confidence:",
                round(
                    confidence * 100,
                    1
                ),
                "%"
            )

            print(
                "Final utility:",
                round(
                    best_score,
                    2
                )
            )

            print(
                "***********************************************"
            )

        return best_target

    def decide(self):

        target = (
            self.observe()
        )

        if target is None:

            return

        self.current_target = (
            target
        )

        self.total_decisions += 1

        self.last_decision_start = (
            self.state_time
        )

        target_name = (
            target.get_name()
        )

        self.last_target_name = (
            target_name
        )

        self.recent_targets.append(
            target_name
        )

        if len(
            self.recent_targets
        ) > self.max_memory:

            self.recent_targets.pop(0)

        warrior_position = (
            self.warrior.get_pos()
        )

        target_position = (
            target.get_pos()
        )

        current_distance = (
            target_position
            - warrior_position
        ).length()

        self.aim_duration = (
            self.calculate_aim_duration(
                current_distance
            )
        )

        self.shoot_delay = (
            self.calculate_shoot_delay(
                current_distance
            )
        )

        print(
            self.name,
            "SELECTED:",
            target_name,
            "| Distance:",
            round(
                current_distance,
                2
            ),
            "| Aim:",
            round(
                self.aim_duration,
                2
            ),
            "| Recovery:",
            round(
                self.shoot_delay,
                2
            ),
            "| Confidence:",
            round(
                self.last_confidence * 100,
                1
            ),
            "%"
        )

        self.game.event_log.add_event(
            self.side,
            "Target: " + target_name
        )

        self.state = "AIM"

        self.state_time = 0.0

        self.aim_time = 0.0

        self.game.event_log.add_event(
            self.side,
            "Aiming..."
        )

    def turn_toward_target(
        self,
        dt
    ):

        if self.current_target is None:

            return True

        warrior_pos = (
            self.warrior.get_pos()
        )

        target_pos = (
            self.current_target.get_pos()
        )

        direction = (
            target_pos
            - warrior_pos
        )

        if direction.length() < 0.001:

            return True

        desired_heading = (
            math.degrees(
                math.atan2(
                    direction.x,
                    direction.y
                )
            )
        )

        current_heading = (
            self.warrior.get_h()
        )

        angle_difference = (
            desired_heading
            - current_heading
        )

        while angle_difference > 180:

            angle_difference -= 360

        while angle_difference < -180:

            angle_difference += 360

        rotation_speed = 190.0

        maximum_rotation = (
            rotation_speed
            * dt
        )

        if (
            abs(angle_difference)
            <= maximum_rotation
        ):

            new_heading = (
                desired_heading
            )

        elif angle_difference > 0:

            new_heading = (
                current_heading
                + maximum_rotation
            )

        else:

            new_heading = (
                current_heading
                - maximum_rotation
            )

        self.warrior.set_h(
            new_heading
        )

        return (
            abs(angle_difference)
            < 3.0
        )

    def shoot(self):

        if self.current_target is None:

            return

        target = (
            self.current_target
        )

        target_name = (
            target.get_name()
        )

        fired_target_position = (
            target.get_pos()
        )

        warrior_position = (
            self.warrior.get_pos()
        )

        distance = (
            fired_target_position
            - warrior_position
        ).length()

        travel_time = (
            self.estimate_travel_time(
                distance
            )
        )

        shot_data = {

            "target": target,

            "target_name": target_name,

            "aim_position":
                Vec3(
                    fired_target_position
                ),

            "travel_time":
                travel_time,

            "elapsed":
                0.0
        }

        self.pending_shots.append(
            shot_data
        )

        print(
            self.name,
            "READY TO SHOOT AT",
            target_name,
            "| Distance:",
            round(
                distance,
                2
            ),
            "| Arrow ETA:",
            round(
                travel_time,
                2
            )
        )

    def resolve_shot(
        self,
        shot
    ):

        target = (
            shot["target"]
        )

        target_name = (
            shot["target_name"]
        )

        aimed_position = (
            shot["aim_position"]
        )

        if target is None:

            return

        try:

            current_position = (
                target.get_pos()
            )

        except Exception:

            return

        movement_distance = (
            current_position
            - aimed_position
        ).length()

        if (
            movement_distance
            >
            self.miss_distance_threshold
        ):

            print(
                "=================================================="
            )

            print(
                self.name,
                "MISS!"
            )

            print(
                "Target:",
                target_name
            )

            print(
                "Target moved:",
                round(
                    movement_distance,
                    2
                )
            )

            print(
                "Allowed movement:",
                round(
                    self.miss_distance_threshold,
                    2
                )
            )

            print(
                "Reason:",
                "TARGET MOVED BEFORE ARROW ARRIVED"
            )

            print(
                "=================================================="
            )

            self.register_miss(
                target_name
            )

            self.game.event_log.add_event(
                self.side,
                "MISS: " + target_name
            )

            return

        print(
            "=================================================="
        )

        print(
            self.name,
            "HIT!"
        )

        print(
            "Target:",
            target_name
        )

        print(
            "Target movement:",
            round(
                movement_distance,
                2
            )
        )

        print(
            "=================================================="
        )

        self.register_hit(
            target_name
        )

        self.game.event_log.add_event(
            self.side,
            "HIT: " + target_name
        )

    def update_pending_shots(
        self,
        dt
    ):

        if not self.pending_shots:

            return

        completed_shots = []

        for shot in self.pending_shots:

            shot["elapsed"] += dt

            if (
                shot["elapsed"]
                >=
                shot["travel_time"]
            ):

                completed_shots.append(
                    shot
                )

        for shot in completed_shots:

            self.resolve_shot(
                shot
            )

            if shot in self.pending_shots:

                self.pending_shots.remove(
                    shot
                )

    def update(
        self,
        task
    ):

        dt = globalClock.getDt()

        #self.update_pending_shots(dt)

        self.state_time += dt

        if self.state == "OBSERVE":

            self.decide()

        elif self.state == "AIM":

            aligned = (
                self.turn_toward_target(
                    dt
                )
            )

            self.aim_time += dt

            if (
                aligned
                and self.aim_time >= self.aim_duration
            ):

                self.state = "SHOOT"

                self.state_time = 0.0

        elif self.state == "SHOOT":

            if not getattr(
                self.game,
                "agents_can_shoot",
                False
            ):

                self.state = "WAIT"

                self.state_time = 0.0

                return task.cont

            if self.current_target is not None:

                target_name = (
                    self.current_target.get_name()
                )

                self.game.trigger_warrior_shot(
                    self.warrior,
                    self.current_target,
                    self.side
                )

                self.shots += 1

                if target_name not in (
                    self.target_attempts
                ):

                    self.target_attempts[
                        target_name
                    ] = 0

                self.target_attempts[
                    target_name
                ] += 1

                # REMOVE duplicate shot-resolution system
                # self.shoot()

                print(
                    self.name,
                    "FIRED AT",
                    target_name
                )

                self.game.event_log.add_event(
                    self.side,
                    "Fired: "
                    + target_name
                )

            self.state = "WAIT"

            self.state_time = 0.0

        elif self.state == "WAIT":

            if (
                self.state_time
                >= self.shoot_delay
            ):

                self.current_target = None

                self.state = "OBSERVE"

                self.state_time = 0.0

        return task.cont

    def register_hit(
        self,
        target_name
    ):

        self.hits += 1

        if target_name not in (
            self.target_hits
        ):

            self.target_hits[
                target_name
            ] = 0

        self.target_hits[
            target_name
        ] += 1

        print(
            self.name,
            "LEARNED:",
            target_name,
            "HIT"
        )

    def register_miss(
        self,
        target_name
    ):

        self.misses += 1

        print(
            self.name,
            "LEARNED:",
            target_name,
            "MISS"
        )

    def get_decision_info(self):

        return {

            "agent": self.name,

            "policy": self.policy_name,

            "state": self.state,

            "target": self.last_target_name,

            "strategy": self.last_strategy,

            "confidence": self.last_confidence,

            "utility": self.last_decision_score,

            "own_score": self.get_own_score(),

            "opponent_score": self.get_opponent_score(),

            "score_difference":
                self.get_score_difference(),

            "shots": self.shots,

            "hits": self.hits,

            "misses": self.misses,

            "decisions":
                self.total_decisions
        }