import pygame
from config import *
from unit import Unit
from button import Button
from unit_classes import *
from utils import *
from buy_bar import *
from player_actions import Player
pygame.init()

# Vytvoření obrazovky
screen = pygame.display.set_mode((WIDTH, HEIGHT))

 
my_font = pygame.font.Font(MAIN_FONT_URL, 15)

selected_unit = None
render_units_attack_screen = False
unit_placement_mode = None
cur_player = RED


def switch_player():
    global cur_player
    cur_player = BLUE if cur_player == RED else RED
    print(cur_player)

living_units = []

red_player = Player(RED, 0, 0)
blue_player = Player(BLUE, WIDTH - 40, 0)
players = [red_player, blue_player]
blue_player.create_starting_unit((Musketeer, 200, 200, BLUE), living_units)
red_player.create_starting_unit((Canon, 300, 300, RED), living_units)
red_player.create_starting_unit((Shield, 400, 300, RED), living_units)
blue_player.create_starting_unit((Medic, 500, 400, BLUE), living_units)
blue_player.create_starting_unit((Commander, 600, 100, BLUE), living_units)
red_player.create_starting_unit((Commander, 500, 100, RED), living_units)
red_player.create_starting_unit((Pikeman, 700, 100, RED), living_units)
blue_player.create_starting_unit((SupplyCart, 800, 300, BLUE), living_units)
blue_player.create_starting_unit((Observer, 200, 150, BLUE), living_units)

screen.fill(GREEN)
lets_continue = True
fps = 60
clock = pygame.time.Clock()  # will tick eveery second

def find_players_with_same_color(players, cur_player):
    same_color_player = None
    for player in players:
        if player.color == cur_player:
            same_color_player = player
            break  # No need to continue searching once a match is found

    if same_color_player is None:
        raise ValueError(f"No player found with color {cur_player}")

    return same_color_player

# def check_game_ended(teams):
#     for team_units in teams.values():
#         print(team_units)
#         has_commander = any(isinstance(unit, Commander) for unit in team_units)
#         print(has_commander)
#         if not has_commander:
#             return True
#     return False


def next_turn():
    global living_units
    global teams

    # Your next turn logic here
    # is_win =  check_game_ended(teams)
    # print("game won?", is_win)
    for unit in living_units:
        if isinstance(unit, Medic):
            unit.reset_for_next_turn(living_units)
        elif isinstance(unit, SupplyCart):
            unit.reset_for_next_turn(living_units)
        else:
            unit.reset_for_next_turn()
        # tohle musím přepsart abych nemusel používat tenhle divnžý elif
    print("Next Turn")
    switch_player()

def disable_unit_for_turn():
    global render_units_attack_screen  # Add this line to access the global variable
    global selected_unit
    print("disabled")
    selected_unit.able_to_move = False
    selected_unit = None
    render_units_attack_screen = None  # Set render_units_attack_screen to False
    print(selected_unit, render_units_attack_screen)


def deselct_unit():
    global selected_unit
    global render_units_attack_screen
    selected_unit = None
    render_units_attack_screen = None  # Set render_units_attack_screen to False


def select_unit():
    global living_units
    global selected_unit
    global render_units_attack_screen
    global cur_player

    if next_turn_button.is_clicked(event.pos):
        next_turn_button.callback()  # Call the callback function when the button is clicked
        # Check if any living unit has been clicked
    for unit in living_units:

        if not unit.able_to_move:
            continue
        print(unit.color, cur_player)
        if unit.color != cur_player:
            continue
        if unit.rect.collidepoint(event.pos):

            selected_unit = unit
            render_units_attack_screen = True

            break


def process_attack(attacker, attacked_pos):
    global living_units
    attack_result = attacker.try_attack(
        event.pos, living_units)
    print(attack_result)
    if attack_result[0] == "UNIT ATTACKS":
        attack_pos = attack_result[1]
        attacked_enemy = attack_result[2]
        attacker.attack_square(attacked_pos)
        hit_result = attacked_enemy.check_if_hit(1)  # 80% hit chance
        print(f"{attacker} hit {unit}?", hit_result)
        if hit_result:
            remaining_hp = attacked_enemy.take_damage()
            if remaining_hp <= 0:
                global cur_player
                attacked_player = find_players_with_same_color(
                    players, attacked_enemy.color)
               
                attacked_enemy.remove_from_game(living_units, attacked_player)
                if isinstance(attacked_enemy, Commander):
                    attacked_enemy.lose_game()
        disable_unit_for_turn()
    elif attack_result == "SUPPORTS DONT ATTACK":
        print("XX")
        deselct_unit()
    if attack_result[0] == "CANT ATTACK SELF" or attack_result[0] == "YOU CANT DO FRIENDLY FIRE":
        deselct_unit()


def check_in_observers_range():
    if issubclass(selected_unit.__class__, Ranged):
        for unit in living_units:
            if isinstance(unit, Observer) and unit.color == selected_unit.color:
                observer_unit = unit
                distance = get_two_units_center_distance(
                    selected_unit, observer_unit)
                if distance <= 75:
                    selected_unit.attack_range_modifiers += 0.5  # Add "in_observer_range" modifier

def check_in_range(itself, other_object):
    pass

def buy_unit(click_pos):
    global unit_placement_mode
    print("bought", unit_placement_mode)
    unit_type_class = globals().get(unit_placement_mode)
    if unit_type_class:
        # Call the create_unit function with the class name
        player_to_append = find_players_with_same_color(
            players, cur_player)
        print(player_to_append)
        player_to_append.create_unit(
            (unit_type_class, click_pos[0], click_pos[1], cur_player), living_units)
        print(unit_placement_mode, living_units)
    else:
        print(f"Error: Unit type {unit_placement_mode} not found.")
    unit_placement_mode = None

def try_select_unit(click_pos, unit):
    if unit.rect.collidepoint(click_pos):
        return ("unit wasnt clicked on", click_pos)

    if unit.able_to_move:
        return 
        select_unit()
    else:
        print("no attacks or ammo left for this unit")
    print(
        f"Selected {unit.__class__.__name__} with right button")
    

button_bar = ButtonBar(WIDTH, buy_buttons)
next_turn_button = Button("Next Turn", 400, 30, 100, 30, next_turn)

while lets_continue:
    # check for events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            print(event)
            lets_continue = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check if any button in the button bar is clicked
            clicked_button = button_bar.get_clicked_button(event.pos)
            if clicked_button and not selected_unit:
                print(f"Clicked {clicked_button.unit_type} button.")
                unit_placement_mode = clicked_button.unit_type

            elif unit_placement_mode:
                buy_unit(event.pos)

            else:
                select_unit()

        if event.type == pygame.MOUSEBUTTONUP and event.button == 3:
            if render_units_attack_screen:
                process_attack(selected_unit, event.pos)

            else:
                for unit in living_units:
                    can_select = try_select_unit(event.pos, unit)
                    if can_select:
                        select_unit():
                    break
                     

        if event.type == pygame.MOUSEMOTION and event.buttons[0] == 1:
            if selected_unit:
                selected_unit.move_in_game_field(event.pos, living_units)

    pygame.display.update()

    # RESET THE GAMEBOARD
    screen.fill(GREEN)

    # RENDER ELEMENTS
    red_player.render_tender(screen)
    blue_player.render_tender(screen)
    next_turn_button.draw(screen)
    button_bar.draw(screen, HEIGHT - BUTTON_BAR_HEIGHT)

    if selected_unit:
        selected_unit.draw_as_active(screen)
        selected_unit.attack_range_modifiers = 1
    for unit in living_units:
        unit.render_on_screen(screen)
    if hasattr(selected_unit, 'attack_cross_position'):
        selected_unit.render_attack_cross(screen)
    if render_units_attack_screen:
        if selected_unit.remain_actions > 0:
            check_in_observers_range()
            selected_unit.render_attack_circle(screen)
    if unit_placement_mode:
        print("unit placement mode")
    clock.tick(fps)

# Ukončení pygame
pygame.quit()
