"""
Snake Eater
Made with PyGame
"""

import pygame, sys, time, random, json
from scipy.stats import gamma


# Difficulty settings
# Easy      ->  10
# Medium    ->  25
# Hard      ->  40
# Harder    ->  60
# Impossible->  120
initial_difficulty = 12



# Gamerules
show_pos = False
show_food_pos = False
show_difficulty = True

steering_type = "LOCAL" # LOCAL: left/right, relative to direction of snake
                        # GLOBAL: left/right/up/down, relative to direction of canvas


wall_collisions = False # True: death on collision with walls
                       # False: repeat to other side on collision with walls


body_collisions = True # True: death on collision with snake body
                        # False: can go through snake body


dynamic_difficulty = False # True: game speed scales with score
                           # False: game speed is constant

# Config Options

volume = 1.0 # Float between 0 and 1


# Window size
frame_size_x = 720
frame_size_y = 480

renderScale = 1.85

# Checks for errors encountered
check_errors = pygame.init()
# pygame.init() example output -> (6, 0)
# second number in tuple gives number of errors
if check_errors[1] > 0:
    print(f'[!] Had {check_errors[1]} errors when initialising game, exiting...')
    sys.exit(-1)
else:
    print('[+] Game successfully initialised')


# Mixer initiation
pygame.mixer.init()

# Initialise game window and draw logo
pygame.display.set_caption('Snake Eater')
game_window = pygame.display.set_mode((round(frame_size_x*renderScale), round(frame_size_y*renderScale)))
game_window.fill((255,255,255))

logo = pygame.transform.smoothscale(pygame.image.load("logo.png"), [round(frame_size_x*renderScale)//2]*2)
logo_rect = logo.get_rect()
logo_rect.center = [round(frame_size_x*renderScale)//2, round(frame_size_y*renderScale)//2]
game_window.blit(logo, logo_rect)

pygame.display.flip()




# Colors (R, G, B)
black = pygame.Color(0, 0, 0)
white = pygame.Color(255, 255, 255)
red = pygame.Color(255, 0, 0)
green = pygame.Color(0, 255, 0)
blue = pygame.Color(0, 0, 255)


# FPS (frames per second) controller
fps_controller = pygame.time.Clock()

# Highscore
def save_highscore(score):
    if score < get_highscore(0): # do nothing if score is lower than highscore
        return
    with open("playerdata.json", "w+") as playerdata_file:
        file_data = playerdata_file.read()
        playerdata = json.loads(file_data) if file_data else {}
        playerdata["highscore"] = score
        playerdata_file.write(json.dumps(playerdata))

def get_highscore(default="N/A"):
    with open("playerdata.json", "r") as playerdata_file:
        file_data = playerdata_file.read()
        playerdata = json.loads(file_data) if file_data else {}
        return playerdata.get("highscore", default)

def fade(seconds):
    original_surface = game_window.copy()
    fade = pygame.Surface(game_window.get_rect().size)
    fade.fill((0,0,0))
    for alpha in range(0, 300):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        fade.set_alpha(alpha)
        game_window.blit(original_surface, (0,0))
        game_window.blit(fade, (0,0))
        pygame.display.update()
        fps_controller.tick(300/seconds)
        


# Game Over
def game_over(score):
    fade(2.3129251701)
    
    my_font = pygame.font.SysFont('times new roman', round(90*renderScale))
    game_over_surface = my_font.render('YOU DIED', True, red)
    game_over_rect = game_over_surface.get_rect()
    game_over_rect.midtop = (round(frame_size_x*renderScale)//2, frame_size_y//4)
    game_window.fill(black)
    game_window.blit(game_over_surface, game_over_rect)
    draw_score(score, 0, red, 'times', 20)
    
    pygame.display.flip()

    save_highscore(score)
    draw_highscore(get_highscore(), 0, red, "times", 20)
    
    #click anywhere to restart or any key
    other_font = pygame.font.SysFont('times new roman', 40)
    
    deltaTime = time.time()
    color = 255
    click_anywhere = other_font.render("Press anything to restart",True,[color]*3)
    click_anywhere_rect = click_anywhere.get_rect()
    click_anywhere_rect.center = ((frame_size_x*renderScale)//2, frame_size_y//2)
    game_window.blit(click_anywhere, click_anywhere_rect)
    deltaTime = time.time()
    pygame.display.update()

    color_direction = 1
    color_speed = 240


    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                game()
        pygame.draw.rect(game_window, black, click_anywhere_rect)
        click_anywhere = other_font.render("Press anything to restart",True,[int(color)]*3)
        click_anywhere_rect = click_anywhere.get_rect()
        click_anywhere_rect.center = ((frame_size_x*renderScale)//2, (frame_size_y*renderScale)//2)
        game_window.blit(click_anywhere, click_anywhere_rect)
        pygame.display.flip()

        color_direction = 1 if color <= 0 else -1 if color >= 255 else color_direction
        increase = color_direction*color_speed*(time.time()-deltaTime)
        color += increase
        if not (0 < color < 255):
            color -= increase
            color_direction = {1:-1,-1:1}[color_direction]
        deltaTime = time.time()
        


# Drawing text
def draw_score(score, choice, color, font, size):
    score_font = pygame.font.SysFont(font, round(size*renderScale))
    score_surface = score_font.render('Score : ' + str(score), True, color)
    score_rect = score_surface.get_rect()
    if choice == 1:
        score_rect.topleft = (15*renderScale, 15*renderScale)
    else:
        score_rect.midtop = ((frame_size_x*renderScale)//2, (frame_size_y*renderScale)//1.25)
    game_window.blit(score_surface, score_rect)

def draw_highscore(score, choice, color, font, size):
    score_font = pygame.font.SysFont(font, round(size*renderScale))
    score_surface = score_font.render('Highscore : ' + str(score), True, color)
    score_rect = score_surface.get_rect()
    if choice == 1:
        score_rect.midtop = ((frame_size_x*renderScale)//2, 15*renderScale)
    else:
        score_rect.midtop = ((frame_size_x*renderScale)//2, (frame_size_y*renderScale)//1.2)
    game_window.blit(score_surface, score_rect)

def draw_label(pos, label, color, font, size, offset_y=0, offset_x=0):
    score_font = pygame.font.SysFont(font, round(size*renderScale))
    score_surface = score_font.render(f'{label} : {pos}', True, color)
    score_rect = score_surface.get_rect()
    score_rect.midtop = (round((frame_size_x*renderScale)/2)+(offset_x*renderScale)), round(((frame_size_y*renderScale)/1.25)+(offset_y*renderScale))
    game_window.blit(score_surface, score_rect)


def get_local_steering(event, direction):
    if event.key in (pygame.K_RIGHT, ord("d")):
        return 'UP' if direction == "LEFT" else ("LEFT" if direction == "DOWN" else ("DOWN" if direction == "RIGHT" else "RIGHT"))
    elif event.key in (pygame.K_LEFT, ord("a")):
        return 'UP' if direction == "RIGHT" else ("RIGHT" if direction == "DOWN" else ("DOWN" if direction == "LEFT" else "LEFT"))
    return direction

def get_global_steering(event, direction):
    print(direction)
    if event.key in (pygame.K_RIGHT, ord("d")) and direction != "LEFT":
        return "RIGHT"
    elif event.key in (pygame.K_LEFT, ord("a")) and (direction != "RIGHT"):
        return "LEFT"
    elif event.key in (pygame.K_UP, ord("w")) and direction != "DOWN":
        return "UP"
    elif event.key in (pygame.K_DOWN, ord("s")) and direction != "UP":
        return "DOWN"
    return direction


def game():
    # Sounds
    food_sound = pygame.mixer.Sound("sounds/eat_food.wav")
    crash_sound = pygame.mixer.Sound("sounds/collision.wav")
    # Set volumes
    food_sound.set_volume(volume)
    crash_sound.set_volume(volume)
    
    # Game variables
    snake_pos = [100, 50]
    snake_body = [[100, 50], [100-10, 50], [100-(2*10), 50]]

    food_pos = [random.randrange(1, (frame_size_x//10)) * 10, random.randrange(1, (frame_size_y//10)) * 10]
    food_spawn = True

    direction = 'RIGHT'

    score = 0
    highscore = get_highscore()

    difficulty = initial_difficulty

    
        
    # Main logic
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_highscore(score)
                pygame.quit()
                sys.exit()
            # Whenever a key is pressed down
            elif event.type == pygame.KEYDOWN:
                if steering_type == "LOCAL":
                    direction = get_local_steering(event, direction)
                else:
                    direction = get_global_steering(event, direction)
                # Esc -> Create event to quit the game
                if event.key == pygame.K_ESCAPE:
                    pygame.event.post(pygame.event.Event(pygame.QUIT))

        # Moving the snake
        if direction == 'UP':
            snake_pos[1] -= 10
        if direction == 'DOWN':
            snake_pos[1] += 10
        if direction == 'LEFT':
            snake_pos[0] -= 10
        if direction == 'RIGHT':
            snake_pos[0] += 10

        #Loop snake back if touches the edge using modulus if wall_collisions == False
        if not wall_collisions:
            snake_body = list(map(lambda x: [x[0]%(frame_size_x), x[1]%(frame_size_y)], snake_body))
            snake_pos = [snake_pos[0]%(frame_size_x), snake_pos[1]%(frame_size_y)]
            
        #Otherwise kill the player
        elif [snake_pos[0]%(frame_size_x), snake_pos[1]%(frame_size_y)] != snake_pos:
            crash_sound.play()
            game_over(score)

        # Snake body growing mechanism
        snake_body.insert(0, list(snake_pos))
        if snake_pos == food_pos:
            food_sound.play()
            score += 1
            food_spawn = False
        else:
            snake_body.pop()

        # Spawning food on the screen
        if not food_spawn:
            food_pos = [random.randrange(1, (frame_size_x//10)) * 10, random.randrange(1, (frame_size_y//10)) * 10]
        food_spawn = True

        game_window.fill(black)

        # Snake food
        pygame.draw.rect(game_window, white, pygame.Rect(round(food_pos[0]*renderScale), round(food_pos[1]*renderScale), round(10*renderScale), round(10*renderScale)))

        # GFX
        
        for i in range(len(snake_body)):
            # Snake body
            # .draw.rect(play_surface, color, xy-coordinate)
            # xy-coordinate -> .Rect(x, y, size_x, size_y)
            pygame.draw.rect(game_window, (0, 255, (200*(i/len(snake_body)))), pygame.Rect(round(snake_body[i][0]*renderScale), round(snake_body[i][1]*renderScale), round(10*renderScale), round(10*renderScale)))

        
        # Speed up game by score
        if dynamic_difficulty:
            difficulty = initial_difficulty*(1.0075**score)


        # Game Over conditions
        # Touching the snake body
        for block in snake_body[1:]:
            if snake_pos[0] == block[0] and snake_pos[1] == block[1] and body_collisions:
                crash_sound.play()
                game_over(score)

        
        draw_score(score, 1, white, 'consolas', 20)
        draw_highscore(get_highscore(), 1, white, "consolas", 20)
        if show_difficulty:
            draw_label(difficulty,"Difficulty",white,"consolas",20, offset_y = -40)
        if show_pos:
            draw_label(snake_pos, "Position", white, "consolas",20)
        if show_food_pos:
            draw_label(food_pos, 'Food Position', white, "consolas", 20, offset_y=40)
        # Refresh game screen
        pygame.display.update()
        # Refresh rate
        fps_controller.tick(difficulty)

def start():
    pygame.draw.rect(game_window, white, logo_rect)
    lastFrame = time.time()
    new_logo_rect = pygame.Rect(logo_rect)
    sub = 0

    movement_function = lambda x: gamma.pdf(x/(frame_size_x/10), 100, 130)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        if not new_logo_rect.x < frame_size_x/10:
            pygame.draw.rect(game_window, white, new_logo_rect)
            sub += (time.time()-lastFrame)*movement_function(sub)
            new_logo_rect = pygame.Rect(logo_rect)
            new_logo_rect.x-=int(sub)

        game_window.blit(logo, new_logo_rect)
        pygame.display.update()

game()
