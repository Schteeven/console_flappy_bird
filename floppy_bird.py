import sys
import termios
import time
from collections import deque
from random import randint
from select import select
from typing import Deque, List, Tuple

Playground = List[Deque[str]]
Obstacle = Tuple[int, int]
Bird_Coords = Tuple[int, int]

PLAYGROUND_ROWS = 11
PLAYGROUND_COLS = 50

INITIAL_OBSTACLE = (4, 4)
NO_OBSTACLE = (0, 0)

INITIAL_BIRD_HEIGHT = 5
INITIAL_BIRD_DISTANCE = 6

OBSTACLE = "│"
FREE = " "
BIRD = "B"

DOWN = 0
STRAIGHT = 1
UP = 2

ESC = 27
SPACE = 32

# idea for hide input, key checking terminal:
# https://simondlevy.academic.wlu.edu/files/software/kbhit.py


def empty_playground() -> Playground:
    playground = []
    for i in range(PLAYGROUND_ROWS):
        playground.append(deque())
        playground[i] = deque((FREE for _ in range(PLAYGROUND_COLS)))

    playground[INITIAL_BIRD_HEIGHT][INITIAL_BIRD_DISTANCE] = BIRD

    return playground


def print_playground(playground: Playground) -> None:
    for _ in range(50):
        print()

    print_line()

    for i in range(PLAYGROUND_ROWS):
        for j in range(PLAYGROUND_COLS):
            print(playground[i][j], end="")
        print()

    print_line()


def print_line() -> None:
    for _ in range(50):
        print("-", end="")
    print()


def generate_obstacle() -> Obstacle:
    upper = randint(3, PLAYGROUND_ROWS) - 3
    gap = randint(3, 4)
    lower = PLAYGROUND_ROWS - upper - gap

    return upper, lower


def move_playground(playground: Playground, obstacles: Obstacle) -> None:
    upper, lower = obstacles

    for num, row in enumerate(playground):
        row.popleft()

        if num < upper or PLAYGROUND_ROWS - lower <= num:
            row.append(OBSTACLE)
        else:
            row.append(FREE)


def bird_can_move(playground: Playground, bird: Bird_Coords, direction: int) -> bool:
    height, distance = bird

    if playground[height][distance + 1] == OBSTACLE:
        return False

    if direction == UP and \
            (height == 0 or playground[height - 1][distance + 1] == OBSTACLE):
        return False

    if direction == DOWN and \
            (height == 10 or playground[height + 1][distance + 1] == OBSTACLE):
        return False

    return True


def move_bird(playground: Playground, direction: int, bird: Bird_Coords)\
        -> Tuple[int, int, int]:
    bird_height, bird_distance = bird
    playground[bird_height][bird_distance - 1] = FREE

    if direction == UP:
        direction = STRAIGHT
        bird_height -= 1
    elif direction == STRAIGHT:
        direction = DOWN
    else:
        bird_height += 1

    playground[bird_height][bird_distance] = BIRD

    return direction, bird_height, bird_distance


def key_pressed() -> bool:
    dr, _, _ = select([sys.stdin], [], [], 0)
    return dr != []


def main() -> None:
    # Save current terminal settings
    fd = sys.stdin.fileno()
    old_term = termios.tcgetattr(fd)

    # New terminal settings
    new_term = termios.tcgetattr(fd)
    new_term[3] = (new_term[3] & ~termios.ICANON & ~termios.ECHO)
    termios.tcsetattr(fd, termios.TCSAFLUSH, new_term)

    playground = empty_playground()
    turn = 0
    last_obstacle = INITIAL_OBSTACLE
    bird_height = INITIAL_BIRD_HEIGHT
    bird_distance = INITIAL_BIRD_DISTANCE
    direction = UP

    print_playground(playground)

    while bird_can_move(playground, (bird_height, bird_distance), direction):
        move_playground(playground, last_obstacle)
        direction, bird_height, bird_distance = \
            move_bird(playground, direction, (bird_height, bird_distance))

        if key_pressed():
            char = sys.stdin.read(1)
            if ord(char) == ESC:
                print("GAME TERMINATED")
                break
            elif ord(char) == SPACE:
                direction = UP

        turn += 1
        last_obstacle = generate_obstacle() if turn % 12 == 0 else NO_OBSTACLE
        time.sleep(0.2)
        print_playground(playground)

    print("Your score is {}".format(turn))

    # Old terminal settings reset
    termios.tcsetattr(fd, termios.TCSAFLUSH, old_term)


if __name__ == '__main__':
    main()