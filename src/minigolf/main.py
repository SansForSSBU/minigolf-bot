import sys

import pygame

from minigolf.components import Collider, PhysicsBody, Position, Renderable, Velocity
from minigolf.systems.collision import detect_collisions, resolve_collisions
from minigolf.systems.movement import movement_system
from minigolf.systems.physics import physics_system
from minigolf.systems.rendering import render_system
from minigolf.world import World

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()
world = World()

# Entity creation
ball = world.create_entity()
world.components[Position][ball] = Position(100, 100)
world.components[Velocity][ball] = Velocity(3, 2)
world.components[PhysicsBody][ball] = PhysicsBody(1, 0.9, 0.01)
world.components[Collider][ball] = Collider(20, 20)
world.components[Renderable][ball] = Renderable((255, 255, 255))

wall = world.create_entity()
world.components[Position][wall] = Position(400, 300)
world.components[Collider][wall] = Collider(200, 30)
world.components[Renderable][wall] = Renderable((255, 0, 0))


# Game loop
def main():
    while True:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Update systems
        physics_system(world)
        movement_system(world)
        # Detect and resolve collisions
        collisions = detect_collisions(world)
        resolve_collisions(world, collisions)
        # Render the world
        render_system(world, screen)

        clock.tick(60)
