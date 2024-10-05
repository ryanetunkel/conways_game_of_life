"""Main functions"""

import math
import random

import pygame


pygame.init()

PIXEL_SIZE = 1
GLOBAL_SCALAR = PIXEL_SIZE / 4
WINDOW_WIDTH = 512
WINDOW_HEIGHT = 512
WINDOW_SIZE = (WINDOW_WIDTH,WINDOW_HEIGHT)
CENTER_WIDTH = WINDOW_WIDTH / 2
CENTER_HEIGHT = WINDOW_HEIGHT / 2
CENTER_SCREEN = (CENTER_WIDTH,CENTER_HEIGHT)
MAX_CELL_WIDTH = int(WINDOW_WIDTH * GLOBAL_SCALAR) * 2
MAX_CELL_HEIGHT = int(WINDOW_HEIGHT * GLOBAL_SCALAR) * 2
CELL_CHANCE = 5

screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Conway's Game of Life")

clock = pygame.time.Clock()

font_size = int(WINDOW_HEIGHT/20) if WINDOW_HEIGHT < WINDOW_WIDTH else int(WINDOW_WIDTH/20)
font = pygame.font.Font("font/Pixeltype.ttf",font_size)

zoom = 4
zoom_changed = False
num_cells = 0
gen = 0
offset_x = 0
offset_y = 0
pan_speed = 1

grid = []
MIN_ZOOM = 4
MAX_ZOOM = 128
mouse_pos = (0,0)
current_idx = (0,0)
start_idx = (0,0)
new_start_idx = True
erase = False
play = False


edit = False
blank = True
rand = False
interim = False

first_grid = True

location = False

rects = ()

def create_grid(width:int=0,height:int=0,empty:bool=False) -> tuple[list[list[int]],int]:
    width = MAX_CELL_WIDTH if not width or width >= MAX_CELL_WIDTH else width
    height = MAX_CELL_HEIGHT if not height or height >= MAX_CELL_HEIGHT else height
    count = 0
    for y_idx in range(height):
        grid.append([])
        for x_idx in range(width):
            if not empty:
                if random.randint(0,100) < CELL_CHANCE:
                    grid[y_idx].append(1)
                    count += 1
                else:
                    grid[y_idx].append(0)
            else:
                grid[y_idx].append(0)
    return [grid,count]


def display_grid(
    grid:list[list[int]]=[[]],
    zoom:int=4,
    offset_x:int=0,
    offset_y:int=0,
) -> int:
    if grid and zoom:
        for y_idx in range(len(grid)):
            for x_idx in range(len(grid[y_idx])):
                if grid[y_idx][x_idx]:
                    cell_x_pos = (x_idx + offset_x)*zoom
                    cell_y_pos = (y_idx + offset_y)*zoom
                    cell_width = zoom
                    cell_height = zoom
                    if 0 <= cell_x_pos <= WINDOW_WIDTH and 0 <= cell_y_pos <= WINDOW_HEIGHT:
                        pygame.draw.rect(screen,"#FFFFFF",(cell_x_pos,cell_y_pos,cell_width,cell_height))


def display_grid_outline(
    zoom:int=4,
    offset_x:int=0,
    offset_y:int=0,
):
    pygame.draw.rect(screen,"#FFFFFF",(offset_x*zoom,offset_y*zoom,MAX_CELL_WIDTH*zoom,MAX_CELL_HEIGHT*zoom),1)


def count_surrounding_cells(x_pos:int,y_pos:int,grid:list[list[int]])->int:
    width = len(grid[0])
    height = len(grid)
    if 0 <= x_pos < width and 0 <= y_pos < height:
        count = 0
        if y_pos - 1 >= 0:
            if x_pos - 1 >= 0:
                count+=grid[y_pos-1][x_pos-1]
            count+=grid[y_pos-1][x_pos]
            if x_pos + 1 < width:
                count+=grid[y_pos-1][x_pos+1]
        if x_pos - 1 >= 0:
            count+=grid[y_pos][x_pos-1]
        if x_pos + 1 < width:
            count+=grid[y_pos][x_pos+1]
        if y_pos + 1 < height:
            if x_pos - 1 >= 0:
                count+=grid[y_pos+1][x_pos-1]
            count+=grid[y_pos+1][x_pos]
            if x_pos + 1 < width:
                count+=grid[y_pos+1][x_pos+1]
        return count
    else:
        return -1


def calc_next_step(grid:list[list[int]]) -> tuple[list[list[int]],int]:
    new_grid = []
    count = 0
    for y_idx in range(len(grid)):
        new_grid.append([])
        for x_idx in range(len(grid[y_idx])):
            if grid[y_idx][x_idx] == 1:
                if count_surrounding_cells(x_idx,y_idx,grid) < 2:
                    new_grid[y_idx].append(0)
                elif count_surrounding_cells(x_idx,y_idx,grid) > 3:
                    new_grid[y_idx].append(0)
                else:
                    new_grid[y_idx].append(1)
                    count += 1
            else:
                if count_surrounding_cells(x_idx,y_idx,grid) == 3:
                    new_grid[y_idx].append(1)
                    count += 1
                else:
                    new_grid[y_idx].append(0)
    return (new_grid,count)


def display_instructions() -> tuple[pygame.Rect,pygame.Rect]:
    # Surfs and Rects
    instructions_surf = font.render("Reset: [Space]    Pause/Play: [Enter]    Exit: [Esc]", False, "#00FF00")
    instructions_rect = instructions_surf.get_rect(center = (WINDOW_WIDTH*1/2,WINDOW_HEIGHT*15/16))
    controls_surf = font.render("Zoom: [Scroll Wheel]    Pan Camera: [Arrow Keys or WASD]", False, "#00FF00")
    controls_rect = controls_surf.get_rect(center = (WINDOW_WIDTH*1/2,WINDOW_HEIGHT*31/32))
    # Back Rect
    padding = PIXEL_SIZE
    left = instructions_rect.left - (padding * 2) if instructions_rect.left < controls_rect.left else controls_rect.left - (padding * 2)
    top = instructions_rect.top - (padding * 2)
    width = instructions_rect.width if instructions_rect.width > controls_rect.width else controls_rect.width + padding*4
    height = instructions_rect.height + (controls_rect.top - instructions_rect.bottom) + controls_rect.height + padding*2
    draw_surf = pygame.Surface((width, height), pygame.SRCALPHA)
    draw_surf.fill(pygame.Color("#22222299"))
    draw_coords = (left,top)
    # Blits
    screen.blit(draw_surf,draw_coords)
    screen.blit(instructions_surf,instructions_rect)
    screen.blit(controls_surf,controls_rect)
    return (instructions_rect,instructions_rect)


def display_gen_and_pop(generation:int,population:int) -> tuple[pygame.Rect,pygame.Rect]:
    # Surfs and Rects
    generation_surf = font.render(f"Generation: {generation}", False, "#00FF00")
    generation_rect = generation_surf.get_rect(midleft = (0,WINDOW_HEIGHT*1/32))
    population_surf = font.render(f"Population: {population}", False, "#00FF00")
    population_rect = population_surf.get_rect(midleft = (0,WINDOW_HEIGHT*1/16))
    # Back Rect
    padding = PIXEL_SIZE
    left = 0
    top = generation_rect.top - (padding * 3)
    width = generation_rect.width if generation_rect.width > population_rect.width else population_rect.width + padding*2
    height = generation_rect.height + (population_rect.top - generation_rect.bottom) + population_rect.height + padding*2
    draw_surf = pygame.Surface((width, height), pygame.SRCALPHA)
    draw_surf.fill(pygame.Color("#22222299"))
    draw_coords = (left,top)
    # Blits
    screen.blit(draw_surf,draw_coords)
    screen.blit(generation_surf,generation_rect)
    screen.blit(population_surf,population_rect)
    return (generation_rect,population_rect)


def display_options(edit:bool=False,blank:bool=True,rand:bool=False,) -> tuple[pygame.Rect,pygame.Rect,pygame.Rect]:
    # Colors
    edit_color = "#22222299" if not edit else "#55555599"
    blank_color = "#22222299" if not blank else "#55555599"
    rand_color = "#22222299" if not rand else "#55555599"

    # Surfs and Rects
    edit_surf = font.render(f"Edit: [E]", False, "#00FF00")
    edit_rect = edit_surf.get_rect(midright = (WINDOW_WIDTH,WINDOW_HEIGHT*1/32))
    blank_surf = font.render(f"Blank: [B]", False, "#00FF00")
    blank_rect = blank_surf.get_rect(midright = (WINDOW_WIDTH,WINDOW_HEIGHT*1/16))
    random_surf = font.render(f"Random: [R]", False, "#00FF00")
    random_rect = random_surf.get_rect(midright = (WINDOW_WIDTH,WINDOW_HEIGHT*3/32))

    # Left & Width Calc
    if edit_rect.left <= blank_rect.left and edit_rect.left <= random_rect.left:
        left = edit_rect.left
        width = edit_rect.width
    elif blank_rect.left <= random_rect.left and blank_rect.left <= edit_rect.left:
        left = blank_rect.left
        width = blank_rect.width
    elif random_rect.left <= edit_rect.left and random_rect.left <= blank_rect.left:
        left = random_rect.left
        width = random_rect.width

    padding = PIXEL_SIZE
    # Edit Back Rect
    edit_top = edit_rect.top - (padding * 2)
    edit_height = edit_rect.height + ((blank_rect.top - edit_rect.bottom) / 2)
    edit_draw_surf = pygame.Surface((width, edit_height), pygame.SRCALPHA)
    edit_draw_surf.fill(pygame.Color(edit_color))
    edit_draw_coords = (left,edit_top)
    # Blank Back Rect
    blank_top = blank_rect.top - (padding * 2)
    blank_height = blank_rect.height + ((random_rect.top - blank_rect.bottom) / 2)
    blank_draw_surf = pygame.Surface((width, blank_height), pygame.SRCALPHA)
    blank_draw_surf.fill(pygame.Color(blank_color))
    blank_draw_coords = (left,blank_top)
    # Random Back Rect
    random_top = random_rect.top - (padding * 2)
    random_height = random_rect.height + padding
    random_draw_surf = pygame.Surface((width, random_height), pygame.SRCALPHA)
    random_draw_surf.fill(pygame.Color(rand_color))
    random_draw_coords = (left,random_top)

    # Blits
    screen.blit(edit_draw_surf,edit_draw_coords)
    screen.blit(blank_draw_surf,blank_draw_coords)
    screen.blit(random_draw_surf,random_draw_coords)
    screen.blit(edit_surf,edit_rect)
    screen.blit(blank_surf,blank_rect)
    screen.blit(random_surf,random_rect)

    return (edit_rect,blank_rect,random_rect)


def display_texts(
    generation:int,
    population:int,
    edit:bool,
    blank:bool,
    rand:bool
) -> tuple[tuple[pygame.Rect,pygame.Rect],tuple[pygame.Rect,pygame.Rect],tuple[pygame.Rect,pygame.Rect,pygame.Rect],]:
    return (display_instructions(), display_gen_and_pop(generation,population), display_options(edit,blank,rand))


while True:
    (mouse_x,mouse_y) = pygame.mouse.get_pos()
    mouse_pos = (mouse_x,mouse_y)
    keys_pressed = pygame.key.get_pressed()
    mouse_pressed = pygame.mouse.get_pressed()

    for event in pygame.event.get():
        if first_grid:
            create_grid(empty=True)
            first_grid = False

        # Quitting
        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.quit()
            exit()

        # Scrolling
        if event.type == pygame.MOUSEWHEEL:
            if MIN_ZOOM <= zoom <= MAX_ZOOM:
                zoom += int(event.y * (zoom/6))
                if not (MIN_ZOOM <= zoom <= MAX_ZOOM):
                    zoom = MAX_ZOOM if abs(MAX_ZOOM-zoom) <= abs(MIN_ZOOM-zoom) else MIN_ZOOM

        # Checking Location
        if location:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                print((math.floor(mouse_x/zoom)-offset_x),(math.floor(mouse_y/zoom)-offset_y))

        # Key Press
        if event.type == pygame.KEYDOWN:
            # Edit Mode Switch
            if event.key == pygame.K_e:
                if not edit:
                    edit = True
                    blank = False
                    rand = False
                    interim = False
                else:
                    edit = False
                    blank = False
                    rand = False
                    interim = True
            # Blank Grid Creation Switch
            if event.key == pygame.K_b:
                if not blank:
                    edit = False
                    blank = True
                    rand = False
                    interim = False
                else:
                    edit = False
                    blank = False
                    rand = False
                    interim = True
            # Random Grid Creation Switch
            if event.key == pygame.K_r:
                if not rand:
                    edit = False
                    blank = False
                    rand = True
                    interim = False
                else:
                    edit = False
                    blank = False
                    rand = False
                    interim = True
            # Grid Creation/Recreation
            if event.key == pygame.K_SPACE:
                zoom = 4
                grid = []
                num_cells = 0
                gen = 0
                pan_speed = 1
                empty_bool = False if rand else True
                (grid,num_cells) = create_grid(empty=empty_bool)
                if not zoom_changed:
                    zoom = 4
            # Play
            if event.key == pygame.K_RETURN:
                play = not play
                edit = False
                blank = False
                rand = False
                interim = True

    # Panning
    # Left
    if keys_pressed[pygame.K_a] or keys_pressed[pygame.K_LEFT]:
        offset_x += pan_speed
    # Right
    if keys_pressed[pygame.K_d] or keys_pressed[pygame.K_RIGHT]:
        offset_x -= pan_speed
    # Up
    if keys_pressed[pygame.K_w] or keys_pressed[pygame.K_UP]:
        offset_y += pan_speed
    # Down
    if keys_pressed[pygame.K_s] or keys_pressed[pygame.K_DOWN]:
        offset_y -= pan_speed

    pygame.draw.rect(screen,"#000000",(0,0,WINDOW_WIDTH,WINDOW_HEIGHT))


    # Placing Cells
    if edit:
        if mouse_pressed[0]:
            placement = True
            for rect_tuple in rects:
                for rect in rect_tuple:
                    if rect:
                        if rect.collidepoint(mouse_x,mouse_y):
                            placement = False
            if placement:
                x_idx = (math.floor(mouse_x/zoom)-offset_x)
                y_idx = (math.floor(mouse_y/zoom)-offset_y)
                if new_start_idx:
                    new_start_idx = False
                    erase = True if grid[y_idx][x_idx] else False
                if current_idx != (x_idx,y_idx):
                    replacement = 0 if erase else 1
                    grid[y_idx][x_idx] = replacement
                current_idx = (x_idx,y_idx)
        else:
            new_start_idx = True

    if grid:
        display_grid(grid,zoom,offset_x,offset_y)
    display_grid_outline(zoom,offset_x,offset_y)
    rects = display_texts(gen,num_cells,edit,blank,rand)

    pygame.display.update()
    if play:
        (grid,num_cells) = calc_next_step(grid)
        gen += 1
        clock.tick(60)