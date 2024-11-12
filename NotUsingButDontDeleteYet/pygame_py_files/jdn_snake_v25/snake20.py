import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Double the resolution (Higher resolution)
WIDTH, HEIGHT = 1500, 1000  # Double the original width and height
CELL_SIZE = 5  # Keeping the small grid size, but doubling the snake's visual size

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
background_image = pygame.image.load('haunted_corn_maze.png').convert()
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

# Load images and scale them to appropriate sizes
pumpkin_small_img = pygame.image.load('pumpkin.small.png').convert_alpha()
pumpkin_small_img = pygame.transform.scale(pumpkin_small_img, (3 * CELL_SIZE, 6 * CELL_SIZE))

pumpkin_medium_img = pygame.image.load('pumpkin.medium.png').convert_alpha()
pumpkin_medium_img = pygame.transform.scale(pumpkin_medium_img, (10 * CELL_SIZE, 20 * CELL_SIZE))

pumpkin_large_img = pygame.image.load('pumpkin.big.png').convert_alpha()
pumpkin_large_img = pygame.transform.scale(pumpkin_large_img, (20 * CELL_SIZE, 40 * CELL_SIZE))

apple_light_img = pygame.image.load('apple.light.png').convert_alpha()
apple_light_img = pygame.transform.scale(apple_light_img, (6 * CELL_SIZE, 8 * CELL_SIZE))

apple_dark_img = pygame.image.load('apple.dark.png').convert_alpha()
apple_dark_img = pygame.transform.scale(apple_dark_img, (20 * CELL_SIZE, 30 * CELL_SIZE))

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
tealghost_img = pygame.image.load('tealghost.png').convert_alpha()
tealghost_img = pygame.transform.scale(tealghost_img, (7 * CELL_SIZE, 10 * CELL_SIZE))
maroonghost_img = pygame.image.load('maroonghost.png').convert_alpha()
maroonghost_img = pygame.transform.scale(maroonghost_img, (7 * CELL_SIZE, 10 * CELL_SIZE))

# Skeletons, same size as big pumpkins (20x40 pixels)
tealskeleton_img = pygame.image.load('tealskeleton.png').convert_alpha()
tealskeleton_img = pygame.transform.scale(tealskeleton_img, (8 * CELL_SIZE, 20 * CELL_SIZE))
maroonskeleton_img = pygame.image.load('maroonskeleton.png').convert_alpha()
maroonskeleton_img = pygame.transform.scale(maroonskeleton_img, (8 * CELL_SIZE, 20 * CELL_SIZE))

# Zombies, slightly bigger than big pumpkins
# Big pumpkins are 20x40 pixels; zombies will be 24x50 pixels
tealzombie_img = pygame.image.load('tealzombie.png').convert_alpha()
tealzombie_img = pygame.transform.scale(tealzombie_img, (11 * CELL_SIZE, 25 * CELL_SIZE))
maroonzombie_img = pygame.image.load('maroonzombie.png').convert_alpha()
maroonzombie_img = pygame.transform.scale(maroonzombie_img, (11 * CELL_SIZE, 25 * CELL_SIZE))

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
    """Draw food items based on their types and sizes."""
    for item in food_items:
        pos = item['pos']
        item_type = item['type']
        image = FOOD_IMAGES[item_type]
        screen.blit(image, pos)

def draw_monsters(monsters):
    """Draw the monsters on the screen."""
    for monster in monsters:
        pos = monster['pos']
        image = MONSTER_IMAGES[monster['owner']][monster['type']]
        screen.blit(image, pos)

def spawn_food(snake_body1, snake_body2, image):
    """Generate food at random locations that doesn't overlap with the snakes."""
    while True:
        food_pos = [
            random.randrange(0, (WIDTH - image.get_width()) // CELL_SIZE) * CELL_SIZE,
            random.randrange(0, (HEIGHT - image.get_height()) // CELL_SIZE) * CELL_SIZE
        ]
        rect = pygame.Rect(food_pos[0], food_pos[1], image.get_width(), image.get_height())
        collision = any(rect.collidepoint(segment) for segment in snake_body1 + snake_body2)
        if not collision:
            return food_pos

def spawn_monster(monster_type, owner, target, snake_body1, snake_body2):
    """Spawn a monster at a random location."""
    image = MONSTER_IMAGES[owner][monster_type]
    size = (image.get_width(), image.get_height())
    while True:
        pos = [
            random.randrange(0, (WIDTH - size[0]) // CELL_SIZE) * CELL_SIZE,
            random.randrange(0, (HEIGHT - size[1]) // CELL_SIZE) * CELL_SIZE
        ]
        rect = pygame.Rect(pos[0], pos[1], size[0], size[1])
        collision = any(rect.collidepoint(segment) for segment in snake_body1 + snake_body2)
        if not collision:
            return {'type': monster_type, 'pos': pos, 'spawn_time': pygame.time.get_ticks(), 'size': size, 'owner': owner, 'target': target}

def display_scores(score1, score2):
    """Display the scores of both players."""
    font = pygame.font.SysFont('arial', 15)  # Reduced font size
    score_surface1 = font.render(f'Hannah (Player 1) Score: {int(score1)}', True, (255, 255, 255))
    score_surface2 = font.render(f'Jon (Player 2) Score: {int(score2)}', True, (255, 255, 255))
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

def game_over_screen(winner_name, score1, score2, counts1, counts2):
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
    final_score_surface1 = final_score_font.render(f'Hannah Final Score: {int(score1)}', True, (255, 255, 255))
    final_score_surface2 = final_score_font.render(f'Jon Final Score: {int(score2)}', True, (255, 255, 255))
    winner_surface = final_score_font.render(f'Winner: {winner_name}', True, (255, 215, 0))

    screen.blit(final_score_surface1, (WIDTH / 4, HEIGHT / 3))
    screen.blit(final_score_surface2, (WIDTH / 4, HEIGHT / 3 + 30))
    screen.blit(winner_surface, (WIDTH / 4, HEIGHT / 3 + 60))

    # Display item breakdowns for each player
    breakdown_font = pygame.font.SysFont('arial', 20)  # Reduced font size
    y_offset = HEIGHT / 3 + 100
    for player, counts in [('Hannah', counts1), ('Jon', counts2)]:
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
                    main()  # Restart the game
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

def main():
    # Global score variables and item counts
    score1 = 0
    score2 = 0
    counts1 = {'small': 0, 'medium': 0, 'large': 0, 'light_apple': 0, 'dark_apple': 0}
    counts2 = {'small': 0, 'medium': 0, 'large': 0, 'light_apple': 0, 'dark_apple': 0}

    # Initial snake positions and bodies
    snake1_pos = [100, 50]
    snake1_body = [[100, 50], [80, 50], [60, 50]]

    snake2_pos = [400, 50]
    snake2_body = [[400, 50], [420, 50], [440, 50]]

    # Snake growth pending and blinking status
    snake1_growth_pending = 0
    snake2_growth_pending = 0
    snake1_blinking = False
    snake2_blinking = False
    snake1_blink_timer = 0
    snake2_blink_timer = 0
    BLINK_DURATION = 20  # Total frames to blink
    BLINK_FREQUENCY = 5  # Blink every 5 frames

    # Initial food items
    food_items = [
        {'type': 'small'},
        {'type': 'medium'},
        {'type': 'large'},
        {'type': 'light_apple'},
        {'type': 'dark_apple'}
    ]
    for item in food_items:
        image = FOOD_IMAGES[item['type']]
        item['pos'] = spawn_food(snake1_body, snake2_body, image)

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

    # Main loop
    while not game_over:
        elapsed_time = (pygame.time.get_ticks() - game_start_time) / 1000
        remaining_time = max(0, total_game_time - elapsed_time)
        if remaining_time <= 0:
            game_over = True
            break  # Exit the main loop to display game over screen

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # When a key is pressed for player 1 (arrow keys)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and direction1 != 'DOWN':
                    change_to1 = 'UP'
                elif event.key == pygame.K_DOWN and direction1 != 'UP':
                    change_to1 = 'DOWN'
                elif event.key == pygame.K_LEFT and direction1 != 'RIGHT':
                    change_to1 = 'LEFT'
                elif event.key == pygame.K_RIGHT and direction1 != 'LEFT':
                    change_to1 = 'RIGHT'

                # When a key is pressed for player 2 (WASD)
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
            snake1_pos[1] -= CELL_SIZE
        elif direction1 == 'DOWN':
            snake1_pos[1] += CELL_SIZE
        elif direction1 == 'LEFT':
            snake1_pos[0] -= CELL_SIZE
        elif direction1 == 'RIGHT':
            snake1_pos[0] += CELL_SIZE

        if direction2 == 'UP':
            snake2_pos[1] -= CELL_SIZE
        elif direction2 == 'DOWN':
            snake2_pos[1] += CELL_SIZE
        elif direction2 == 'LEFT':
            snake2_pos[0] -= CELL_SIZE
        elif direction2 == 'RIGHT':
            snake2_pos[0] += CELL_SIZE

        # Wrap-around logic for walls for both players
        snake1_pos[0] = snake1_pos[0] % WIDTH
        snake1_pos[1] = snake1_pos[1] % HEIGHT

        snake2_pos[0] = snake2_pos[0] % WIDTH
        snake2_pos[1] = snake2_pos[1] % HEIGHT

        # Snake body growing mechanism for both players
        snake1_body.insert(0, list(snake1_pos))
        snake2_body.insert(0, list(snake2_pos))

        # Check for food collisions for both snakes
        for item in food_items:
            if check_food_collision(snake1_pos, item):
                if item['type'] == 'light_apple':
                    score1 *= 0.5  # Reduce score by 50%
                    counts1['light_apple'] += 1
                    snake1_blinking = True
                    snake1_blink_timer = 0
                elif item['type'] == 'dark_apple':
                    score1 *= 0.8  # Reduce score by 20%
                    counts1['dark_apple'] += 1
                    snake1_blinking = True
                    snake1_blink_timer = 0
                else:
                    points = {'small': 36, 'medium': 18, 'large': 12}[item['type']]
                    score1 += points
                    counts1[item['type']] += 1
                    snake1_growth_pending += 2
                    # Spawn monster for player 2
                    if item['type'] == 'small':
                        monster_type = 'ghost'
                        damage = 6
                    elif item['type'] == 'medium':
                        monster_type = 'skeleton'
                        damage = 12
                    elif item['type'] == 'large':
                        monster_type = 'zombie'
                        damage = 18
                    monster = spawn_monster(monster_type, 'player1', 'player2', snake1_body, snake2_body)
                    monster['damage'] = damage
                    monsters.append(monster)
                image = FOOD_IMAGES[item['type']]
                item['pos'] = spawn_food(snake1_body, snake2_body, image)
                break
        else:
            if snake1_growth_pending > 0:
                snake1_growth_pending -= 1
            else:
                snake1_body.pop()

        for item in food_items:
            if check_food_collision(snake2_pos, item):
                if item['type'] == 'light_apple':
                    score2 *= 0.5  # Reduce score by 50%
                    counts2['light_apple'] += 1
                    snake2_blinking = True
                    snake2_blink_timer = 0
                elif item['type'] == 'dark_apple':
                    score2 *= 0.8  # Reduce score by 20%
                    counts2['dark_apple'] += 1
                    snake2_blinking = True
                    snake2_blink_timer = 0
                else:
                    points = {'small': 36, 'medium': 18, 'large': 12}[item['type']]
                    score2 += points
                    counts2[item['type']] += 1
                    snake2_growth_pending += 2
                    # Spawn monster for player 1
                    if item['type'] == 'small':
                        monster_type = 'ghost'
                        damage = 6
                    elif item['type'] == 'medium':
                        monster_type = 'skeleton'
                        damage = 12
                    elif item['type'] == 'large':
                        monster_type = 'zombie'
                        damage = 18
                    monster = spawn_monster(monster_type, 'player2', 'player1', snake1_body, snake2_body)
                    monster['damage'] = damage
                    monsters.append(monster)
                image = FOOD_IMAGES[item['type']]
                item['pos'] = spawn_food(snake1_body, snake2_body, image)
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

        # Check for monster collisions
        current_time = pygame.time.get_ticks()
        for monster in monsters[:]:
            # Check if the monster has expired
            if (current_time - monster['spawn_time']) / 1000 > 20:
                monsters.remove(monster)
                continue

            # Check collision with the target player
            if monster['target'] == 'player1' and check_monster_collision(snake1_pos, monster):
                score1 -= monster['damage']
                monsters.remove(monster)
            elif monster['target'] == 'player2' and check_monster_collision(snake2_pos, monster):
                score2 -= monster['damage']
                monsters.remove(monster)

        # Clear screen and draw background
        screen.blit(background_image, (0, 0))

        # Draw both snakes, food, monsters, and scores
        draw_snake(snake1_body, TEAL_SHADES, snake1_blinking, direction1)
        draw_snake(snake2_body, MAROON_SHADES, snake2_blinking, direction2)
        draw_food(food_items)
        draw_monsters(monsters)
        display_scores(score1, score2)
        display_timer(remaining_time)

        # Check if either snake hits itself
        for block in snake1_body[1:]:
            if snake1_pos == block:
                score1 //= 2  # Halve Player 1's score
                # Reset snake1 position and body
                snake1_pos = [100, 50]
                snake1_body = [[100, 50], [80, 50], [60, 50]]
                direction1 = 'RIGHT'
                change_to1 = direction1
                break

        for block in snake2_body[1:]:
            if snake2_pos == block:
                score2 //= 2  # Halve Player 2's score
                # Reset snake2 position and body
                snake2_pos = [400, 50]
                snake2_body = [[400, 50], [420, 50], [440, 50]]
                direction2 = 'LEFT'
                change_to2 = direction2
                break

        # Update the display
        pygame.display.flip()

        # Control the game speed
        clock.tick(150)

    # Determine winner based on score
    if score1 > score2:
        winner = 'Hannah'
    elif score2 > score1:
        winner = 'Jon'
    else:
        winner = 'It\'s a tie!'

    # Game Over screen with winner and breakdowns
    game_over_screen(winner, score1, score2, counts1, counts2)

if __name__ == "__main__":
    main()
