import pygame
from math import sqrt
from random import randint
pygame.init()


def draw_text(text, x, y, color, screen: pygame.surface.Surface):
    img = Game.font.render(text, True, color)
    screen.blit(img, (x, y))


def convert_input_to_int(keys_index):
    if keys_index == 0:
        if pygame.key.get_pressed()[pygame.K_LEFT]:
            return True
        else:
            return False
    if keys_index == 1:
        if pygame.key.get_pressed()[pygame.K_UP]:
            return True
        else:
            return False
    if keys_index == 2:
        if pygame.key.get_pressed()[pygame.K_DOWN]:
            return True
        else:
            return False
    if keys_index == 3:
        if pygame.key.get_pressed()[pygame.K_RIGHT]:
            return True
        else:
            return False


class Entity:
    #  The first four colors are for ghosts, and the last one is for PacMan (index=4).
    colors = [(255, 184, 255), (255, 0, 0), (255, 184, 82), (0, 255, 255),
              (248, 224, 8)]

    def __init__(self, game, pos: tuple or list, index_color: int, d=0):
        self.game = game

        self.x = pos[0]
        self.y = pos[1]
        self.current_direction = d
        self.new_direction = d
        self.is_frightened = False
        self.is_out = 0
        self.color = self.colors[index_color]

        pygame.draw.rect(game.display, self.color, pygame.Rect(int(self.x * 10) + 136, int(self.y * 10) - 3, 8, 8))

    def is_move_allowed(self, dx=-1, dy=-1):
        if dx == dy:
            dx, dy = ((-0.1, 0), (0, -0.1), (0, 0.1), (0.1, 0))[self.new_direction]
        return (not self.game.map.data['terrain'][int(self.y + 5.5 * dy)] >> (self.game.map.bits - 1 - int(self.x + 5.5
                                                                                                           * dx)
                                                                              ) & 1 and (
                            (dx != 0 and self.y % 1 == 0.5) or
                            (dy != 0 and self.x % 1 == 0.5)))

    def move(self):
        dx, dy = ((-0.1, 0), (0, -0.1), (0, 0.1), (0.1, 0))[self.current_direction]
        if self.is_move_allowed(dx, dy):
            # Clear the previous position of the entity
            pygame.draw.rect(self.game.display, self.game.colors[0],
                             pygame.Rect(int(self.x * 10) + 136, int(self.y * 10) - 3, 8, 8))

            # Update the position of the entity based on the direction
            self.x = (round(self.x + dx, 1) - 0.5) % 16.5 + 0.5
            self.y = round(self.y + dy, 1)

            # Draw the entity at the new position with its color
            pygame.draw.rect(self.game.display, self.color,
                             pygame.Rect(int(self.x * 10) + 136, int(self.y * 10) - 3, 8, 8))

        #  Check if Entity is PACMAN
        if self.color == self.colors[4]:
            # Remove pacgommes from data, if pacman and pacgommes collide together
            if self.game.map.data['pacgommes'][int(self.y)] >> (self.game.map.bits - 1 - int(self.x)) & 1:
                self.game.map.data['pacgommes'][int(self.y)] -= 1 << (self.game.map.bits - 1 - int(self.x))
                self.game.score += 10

            # Checks and processes SuperPacGums
            if self.game.map.data['superpacgommes'][int(self.y)] >> (self.game.map.bits - 1 - int(self.x)) & 1:
                self.game.map.data['superpacgommes'][int(self.y)] -= 1 << (self.game.map.bits - 1 - int(self.x))
                self.game.score += 50
                self.game.chained = 0
                self.game.frightened = pygame.time.get_ticks()

                # Handles ghost behavior when Pac-Man eats SuperPacGum
                for ghost in self.game.ghosts:
                    if ghost.is_out:
                        ghost.color = self.game.colors[1]
                        ghost.current_direction = (3, 2, 1, 0)[ghost.current_direction]
                        ghost.is_frightened = 1

            for ghost in range(4):
                if sqrt((self.x - self.game.ghosts[ghost].x) ** 2 + (self.y - self.game.ghosts[ghost].y) ** 2) < 0.6:
                    if self.game.ghosts[ghost].is_frightened:
                        # Scared ghost - point management and reset
                        self.game.chained += 1
                        self.game.total += 1
                        self.game.score += (1 << self.game.chained) * 100
                        self.game.ghosts[ghost].is_frightened = 0
                        self.game.ghosts[ghost].color = self.colors[ghost]
                        self.game.ghosts[ghost].x = 9
                        self.game.ghosts[ghost].y = 8.5
                        if self.game.total == 16:
                            self.game.score += 12000
                    else:
                        # Normal ghost - life loss management and reset
                        for ghost_index in range(4):
                            self.game.ghosts[ghost_index].is_frightened = 0
                            self.game.ghosts[ghost_index].color = self.colors[ghost_index]
                            self.game.ghosts[ghost_index].x = 9
                            self.game.ghosts[ghost_index].y = 10.5
                            self.game.ghosts[ghost_index].out = 0
                        self.x = 9
                        self.y = 16.5
                        self.current_direction, self.new_direction = 0, 0
                        self.game.lives -= 1
                        return self.game.render()

            if not self.game.won and self.game.score > 10000:
                self.game.lives += 1
                self.game.won = 1
        px, py = int(self.x - 5.5 * dx), int(self.y - 5.5 * dy)
        if self.game.map.data['pacgommes'][py] >> (self.game.map.bits - 1 - px) & 1:
            pygame.draw.rect(self.game.display, (250, 207, 173), pygame.Rect(px * 10 + 144, py * 10 + 5, 2, 2))

        if self.game.map.data['superpacgommes'][py] >> (self.game.map.bits - 1 - px) & 1:
            pygame.draw.rect(self.game.display, (250, 207, 173), pygame.Rect(px * 10 + 143, py * 10 + 4, 4, 4))

    def ia(self, x, y):
        if self.is_frightened:
            while True:
                direction = randint(0, 3)
                dx, dy = ((-0.1, 0), (0, -0.1), (0, 0.1), (0.1, 0))[direction]
                if direction != (3, 2, 1, 0)[self.current_direction] and self.is_move_allowed(dx, dy):
                    self.current_direction = direction
                    break
        else:
            distances = [9999 for _ in range(4)]

            for i in range(4):
                if i != (3, 2, 1, 0)[self.current_direction]:
                    dx, dy = ((-0.1, 0), (0, -0.1), (0, 0.1), (0.1, 0))[i]
                    if self.is_move_allowed(dx, dy):
                        distances[i] = sqrt((self.y + dy - y) ** 2 + (self.x + dx - x) ** 2)
            self.current_direction = distances.index(min(distances))


class Map:
    width = 320
    height = 222
    map_size = (width, height)
    bits = 18

    def __init__(self):
        self.data = {'terrain': (262143, 131841, 187245, 187245, 131073, 186285, 135969, 252783, 249903, 251823, 1152,
                                 251823, 249903, 251823, 131841, 187245, 147465, 219051, 135969, 195453, 131073, 262143)
                     }
        self.load_new_map()

    def load_new_map(self):
        self.data['pacgommes'] = [0, 130302, 9360, 74898, 131070, 75858, 126174, 8208, 8208, 8208, 8208, 8208, 8208,
                                  8208, 130302, 74898, 49140, 43092, 126174, 66690, 131070, 0]
        self.data['superpacgommes'] = [0, 0, 65538, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 65538, 0, 0, 0, 0, 0, 0]


class Game:
    colors = ((0, 0, 0), (32, 48, 248), (248, 224, 8), (255, 183, 52))
    font = pygame.font.SysFont('Comics Sans MS', 20, True)
    keys = [pygame.K_UP, pygame.K_RIGHT, pygame.K_DOWN, pygame.K_LEFT]

    def __init__(self):
        self.map = Map()
        self.display = pygame.display.set_mode(self.map.map_size)
        self.clock = pygame.time.Clock()

        self.level = 0
        self.score = 0
        self.lives = 2
        self.frightened = 0
        self.chained = 0
        self.total = 0
        self.won = 0
        self.arrival = pygame.time.get_ticks()

        self.ghosts = [Entity(self, (9, 10.5), i) for i in range(4)]
        self.pacman = Entity(self, (9, 10.5), 4)

    def prebuild(self):
        self.display.fill(self.colors[0])
        draw_text("PACMAN", 40, 10, self.colors[3], self.display)

        pygame.draw.rect(self.display, self.colors[3], pygame.Rect(138, 0, 2, self.map.height))

    def render(self):

        if self.lives == -1:
            return 42

        self.total = 0
        draw_text(f"Score : ", 5, 50, (255,) * 3, self.display)
        draw_text(f"Level : ", 5, 80, (255,) * 3, self.display)

        #        #  ______DRAW LIVES______  #

        #  Hide useless visualisation of pacman's live(s)
        pygame.draw.rect(self.display, self.colors[0], pygame.Rect(0, 150, 138, 60))
        #  Create a visualisation of pacman's lives
        for i in range(self.lives):
            pygame.draw.rect(self.display, self.colors[2],
                             pygame.Rect(60 - (self.lives - 1) * 20 + i * 40, 180, 20, 20))

        #        #  ______DRAW MAP______  #
        for row_index in range(len(self.map.data['terrain'])):
            for col_index in range(self.map.bits):
                #  Reset the game space for the new map I think ??
                pygame.draw.rect(self.display, self.colors[0],
                                 pygame.Rect(col_index * 10 + 140, row_index * 10 + 1, 10, 10))
                if self.map.data['pacgommes'][row_index] >> (self.map.bits - 1 - col_index) & 1:
                    pygame.draw.rect(self.display, (250, 207, 173),
                                     pygame.Rect(col_index * 10 + 144, row_index * 10 + 5, 2, 2))

                if self.map.data['superpacgommes'][row_index] >> (self.map.bits - 1 - col_index) & 1:
                    pygame.draw.rect(self.display, (250, 207, 173),
                                     pygame.Rect(col_index * 10 + 143, row_index * 10 + 4, 4, 4))
                if self.map.data['terrain'][row_index] >> (self.map.bits - 1 - col_index) & 1:
                    for direction in ((1, 0), (0, 1), (-1, 0), (0, -1)):
                        if (0 <= row_index + direction[0] <= len(self.map.data['terrain']) - 1 and 0 <= col_index +
                                direction[1] <= self.map.bits - 1 and not
                                self.map.data['terrain'][row_index + direction[0]] >>
                                (self.map.bits - 1 - (col_index + direction[1])) & 1):
                            pygame.draw.rect(self.display, self.colors[1],
                                             (col_index * 10 + 140 + 9 * (direction[1] == 1),
                                              row_index * 10 + 1 + 9 * (direction[0] == 1),
                                              1 + 9 * (direction[1] == 0),
                                              1 + 9 * (direction[0] == 0)))
        self.arrival = pygame.time.get_ticks()

    def run(self):
        self.prebuild()
        while True:
            self.map.load_new_map()
            self.level += 1
            self.score = 0
            self.render()
            self.ghosts = [Entity(self, (9, 10.5), i) for i in range(4)]
            self.pacman = Entity(self, (9, 16.5), 4)

            while sum(self.map.data['pacgommes']) + sum(self.map.data['superpacgommes']):
                start = pygame.time.get_ticks()
                for i in range(4):
                    if convert_input_to_int(i):
                        if i == (3, 2, 1, 0)[self.pacman.current_direction]:
                            self.pacman.current_direction = i
                        self.pacman.new_direction = i
                while pygame.time.get_ticks() - start < 0.01:
                    if self.pacman.is_move_allowed():
                        self.pacman.current_direction = self.pacman.new_direction
                    if self.pacman.move() == 42:
                        draw_text('GAME OVER', 185, 100, self.colors[3], self.display)
                        return 69
                pygame.draw.rect(self.display, 'black', pygame.Rect(100, 50, 30, 20))
                draw_text(f"{self.score}", 100, 50, (255,) * 3, self.display)

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return pygame.quit()

                if self.frightened:
                    if pygame.time.get_ticks() - self.frightened > 6.5:
                        for ghost in self.ghosts:
                            if ghost.is_frightened:
                                ghost.color = (255,) * 3
                    if pygame.time.get_ticks() - self.frightened > 8.5:
                        self.frightened = 0
                        for ghost_index in range(4):
                            self.ghosts[ghost_index].color = self.ghosts[ghost_index].colors[ghost_index]
                            self.ghosts[ghost_index].is_frightened = 0

                if self.arrival:
                    if pygame.time.get_ticks() - self.arrival > 0 and not self.ghosts[1].is_out:
                        self.ghosts[1].is_out = 1
                        self.ghosts[1].y = 8.5
                    if pygame.time.get_ticks() - self.arrival > 2.5 and not self.ghosts[0].is_out:
                        self.ghosts[0].is_out = 1
                        self.ghosts[0].y = 8.5
                    if pygame.time.get_ticks() - self.arrival > 5 and not self.ghosts[3].is_out:
                        self.ghosts[3].is_out = 1
                        self.ghosts[3].y = 8.5
                    if pygame.time.get_ticks() - self.arrival > 7.5 and not self.ghosts[2].is_out:
                        self.ghosts[2].is_out = 1
                        self.ghosts[2].y = 8.5
                        pygame.draw.rect(self.display, self.colors[0], pygame.Rect(220, 101, 20, 10))
                        self.arrival = 0

                pdx, pdy = ((-0.1, 0), (0, -0.1), (0, 0.1), (0.1, 0))[self.pacman.current_direction]

                # Pinky
                self.ghosts[0].ia(self.pacman.x + 20 * pdx, self.pacman.y + 20 * pdy)
                self.ghosts[0].move()

                # Inky
                self.ghosts[3].ia(max(min(self.ghosts[1].x + 2 *
                                          (self.pacman.x + 20 * pdx - self.ghosts[1].x), 16.5), 1.5),
                                  max(min(self.ghosts[1].y + 2 * (self.pacman.y + 20 * pdy - self.ghosts[1].y), 21.5),
                                      1.5))
                self.ghosts[3].move()

                # Blinky
                self.ghosts[1].ia(self.pacman.x, self.pacman.y)
                self.ghosts[1].move()

                # Clyde
                if sqrt((self.ghosts[2].x - self.pacman.x) ** 2 + (self.ghosts[2].y - self.pacman.y) ** 2) > 4:
                    self.ghosts[2].ia(self.pacman.x, self.pacman.y)
                else:
                    self.ghosts[2].ia(1.5, 20.5)
                self.ghosts[2].move()

                _dt = self.clock.tick(50)
                pygame.display.update()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    Game().run()
