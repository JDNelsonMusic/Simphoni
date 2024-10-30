import pygame
import sys
import random
import math

# Initialize Pygame
pygame.init()

# Double the resolution (Higher resolution)
WIDTH, HEIGHT = 1800, 1000  # Double the original width and height
CELL_SIZE = 3  # Keeping the small grid size, but doubling the snake's visual size

# Colors
TEAL_SHADES = [
    (0, 128, 128),
    (0, 139, 139),
    (0, 150, 150),
    (0, 160, 160),
    (0, 170, 170)
]
MAROON_SHADES = [
    (128, 0, 0),
    (139, 0, 0),
    (150, 0, 0),
    (160, 0, 0),
    (170, 0, 0)
]

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Two-Player Snake Game')

# Load and scale the background image
background_image = pygame.image.load('pygame_py_files/jdn_snake_v25/haunted_corn_maze.png').convert()
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

# Load images and scale them to appropriate sizes
pumpkin_small_img = pygame.image.load('pygame_py_files/jdn_snake_v25/pumpkin.small.png').convert_alpha()
pumpkin_small_img = pygame.transform.scale(pumpkin_small_img, (9 * CELL_SIZE, 22 * CELL_SIZE))

pumpkin_medium_img = pygame.image.load('pygame_py_files/jdn_snake_v25/pumpkin.medium.png').convert_alpha()
pumpkin_medium_img = pygame.transform.scale(pumpkin_medium_img, (18 * CELL_SIZE, 42 * CELL_SIZE))

pumpkin_large_img = pygame.image.load('pygame_py_files/jdn_snake_v25/pumpkin.big.png').convert_alpha()
pumpkin_large_img = pygame.transform.scale(pumpkin_large_img, (36 * CELL_SIZE, 72 * CELL_SIZE))

apple_light_img = pygame.image.load('pygame_py_files/jdn_snake_v25/apple.light.png').convert_alpha()
apple_light_img = pygame.transform.scale(apple_light_img, (12 * CELL_SIZE, 12 * CELL_SIZE))

apple_dark_img = pygame.image.load('pygame_py_files/jdn_snake_v25/apple.dark.png').convert_alpha()
apple_dark_img = pygame.transform.scale(apple_dark_img, (18 * CELL_SIZE, 30 * CELL_SIZE))

# Map item types to images
FOOD_IMAGES = {
    'small': pumpkin_small_img,
    'medium': pumpkin_medium_img,
    'large': pumpkin_large_img,
    'light_apple': apple_light_img,
    'dark_apple': apple_dark_img
}

# Load monster images and scale them appropriately

# Ghosts (aspect ratio ~1:3), same size as medium pumpkins (10x20 pixels)
tealghost_img = pygame.image.load('pygame_py_files/jdn_snake_v25/tealghost.png').convert_alpha()
tealghost_img = pygame.transform.scale(tealghost_img, (20 * CELL_SIZE, 30 * CELL_SIZE))
maroonghost_img = pygame.image.load('pygame_py_files/jdn_snake_v25/maroonghost.png').convert_alpha()
maroonghost_img = pygame.transform.scale(maroonghost_img, (20 * CELL_SIZE, 30 * CELL_SIZE))

# Skeletons, same size as big pumpkins (20x40 pixels)
tealskeleton_img = pygame.image.load('pygame_py_files/jdn_snake_v25/tealskeleton.png').convert_alpha()
tealskeleton_img = pygame.transform.scale(tealskeleton_img, (10 * CELL_SIZE, 30 * CELL_SIZE))
maroonskeleton_img = pygame.image.load('pygame_py_files/jdn_snake_v25/maroonskeleton.png').convert_alpha()
maroonskeleton_img = pygame.transform.scale(maroonskeleton_img, (10 * CELL_SIZE, 30 * CELL_SIZE))

# Zombies, slightly bigger than big pumpkins
# Big pumpkins are 20x40 pixels; zombies will be 24x50 pixels
tealzombie_img = pygame.image.load('pygame_py_files/jdn_snake_v25/tealzombie.png').convert_alpha()
tealzombie_img = pygame.transform.scale(tealzombie_img, (20 * CELL_SIZE, 50 * CELL_SIZE))
maroonzombie_img = pygame.image.load('pygame_py_files/jdn_snake_v25/maroonzombie.png').convert_alpha()
maroonzombie_img = pygame.transform.scale(maroonzombie_img, (20 * CELL_SIZE, 50 * CELL_SIZE))

# Map monster types to images for each player
MONSTER_IMAGES = {
    'player1': {
        'ghost': tealghost_img,
        'skeleton': tealskeleton_img,
        'zombie': tealzombie_img
    },
    'player2': {
        'ghost': maroonghost_img,
        'skeleton': maroonskeleton_img,
        'zombie': maroonzombie_img
    }
}

# Load sounds
pygame.mixer.init()
pygame.mixer.set_num_channels(32)  # Increase number of channels for overlapping sounds

# Volume control variables
MUSIC_VOLUME = 1.0  # Main music track volume (default same as now)
SFX_VOLUME = 0.5    # Each SFX volume (half of what they are now)

# Load sound effects
SOUND_EFFECTS = {
    'monsterspawn': pygame.mixer.Sound('pygame_py_files/jdn_snake_v25/sfx.monsterspawn.mp3'),
    'tinypumpkin': pygame.mixer.Sound('pygame_py_files/jdn_snake_v25/sfx.tinypumpkin.mp3'),
    'mediumpumpkin': pygame.mixer.Sound('pygame_py_files/jdn_snake_v25/sfx.mediumpumpkin.mp3'),
    'bigpumpkin': pygame.mixer.Sound('pygame_py_files/jdn_snake_v25/sfx.bigpumpkin.mp3'),
    'redapple': pygame.mixer.Sound('pygame_py_files/jdn_snake_v25/sfx.redapple.mp3'),
    'greenapple': pygame.mixer.Sound('pygame_py_files/jdn_snake_v25/sfx.greenapple.mp3'),
    'ghost': pygame.mixer.Sound('pygame_py_files/jdn_snake_v25/sfx.ghost.mp3'),
    'skeleton': pygame.mixer.Sound('pygame_py_files/jdn_snake_v25/sfx.skeleton.mp3'),
    'zombie': pygame.mixer.Sound('pygame_py_files/jdn_snake_v25/sfx.zombie.mp3'),
}

# Set volume for sound effects
for sfx in SOUND_EFFECTS.values():
    sfx.set_volume(SFX_VOLUME)

# Clock for controlling the frame rate
clock = pygame.time.Clock()

def draw_snake(snake_body, colors, is_blinking, direction):
    """Draw the snake with a head and body."""
    body_thickness = 2 * CELL_SIZE
    head_size = int(1.5 * body_thickness)

    # Determine color (red) if blinking due to poison apple
    if is_blinking:
        colors = [(255, 0, 0)] * len(snake_body)

    # Draw the body segments
    for i, segment in enumerate(snake_body[1:]):
        color = colors[i % len(colors)]
        pygame.draw.rect(screen, color, pygame.Rect(segment[0], segment[1], body_thickness, body_thickness))

    # Draw the head
    head_pos = snake_body[0]
    head_rect = pygame.Rect(head_pos[0], head_pos[1], head_size, head_size)
    if direction == 'UP':
        head_rect.center = (head_pos[0] + body_thickness // 2, head_pos[1])
    elif direction == 'DOWN':
        head_rect.center = (head_pos[0] + body_thickness // 2, head_pos[1] + body_thickness)
    elif direction == 'LEFT':
        head_rect.center = (head_pos[0], head_pos[1] + body_thickness // 2)
    elif direction == 'RIGHT':
        head_rect.center = (head_pos[0] + body_thickness, head_pos[1] + body_thickness // 2)

    pygame.draw.ellipse(screen, colors[0], head_rect)

    # Draw fangs
    fang_length = CELL_SIZE
    if direction == 'UP':
        fang1 = [(head_rect.centerx - CELL_SIZE, head_rect.centery),
                 (head_rect.centerx - CELL_SIZE // 2, head_rect.centery - fang_length)]
        fang2 = [(head_rect.centerx + CELL_SIZE, head_rect.centery),
                 (head_rect.centerx + CELL_SIZE // 2, head_rect.centery - fang_length)]
    elif direction == 'DOWN':
        fang1 = [(head_rect.centerx - CELL_SIZE, head_rect.centery),
                 (head_rect.centerx - CELL_SIZE // 2, head_rect.centery + fang_length)]
        fang2 = [(head_rect.centerx + CELL_SIZE, head_rect.centery),
                 (head_rect.centerx + CELL_SIZE // 2, head_rect.centery + fang_length)]
    elif direction == 'LEFT':
        fang1 = [(head_rect.centerx, head_rect.centery - CELL_SIZE),
                 (head_rect.centerx - fang_length, head_rect.centery - CELL_SIZE // 2)]
        fang2 = [(head_rect.centerx, head_rect.centery + CELL_SIZE),
                 (head_rect.centerx - fang_length, head_rect.centery + CELL_SIZE // 2)]
    elif direction == 'RIGHT':
        fang1 = [(head_rect.centerx, head_rect.centery - CELL_SIZE),
                 (head_rect.centerx + fang_length, head_rect.centery - CELL_SIZE // 2)]
        fang2 = [(head_rect.centerx, head_rect.centery + CELL_SIZE),
                 (head_rect.centerx + fang_length, head_rect.centery + CELL_SIZE // 2)]
    pygame.draw.lines(screen, (255, 255, 255), False, fang1, 2)
    pygame.draw.lines(screen, (255, 255, 255), False, fang2, 2)

def draw_food(food_items):
    """Draw food items based on their types and sizes with fade-in effect."""
    current_time = pygame.time.get_ticks()
    for item in food_items:
        pos = item['pos']
        item_type = item['type']
        image = FOOD_IMAGES[item_type].copy()

        # Apply fade-in effect
        time_since_spawn = (current_time - item['spawn_time']) / 1000
        if time_since_spawn <= item['fade_duration']:
            alpha = int(255 * (time_since_spawn / item['fade_duration']))
            image.set_alpha(alpha)
        else:
            image.set_alpha(255)

        screen.blit(image, pos)

def draw_monsters(monsters):
    """Draw the monsters on the screen."""
    for monster in monsters:
        pos = (monster['pos'][0], monster['pos'][1])
        image = MONSTER_IMAGES[monster['owner']][monster['type']].copy()
        # Apply alpha for fade-in effect
        image.set_alpha(monster['alpha'])
        screen.blit(image, pos)

def spawn_food(snake_body1, snake_body2, image, food_items):
    """Generate food at random locations that doesn't overlap with the snakes or other food."""
    while True:
        food_pos = [
            random.randrange(0, (WIDTH - image.get_width()) // CELL_SIZE) * CELL_SIZE,
            random.randrange(0, (HEIGHT - image.get_height()) // CELL_SIZE) * CELL_SIZE
        ]
        rect = pygame.Rect(food_pos[0], food_pos[1], image.get_width(), image.get_height())
        collision_with_snake = any(rect.collidepoint(segment) for segment in snake_body1 + snake_body2)
        collision_with_food = any(rect.colliderect(pygame.Rect(item['pos'][0], item['pos'][1], FOOD_IMAGES[item['type']].get_width(), FOOD_IMAGES[item['type']].get_height())) for item in food_items)
        if not collision_with_snake and not collision_with_food:
            return food_pos

def spawn_monster(monster_type, owner, target, snake_body1, snake_body2, spawn_pos):
    """Spawn a monster at the pumpkin's position."""
    image = MONSTER_IMAGES[owner][monster_type]
    size = (image.get_width(), image.get_height())
    pos = list(spawn_pos)  # Start position is the pumpkin's position

    # Calculate direction toward the furthest corner
    corners = [(0, 0), (WIDTH, 0), (0, HEIGHT), (WIDTH, HEIGHT)]
    max_distance = -1
    furthest_corner = None
    for corner in corners:
        dx = corner[0] - pos[0]
        dy = corner[1] - pos[1]
        distance = math.hypot(dx, dy)
        if distance > max_distance:
            max_distance = distance
            furthest_corner = corner

    # Calculate unit direction vector toward furthest corner
    direction_vector = (furthest_corner[0] - pos[0], furthest_corner[1] - pos[1])
    direction_length = math.hypot(*direction_vector)
    if direction_length == 0:
        direction = (0, 0)
    else:
        direction = (direction_vector[0] / direction_length, direction_vector[1] / direction_length)

    # Set speeds
    FAST_SPEED = 3  # pixels per frame
    MEDIUM_SPEED = 2  # pixels per frame
    SLOW_SPEED = 1  # pixels per frame

    # Initialize monster properties
    monster = {
        'type': monster_type,
        'pos': pos,
        'spawn_time': pygame.time.get_ticks(),
        'size': size,
        'owner': owner,
        'target': target,
        'alpha': 0,  # For fade-in effect
        'fade_duration': 1.0,  # 1 second fade-in
        'direction': direction,
        'damage': 0,
        'speed': 0,
        'movement_timer': 0  # For zombie speed toggling
    }

    if monster_type == 'ghost':
        monster['damage'] = 6
        monster['speed'] = SLOW_SPEED
    elif monster_type == 'skeleton':
        monster['damage'] = 12
        monster['speed'] = MEDIUM_SPEED
    elif monster_type == 'zombie':
        monster['damage'] = 18
        monster['speed'] = 0  # Starts stationary
        monster['is_fast'] = False  # To toggle between speeds
        monster['fast_duration'] = 0.15  # Fast movement lasts 0.15 seconds
        monster['slow_duration'] = 0.5  # Slow movement duration (stationary)
        monster['movement_timer'] = 0

    return monster

def display_scores(score1, score2, player1_name, player2_name):
    """Display the scores of both players."""
    font = pygame.font.SysFont('arial', 15)  # Reduced font size
    score_surface1 = font.render(f'{player1_name} (Player 1) Score: {int(score1)}', True, (255, 255, 255))
    score_surface2 = font.render(f'{player2_name} (Player 2) Score: {int(score2)}', True, (255, 255, 255))
    screen.blit(score_surface1, (WIDTH - 350, 10))
    screen.blit(score_surface2, (10, 10))

def display_timer(remaining_time):
    """Display the remaining time at the top center of the screen."""
    font = pygame.font.SysFont('arial', 15)  # Reduced font size
    minutes = int(remaining_time) // 60
    seconds = int(remaining_time) % 60
    timer_surface = font.render(f'Time Left: {minutes:02d}:{seconds:02d}', True, (255, 255, 255))
    timer_rect = timer_surface.get_rect(center=(WIDTH / 2, 20))
    screen.blit(timer_surface, timer_rect)

def game_over_screen(winner_name, score1, score2, counts1, counts2, player1_name, player2_name):
    """Display the 'Game Over' message with breakdowns and options."""
    font = pygame.font.SysFont('arial', 50)  # Reduced font size
    message = 'GAME OVER'
    screen.blit(background_image, (0, 0))  # Display the background

    # Display the 'GAME OVER' message
    for i, letter in enumerate(message):
        letter_surface = font.render(letter, True, (255, 165, 0))
        screen.blit(letter_surface, (WIDTH / 2 - 150 + i * 40, HEIGHT / 6))

    # Display final scores and winner
    final_score_font = pygame.font.SysFont('arial', 25)  # Reduced font size
    final_score_surface1 = final_score_font.render(f'{player1_name} Final Score: {int(score1)}', True, (255, 255, 255))
    final_score_surface2 = final_score_font.render(f'{player2_name} Final Score: {int(score2)}', True, (255, 255, 255))
    winner_surface = final_score_font.render(f'Winner: {winner_name}', True, (255, 215, 0))

    screen.blit(final_score_surface1, (WIDTH / 4, HEIGHT / 3))
    screen.blit(final_score_surface2, (WIDTH / 4, HEIGHT / 3 + 30))
    screen.blit(winner_surface, (WIDTH / 4, HEIGHT / 3 + 60))

    # Display item breakdowns for each player
    breakdown_font = pygame.font.SysFont('arial', 20)  # Reduced font size
    y_offset = HEIGHT / 3 + 100
    for player, counts in [(player1_name, counts1), (player2_name, counts2)]:
        breakdown_surface = breakdown_font.render(f"{player}'s Item Breakdown:", True, (255, 255, 255))
        screen.blit(breakdown_surface, (WIDTH / 4, y_offset))
        y_offset += 25
        for item_type in ['small', 'medium', 'large', 'light_apple', 'dark_apple']:
            count = counts[item_type]
            if item_type == 'light_apple':
                item_name = 'Light Poison Apples'
            elif item_type == 'dark_apple':
                item_name = 'Dark Poison Apples'
            else:
                item_name = f"{item_type.capitalize()} Pumpkins"
            item_surface = breakdown_font.render(f"{item_name}: {count}", True, (255, 255, 255))
            screen.blit(item_surface, (WIDTH / 4 + 20, y_offset))
            y_offset += 20
        y_offset += 15

    # Add buttons
    button_font = pygame.font.SysFont('arial', 20)  # Reduced font size
    new_game_button = pygame.Rect(WIDTH / 4, HEIGHT - 150, 250, 50)
    close_game_button = pygame.Rect(WIDTH / 2 + 50, HEIGHT - 150, 250, 50)
    pygame.draw.rect(screen, (0, 128, 0), new_game_button)
    pygame.draw.rect(screen, (128, 0, 0), close_game_button)

    new_game_surface = button_font.render('Start New Game', True, (255, 255, 255))
    close_game_surface = button_font.render('Close Game', True, (255, 255, 255))
    screen.blit(new_game_surface, (new_game_button.x + 20, new_game_button.y + 10))
    screen.blit(close_game_surface, (close_game_button.x + 50, close_game_button.y + 10))

    pygame.display.flip()

    # Event loop for the game over screen
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if new_game_button.collidepoint(event.pos):
                    player_setup_screen()  # Go back to player setup screen
                elif close_game_button.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

def check_food_collision(snake_pos, item):
    """Check if the snake has collided with the bottom two-thirds of the food item."""
    item_pos = item['pos']
    image = FOOD_IMAGES[item['type']]
    image_width = image.get_width()
    image_height = image.get_height()

    # Define the collision rect as the bottom two-thirds of the image
    collision_rect = pygame.Rect(
        item_pos[0],
        item_pos[1] + image_height / 3,  # Start from one-third down the image
        image_width,
        image_height * 2 / 3  # Cover the bottom two-thirds
    )
    snake_rect = pygame.Rect(snake_pos[0], snake_pos[1], 2 * CELL_SIZE, 2 * CELL_SIZE)
    return collision_rect.colliderect(snake_rect)

def check_monster_collision(snake_pos, monster):
    """Check if the snake has collided with the monster."""
    item_pos = monster['pos']
    image = MONSTER_IMAGES[monster['owner']][monster['type']]
    rect = pygame.Rect(item_pos[0], item_pos[1], image.get_width(), image.get_height())
    snake_rect = pygame.Rect(snake_pos[0], snake_pos[1], 2 * CELL_SIZE, 2 * CELL_SIZE)
    return rect.colliderect(snake_rect)

def player_setup_screen():
    """Display the player setup screen and collect player names and speed settings."""
    # Variables for player names and speeds
    player1_name = ''
    player2_name = ''
    active_name_field = None  # None, 'player1', or 'player2'

    # Default speed settings
    player1_speed_setting = 'hunting'
    player2_speed_setting = 'hunting'

    # Speed options and their corresponding speeds
    speed_options = {
        'stalking': 2,
        'hunting': 4,
        'fleeing': 8
    }

    # Font settings
    font = pygame.font.SysFont('arial', 30)
    small_font = pygame.font.SysFont('arial', 20)
    bullet_font = pygame.font.SysFont('arial', 25)

    # Input boxes and positions
    input_box_width = 200
    input_box_height = 40
    player1_input_box = pygame.Rect(WIDTH * 3 / 4 - input_box_width / 2, HEIGHT / 4, input_box_width, input_box_height)
    player2_input_box = pygame.Rect(WIDTH / 4 - input_box_width / 2, HEIGHT / 4, input_box_width, input_box_height)

    # Positions for speed options
    player1_speed_positions = {}
    player2_speed_positions = {}
    speeds = ['stalking', 'hunting', 'fleeing']
    y_offset = HEIGHT / 2

    for i, speed in enumerate(speeds):
        player1_speed_positions[speed] = (WIDTH * 3 / 4 - 50, y_offset + i * 40)
        player2_speed_positions[speed] = (WIDTH / 4 - 50, y_offset + i * 40)

    # Start button
    start_button = pygame.Rect(WIDTH / 2 - 100, HEIGHT - 100, 200, 50)

    # Load snake images for display
    snake1_image = pygame.Surface((60, 60), pygame.SRCALPHA)
    draw_snake_image(snake1_image, TEAL_SHADES)
    snake2_image = pygame.Surface((60, 60), pygame.SRCALPHA)
    draw_snake_image(snake2_image, MAROON_SHADES)

    # Main loop for the setup screen
    while True:
        screen.blit(background_image, (0, 0))
        # Divide screen into two halves
        pygame.draw.line(screen, (255, 255, 255), (WIDTH / 2, 0), (WIDTH / 2, HEIGHT), 2)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if player1_input_box.collidepoint(event.pos):
                    active_name_field = 'player1'
                elif player2_input_box.collidepoint(event.pos):
                    active_name_field = 'player2'
                else:
                    active_name_field = None

                # Check speed option clicks for player 1
                for speed, pos in player1_speed_positions.items():
                    bullet_rect = pygame.Rect(pos[0] - 10, pos[1] - 10, 20, 20)
                    if bullet_rect.collidepoint(event.pos):
                        player1_speed_setting = speed

                # Check speed option clicks for player 2
                for speed, pos in player2_speed_positions.items():
                    bullet_rect = pygame.Rect(pos[0] - 10, pos[1] - 10, 20, 20)
                    if bullet_rect.collidepoint(event.pos):
                        player2_speed_setting = speed

                # Check if start button is clicked
                if start_button.collidepoint(event.pos):
                    if player1_name.strip() == '':
                        player1_name = 'Player 1'
                    if player2_name.strip() == '':
                        player2_name = 'Player 2'
                    main(player1_name, player2_name, speed_options[player1_speed_setting], speed_options[player2_speed_setting])
                    return

            if event.type == pygame.KEYDOWN:
                if active_name_field == 'player1':
                    if event.key == pygame.K_BACKSPACE:
                        player1_name = player1_name[:-1]
                    else:
                        player1_name += event.unicode
                elif active_name_field == 'player2':
                    if event.key == pygame.K_BACKSPACE:
                        player2_name = player2_name[:-1]
                    else:
                        player2_name += event.unicode

        # Draw input boxes and names
        pygame.draw.rect(screen, (255, 255, 255), player1_input_box, 2)
        pygame.draw.rect(screen, (255, 255, 255), player2_input_box, 2)
        player1_name_surface = font.render(player1_name, True, (255, 255, 255))
        player2_name_surface = font.render(player2_name, True, (255, 255, 255))
        screen.blit(player1_name_surface, (player1_input_box.x + 5, player1_input_box.y + 5))
        screen.blit(player2_name_surface, (player2_input_box.x + 5, player2_input_box.y + 5))

        # Labels for input boxes
        player1_label = font.render('Player 1 Name:', True, (255, 255, 255))
        player2_label = font.render('Player 2 Name:', True, (255, 255, 255))
        screen.blit(player1_label, (player1_input_box.x, player1_input_box.y - 40))
        screen.blit(player2_label, (player2_input_box.x, player2_input_box.y - 40))

        # Draw speed options
        for speed, pos in player1_speed_positions.items():
            # Bullet point
            bullet_color = (255, 165, 0) if player1_speed_setting == speed else (255, 255, 255)
            pygame.draw.circle(screen, bullet_color, (int(pos[0]), int(pos[1])), 10)
            # Label
            label = small_font.render(speed.capitalize(), True, (255, 255, 255))
            screen.blit(label, (pos[0] + 20, pos[1] - 10))

        for speed, pos in player2_speed_positions.items():
            bullet_color = (255, 165, 0) if player2_speed_setting == speed else (255, 255, 255)
            pygame.draw.circle(screen, bullet_color, (int(pos[0]), int(pos[1])), 10)
            label = small_font.render(speed.capitalize(), True, (255, 255, 255))
            screen.blit(label, (pos[0] + 20, pos[1] - 10))

        # Labels for speed options
        player1_speed_label = font.render('Speed Settings:', True, (255, 255, 255))
        player2_speed_label = font.render('Speed Settings:', True, (255, 255, 255))
        screen.blit(player1_speed_label, (WIDTH * 3 / 4 - 100, y_offset - 50))
        screen.blit(player2_speed_label, (WIDTH / 4 - 100, y_offset - 50))

        # Draw snakes
        screen.blit(snake1_image, (WIDTH * 3 / 4 - 30, player1_input_box.y + 100))
        screen.blit(snake2_image, (WIDTH / 4 - 30, player2_input_box.y + 100))

        # Draw start button
        pygame.draw.rect(screen, (0, 128, 0), start_button)
        start_label = font.render('Start', True, (255, 255, 255))
        start_label_rect = start_label.get_rect(center=start_button.center)
        screen.blit(start_label, start_label_rect)

        pygame.display.flip()
        clock.tick(60)

def draw_snake_image(surface, colors):
    """Draw a snake image for the setup screen."""
    body_thickness = 20
    # Draw head
    pygame.draw.circle(surface, colors[0], (30, 30), 15)
    # Draw body segments
    for i in range(3):
        pygame.draw.rect(surface, colors[(i + 1) % len(colors)], pygame.Rect(30 - i * 15, 30, body_thickness, body_thickness))

def main(player1_name, player2_name, player1_speed, player2_speed):
    # Global score variables and item counts
    score1 = 0
    score2 = 0
    counts1 = {'small': 0, 'medium': 0, 'large': 0, 'light_apple': 0, 'dark_apple': 0}
    counts2 = {'small': 0, 'medium': 0, 'large': 0, 'light_apple': 0, 'dark_apple': 0}

    # Initial snake positions and bodies
    snake1_pos = [100.0, 50.0]
    snake1_body = [[100.0, 50.0], [80.0, 50.0], [60.0, 50.0]]

    snake2_pos = [400.0, 50.0]
    snake2_body = [[400.0, 50.0], [420.0, 50.0], [440.0, 50.0]]

    # Snake growth pending and blinking status
    snake1_growth_pending = 0
    snake2_growth_pending = 0
    snake1_blinking = False
    snake2_blinking = False
    snake1_blink_timer = 0
    snake2_blink_timer = 0
    BLINK_DURATION = 50  # Total frames to blink
    BLINK_FREQUENCY = 10  # Blink every 5 frames

    # Initial food items
    food_items = []
    for item_type in ['small', 'medium', 'large', 'light_apple', 'dark_apple']:
        item = {'type': item_type}
        image = FOOD_IMAGES[item_type]
        item['pos'] = spawn_food(snake1_body, snake2_body, image, food_items)
        item['spawn_time'] = pygame.time.get_ticks()
        item['fade_duration'] = 1.0  # 1 second fade-in
        food_items.append(item)

    # Monsters list
    monsters = []

    # Initial directions
    direction1 = 'RIGHT'
    change_to1 = direction1
    direction2 = 'LEFT'
    change_to2 = direction2

    # Game Over flag
    game_over = False

    # Game timer
    game_start_time = pygame.time.get_ticks()
    total_game_time = 210  # 3 minutes and 30 seconds

    # Initialize background music
    background_music = pygame.mixer.Sound('pygame_py_files/jdn_snake_v25/twistingfate.mp3')
    background_music.set_volume(MUSIC_VOLUME)
    music_channel1 = pygame.mixer.Channel(0)
    music_channel2 = pygame.mixer.Channel(1)

    # Music settings
    music_length = background_music.get_length() * 1000  # Convert to milliseconds
    overlap_time = 12 * 1000  # Convert to milliseconds
    music_restart_interval = music_length - overlap_time

    # Start playing music on channel1
    music_channel1.play(background_music)
    current_music_channel = music_channel1

    # Schedule next music start time
    next_music_start_time = pygame.time.get_ticks() + music_restart_interval

    while not game_over:
        elapsed_time = (pygame.time.get_ticks() - game_start_time) / 1000
        remaining_time = max(0, total_game_time - elapsed_time)
        if remaining_time <= 0:
            game_over = True
            break  # Exit the main loop to display game over screen

        # Music looping with overlap
        current_time = pygame.time.get_ticks()
        if current_time >= next_music_start_time:
            # Start music on the other channel
            if current_music_channel == music_channel1:
                music_channel2.play(background_music)
                current_music_channel = music_channel2
            else:
                music_channel1.play(background_music)
                current_music_channel = music_channel1
                
                # Schedule next music start time
                next_music_start_time = current_time + music_restart_interval

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                # Player 1 controls (arrow keys)
                if event.key == pygame.K_UP and direction1 != 'DOWN':
                    change_to1 = 'UP'
                elif event.key == pygame.K_DOWN and direction1 != 'UP':
                    change_to1 = 'DOWN'
                elif event.key == pygame.K_LEFT and direction1 != 'RIGHT':
                    change_to1 = 'LEFT'
                elif event.key == pygame.K_RIGHT and direction1 != 'LEFT':
                    change_to1 = 'RIGHT'

                # Player 2 controls (WASD)
                if event.key == pygame.K_w and direction2 != 'DOWN':
                    change_to2 = 'UP'
                elif event.key == pygame.K_s and direction2 != 'UP':
                    change_to2 = 'DOWN'
                elif event.key == pygame.K_a and direction2 != 'RIGHT':
                    change_to2 = 'LEFT'
                elif event.key == pygame.K_d and direction2 != 'LEFT':
                    change_to2 = 'RIGHT'
                        
        # Update the direction for both players
        direction1 = change_to1
        direction2 = change_to2

        # Move both snakes
        if direction1 == 'UP':
            snake1_pos[1] -= player1_speed
        elif direction1 == 'DOWN':
            snake1_pos[1] += player1_speed
        elif direction1 == 'LEFT':
            snake1_pos[0] -= player1_speed
        elif direction1 == 'RIGHT':
            snake1_pos[0] += player1_speed

        if direction2 == 'UP':
            snake2_pos[1] -= player2_speed
        elif direction2 == 'DOWN':
            snake2_pos[1] += player2_speed
        elif direction2 == 'LEFT':
            snake2_pos[0] -= player2_speed
        elif direction2 == 'RIGHT':
            snake2_pos[0] += player2_speed

        # Wrap-around logic for walls for both players
        snake1_pos[0] = snake1_pos[0] % WIDTH
        snake1_pos[1] = snake1_pos[1] % HEIGHT

        snake2_pos[0] = snake2_pos[0] % WIDTH
        snake2_pos[1] = snake2_pos[1] % HEIGHT

        # Snake body growing mechanism for both players
        snake1_body.insert(0, list(snake1_pos))
        snake2_body.insert(0, list(snake2_pos))

        # Ensure the snake bodies don't grow infinitely due to fractional movement
        if len(snake1_body) > 1000:
            snake1_body = snake1_body[:1000]
        if len(snake2_body) > 1000:
            snake2_body = snake2_body[:1000]

        # Check for food collisions for both snakes
        for item in food_items:
            if check_food_collision(snake1_pos, item):
                image = FOOD_IMAGES[item['type']]
                if item['type'] == 'light_apple':
                    score1 *= 0.5  # Reduce score by 50%
                    counts1['light_apple'] += 1
                    snake1_blinking = True
                    snake1_blink_timer = 0
                    SOUND_EFFECTS['redapple'].play()
                elif item['type'] == 'dark_apple':
                    score1 *= 0.8  # Reduce score by 20%
                    counts1['dark_apple'] += 1
                    snake1_blinking = True
                    snake1_blink_timer = 0
                    SOUND_EFFECTS['greenapple'].play()
                else:
                    points = {'small': 36, 'medium': 18, 'large': 12}[item['type']]
                    score1 += points
                    counts1[item['type']] += 1
                    snake1_growth_pending += 2
                    # Play pumpkin sound
                    if item['type'] == 'small':
                        SOUND_EFFECTS['tinypumpkin'].play()
                    elif item['type'] == 'medium':
                        SOUND_EFFECTS['mediumpumpkin'].play()
                    elif item['type'] == 'large':
                        SOUND_EFFECTS['bigpumpkin'].play()
                    # Play monster spawn sound
                    SOUND_EFFECTS['monsterspawn'].play()
                    # Spawn monster for player 2
                    if item['type'] == 'small':
                        monster_type = 'ghost'
                    elif item['type'] == 'medium':
                        monster_type = 'skeleton'
                    elif item['type'] == 'large':
                        monster_type = 'zombie'
                    monster = spawn_monster(monster_type, 'player1', 'player2', snake1_body, snake2_body, item['pos'])
                    monsters.append(monster)
                # Respawn the food item
                item['pos'] = spawn_food(snake1_body, snake2_body, image, food_items)
                item['spawn_time'] = pygame.time.get_ticks()
                break
        else:
            if snake1_growth_pending > 0:
                snake1_growth_pending -= 1
            else:
                snake1_body.pop()

        for item in food_items:
            if check_food_collision(snake2_pos, item):
                image = FOOD_IMAGES[item['type']]
                if item['type'] == 'light_apple':
                    score2 *= 0.5  # Reduce score by 50%
                    counts2['light_apple'] += 1
                    snake2_blinking = True
                    snake2_blink_timer = 0
                    SOUND_EFFECTS['redapple'].play()
                elif item['type'] == 'dark_apple':
                    score2 *= 0.8  # Reduce score by 20%
                    counts2['dark_apple'] += 1
                    snake2_blinking = True
                    snake2_blink_timer = 0
                    SOUND_EFFECTS['greenapple'].play()
                else:
                    points = {'small': 36, 'medium': 18, 'large': 12}[item['type']]
                    score2 += points
                    counts2[item['type']] += 1
                    snake2_growth_pending += 2
                    # Play pumpkin sound
                    if item['type'] == 'small':
                        SOUND_EFFECTS['tinypumpkin'].play()
                    elif item['type'] == 'medium':
                        SOUND_EFFECTS['mediumpumpkin'].play()
                    elif item['type'] == 'large':
                        SOUND_EFFECTS['bigpumpkin'].play()
                    # Play monster spawn sound
                    SOUND_EFFECTS['monsterspawn'].play()
                    # Spawn monster for player 1
                    if item['type'] == 'small':
                        monster_type = 'ghost'
                    elif item['type'] == 'medium':
                        monster_type = 'skeleton'
                    elif item['type'] == 'large':
                        monster_type = 'zombie'
                    monster = spawn_monster(monster_type, 'player2', 'player1', snake1_body, snake2_body, item['pos'])
                    monsters.append(monster)
                # Respawn the food item
                item['pos'] = spawn_food(snake1_body, snake2_body, image, food_items)
                item['spawn_time'] = pygame.time.get_ticks()
                break
        else:
            if snake2_growth_pending > 0:
                snake2_growth_pending -= 1
            else:
                snake2_body.pop()

        # Update blink timers
        if snake1_blinking:
            snake1_blink_timer += 1
            if snake1_blink_timer >= BLINK_DURATION:
                snake1_blinking = False
                snake1_blink_timer = 0

        if snake2_blinking:
            snake2_blink_timer += 1
            if snake2_blink_timer >= BLINK_DURATION:
                snake2_blinking = False
                snake2_blink_timer = 0

        # Update monsters
        current_time = pygame.time.get_ticks()
        for monster in monsters[:]:
            # Fade-in effect
            time_since_spawn = (current_time - monster['spawn_time']) / 1000
            if time_since_spawn <= monster['fade_duration']:
                monster['alpha'] = int(255 * (time_since_spawn / monster['fade_duration']))
            else:
                monster['alpha'] = 255

            # Monster movement
            if monster['type'] == 'ghost':
                # Move in sine-wave pattern
                amplitude = 1  # Amplitude of sine wave
                frequency = 0.005  # Frequency of sine wave
                monster['pos'][0] += monster['direction'][0] * monster['speed']
                monster['pos'][1] += monster['direction'][1] * monster['speed'] + amplitude * math.sin(frequency * current_time)
            elif monster['type'] == 'skeleton':
                # Move in straight line
                monster['pos'][0] += monster['direction'][0] * monster['speed']
                monster['pos'][1] += monster['direction'][1] * monster['speed']
            elif monster['type'] == 'zombie':
                # Alternate speed
                monster['movement_timer'] += clock.get_time() / 1000  # Convert to seconds
                if monster['is_fast']:
                    if monster['movement_timer'] >= monster['fast_duration']:
                        monster['is_fast'] = False
                        monster['speed'] = 0  # Stay still
                        monster['movement_timer'] = 0
                else:
                    if monster['movement_timer'] >= monster['slow_duration']:
                        monster['is_fast'] = True
                        monster['speed'] = 5  # Fast speed
                        monster['movement_timer'] = 0
                # Move only if speed > 0
                if monster['speed'] > 0:
                    monster['pos'][0] += monster['direction'][0] * monster['speed']
                    monster['pos'][1] += monster['direction'][1] * monster['speed']

            # Check if the monster is off-screen
            if (monster['pos'][0] < -monster['size'][0] or monster['pos'][0] > WIDTH or
                monster['pos'][1] < -monster['size'][1] or monster['pos'][1] > HEIGHT):
                monsters.remove(monster)
                continue

            # Check collision with the target player
            if monster['target'] == 'player1' and check_monster_collision(snake1_pos, monster):
                score1 -= monster['damage']
                monsters.remove(monster)
                # Play collision sound
                SOUND_EFFECTS[monster['type']].play()
            elif monster['target'] == 'player2' and check_monster_collision(snake2_pos, monster):
                score2 -= monster['damage']
                monsters.remove(monster)
                # Play collision sound
                SOUND_EFFECTS[monster['type']].play()

        # Clear screen and draw background
        screen.blit(background_image, (0, 0))

        # Draw both snakes, food, monsters, and scores
        draw_snake(snake1_body, TEAL_SHADES, snake1_blinking, direction1)
        draw_snake(snake2_body, MAROON_SHADES, snake2_blinking, direction2)
        draw_food(food_items)
        draw_monsters(monsters)
        display_scores(score1, score2, player1_name, player2_name)
        display_timer(remaining_time)

        # Check if either snake hits itself
        for block in snake1_body[1:]:
            if abs(snake1_pos[0] - block[0]) < player1_speed and abs(snake1_pos[1] - block[1]) < player1_speed:
                score1 //= 2  # Halve Player 1's score
                # Reset snake1 position and body
                snake1_pos = [100.0, 50.0]
                snake1_body = [[100.0, 50.0], [80.0, 50.0], [60.0, 50.0]]
                direction1 = 'RIGHT'
                change_to1 = direction1
                break

        for block in snake2_body[1:]:
            if abs(snake2_pos[0] - block[0]) < player2_speed and abs(snake2_pos[1] - block[1]) < player2_speed:
                score2 //= 2  # Halve Player 2's score
                # Reset snake2 position and body
                snake2_pos = [400.0, 50.0]
                snake2_body = [[400.0, 50.0], [420.0, 50.0], [440.0, 50.0]]
                direction2 = 'LEFT'
                change_to2 = direction2
                break

        # Update the display
        pygame.display.flip()

        # Control the game speed
        clock.tick(150)

    # Determine winner based on score
    if score1 > score2:
        winner = player1_name
    elif score2 > score1:
        winner = player2_name
    else:
        winner = 'It\'s a tie!'

    # Game Over screen with winner and breakdowns
    game_over_screen(winner, score1, score2, counts1, counts2, player1_name, player2_name)

if __name__ == "__main__":
    player_setup_screen()
