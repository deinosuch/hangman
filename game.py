import pygame
import numpy as np
from numpy import random as rnd


class Game:
    def __init__(
        self,
        game_speed=4,
        food_count=1,
        width=1200,
        height=800,
        cell_size=40,
        cell_offset=2,
        food_cell_offset=6,
        snek_starting_length=2,
        training=False,
    ):
        self.window_set_up = False

        if not self.window_set_up:
            pygame.init()
            pygame.display.set_caption("Snek")
            self._win = pygame.display.set_mode((width, height))
            self.fps_counter = pygame.time.Clock()

        self.BACKGROUND_COL = (0, 0, 0)
        self.TAIL_COL_MIN = (20, 60, 20)
        self.TAIL_COL_MAX = (50, 140, 50)
        self.FOOD_COL = (160, 70, 20)
        self.HEAD_COL = (0, 255, 0)
        self.WALL_COL = (70, 50, 50)
        self.DIRS = {"up": (0, -1), "right": (1, 0), "down": (0, 1), "left": (-1, 0)}

        self.ACTIONS = ["up", "right", "down", "left"]

        self.food_count_mem = food_count
        self.game_speed_mem = game_speed
        self.width_mem = width
        self.height_mem = height
        self.cell_size_mem = cell_size
        self.cell_offset_mem = cell_offset
        self.food_cell_offset_mem = food_cell_offset
        self.snek_starting_length_mem = snek_starting_length
        self.training_mem = training

        self.init()

    def init(self):
        self.training = self.training_mem
        self.game_speed = self.game_speed_mem
        self.board = Board(
            self,
            self.width_mem,
            self.height_mem,
            self.cell_size_mem,
            self.cell_offset_mem,
        )
        self.snek = Snake(self, self.snek_starting_length_mem)

        if self.food_count_mem > self.board.tiles - self.snek_starting_length_mem:
            self.food_count_mem = self.board.tiles - self.snek_starting_length_mem
        self.food_manager = []
        for i in range(self.food_count_mem):
            self.food_manager.append(FoodManager(self, self.food_cell_offset_mem))

        self.draw()
        if not self.training:
            self.game()

    def update(self):
        if not self.training:
            self.fps_counter.tick(self.game_speed)
            dir = self.snek.move_dir
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w:
                        dir = "up"
                    elif event.key == pygame.K_d:
                        dir = "right"
                    elif event.key == pygame.K_s:
                        dir = "down"
                    elif event.key == pygame.K_a:
                        dir = "left"
                    elif event.key == pygame.K_ESCAPE:
                        self.game_quit()
                    elif event.key == pygame.K_SPACE:
                        self.pause()
                    elif event.key == pygame.K_r:
                        self.init()
                        return
            # print(
            #     self.get_pixels().shape, self.board.grid_height, self.board.grid_width
            # )

            self.snek.move(dir)
            # print(self.snek.steps_without_food)
            print(self.get_state())
            self.draw()

            pygame.display.update()

    def train_update(self, action):
        if not self.snek.is_dead:
            self.fps_counter.tick(self.game_speed)
            dir = action
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.game_quit()
                    elif event.key == pygame.K_SPACE:
                        self.pause()
                    elif event.key == pygame.K_r:
                        self.init()
                        return

            self.snek.move(dir)
            self.draw()
            pygame.display.update()

    def post_game_update(self):
        if not self.training:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.game_quit()
                    elif event.key == pygame.K_SPACE:
                        self.pause()
                    elif event.key == pygame.K_r:
                        self.init()
                        return

            self.snek.blink()
            pygame.display.update()
            self.fps_counter.tick(4)

    def pause(self):
        self.paused = True
        while self.paused:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.type == pygame.QUIT:
                        self.game_quit()
                    if event.key == pygame.K_SPACE:
                        self.paused = not self.paused
                    elif event.key == pygame.K_ESCAPE:
                        self.game_quit()
                    elif event.key == pygame.K_r:
                        self.init()
                        return
            self.fps_counter.tick(60)

    def game(self):
        while not self.snek.is_dead:
            self.update()
        while True:
            self.post_game_update()

    def draw(self):
        self._win.fill(self.BACKGROUND_COL)
        for f_mg in self.food_manager:
            f_mg.draw()
        self.board.draw()
        self.snek.draw()

    def game_quit(self):
        pygame.quit()
        quit()

    def get_pixels(self):
        pixels = np.zeros(
            (self.board.grid_height, self.board.grid_width, 3), dtype=np.int32
        )
        # pixels = np.zeros((self.board.grid_height, self.board.grid_width), dtype=np.int32)
        for i in range(self.board.grid_height):
            for j in range(self.board.grid_width):
                pixels[i, j] = pygame.Surface.get_at(self._win, (j, i))[:3]
        return pixels

    def get_state(self):
        hazard = np.zeros((2, 3, 3), dtype=np.int32)
        # x, y = (
        #     self.board.center_x + self.board.cell_size // 2,
        #     self.board.center_y + self.board.cell_size // 2,
        # )
        x, y = self.snek.segments[0][0].center
        points = []
        points = [
            (x - 1 * self.board.cell_size, y - 1 * self.board.cell_size),
            (x, y - 1 * self.board.cell_size),
            (x + 1 * self.board.cell_size, y - 1 * self.board.cell_size),
            (x - 1 * self.board.cell_size, y),
            (x, y),
            (x + 1 * self.board.cell_size, y),
            (x - 1 * self.board.cell_size, y + 1 * self.board.cell_size),
            (x, y + 1 * self.board.cell_size),
            (x + 1 * self.board.cell_size, y + 1 * self.board.cell_size),
        ]
        # for _y in range(
        #     y - (self.board.grid_height // 2) * self.board.cell_size,
        #     y + ((self.board.grid_height + 1) // 2) * self.board.cell_size,
        #     self.board.cell_size,
        # ):
        #     for _x in range(
        #         x - (self.board.grid_width // 2) * self.board.cell_size,
        #         x + ((self.board.grid_width + 1) // 2) * self.board.cell_size,
        #         self.board.cell_size,
        #     ):
        #         points.append((_x, _y))

        points = np.array(points).reshape(3, 3, 2)

        for rct in self.board.walls + [sgm[0] for sgm in self.snek.segments[1:]]:
            for i, row in enumerate(points):
                for j, point in enumerate(row):
                    if rct.collidepoint(point):
                        hazard[0, i, j] = 1

        # for rct in self.board.walls + [sgm[0] for sgm in self.snek.segments[1:]]:
        #     _x, _y = rct.centerx, rct.centery
        #     i, j = (
        #         int((y - _y) / (self.board.cell_size)),
        #         int((x - _x) / (self.board.cell_size)),
        #     )
        #     hazard[i, j] = 1

        # for f_m in self.food_manager:
        #     _x, _y = f_m.food.centerx, f_m.food.centery
        #     i, j = (
        #         int((y - _y) / (self.board.cell_size)),
        #         int((x - _x) / (self.board.cell_size)),
        #     )
        #     hazard[0, i, j] = 2

        # hazard[
        #     int((y - self.snek.segments[0][0].centery) / self.board.cell_size),
        #     int((x - self.snek.segments[0][0].centerx) / self.board.cell_size),
        # ] = -1

        # training info 
        head_from_apple = (
            self.food_manager[0].food.centerx - self.snek.segments[0][0].centerx,
            self.food_manager[0].food.centery - self.snek.segments[0][0].centery,
        )

        tail_from_apple = (
            self.food_manager[0].food.centerx - self.snek.segments[1][0].centerx,
            self.food_manager[0].food.centery - self.snek.segments[1][0].centery,
        )

        bonus = -15
        if tuple(np.abs(head_from_apple)) < tuple(np.abs(tail_from_apple)):
            bonus = 10

        _arctan = 0
        try:
            _arctan = (
                np.arctan(np.abs(head_from_apple[1] / head_from_apple[0])) * 180 / np.pi
            )
        except ZeroDivisionError:
            _arctan = 90

        if head_from_apple[1] <= 0:
            if head_from_apple[0] <= 0:
                i = 0
                j = 0
                if _arctan > 60:
                    j += 1
                elif _arctan < 30:
                    i += 1
            else:
                i = 0
                j = 2
                if _arctan > 60:
                    j -= 1
                elif _arctan < 30:
                    i += 1
        else:
            if head_from_apple[0] <= 0:
                i = 2
                j = 0
                if _arctan > 60:
                    j += 1
                elif _arctan < 30:
                    i -= 1
            else:
                i = 2
                j = 2
                if _arctan > 60:
                    j -= 1
                elif _arctan < 30:
                    i -= 1
        hazard[1, i, j] = 2
        return hazard, bonus


class Board:
    def __init__(self, game, width, height, cell_size, cell_offset):
        self.game = game
        assert width % cell_size == 0
        assert height % cell_size == 0
        self.width, self.height = width, height
        self.cell_size = cell_size
        self.cell_offset = cell_offset
        self.grid_width = int(self.width / self.cell_size)
        self.grid_height = int(self.height / self.cell_size)
        self.cell_size_normalized = self.cell_size - 2 * self.cell_offset
        self.center_x = ((self.width // 2) // self.cell_size) * self.cell_size
        self.center_y = ((self.height // 2) // self.cell_size) * self.cell_size
        self.walls = []
        self.build_walls()
        self.tiles = int(
            (
                (self.width - 2 * self.cell_size)
                * (self.height - 2 * self.cell_size)
                / (self.cell_size ** 2)
            )
        )

    def build_walls(self):
        for i in range(self.grid_width - 1):
            self.walls.append(
                pygame.Rect(i * self.cell_size, 0, self.cell_size, self.cell_size)
            )
            self.walls.append(
                pygame.Rect(
                    (i + 1) * self.cell_size,
                    self.height - self.cell_size,
                    self.cell_size,
                    self.cell_size,
                )
            )

        for i in range(self.grid_height):
            self.walls.append(
                pygame.Rect(0, (i + 1) * self.cell_size, self.cell_size, self.cell_size)
            )
            self.walls.append(
                pygame.Rect(
                    self.width - self.cell_size,
                    (i) * self.cell_size,
                    self.cell_size,
                    self.cell_size,
                )
            )

    def draw(self):
        for wall in self.walls:
            pygame.draw.rect(self.game._win, self.game.WALL_COL, wall)

    def get_center(self, grid_x, grid_y):
        return (
            grid_x * self.cell_size + self.cell_size // 2,
            grid_y * self.cell_size + self.cell_size // 2,
        )


class FoodManager:
    def __init__(self, game, cell_offset):
        self.game = game
        self.cell_offset = cell_offset
        self.cell_size_normalized = self.game.board.cell_size - 2 * cell_offset
        self.food = self.get_rand_rect()

    def eaten(self):
        self.food = self.get_rand_rect()
        # print(snek.length)
        # print((board.tiles))

    def draw(self):
        pygame.draw.rect(
            self.game._win, self.game.FOOD_COL, self.food,
        )

    def get_rand_rect(self):
        while True:
            stop = True
            self.grid_pos = (
                rnd.randint(1, self.game.board.grid_width - 1),
                rnd.randint(1, self.game.board.grid_height - 1),
            )
            R = pygame.Rect(
                self.grid_pos[0] * self.game.board.cell_size + self.cell_offset,
                self.grid_pos[1] * self.game.board.cell_size + self.cell_offset,
                self.cell_size_normalized,
                self.cell_size_normalized,
            )
            for rct in (
                [i[0] for i in self.game.snek.segments]
                + self.game.board.walls
                + [f_mg.food for f_mg in self.game.food_manager]
            ):
                if R.colliderect(rct):
                    stop = False
                    break
            if (
                stop
                or self.game.snek.length
                > self.game.board.tiles - self.game.food_count_mem
            ):
                break
        return R


class Snake:
    def __init__(self, game, starting_segments):
        self.game = game
        self.segments = []
        for i in range(starting_segments):
            if i == 0:
                self.segments.append(
                    [
                        pygame.Rect(
                            self.game.board.center_x + self.game.board.cell_offset // 2,
                            self.game.board.center_y + self.game.board.cell_offset // 2,
                            self.game.board.cell_size
                            - 2 * (self.game.board.cell_offset // 2),
                            self.game.board.cell_size
                            - 2 * (self.game.board.cell_offset // 2),
                        ),
                        self.game.HEAD_COL,
                    ]
                )
            else:
                self.segments.append(
                    [
                        pygame.Rect(
                            self.game.board.center_x + self.game.board.cell_offset,
                            self.game.board.center_y
                            + self.game.board.cell_offset
                            + i * self.game.board.cell_size,
                            self.game.board.cell_size_normalized,
                            self.game.board.cell_size_normalized,
                        ),
                        self.get_tail_color(),
                    ]
                )
        self.is_dead = False
        self.length = len(self.segments)
        self.food_eaten = 0
        self.steps_without_food = 0
        self.move_dir = "up"
        self.can_blink = True

    def get_tail_color(self):
        col = []
        for i in range(len(self.game.TAIL_COL_MAX)):
            col.append(
                rnd.randint(self.game.TAIL_COL_MIN[i], self.game.TAIL_COL_MAX[i] + 1)
            )
        return tuple(col)

    def draw(self):
        for sgm in self.segments[1:]:
            pygame.draw.rect(
                self.game._win, sgm[1], sgm[0],
            )
        pygame.draw.rect(self.game._win, self.game.HEAD_COL, self.segments[0][0])

    def blink(self):
        if self.can_blink:
            pygame.draw.rect(
                self.game._win, self.game.BACKGROUND_COL, self.segments[0][0]
            )
            for sgm in [_sgm[0] for _sgm in self.segments[1:]]:
                pygame.draw.rect(
                    self.game._win, self.game.BACKGROUND_COL, sgm,
                )
        else:
            self.draw()
        self.can_blink = not self.can_blink

    def move(self, dir):
        self.steps_without_food += 1
        opposite_move_dir = tuple([-1 * cord for cord in self.game.DIRS[self.move_dir]])
        if self.game.DIRS[dir] != opposite_move_dir:
            self.move_dir = dir
        x, y = self.game.DIRS[self.move_dir]

        self.last_segment_memory = (
            self.segments[len(self.segments) - 1][0].x,
            self.segments[len(self.segments) - 1][0].y,
        )
        self.check_collision(
            pygame.Rect(
                self.segments[0][0].x + x * self.game.board.cell_size,
                self.segments[0][0].y + y * self.game.board.cell_size,
                self.game.board.cell_size_normalized,
                self.game.board.cell_size_normalized,
            )
        )
        if self.is_dead:
            return
        # Tail movement
        for i in range(len(self.segments) - 1, 0, -1):
            self.segments[i][0] = self.segments[i][0].move(
                self.segments[i - 1][0].centerx - self.segments[i][0].centerx,
                self.segments[i - 1][0].centery - self.segments[i][0].centery,
            )
            # Head movement
        self.segments[0][0] = self.segments[0][0].move(
            x * self.game.board.cell_size, y * self.game.board.cell_size
        )

    def check_collision(self, future_head):
        for f_mg in self.game.food_manager:
            if future_head.colliderect(f_mg.food):
                self.grow(1)
                f_mg.eaten()
                self.steps_without_food = 0
        for rct in [
            i[0] for i in self.segments[1 : (len(self.segments) - 1)]
        ] + self.game.board.walls:  # without the last segment, because checking for future segment (last won't be there)
            if future_head.colliderect(rct):
                self.is_dead = True
                break

    def grow(self, growth_size):
        self.length += growth_size
        for i in range(growth_size):
            self.segments.append(
                [
                    pygame.Rect(
                        self.last_segment_memory[0],
                        self.last_segment_memory[1],
                        # self.segments[len(self.segments) - 1].x,
                        # self.segments[len(self.segments) - 1].y,
                        self.game.board.cell_size_normalized,
                        self.game.board.cell_size_normalized,
                    ),
                    self.get_tail_color(),
                ]
            )


def main():
    game = Game(game_speed=5, food_count=1)


if __name__ == "__main__":
    main()
