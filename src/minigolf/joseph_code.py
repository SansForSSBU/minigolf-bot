import pygame
from typing import Union

SCREEN_DIMS = (1000, 1000)


class Ball:
    def __init__(self, pt):
        self.pt: tuple[int, int] = pt
        self.color: tuple[int, int, int] = (0, 160, 0)
        self.size = 5

    def render(self, viewport):
        pygame.draw.circle(viewport, self.color, self.pt, self.size)


class Hole:
    def __init__(self, pt):
        self.pt: tuple[int, int] = pt
        self.size: int = 10
        self.color: tuple[int, int, int] = (160, 0, 0)

    def render(self, viewport):
        pygame.draw.circle(viewport, self.color, self.pt, self.size)


class Level:
    def __init__(self):
        self.objects: list[Union[Wall, Hole]] = []

    def populate_level1(self):
        # Border walls
        self.objects.append(Wall((100, 900), (900, 900)))
        self.objects.append(Wall((900, 900), (900, 100)))
        self.objects.append(Wall((900, 100), (100, 100)))
        self.objects.append(Wall((100, 100), (100, 900)))
        # Obstacle walls
        self.objects.append(Wall((100, 700), (700, 700)))
        self.objects.append(Wall((700, 700), (700, 300)))
        self.objects.append(Wall((700, 300), (300, 300)))
        self.objects.append(Wall((300, 300), (300, 600)))

        # Inner blockades
        self.objects.append(Wall((400, 600), (600, 600)))
        self.objects.append(Wall((600, 600), (600, 400)))
        self.objects.append(Wall((600, 400), (400, 400)))

        # Hole
        self.objects.append(Hole((500, 500)))

        # Ball
        self.objects.append(Ball((200, 800)))

    def render(self, viewport):
        for object in self.objects:
            object.render(viewport)


class Wall:
    def __init__(self, pt1, pt2):
        self.color: tuple[int, int, int] = (255, 255, 255)
        self.width: int = 1
        self.pt1: tuple[int, int] = pt1
        self.pt2: tuple[int, int] = pt2

    def render(self, viewport):
        pygame.draw.line(viewport, self.color, self.pt1, self.pt2, self.width)


def main():
    level: Level = Level()
    level.populate_level1()
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_DIMS)
    clock = pygame.time.Clock()
    while True:
        level.render(screen)
        pygame.display.flip()
        clock.tick(60) / 1000


if __name__ == "__main__":
    main()
