from pymunk import Vec2d

DEFAULT_WALL_FRICTION = 0.5
DEFAULT_ELASTICITY = 0.4
DEFAULT_FLOOR_FRICTION = 0.8
SIMULATION_SPEED = 3.0
BALL_MOMENT = 1.0
DEFAULT_MOVES: list[list[Vec2d | float]] = list(
    [
        [Vec2d(300.0, 0.0), 10000.0],
        [Vec2d(0.0, -300.0), 10000.0],
        [Vec2d(-300.0, 0.0), 10000.0],
        [Vec2d(-15.0, 500.0), 10000.0],
    ]
)
STOPPING_VELOCITY: float = 10.0
VELOCITY_THRESHOLD: float = 50.0

# Outer proximity gate for enabling the funnel.
# When the ball is within (hole_radius + ball_radius + FUNNEL_EXTRA),
# win_condition_system will *attempt* to apply the funnel pull.
FUNNEL_EXTRA: float = 40.0
# Inner funnel radius, measured from hole centre.
# If the ball is within this distance, apply_funnel will apply
# a distance-proportional pull toward the hole (with damping).
FUNNEL_RADIUS: float = 40.0
# How strong the pull is each frame (experiment: 0.05 → 0.5)
FUNNEL_STRENGTH: float = 0.15
# Extra damping to bleed speed when inside funnel (0.9 = gentle, 0.7 = strong)
FUNNEL_DAMPING: float = 0.85
