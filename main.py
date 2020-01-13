import pygame
import copy
import random

from piece import Piece
from shapes import SHAPES, SHAPE_COLORS
from config import S_HEIGHT, S_WIDTH, PLAY_HEIGHT, PLAY_WIDTH, BLOCK_SIZE, TOP_LEFT_Y, TOP_LEFT_X


def create_grid(locked_positions=None):
    grid = [[(0, 0, 0) for _ in range(10)] for _ in range(20)]

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if locked_positions:
                if (j, i) in locked_positions:
                    c = locked_positions[(j, i)]  # Color for each locked position will be stored/retrieved here
                    grid[i][j] = c

    return grid


def get_shape():
    return Piece(5, 0, random.choice(SHAPES))


def draw_next_shape(piece, surface):
    font = pygame.font.SysFont('arial', 30)
    label = font.render('Next Shape', 1, (255, 255, 255))

    sx = TOP_LEFT_X + PLAY_WIDTH + 50
    sy = TOP_LEFT_Y + PLAY_HEIGHT/2 - 100
    format = piece.shape[piece.rotation % len(piece.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, piece.color,
                                 (sx + j*BLOCK_SIZE, sy + i*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)
        surface.blit(label, (sx + 10, sy - 30))


def convert_shape_format(piece):
    positions = []
    format = piece.shape[piece.rotation % len(piece.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((piece.x + j, piece.y + i))

    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4)  # TODO: test what these values do

    return positions


def get_shadow(piece, grid):
    shadow = copy.deepcopy(piece)
    for i in range(23)[::-1]:
        shadow.y = i
        shadow.color = (179, 179, 179)
        if not valid_space(shadow, grid):
            continue
        else:
            return shadow


def valid_space(piece, grid):
    accepted_positions = [[(j, i) for j in range(10) if grid[i][j] == (0, 0, 0)] for i in range(20)]
    accepted_positions = [j for sub in accepted_positions for j in sub]  # Flatten above list
    formatted = convert_shape_format(piece)

    for pos in formatted:
        if pos not in accepted_positions:
            if pos[1] > -1:
                return False

    return True


def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False


def draw_grid(surface, grid):
    for i in range(len(grid)):
        pygame.draw.line(surface,
                         (128, 128, 128),
                         (TOP_LEFT_X, TOP_LEFT_Y + i * BLOCK_SIZE),
                         (TOP_LEFT_X + PLAY_WIDTH, TOP_LEFT_Y + i * BLOCK_SIZE))
        for j in range(len(grid[i])):
            pygame.draw.line(surface,
                             (128, 128, 128),
                             (TOP_LEFT_X + j * BLOCK_SIZE, TOP_LEFT_Y),
                             (TOP_LEFT_X + j * BLOCK_SIZE, TOP_LEFT_Y + PLAY_HEIGHT))


def draw_window(grid, surface, score=0, last_score=0, level=1):
    surface.fill((0, 0, 0))
    # Title
    add_text(surface, 'TETRIS', TOP_LEFT_X + PLAY_WIDTH / 2 - 90, BLOCK_SIZE, size=60)
    add_text(surface, 'Score: ' + str(score),
             TOP_LEFT_X + PLAY_WIDTH + 70, TOP_LEFT_Y + PLAY_HEIGHT/2 + 60)
    add_text(surface, 'High Score: ' + str(last_score),
             TOP_LEFT_X - 200, TOP_LEFT_Y + 360)
    add_text(surface, 'Level: ' + str(level),
             TOP_LEFT_X + PLAY_WIDTH + 71, TOP_LEFT_Y + PLAY_HEIGHT/2 + 160)
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j], (TOP_LEFT_X + j*BLOCK_SIZE, TOP_LEFT_Y + i*BLOCK_SIZE, BLOCK_SIZE,
                                                   BLOCK_SIZE), 0)

    draw_grid(surface, grid)
    pygame.draw.rect(surface, (255, 0, 0), (TOP_LEFT_X, TOP_LEFT_Y, PLAY_WIDTH, PLAY_HEIGHT), 4)
    # pygame.display.update()


def clear_rows(grid, locked):
    inc = 0
    ind = list()
    for i in range(len(grid)-1, -1, -1):
        row = grid[i]
        if (0, 0, 0) not in row:
            inc += 1
            ind.append(i)
            for j in range(len(row)):
                try:
                    del locked[(j, i)]
                except:
                    continue

    if inc > 0:
        ind = sorted(ind)[::-1]
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            y_delta = 0
            x, y = key
            for row in ind:
                if y < row:
                    y_delta += 1
            if y_delta > 0:
                new_key = (x, y + y_delta)
                locked[new_key] = locked.pop(key)
    return inc


def add_text(surface, text, x=0, y=0, color=(255, 255, 255), font='arial', size=30, middle=False):
    font = pygame.font.SysFont(font, size)
    label = font.render(text, 1, color)
    if middle:
        x = TOP_LEFT_X + PLAY_WIDTH/2 - (label.get_width()/2)
        y = TOP_LEFT_Y + PLAY_HEIGHT/2 - (label.get_height()/2)
    surface.blit(label, (x, y))
    return label


def update_score(new_score, text):
    with open('scores.txt', 'r') as f:
        score_list = [(x.split('|')[0], int(x.split('|')[1])) for x in f.readlines()]

    print(score_list)
    if new_score > score_list[-1][1]:
        score_list.append((text, new_score))

    new_score_list = sorted(score_list, key=lambda x: x[1])[::-1][:10]

    with open('scores.txt', 'w') as fo:
        for x in new_score_list:
            fo.write('{}|{}'.format(x[0], x[1]))


def max_score():
    with open('scores.txt', 'r') as f:
        score_list = [(x.split('|')[0], x.split('|')[1]) for x in f.readlines()]
    return score_list[0][1]


def main(win):
    # global grid

    locked_positions = dict()
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.27
    orig_speed = copy.copy(fall_speed)
    fast_fall = False
    level_time = 0
    score = 0
    level = 1

    while run:
        level_time += clock.get_rawtime()

        if level_time/1000 > 10:
            level_time = 0
            if fall_speed > 0.12:
                level += 1
                fall_speed -= 0.005

        if fall_speed > 0.025:
            orig_speed = copy.deepcopy(fall_speed)

        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        clock.tick()

        if fall_time/1000 >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not (valid_space(current_piece, grid)) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        if fast_fall:
            fall_speed = 0.025
        else:
            fall_speed = orig_speed

        current_shadow = get_shadow(current_piece, grid)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1
                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                elif event.key == pygame.K_DOWN:
                    fast_fall = True
                    # current_piece.y = current_shadow.y
                    # if not valid_space(current_piece, grid):
                    #     current_piece.y -= 1
                #     old_fall_speed = copy.copy(fall_speed)
                #     while pygame.key.get_pressed()[pygame.K_DOWN]:
                #         fall_speed = 0.05
                #     fall_speed = old_fall_speed
                #     # current_piece.y += 1
                #     if not valid_space(current_piece, grid):
                #         current_piece.y -= 1
                elif event.key == pygame.K_UP:
                    current_piece.rotation = current_piece.rotation + 1 % len(current_piece.shape)
                    if not valid_space(current_piece, grid):
                        current_piece.rotation = current_piece.rotation - 1 % len(current_piece.shape)
                current_shadow = get_shadow(current_piece, grid)

        shape_pos = convert_shape_format(current_piece)
        shadow_pos = convert_shape_format(current_shadow)

        for i in range(len(shadow_pos)):
            x, y = shadow_pos[i]
            if y > -1:
                grid[y][x] = current_shadow.color

        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                grid[y][x] = current_piece.color

        if change_piece:  # i.e. if this piece hit the ground
            fast_fall = False
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            score += clear_rows(grid, locked_positions) * 10
            # clear_rows(grid, locked_positions)

        draw_window(grid, win, score, int(max_score()), level)
        draw_next_shape(next_piece, win)
        pygame.display.update()

        if check_lost(locked_positions):
            add_text(win, "GAME OVER", size=80, middle=True)
            pygame.display.update()
            pygame.time.delay(1500)
            run = False

    return score


def main_menu(win):
    run = True
    while run:
        win.fill((0, 0, 0))
        add_text(win, 'Press Any Key To Get Funky', size=60, middle=True)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                final_score = main(win)
                high_score_screen(win, final_score)

    pygame.display.quit()


def high_score_screen(win, score):
    win.fill((0, 0, 0))
    add_text(win, 'Please Enter Name', x=250, y=150, size=40)
    font = pygame.font.Font(None, 32)
    input_box = pygame.Rect(250, 250, 140, 32)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    text = ''
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        if text == '':
                            add_text(win, 'Please enter a name', x=250, y=350, size=20, color=(229, 36, 36))
                        else:
                            update_score(score, text)
                            run = False
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

        txt_surface = font.render(text, True, color)
        width = max(200, txt_surface.get_width() + 10)
        input_box.w = width
        win.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        pygame.draw.rect(win, color, input_box, 2)

        pygame.display.flip()


if __name__ == '__main__':
    pygame.font.init()
    win = pygame.display.set_mode((S_WIDTH, S_HEIGHT))
    pygame.display.set_caption('Tetris')

    main_menu(win)
