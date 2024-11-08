import pygame
import subprocess
import json
import os
import sys
import time
import threading

# Initialize Pygame
pygame.init()

# Double the resolution
INITIAL_WIDTH, INITIAL_HEIGHT = 2880, 1620
SCREEN = pygame.display.set_mode((INITIAL_WIDTH, INITIAL_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Team Purple")

# Clock for controlling frame rate
CLOCK = pygame.time.Clock()
FPS = 60  # Increased FPS for smoother interactions

# Fonts
def get_scaled_fonts(window_width, window_height):
    base_width = 2880
    base_height = 1620
    scale_x = window_width / base_width
    scale_y = window_height / base_height
    scale = min(scale_x, scale_y)
    
    return {
        'font': pygame.font.SysFont("arial", max(24, int(24 * scale))),
        'big_font': pygame.font.SysFont("arial", max(36, int(36 * scale))),
        'title_font': pygame.font.SysFont("arial", max(48, int(48 * scale)), bold=True),
        'message_font': pygame.font.SysFont("arial", max(28, int(28 * scale))),
        'input_font': pygame.font.SysFont("arial", max(24, int(24 * scale)))
    }

# Initial font setup
fonts = get_scaled_fonts(INITIAL_WIDTH, INITIAL_HEIGHT)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GREY = (200, 200, 200)
DARK_GREY = (50, 50, 50)
BLUE = (0, 120, 215)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
DARK_PURPLE = (75, 0, 130)
TRANSPARENT_BLACK = (0, 0, 0, 180)

# Load images with scaling based on window size
def load_image(path, scale=1.0):
    try:
        image = pygame.image.load(path).convert_alpha()
        width, height = image.get_size()
        image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        return image
    except pygame.error as e:
        print(f"Unable to load image at {path}: {e}")
        return None

# Paths
ASSETS_DIR = "assets"
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
AUDIO_DIR = os.path.join(ASSETS_DIR, "audio")

# Scaling factor for avatars based on initial window size
AVATAR_SIZE = (200, 200)  # Increased size for better visibility at higher resolution

# Character avatars
CHARACTER_IMAGES = {
    'project_manager': load_image(os.path.join(IMAGES_DIR, 'project_manager.png'), scale=2.0),
    'musicologist': load_image(os.path.join(IMAGES_DIR, 'musicologist.png'), scale=2.0),
    'neuroscientist': load_image(os.path.join(IMAGES_DIR, 'neuroscientist.png'), scale=2.0),
    'data_scientist': load_image(os.path.join(IMAGES_DIR, 'data_scientist.png'), scale=2.0),
    'technical_researcher': load_image(os.path.join(IMAGES_DIR, 'technical_researcher.png'), scale=2.0),
    'ux_ui_designer': load_image(os.path.join(IMAGES_DIR, 'ux_ui_designer.png'), scale=2.0),
    'ethicist': load_image(os.path.join(IMAGES_DIR, 'ethicist.png'), scale=2.0),
    'qa_engineer': load_image(os.path.join(IMAGES_DIR, 'qa_engineer.png'), scale=2.0),
    'philosophical_writer': load_image(os.path.join(IMAGES_DIR, 'philosophical_writer.png'), scale=2.0),
    'OmniCall': load_image(os.path.join(IMAGES_DIR, 'omnicall.png'), scale=2.0),
    'User': load_image(os.path.join(IMAGES_DIR, 'user.png'), scale=2.0)
}

# Sound Effects
try:
    SOUND_SEND = pygame.mixer.Sound(os.path.join(AUDIO_DIR, 'send.wav'))
    SOUND_RECEIVE = pygame.mixer.Sound(os.path.join(AUDIO_DIR, 'receive.wav'))
    SOUND_SAVE = pygame.mixer.Sound(os.path.join(AUDIO_DIR, 'save.mp3'))
except pygame.error as e:
    print(f"Error loading sound files: {e}")
    SOUND_SEND = None
    SOUND_RECEIVE = None
    SOUND_SAVE = None

BACKGROUND_MUSIC = os.path.join(AUDIO_DIR, '2022_0810_Looping Korale Test_1.mp3')

# Play background music
if os.path.exists(BACKGROUND_MUSIC):
    try:
        pygame.mixer.music.load(BACKGROUND_MUSIC)
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)  # Loop indefinitely
    except pygame.error as e:
        print(f"Error loading background music: {e}")
else:
    print(f"Background music file not found at {BACKGROUND_MUSIC}")

# Conversation history
conversation_history = []

# Thread-safe lock for conversation_history
history_lock = threading.Lock()

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
            return "Error: Unable to generate response."
        else:
            return stdout.strip()
    except Exception as e:
        print(f"Exception when running model '{model_name}': {e}")
        return "Error: Exception occurred during response generation."

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
            'model_name': 'llama3.2:1b',  # Adjust to actual model name
            'context_window': 128000,
            'options': {}
        },
        'musicologist': {
            'nickname': 'The Scholar of Sound',
            'role': 'Musicologist',
            'model_name': 'llama3.2:1b',  # Adjust to actual model name
            'context_window': 128000,
            'options': {}
        },
        'neuroscientist': {
            'nickname': 'The Neural Navigator',
            'role': 'Neuroscientist',
            'model_name': 'llama3.2:1b',  # Adjust to actual model name
            'context_window': 2048,
            'options': {}
        },
        'data_scientist': {
            'nickname': 'The Data Dynamo',
            'role': 'Data Scientist',
            'model_name': 'llama3.2:1b',  # Adjust to actual model name
            'context_window': 2048,
            'options': {}
        },
        'technical_researcher': {
            'nickname': 'The Code Whisperer',
            'role': 'Technical Researcher',
            'model_name': 'llama3.2:1b',  # Adjust to actual model name
            'context_window': 2048,
            'options': {}
        },
        'ux_ui_designer': {
            'nickname': 'The Interface Architect',
            'role': 'UX/UI Designer',
            'model_name': 'llama3.2:1b',  # Adjust to actual model name
            'context_window': 2048,
            'options': {}
        },
        'ethicist': {
            'nickname': 'The Moral Compass',
            'role': 'Ethicist',
            'model_name': 'llama3.2:1b',  # Adjust to actual model name
            'context_window': 2048,
            'options': {}
        },
        'qa_engineer': {
            'nickname': 'The Code Tester',
            'role': 'Quality Assurance Engineer',
            'model_name': 'llama3.2:1b',  # Adjust to actual model name
            'context_window': 2048,
            'options': {}
        },
        'philosophical_writer': {
            'nickname': 'The Visionary',
            'role': 'Philosophical Writer',
            'model_name': 'llama3.2:1b',  # Adjust to actual model name
            'context_window': 2048,
            'options': {}
        }
    }

def get_user_input(screen, prompt_text, window_size):
    """
    Handles user text input using Pygame.

    Args:
        screen (pygame.Surface): The Pygame screen surface.
        prompt_text (str): The prompt to display to the user.
        window_size (tuple): Current window size.

    Returns:
        str: The user's input text.
    """
    global fonts
    input_text = ""
    input_active = True
    cursor_visible = True
    cursor_timer = 0
    cursor_interval = 500  # milliseconds

    # Define input box dimensions based on window size
    input_box_width = int(window_size[0] * 0.8)
    input_box_height = int(window_size[1] * 0.05)
    input_box_x = (window_size[0] - input_box_width) // 2
    input_box_y = int(window_size[1] * 0.3)

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
            if event.type == pygame.VIDEORESIZE:
                # Update window size and fonts
                window_size = event.size
                global SCREEN
                SCREEN = pygame.display.set_mode(window_size, pygame.RESIZABLE)
                fonts = get_scaled_fonts(window_size[0], window_size[1])
                # Recalculate input box dimensions
                input_box_width = int(window_size[0] * 0.8)
                input_box_height = int(window_size[1] * 0.05)
                input_box_x = (window_size[0] - input_box_width) // 2
                input_box_y = int(window_size[1] * 0.3)
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
        title_surface = fonts['title_font'].render("Team Purple", True, DARK_PURPLE)
        screen.blit(title_surface, ((window_size[0] - title_surface.get_width())//2, int(window_size[1] * 0.1)))
        
        # Prompt
        prompt_surface = fonts['font'].render(prompt_text, True, BLACK)
        screen.blit(prompt_surface, (input_box_x, input_box_y - input_box_height - 20))
        
        # Input box
        input_box = pygame.Rect(input_box_x, input_box_y, input_box_width, input_box_height)
        pygame.draw.rect(screen, WHITE, input_box)
        pygame.draw.rect(screen, BLACK, input_box, 2)
        
        # Render text
        draw_text(input_text, fonts['font'], BLACK, screen, input_box_x + 10, input_box_y + 5, input_box_width - 20)
        
        # Cursor
        if cursor_visible:
            cursor_x = input_box_x + 10 + fonts['font'].size(input_text)[0]
            cursor_y_start = input_box_y + 5
            cursor_y_end = input_box_y + input_box_height - 5
            pygame.draw.line(screen, BLACK, (cursor_x, cursor_y_start), (cursor_x, cursor_y_end), 2)
        
        pygame.display.flip()

    return input_text.strip()

def display_achievement(screen, achievement_text, fonts, window_size):
    """
    Displays an achievement popup.

    Args:
        screen (pygame.Surface): The Pygame screen surface.
        achievement_text (str): The achievement message.
        fonts (dict): Dictionary containing scaled fonts.
        window_size (tuple): Current window size.
    """
    # Semi-transparent overlay
    overlay = pygame.Surface(window_size, pygame.SRCALPHA)
    overlay.fill(TRANSPARENT_BLACK)  # Black with opacity
    screen.blit(overlay, (0, 0))

    # Achievement box
    box_width, box_height = int(window_size[0] * 0.25), int(window_size[1] * 0.15)
    box = pygame.Rect((window_size[0] - box_width)//2, (window_size[1] - box_height)//2, box_width, box_height)
    pygame.draw.rect(screen, LIGHT_GREY, box)
    pygame.draw.rect(screen, WHITE, box, 4)

    # Achievement text
    achievement_font = fonts['title_font']
    text_surface = achievement_font.render("Achievement Unlocked!", True, DARK_PURPLE)
    screen.blit(text_surface, ((window_size[0] - text_surface.get_width())//2, box.y + 20))

    # Description
    description_font = fonts['font']
    desc_surface = description_font.render(achievement_text, True, BLACK)
    screen.blit(desc_surface, ((window_size[0] - desc_surface.get_width())//2, box.y + 80))

    pygame.display.flip()
    pygame.time.wait(2000)  # Display for 2 seconds

def display_message(conversation_history, character_images, fonts, window_size, chat_surface, chat_scroll):
    """
    Updates the chat surface with the latest conversation history.

    Args:
        conversation_history (list): List of conversation entries.
        character_images (dict): Dictionary of character avatars.
        fonts (dict): Dictionary containing scaled fonts.
        window_size (tuple): Current window size.
        chat_surface (pygame.Surface): Surface to render chat messages.
        chat_scroll (int): Current scroll offset.

    Returns:
        int: The total height of rendered messages.
    """
    chat_surface.fill(DARK_GREY)  # Background for chat history

    padding = 20
    avatar_size = (100, 100)  # Adjusted avatar size
    y_offset = padding

    with history_lock:
        for entry in conversation_history:
            speaker = entry['speaker']
            message = entry['message']
            avatar = character_images.get(speaker, character_images['User'])
            if avatar:
                avatar = pygame.transform.scale(avatar, avatar_size)
                chat_surface.blit(avatar, (padding, y_offset))
            # Render message text
            text_x = padding * 2 + avatar_size[0]
            text_y = y_offset + 10
            draw_text(message, fonts['message_font'], WHITE, chat_surface, text_x, text_y, chat_surface.get_width() - text_x - padding)
            # Calculate the height of the rendered text to adjust y_offset
            lines = message.split('\n')
            text_height = fonts['message_font'].get_linesize() * len(lines) + 20
            y_offset += max(avatar_size[1], text_height)

    return y_offset

def scroll_chat(chat_scroll, y_offset, chat_box_height):
    """
    Adjusts the scroll offset based on the content height.

    Args:
        chat_scroll (int): Current scroll offset.
        y_offset (int): Total height of rendered messages.
        chat_box_height (int): Height of the chat box.

    Returns:
        int: Updated scroll offset.
    """
    return max(y_offset - chat_box_height, 0)

def model_response_thread(model_name, prompt, model_options, turn, models_info, conversation_goal):
    """
    Thread function to handle model response generation.

    Args:
        model_name (str): Name of the model.
        prompt (str): The prompt to send to the model.
        model_options (dict): Additional generation options.
        turn (int): Current turn number.
        models_info (dict): Information about all models.
        conversation_goal (str): The overarching goal of the conversation.
    """
    response = generate_from_model(model_name, prompt, model_options)
    with history_lock:
        conversation_history.append({'speaker': model_name, 'message': response})
    if SOUND_RECEIVE:
        SOUND_RECEIVE.play()

def main():
    global fonts, SCREEN  # Declare as global to modify within functions

    # Load models info and sequence
    models_info = load_models_info()
    sequence = load_sequence()

    # Get initial window size
    window_size = SCREEN.get_size()

    # Get user input for conversation goal and initial message
    conversation_goal = get_user_input(SCREEN, "Enter the overarching goal or topic for the conversation (optional):", window_size)
    initial_message = get_user_input(SCREEN, "Enter your initial message to start the conversation:", window_size)

    if not initial_message:
        print("No initial message provided. Exiting.")
        pygame.quit()
        sys.exit()

    # Initialize conversation history
    with history_lock:
        conversation_history.append({'speaker': 'User', 'message': initial_message})
    if SOUND_SEND:
        SOUND_SEND.play()

    total_turns = len(sequence)
    turn = 0
    running = True

    # Achievements tracking
    achievements = []
    achievement_steps = {10: "First OmniCall Activated!", 25: "Halfway There!", 48: "Conversation Completed!"}

    # Create chat history surface
    chat_box_width = int(window_size[0] * 0.8)
    chat_box_height = int(window_size[1] * 0.6)
    chat_surface = pygame.Surface((chat_box_width, chat_box_height))
    chat_surface.fill(DARK_GREY)
    chat_scroll = 0  # Scroll offset

    # Initial rendering of conversation
    y_offset = display_message(conversation_history, CHARACTER_IMAGES, fonts, window_size, chat_surface, chat_scroll)
    chat_scroll = scroll_chat(chat_scroll, y_offset, chat_box_height)

    while running and turn < total_turns:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            if event.type == pygame.VIDEORESIZE:
                # Update window size and fonts
                window_size = event.size
                SCREEN = pygame.display.set_mode(window_size, pygame.RESIZABLE)
                fonts = get_scaled_fonts(window_size[0], window_size[1])
                # Recreate chat surface with new size
                chat_box_width = int(window_size[0] * 0.8)
                chat_box_height = int(window_size[1] * 0.6)
                chat_surface = pygame.Surface((chat_box_width, chat_box_height))
                chat_surface.fill(DARK_GREY)
                # Re-render conversation
                y_offset = display_message(conversation_history, CHARACTER_IMAGES, fonts, window_size, chat_surface, chat_scroll)
                chat_scroll = scroll_chat(chat_scroll, y_offset, chat_box_height)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # Scroll up
                    chat_scroll = max(chat_scroll - 50, 0)
                elif event.button == 5:  # Scroll down
                    chat_scroll = scroll_chat(chat_scroll + 50, y_offset, chat_box_height)

        if not running:
            break

        current_speaker = sequence[turn]

        if current_speaker == 'OmniCall':
            # OmniCall: User input
            user_input = get_user_input(SCREEN, "OmniCall activated. Provide input to 'TheGodModel':", window_size)
            if user_input is None:
                running = False
                break
            if user_input:
                with history_lock:
                    conversation_history.append({'speaker': 'TheGodModel', 'message': user_input})
                if SOUND_SEND:
                    SOUND_SEND.play()
                # Achievement check
                if turn + 1 in achievement_steps:
                    achievements.append(achievement_steps[turn + 1])
                    display_achievement(SCREEN, achievement_steps[turn + 1], fonts, window_size)
            turn += 1
            # Update chat surface
            y_offset = display_message(conversation_history, CHARACTER_IMAGES, fonts, window_size, chat_surface, chat_scroll)
            chat_scroll = scroll_chat(chat_scroll, y_offset, chat_box_height)
            continue
        else:
            # Model's turn
            model_info = models_info.get(current_speaker, {})
            model_name = model_info.get('model_name')
            if not model_name:
                print(f"No model name specified for '{current_speaker}'. Skipping.")
                turn += 1
                continue

            # Generate prompt
            with history_lock:
                prompt = construct_prompt(current_speaker, conversation_history, models_info, conversation_goal)

            # Start a new thread for model response
            response_thread = threading.Thread(target=model_response_thread, args=(model_name, prompt, model_info.get('options', {}), turn, models_info, conversation_goal))
            response_thread.start()

            # Achievement check for OmniCall
            if turn + 1 in achievement_steps:
                achievements.append(achievement_steps[turn + 1])
                display_achievement(SCREEN, achievement_steps[turn + 1], fonts, window_size)

            turn += 1

        # Update chat surface with latest conversation
        with history_lock:
            y_offset = display_message(conversation_history, CHARACTER_IMAGES, fonts, window_size, chat_surface, chat_scroll)
        chat_scroll = scroll_chat(chat_scroll, y_offset, chat_box_height)

        # Draw background (solid color since background images are suspended)
        SCREEN.fill(LIGHT_GREY)

        # Draw title
        title_surface = fonts['title_font'].render("Team Purple", True, DARK_PURPLE)
        SCREEN.blit(title_surface, ((window_size[0] - title_surface.get_width())//2, 20))

        # Blit chat surface with scroll
        chat_position_x = int(window_size[0] * 0.1)
        chat_position_y = int(window_size[1] * 0.2)
        screen_rect = pygame.Rect(0, chat_scroll, chat_box_width, chat_box_height)
        SCREEN.blit(chat_surface, (chat_position_x, chat_position_y), area=screen_rect)

        pygame.display.flip()
        CLOCK.tick(FPS)

    # Wait for any remaining threads to finish
    for thread in threading.enumerate():
        if thread != threading.main_thread():
            thread.join()

    # Conversation ended
    # Update chat surface one last time
    with history_lock:
        y_offset = display_message(conversation_history, CHARACTER_IMAGES, fonts, window_size, chat_surface, chat_scroll)
    chat_scroll = scroll_chat(chat_scroll, y_offset, chat_box_height)

    # Draw final state (solid color)
    SCREEN.fill(LIGHT_GREY)

    # Draw title
    title_surface = fonts['title_font'].render("Team Purple", True, DARK_PURPLE)
    SCREEN.blit(title_surface, ((window_size[0] - title_surface.get_width())//2, 20))

    # Blit chat surface with scroll
    chat_position_x = int(window_size[0] * 0.1)
    chat_position_y = int(window_size[1] * 0.2)
    screen_rect = pygame.Rect(0, chat_scroll, chat_box_width, chat_box_height)
    SCREEN.blit(chat_surface, (chat_position_x, chat_position_y), area=screen_rect)

    pygame.display.flip()
    pygame.time.wait(1000)

    # Option to save the conversation
    save_option = get_user_input(SCREEN, "Would you like to save the conversation? (y/n):", window_size)
    if save_option.lower() == 'y':
        file_name = get_user_input(SCREEN, "Enter file name (default 'conversation.txt'):", window_size)
        if not file_name:
            file_name = 'conversation.txt'
        try:
            with open(file_name, 'w', encoding='utf-8') as f:
                with history_lock:
                    for entry in conversation_history:
                        f.write(f"{entry['speaker']}: {entry['message']}\n")
            if SOUND_SAVE:
                SOUND_SAVE.play()
            # Confirmation message
            achievement_text = f"Conversation saved to {file_name}"
            display_achievement(SCREEN, achievement_text, fonts, window_size)
        except Exception as e:
            error_text = f"Error saving conversation: {e}"
            display_achievement(SCREEN, error_text, fonts, window_size)

    # Exit message
    exit_message = "Thank you for using Team Purple! Goodbye."
    with history_lock:
        conversation_history.append({'speaker': 'System', 'message': exit_message})
    display_message(conversation_history, CHARACTER_IMAGES, fonts, window_size, chat_surface, chat_scroll)
    chat_scroll = scroll_chat(chat_scroll, y_offset, chat_box_height)

    # Draw final state
    SCREEN.fill(LIGHT_GREY)

    # Draw title
    title_surface = fonts['title_font'].render("Team Purple", True, DARK_PURPLE)
    SCREEN.blit(title_surface, ((window_size[0] - title_surface.get_width())//2, 20))

    # Blit chat surface with scroll
    chat_position_x = int(window_size[0] * 0.1)
    chat_position_y = int(window_size[1] * 0.2)
    screen_rect = pygame.Rect(0, chat_scroll, chat_box_width, chat_box_height)
    SCREEN.blit(chat_surface, (chat_position_x, chat_position_y), area=screen_rect)

    pygame.display.flip()
    pygame.time.wait(3000)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
