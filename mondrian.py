import random
import sys

import pygame

pygame.init()


class MondrianNode(object):
    def __init__(self):
        self.children = []
        self.subdivide_point = 0.0
        self.subdivide_direction = "horizontal"
        self.colour = pygame.Color(255, 0, 0)

    def generate(self, chance_of_end=0.0, max_levels=10.0):
        self.colour.r = random.randint(0, 255)
        self.colour.g = random.randint(0, 255)
        self.colour.b = random.randint(0, 255)
        if random.random() > chance_of_end:  # Decide whether to stop subdividing
            self.subdivide_direction = random.choice(["horizontal", "vertical"])
            self.subdivide_point = random.uniform(0.4, 0.6)
            self.children = [MondrianNode(), MondrianNode()]
            new_chance_of_end = chance_of_end + 1.0 / max_levels
            for child in self.children:
                child.generate(new_chance_of_end, max_levels)

    def draw(self, surface, width, height, xpos, ypos):
        if width < 100 or height < 100:
            return
        rect = pygame.Rect(xpos, ypos, width, height)
        surface.fill(self.colour, rect)
        pygame.draw.rect(surface, (0, 0, 0), rect, 3)

        if self.children:
            if self.subdivide_direction == "horizontal":
                self.children[0].draw(surface, width * self.subdivide_point, height, xpos, ypos)
                self.children[1].draw(surface, width * (1.0 - self.subdivide_point), height,
                                      xpos + width * self.subdivide_point, ypos)
            else:
                self.children[0].draw(surface, width, height * self.subdivide_point, xpos, ypos)
                self.children[1].draw(surface, width, height * (1.0 - self.subdivide_point), xpos,
                                      ypos + height * self.subdivide_point)


def main():
    tree = MondrianNode()
    tree.generate()
    screen = pygame.display.set_mode((1024, 768))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
        tree.draw(screen, 1024, 768, 0, 0)
        pygame.display.flip()


if __name__ == "__main__":
    main()