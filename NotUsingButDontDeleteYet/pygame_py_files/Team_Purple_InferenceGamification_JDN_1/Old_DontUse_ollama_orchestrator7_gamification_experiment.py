import pygame
import subprocess
import json
import os
import sys
import time

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1000, 700
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Conversation RPG")

# Clock for controlling frame rate
CLOCK = pygame.time.Clock()
FPS = 30

# Fonts
FONT = pygame.font.SysFont("arial", 22)
BIG_FONT = pygame.font.SysFont("arial", 28)
TITLE_FONT = pygame.font.SysFont("arial", 36, bold=True)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GREY = (200, 200, 200)
DARK_GREY = (50, 50, 50)
BLUE = (0, 120, 215)
GREEN = (0, 200, 0)
RED = (200, 0, 0)

# Load images
def load_image(path, size=None):
    try:
        image = pygame.image.load(path).convert_alpha()
        if size:
            image = pygame.transform.scale(image, size)
        return image
    except pygame.error as e:
        print(f"Unable to load image at {path}: {e}")
        return None

# Paths
ASSETS_DIR = "assets"
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
AUDIO_DIR = os.path.join(ASSETS_DIR, "audio")

# Character avatars
CHARACTER_IMAGES = {
    'project_manager': load_image(os.path.join(IMAGES_DIR, 'project_manager.png'), (100, 100)),
    'musicologist': load_image(os.path.join(IMAGES_DIR, 'musicologist.png'), (100, 100)),
    'neuroscientist': load_image(os.path.join(IMAGES_DIR, 'neuroscientist.png'), (100, 100)),
    'data_scientist': load_image(os.path.join(IMAGES_DIR, 'data_scientist.png'), (100, 100)),
    'technical_researcher': load_image(os.path.join(IMAGES_DIR, 'technical_researcher.png'), (100, 100)),
    'ux_ui_designer': load_image(os.path.join(IMAGES_DIR, 'ux_ui_designer.png'), (100, 100)),
    'ethicist': load_image(os.path.join(IMAGES_DIR, 'ethicist.png'), (100, 100)),
    'qa_engineer': load_image(os.path.join(IMAGES_DIR, 'qa_engineer.png'), (100, 100)),
    'philosophical_writer': load_image(os.path.join(IMAGES_DIR, 'philosophical_writer.png'), (100, 100)),
    'TheGodModel': load_image(os.path.join(IMAGES_DIR, 'god_model.png'), (100, 100)),
    'User': load_image(os.path.join(IMAGES_DIR, 'user.png'), (100, 100))
}

# Backgrounds
BACKGROUND_IMAGES = {
    'default': load_image(os.path.join(IMAGES_DIR, 'background_default.jpg'), (WIDTH, HEIGHT)),
    'project_manager': load_image(os.path.join(IMAGES_DIR, 'background_project_manager.jpg'), (WIDTH, HEIGHT)),
    'musicologist': load_image(os.path.join(IMAGES_DIR, 'background_musicologist.jpg'), (WIDTH, HEIGHT)),
    'neuroscientist': load_image(os.path.join(IMAGES_DIR, 'background_neuroscientist.jpg'), (WIDTH, HEIGHT)),
    'data_scientist': load_image(os.path.join(IMAGES_DIR, 'background_data_scientist.jpg'), (WIDTH, HEIGHT)),
    'technical_researcher': load_image(os.path.join(IMAGES_DIR, 'background_technical_researcher.jpg'), (WIDTH, HEIGHT)),
    'ux_ui_designer': load_image(os.path.join(IMAGES_DIR, 'background_ux_ui_designer.jpg'), (WIDTH, HEIGHT)),
    'ethicist': load_image(os.path.join(IMAGES_DIR, 'background_ethicist.jpg'), (WIDTH, HEIGHT)),
    'qa_engineer': load_image(os.path.join(IMAGES_DIR, 'background_qa_engineer.jpg'), (WIDTH, HEIGHT)),
    'philosophical_writer': load_image(os.path.join(IMAGES_DIR, 'background_philosophical_writer.jpg'), (WIDTH, HEIGHT)),
    'TheGodModel': load_image(os.path.join(IMAGES_DIR, 'background_god_model.jpg'), (WIDTH, HEIGHT)),
    'User': load_image(os.path.join(IMAGES_DIR, 'background_user.jpg'), (WIDTH, HEIGHT))
}

# Sound Effects
SOUND_SEND = pygame.mixer.Sound(os.path.join(AUDIO_DIR, 'send.wav'))
SOUND_RECEIVE = pygame.mixer.Sound(os.path.join(AUDIO_DIR, 'receive.wav'))
SOUND_SAVE = pygame.mixer.Sound(os.path.join(AUDIO_DIR, 'save.wav'))
BACKGROUND_MUSIC = os.path.join(AUDIO_DIR, 'background_music.mp3')

# Play background music
if os.path.exists(BACKGROUND_MUSIC):
    pygame.mixer.music.load(BACKGROUND_MUSIC)
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)  # Loop indefinitely
else:
    print(f"Background music file not found at {BACKGROUND_MUSIC}")

# Conversation history
conversation_history = []

def generate_from_model(model_name, prompt, model_options=None):
    """
    Generates a response from a given model using Ollama's CLI.

    Args:
        model_name (str): Name of the model.
        prompt (str): The prompt to send to the model.
        model_options (dict, optional): Additional generation options.

    Returns:
        str: The generated response from the model.
    """
    cmd = ['ollama', 'run']

    # Add model-specific options if provided
    if model_options:
        for key, value in model_options.items():
            cmd.extend([f'--{key}', str(value)])

    # Add the model name
    cmd.append(model_name)

    # Separator for the prompt
    cmd.append('--')

    # Add the prompt
    cmd.append(prompt)

    try:
        # Run the command and capture the output
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            print(f"Error running model '{model_name}': {stderr.strip()}")
            if 'unknown model' in stderr.lower():
                print(f"The model '{model_name}' was not found. Please check the model name.")
            return None
        else:
            return stdout.strip()
    except Exception as e:
        print(f"Exception when running model '{model_name}': {e}")
        return None

def construct_prompt(model_key, conversation_history, models_info, conversation_goal):
    """
    Constructs the prompt for the model based on conversation history.

    Args:
        model_key (str): The key of the current model in models_info.
        conversation_history (list): List of conversation turns.
        models_info (dict): Dictionary containing model roles and other info.
        conversation_goal (str): The overarching goal of the conversation.

    Returns:
        str: The constructed prompt.
    """
    model_info = models_info.get(model_key, {})
    role = model_info.get('role', '')
    nickname = model_info.get('nickname', '')
    context_window = model_info.get('context_window', 2048)  # Default context window

    prompt = ''
    if role:
        prompt += f"Role: {role}"
        if nickname:
            prompt += f" ({nickname})"
        prompt += "\n"
    if conversation_goal:
        prompt += f"Conversation Goal: {conversation_goal}\n"

    # Include relevant conversation history within context window
    # Estimate tokens (rough estimation: 1 token ≈ 4 characters)
    max_characters = context_window * 4
    history_text = ''
    for entry in reversed(conversation_history):
        entry_text = f"{entry['speaker']}: {entry['message']}\n"
        if len(history_text) + len(entry_text) < max_characters:
            history_text = entry_text + history_text
        else:
            break  # Exceeds context window

    prompt += history_text
    prompt += f"{model_key}:"
    return prompt

def draw_text(text, font, color, surface, x, y, max_width):
    """
    Draws text on the given surface with word wrapping.

    Args:
        text (str): The text to draw.
        font (pygame.font.Font): The font to use.
        color (tuple): Text color.
        surface (pygame.Surface): The surface to draw on.
        x (int): X-coordinate.
        y (int): Y-coordinate.
        max_width (int): Maximum width for the text.
    """
    words = text.split(' ')
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] < max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)

    for i, line in enumerate(lines):
        text_obj = font.render(line, True, color)
        surface.blit(text_obj, (x, y + i * font.get_linesize()))

def load_sequence():
    """
    Loads the predefined sequence of 48 steps.

    Returns:
        list: The sequence list.
    """
    return [
        'project_manager',
        'musicologist',
        'neuroscientist',
        'data_scientist',
        'technical_researcher',
        'ux_ui_designer',
        'ethicist',
        'qa_engineer',
        'philosophical_writer',
        'OmniCall',  # Step 10
        'project_manager',
        'data_scientist',
        'technical_researcher',
        'ux_ui_designer',
        'ethicist',
        'qa_engineer',
        'philosophical_writer',
        'OmniCall',  # Step 18
        'musicologist',
        'neuroscientist',
        'data_scientist',
        'technical_researcher',
        'ethicist',
        'qa_engineer',
        'philosophical_writer',
        'OmniCall',  # Step 26
        'project_manager',
        'musicologist',
        'neuroscientist',
        'ux_ui_designer',
        'ethicist',
        'qa_engineer',
        'philosophical_writer',
        'OmniCall',  # Step 34
        'data_scientist',
        'technical_researcher',
        'ux_ui_designer',
        'ethicist',
        'qa_engineer',
        'philosophical_writer',
        'OmniCall',  # Step 42
        'project_manager',
        'musicologist',
        'neuroscientist',
        'data_scientist',
        'technical_researcher',
        'philosophical_writer',
        'OmniCall'   # Step 48
    ]

def load_models_info():
    """
    Loads the models information as per the original application.

    Returns:
        dict: models_info dictionary.
    """
    return {
        'project_manager': {
            'nickname': 'The Taskmaster',
            'role': 'Project Manager',
            'model_name': 'mistral-nemo',  # Adjust to actual model name
            'context_window': 128000,
            'options': {}
        },
        'musicologist': {
            'nickname': 'The Scholar of Sound',
            'role': 'Musicologist',
            'model_name': 'nous-hermes2:34b',  # Adjust to actual model name
            'context_window': 2048,
            'options': {}
        },
        'neuroscientist': {
            'nickname': 'The Neural Navigator',
            'role': 'Neuroscientist',
            'model_name': 'wizard-vicuna-uncensored:30b',  # Adjust to actual model name
            'context_window': 2048,
            'options': {}
        },
        'data_scientist': {
            'nickname': 'The Data Dynamo',
            'role': 'Data Scientist',
            'model_name': 'orca-mini:70b',  # Adjust to actual model name
            'context_window': 2048,
            'options': {}
        },
        'technical_researcher': {
            'nickname': 'The Code Whisperer',
            'role': 'Technical Researcher',
            'model_name': 'codellama:70b',  # Adjust to actual model name
            'context_window': 2048,
            'options': {}
        },
        'ux_ui_designer': {
            'nickname': 'The Interface Architect',
            'role': 'UX/UI Designer',
            'model_name': 'wizard-vicuna-uncensored:30b',  # Adjust to actual model name
            'context_window': 2048,
            'options': {}
        },
        'ethicist': {
            'nickname': 'The Moral Compass',
            'role': 'Ethicist',
            'model_name': 'llama3.1:70B',  # Adjust to actual model name
            'context_window': 2048,
            'options': {}
        },
        'qa_engineer': {
            'nickname': 'The Code Tester',
            'role': 'Quality Assurance Engineer',
            'model_name': 'stable-code',  # Adjust to actual model name
            'context_window': 2048,
            'options': {}
        },
        'philosophical_writer': {
            'nickname': 'The Visionary',
            'role': 'Philosophical Writer',
            'model_name': 'llama3.1:70B',  # Adjust to actual model name
            'context_window': 2048,
            'options': {}
        }
    }

def get_user_input(screen, prompt_text):
    """
    Handles user text input using Pygame.

    Args:
        screen (pygame.Surface): The Pygame screen surface.
        prompt_text (str): The prompt to display to the user.

    Returns:
        str: The user's input text.
    """
    input_text = ""
    input_active = True
    cursor_visible = True
    cursor_timer = 0
    cursor_interval = 500  # milliseconds

    while input_active:
        dt = CLOCK.tick(FPS)
        cursor_timer += dt
        if cursor_timer >= cursor_interval:
            cursor_visible = not cursor_visible
            cursor_timer = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    # Limit input length
                    if len(input_text) < 200:
                        input_text += event.unicode

        # Render input screen
        screen.fill(LIGHT_GREY)
        # Title
        title_surface = TITLE_FONT.render("AI Conversation RPG", True, BLACK)
        screen.blit(title_surface, (WIDTH//2 - title_surface.get_width()//2, 50))
        # Prompt
        prompt_surface = FONT.render(prompt_text, True, BLACK)
        screen.blit(prompt_surface, (50, 150))
        # Input box
        input_box = pygame.Rect(50, 200, WIDTH - 100, 50)
        pygame.draw.rect(screen, WHITE, input_box)
        pygame.draw.rect(screen, BLACK, input_box, 2)
        # Render text
        draw_text(input_text, FONT, BLACK, screen, 60, 210, WIDTH - 120)
        # Cursor
        if cursor_visible:
            cursor_x = 60 + FONT.size(input_text)[0]
            pygame.draw.line(screen, BLACK, (cursor_x, 210), (cursor_x, 240), 2)
        pygame.display.flip()

    return input_text.strip()

def display_message(screen, conversation_history, character_images, current_background):
    """
    Displays the conversation history on the screen.

    Args:
        screen (pygame.Surface): The Pygame screen surface.
        conversation_history (list): List of conversation entries.
        character_images (dict): Dictionary of character avatars.
        current_background (pygame.Surface): The current background image.
    """
    # Draw background
    if current_background and current_background.get_width() == WIDTH and current_background.get_height() == HEIGHT:
        screen.blit(current_background, (0, 0))
    else:
        screen.fill(WHITE)

    # Draw conversation box
    conversation_box = pygame.Rect(50, HEIGHT - 300, WIDTH - 100, 250)
    pygame.draw.rect(screen, DARK_GREY, conversation_box)
    pygame.draw.rect(screen, BLACK, conversation_box, 2)

    # Display last few messages
    y_offset = HEIGHT - 290
    for entry in conversation_history[-5:]:
        speaker = entry['speaker']
        message = entry['message']
        # Avatar
        avatar = character_images.get(speaker, character_images['User'])
        if avatar:
            screen.blit(avatar, (60, y_offset))
        # Text
        text_x = 170
        text_y = y_offset + 10
        draw_text(f"{speaker}: {message}", FONT, WHITE, screen, text_x, text_y, WIDTH - 220)
        y_offset += 50

    # Draw progress bar
    progress = min(len(conversation_history), 48) / 48
    progress_bar_width = WIDTH - 100
    progress_bar_height = 20
    progress_bar = pygame.Rect(50, HEIGHT - 350, progress_bar_width, progress_bar_height)
    pygame.draw.rect(screen, WHITE, progress_bar)
    pygame.draw.rect(screen, BLACK, progress_bar, 2)
    inner_bar = pygame.Rect(50, HEIGHT - 350, (WIDTH - 100) * progress, progress_bar_height)
    pygame.draw.rect(screen, GREEN, inner_bar)

    # Progress text
    progress_text = FONT.render(f"Progress: {min(len(conversation_history), 48)}/48", True, WHITE)
    screen.blit(progress_text, (50, HEIGHT - 375))

def display_achievement(screen, achievement_text):
    """
    Displays an achievement popup.

    Args:
        screen (pygame.Surface): The Pygame screen surface.
        achievement_text (str): The achievement message.
    """
    # Semi-transparent overlay
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # Black with opacity
    screen.blit(overlay, (0, 0))

    # Achievement box
    box_width, box_height = 600, 200
    box = pygame.Rect((WIDTH - box_width)//2, (HEIGHT - box_height)//2, box_width, box_height)
    pygame.draw.rect(screen, LIGHT_GREY, box)
    pygame.draw.rect(screen, WHITE, box, 4)

    # Achievement text
    achievement_font = TITLE_FONT
    text_surface = achievement_font.render("Achievement Unlocked!", True, BLACK)
    screen.blit(text_surface, ((WIDTH - text_surface.get_width())//2, (HEIGHT - box_height)//2 + 30))

    # Description
    description_font = FONT
    desc_surface = description_font.render(achievement_text, True, BLACK)
    screen.blit(desc_surface, ((WIDTH - desc_surface.get_width())//2, (HEIGHT - box_height)//2 + 100))

    pygame.display.flip()
    pygame.time.wait(2000)  # Display for 2 seconds

def main():
    # Load models info and sequence
    models_info = load_models_info()
    sequence = load_sequence()

    # Get user input for conversation goal and initial message
    conversation_goal = get_user_input(SCREEN, "Enter the overarching goal or topic for the conversation (optional):")
    initial_message = get_user_input(SCREEN, "Enter your initial message to start the conversation:")

    if not initial_message:
        print("No initial message provided. Exiting.")
        pygame.quit()
        sys.exit()

    # Initialize conversation history
    conversation_history.append({'speaker': 'User', 'message': initial_message})
    SOUND_SEND.play()

    total_turns = len(sequence)
    turn = 0
    running = True

    # Current background
    current_background = BACKGROUND_IMAGES.get('default', None)

    # Achievements tracking
    achievements = []
    achievement_steps = {10: "First OmniCall Activated!", 25: "Halfway There!", 48: "Conversation Completed!"}

    while running and turn < total_turns:
        current_speaker = sequence[turn]

        if current_speaker == 'OmniCall':
            # OmniCall: User input
            user_input = get_user_input(SCREEN, "OmniCall activated. Provide input to 'TheGodModel':")
            if user_input is None:
                running = False
                break
            if user_input:
                conversation_history.append({'speaker': 'TheGodModel', 'message': user_input})
                SOUND_RECEIVE.play()
                # Achievement check
                if turn + 1 in achievement_steps:
                    achievements.append(achievement_steps[turn + 1])
                    display_message(SCREEN, conversation_history, CHARACTER_IMAGES, current_background)
                    display_achievement(SCREEN, achievement_steps[turn + 1])
            turn += 1
            continue
        else:
            # Model's turn
            model_info = models_info.get(current_speaker, {})
            model_name = model_info.get('model_name')
            if not model_name:
                print(f"No model name specified for '{current_speaker}'. Skipping.")
                turn += 1
                continue

            # Update background based on current speaker
            current_background = BACKGROUND_IMAGES.get(current_speaker, BACKGROUND_IMAGES.get('default'))

            # Display current speaker
            display_message(SCREEN, conversation_history, CHARACTER_IMAGES, current_background)
            pygame.display.flip()
            pygame.time.wait(1000)  # Wait for a second before generating response

            # Generate prompt and get response
            prompt = construct_prompt(current_speaker, conversation_history, models_info, conversation_goal)
            response = generate_from_model(model_name, prompt, model_info.get('options', {}))
            if response:
                conversation_history.append({'speaker': current_speaker, 'message': response})
                SOUND_RECEIVE.play()
                # Achievement check
                if turn + 1 in achievement_steps:
                    achievements.append(achievement_steps[turn + 1])
                    display_message(SCREEN, conversation_history, CHARACTER_IMAGES, current_background)
                    display_achievement(SCREEN, achievement_steps[turn + 1])
            else:
                conversation_history.append({'speaker': current_speaker, 'message': "Error: No response received."})
                SOUND_RECEIVE.play()
            turn += 1

        # Display conversation
        display_message(SCREEN, conversation_history, CHARACTER_IMAGES, current_background)
        pygame.display.flip()
        CLOCK.tick(FPS)

    # Conversation ended
    display_message(SCREEN, conversation_history, CHARACTER_IMAGES, current_background)
    pygame.display.flip()
    pygame.time.wait(1000)

    # Option to save the conversation
    save_option = get_user_input(SCREEN, "Would you like to save the conversation? (y/n):")
    if save_option.lower() == 'y':
        file_name = get_user_input(SCREEN, "Enter file name (default 'conversation.txt'):")
        if not file_name:
            file_name = 'conversation.txt'
        try:
            with open(file_name, 'w', encoding='utf-8') as f:
                for entry in conversation_history:
                    f.write(f"{entry['speaker']}: {entry['message']}\n")
            SOUND_SAVE.play()
            # Confirmation message
            achievement_text = f"Conversation saved to {file_name}"
            display_message(SCREEN, conversation_history, CHARACTER_IMAGES, current_background)
            display_achievement(SCREEN, achievement_text)
        except Exception as e:
            error_text = f"Error saving conversation: {e}"
            display_message(SCREEN, conversation_history, CHARACTER_IMAGES, current_background)
            display_achievement(SCREEN, error_text)

    # Exit message
    exit_message = "Thank you for using AI Conversation RPG! Goodbye."
    conversation_history.append({'speaker': 'System', 'message': exit_message})
    display_message(SCREEN, conversation_history, CHARACTER_IMAGES, current_background)
    pygame.display.flip()
    pygame.time.wait(3000)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
