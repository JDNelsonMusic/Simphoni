import pygame
import subprocess
import os
import sys
import threading

# Initialize Pygame
pygame.init()
pygame.font.init()  # Explicitly initialize font module

# Set initial resolution
INITIAL_WIDTH, INITIAL_HEIGHT = 1440, 810
SCREEN = pygame.display.set_mode((INITIAL_WIDTH, INITIAL_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Team Purple - Backgrounds Disabled")

# Clock for controlling frame rate
CLOCK = pygame.time.Clock()
FPS = 60  # Increased FPS for smoother interactions

# Fonts
def get_scaled_fonts(window_width, window_height):
    base_width = 1440
    base_height = 810
    scale_x = window_width / base_width
    scale_y = window_height / base_height
    scale = min(scale_x, scale_y)

    return {
        'font': pygame.font.SysFont("arial", max(int(14 * scale), 14)),
        'big_font': pygame.font.SysFont("arial", max(int(18 * scale), 18)),
        'title_font': pygame.font.SysFont("arial", max(int(32 * scale), 28), bold=True),
        'message_font': pygame.font.SysFont("arial", max(int(20 * scale), 16)),
        'input_font': pygame.font.SysFont("arial", max(int(16 * scale), 14))
    }

# Initial font setup
fonts = get_scaled_fonts(INITIAL_WIDTH, INITIAL_HEIGHT)

# Debugging font sizes
print(f"Initial Message Font Size: {fonts['message_font'].get_height()}")
print(f"Initial Title Font Size: {fonts['title_font'].get_height()}")

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

# Background Rendering Disabled
# All background images loading and rendering code has been removed for testing purposes.

# Character avatars
def load_image(path, scale=1.0):
    try:
        image = pygame.image.load(path).convert_alpha()
        width, height = image.get_size()
        image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        print(f"Loaded image from {path} with scale {scale}")
        return image
    except pygame.error as e:
        print(f"Unable to load image at {path}: {e}")
        return None

ASSETS_DIR = "assets"
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
AUDIO_DIR = os.path.join(ASSETS_DIR, "audio")

AVATAR_SIZE = (80, 80)  # Adjusted avatar size

CHARACTER_IMAGES = {
    'project_manager': load_image(os.path.join(IMAGES_DIR, 'project_manager.png'), scale=0.3),
    'musicologist': load_image(os.path.join(IMAGES_DIR, 'musicologist.png'), scale=0.3),
    'neuroscientist': load_image(os.path.join(IMAGES_DIR, 'neuroscientist.png'), scale=0.3),
    'data_scientist': load_image(os.path.join(IMAGES_DIR, 'data_scientist.png'), scale=0.3),
    'technical_researcher': load_image(os.path.join(IMAGES_DIR, 'technical_researcher.png'), scale=0.3),
    'ux_ui_designer': load_image(os.path.join(IMAGES_DIR, 'ux_ui_designer.png'), scale=0.3),
    'ethicist': load_image(os.path.join(IMAGES_DIR, 'ethicist.png'), scale=0.3),
    'qa_engineer': load_image(os.path.join(IMAGES_DIR, 'qa_engineer.png'), scale=0.3),
    'philosophical_writer': load_image(os.path.join(IMAGES_DIR, 'philosophical_writer.png'), scale=0.3),
    'OmniCall': load_image(os.path.join(IMAGES_DIR, 'omnicall.png'), scale=0.3),
    'User': load_image(os.path.join(IMAGES_DIR, 'user.png'), scale=0.3)
}

# Sound Effects
try:
    SOUND_SEND = pygame.mixer.Sound(os.path.join(AUDIO_DIR, 'send.wav'))
    SOUND_RECEIVE = pygame.mixer.Sound(os.path.join(AUDIO_DIR, 'receive.wav'))
    SOUND_SAVE = pygame.mixer.Sound(os.path.join(AUDIO_DIR, 'save.mp3'))
    print("Loaded sound effects successfully.")
except pygame.error as e:
    print(f"Error loading sound: {e}")
    SOUND_SEND = SOUND_RECEIVE = SOUND_SAVE = None

BACKGROUND_MUSIC = os.path.join(AUDIO_DIR, '2022_0810_Looping_Korale_Test_1.mp3')

# Play background music if available
if os.path.exists(BACKGROUND_MUSIC):
    try:
        pygame.mixer.music.load(BACKGROUND_MUSIC)
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)  # Loop indefinitely
        print("Background music playing.")
    except pygame.error as e:
        print(f"Error playing background music: {e}")
else:
    print(f"Background music file not found at {BACKGROUND_MUSIC}")

# Conversation history
conversation_history = []

# Define states
STATE_IDLE = 'idle'
STATE_WAITING_FOR_INPUT = 'waiting_for_input'
STATE_PROCESSING_MODEL = 'processing_model'

# Initialize state
current_state = STATE_IDLE

# Input variables
input_active = False
input_text = ""
input_prompt = ""
cursor_visible = True
cursor_timer = 0
cursor_interval = 500  # milliseconds

# Scroll variables
chat_scroll = 0  # Current scroll offset
scroll_speed = 20  # Pixels per scroll event

# Threading lock
conversation_lock = threading.Lock()

# Flags
model_thread = None
model_response = None

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
            return "Error: Failed to generate response."
        else:
            response = stdout.strip()
            print(f"Model '{model_name}' response: {response}")  # Debugging
            return response
    except Exception as e:
        print(f"Exception when running model '{model_name}': {e}")
        return "Error: Exception during response generation."

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
    print(f"Constructed prompt for '{model_key}':\n{prompt}")  # Debugging
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

    Returns:
        int: The total height of the text rendered.
    """
    words = text.split(' ')
    lines = []
    current_line = ""
    for word in words:
        if current_line == "":
            test_line = word
        else:
            test_line = current_line + ' ' + word
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)

    for i, line in enumerate(lines):
        text_obj = font.render(line, True, color)
        surface.blit(text_obj, (x, y + i * font.get_linesize()))

    total_height = len(lines) * font.get_linesize()
    return total_height

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
            'model_name': 'llama2',  # Adjust to actual model name
            'context_window': 2048,
            'options': {}
        },
        'musicologist': {
            'nickname': 'The Scholar of Sound',
            'role': 'Musicologist',
            'model_name': 'llama2',  # Adjust to actual model name
            'context_window': 2048,
            'options': {}
        },
        'neuroscientist': {
            'nickname': 'The Neural Navigator',
            'role': 'Neuroscientist',
            'model_name': 'llama2',  # Adjust to actual model name
            'context_window': 2048,
            'options': {}
        },
        'data_scientist': {
            'nickname': 'The Data Dynamo',
            'role': 'Data Scientist',
            'model_name': 'llama2',  # Adjust to actual model name
            'context_window': 2048,
            'options': {}
        },
        'technical_researcher': {
            'nickname': 'The Code Whisperer',
            'role': 'Technical Researcher',
            'model_name': 'llama2',  # Adjust to actual model name
            'context_window': 2048,
            'options': {}
        },
        'ux_ui_designer': {
            'nickname': 'The Interface Architect',
            'role': 'UX/UI Designer',
            'model_name': 'llama2',  # Adjust to actual model name
            'context_window': 2048,
            'options': {}
        },
        'ethicist': {
            'nickname': 'The Moral Compass',
            'role': 'Ethicist',
            'model_name': 'llama2',  # Adjust to actual model name
            'context_window': 2048,
            'options': {}
        },
        'qa_engineer': {
            'nickname': 'The Code Tester',
            'role': 'Quality Assurance Engineer',
            'model_name': 'llama2',  # Adjust to actual model name
            'context_window': 2048,
            'options': {}
        },
        'philosophical_writer': {
            'nickname': 'The Visionary',
            'role': 'Philosophical Writer',
            'model_name': 'llama2',  # Adjust to actual model name
            'context_window': 2048,
            'options': {}
        }
    }

def start_model_processing(model_name, prompt, model_options, callback):
    """
    Starts the model processing in a separate thread.

    Args:
        model_name (str): Name of the model.
        prompt (str): The prompt to send to the model.
        model_options (dict): Additional generation options.
        callback (function): Function to call with the response.
    """
    def model_thread():
        response = generate_from_model(model_name, prompt, model_options)
        callback(response)

    thread = threading.Thread(target=model_thread)
    thread.start()
    return thread

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
    box_width, box_height = int(window_size[0] * 0.5), int(window_size[1] * 0.3)
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
    # Center the description
    desc_rect = desc_surface.get_rect(center=(window_size[0]//2, box.y + 80))
    screen.blit(desc_surface, desc_rect)

    pygame.display.flip()
    pygame.time.wait(2000)  # Display for 2 seconds

def display_message(conversation_history, character_images, fonts, chat_surface):
    """
    Updates the chat surface with the latest conversation history.

    Args:
        conversation_history (list): List of conversation entries.
        character_images (dict): Dictionary of character avatars.
        fonts (dict): Dictionary containing scaled fonts.
        chat_surface (pygame.Surface): Surface to render chat messages.

    Returns:
        int: The cumulative height of all messages rendered.
    """
    chat_surface.fill(DARK_GREY)  # Background for chat history

    padding = 20
    avatar_size = AVATAR_SIZE  # Using predefined avatar size
    y_offset = padding

    for entry in conversation_history:
        speaker = entry['speaker']
        message = entry['message']
        avatar = character_images.get(speaker, character_images.get('User'))
        if avatar:
            avatar_scaled = pygame.transform.scale(avatar, avatar_size)
            chat_surface.blit(avatar_scaled, (padding, y_offset))
        # Render message text
        text_x = padding * 2 + avatar_size[0]
        text_y = y_offset + 10
        text_max_width = chat_surface.get_width() - text_x - padding
        text_height = draw_text(message, fonts['message_font'], WHITE, chat_surface, text_x, text_y, text_max_width)
        # Adjust y_offset based on text and avatar height
        y_offset += max(avatar_size[1], text_height + 20)

    # Debugging: Print y_offset to ensure messages are within chat_surface
    print(f"Total chat height: {y_offset}, Chat surface height: {chat_surface.get_height()}")

    return y_offset

def main():
    global SCREEN, fonts  # Declare 'SCREEN' and 'fonts' as global

    # Load models info and sequence
    models_info = load_models_info()
    sequence = load_sequence()
    total_turns = len(sequence)
    print(f"Total turns loaded: {total_turns}")  # Debugging

    # Get initial window size
    window_size = SCREEN.get_size()

    # Conversation goal and initial message will be obtained via input prompts
    state_queue = [
        ('get_goal', "Enter the overarching goal or topic for the conversation (optional):"),
        ('get_initial', "Enter your initial message to start the conversation:")
    ]

    current_turn = 0

    # Achievements tracking
    achievements = []
    achievement_steps = {10: "First OmniCall Activated!", 25: "Halfway There!", 48: "Conversation Completed!"}

    # Create chat history surface
    chat_box_width = int(window_size[0] * 0.8)
    chat_box_height = int(window_size[1] * 0.6)
    chat_surface = pygame.Surface((chat_box_width, chat_box_height))
    chat_surface.fill(DARK_GREY)
    chat_scroll = 0  # Scroll offset

    # Initialize conversation history
    conversation_history = []

    # Function to handle model response callback
    def handle_model_response(response):
        nonlocal conversation_history, chat_surface, y_offset, chat_scroll, model_response, current_state, current_turn
        with conversation_lock:
            conversation_history.append({'speaker': current_speaker, 'message': response})
            if SOUND_RECEIVE:
                SOUND_RECEIVE.play()
            print(f"Added message from {current_speaker}: {response}")  # Debugging
            # Update chat surface
            y_offset = display_message(conversation_history, CHARACTER_IMAGES, fonts, chat_surface)
            chat_scroll = max(y_offset - chat_box_height, 0)
            print(f"Updated chat_scroll after {current_speaker} message: {chat_scroll}")  # Debugging

            # Achievement check
            if current_turn + 1 in achievement_steps:
                achievements.append(achievement_steps[current_turn + 1])
                display_achievement(SCREEN, achievement_steps[current_turn + 1], fonts, window_size)

            # Reset state to idle
            current_state = STATE_IDLE
            model_thread = None

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.VIDEORESIZE:
                window_size = event.size
                SCREEN = pygame.display.set_mode(window_size, pygame.RESIZABLE)
                fonts = get_scaled_fonts(window_size[0], window_size[1])
                # Recreate chat surface with new size
                chat_box_width = int(window_size[0] * 0.8)
                chat_box_height = int(window_size[1] * 0.6)
                chat_surface = pygame.Surface((chat_box_width, chat_box_height))
                chat_surface.fill(DARK_GREY)
                # Redraw conversation
                with conversation_lock:
                    y_offset = display_message(conversation_history, CHARACTER_IMAGES, fonts, chat_surface)
                    chat_scroll = max(y_offset - chat_box_height, 0)
                print(f"Window resized to: {window_size}")  # Debugging
                print(f"Updated chat_scroll after resize: {chat_scroll}")  # Debugging

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # Scroll up
                    chat_scroll = max(chat_scroll - scroll_speed, 0)
                elif event.button == 5:  # Scroll down
                    y_offset = display_message(conversation_history, CHARACTER_IMAGES, fonts, chat_surface)
                    chat_scroll = min(chat_scroll + scroll_speed, max(y_offset - chat_box_height, 0))

            elif event.type == pygame.KEYDOWN:
                if current_state == STATE_WAITING_FOR_INPUT:
                    if event.key == pygame.K_RETURN:
                        # Submit input
                        submitted_text = input_text.strip()
                        if input_prompt == "Enter the overarching goal or topic for the conversation (optional):":
                            conversation_goal = submitted_text
                            print(f"Conversation Goal: {conversation_goal}")  # Debugging
                            state_queue.pop(0)
                            current_state = STATE_IDLE
                        elif input_prompt == "Enter your initial message to start the conversation:":
                            if submitted_text:
                                initial_message = submitted_text
                                conversation_history.append({'speaker': 'User', 'message': initial_message})
                                if SOUND_SEND:
                                    SOUND_SEND.play()
                                print(f"Initial message from User: {initial_message}")  # Debugging
                                # Update chat surface
                                y_offset = display_message(conversation_history, CHARACTER_IMAGES, fonts, chat_surface)
                                chat_scroll = max(y_offset - chat_box_height, 0)
                                # Proceed to processing turns
                                state_queue.pop(0)
                                current_state = STATE_IDLE
                        elif input_prompt == "OmniCall activated. Provide input to 'TheGodModel':":
                            if submitted_text:
                                conversation_history.append({'speaker': 'TheGodModel', 'message': submitted_text})
                                if SOUND_RECEIVE:
                                    SOUND_RECEIVE.play()
                                print(f"Added message from TheGodModel: {submitted_text}")  # Debugging
                                # Update chat surface
                                y_offset = display_message(conversation_history, CHARACTER_IMAGES, fonts, chat_surface)
                                chat_scroll = max(y_offset - chat_box_height, 0)
                                # Achievement check
                                if current_turn + 1 in achievement_steps:
                                    achievements.append(achievement_steps[current_turn + 1])
                                    display_achievement(SCREEN, achievement_steps[current_turn + 1], fonts, window_size)
                            # Reset state
                            current_state = STATE_IDLE
                        elif input_prompt == "Would you like to save the conversation? (y/n):":
                            if submitted_text.lower() == 'y':
                                state_queue.insert(0, ('save_conversation', "Enter file name (default 'conversation.txt'):", 'save'))
                            else:
                                state_queue.pop(0)
                                current_state = STATE_IDLE
                        elif input_prompt == "Enter file name (default 'conversation.txt'):":
                            file_name = submitted_text.strip() if submitted_text else 'conversation.txt'
                            try:
                                with open(file_name, 'w', encoding='utf-8') as f:
                                    for entry in conversation_history:
                                        f.write(f"{entry['speaker']}: {entry['message']}\n")
                                if SOUND_SAVE:
                                    SOUND_SAVE.play()
                                # Confirmation message
                                achievement_text = f"Conversation saved to {file_name}"
                                display_achievement(SCREEN, achievement_text, fonts, window_size)
                                print(f"Conversation saved to {file_name}")  # Debugging
                            except Exception as e:
                                error_text = f"Error saving conversation: {e}"
                                display_achievement(SCREEN, error_text, fonts, window_size)
                                print(f"Error saving conversation: {e}")  # Debugging
                            state_queue.pop(0)
                            current_state = STATE_IDLE

                    elif current_state == STATE_WAITING_FOR_INPUT:
                        if event.key == pygame.K_BACKSPACE:
                            input_text = input_text[:-1]
                        else:
                            # Limit input length
                            if len(input_text) < 200:
                                input_text += event.unicode

            elif event.type == pygame.TEXTINPUT:
                if current_state == STATE_WAITING_FOR_INPUT:
                    if len(input_text) < 200:
                        input_text += event.text

        # Handle state transitions
        if current_state == STATE_IDLE and state_queue:
            next_state = state_queue[0]
            if next_state[0] == 'get_goal':
                input_prompt = next_state[1]
                input_text = ""
                current_state = STATE_WAITING_FOR_INPUT
                state_queue.pop(0)
            elif next_state[0] == 'get_initial':
                input_prompt = next_state[1]
                input_text = ""
                current_state = STATE_WAITING_FOR_INPUT
                state_queue.pop(0)
            elif next_state[0] == 'save_conversation':
                input_prompt = next_state[1]
                input_text = ""
                current_state = STATE_WAITING_FOR_INPUT
                state_queue.pop(0)

        # If all initial inputs are done, proceed to processing turns
        if not state_queue and current_turn < total_turns and current_state == STATE_IDLE and not model_thread:
            current_speaker = sequence[current_turn]
            print(f"Turn {current_turn+1}/{total_turns}: Current speaker - {current_speaker}")  # Debugging

            if current_speaker == 'OmniCall':
                # OmniCall: Prompt user input
                input_prompt = "OmniCall activated. Provide input to 'TheGodModel':"
                input_text = ""
                current_state = STATE_WAITING_FOR_INPUT
            else:
                # Model's turn
                model_info = models_info.get(current_speaker, {})
                model_name = model_info.get('model_name')
                if not model_name:
                    print(f"No model name specified for '{current_speaker}'. Skipping.")
                    current_turn += 1
                    continue

                # Since backgrounds are disabled, fill screen with solid color
                SCREEN.fill(DARK_GREY)  # Using dark grey as background color

                # Draw title
                title_surface = fonts['title_font'].render("Team Purple", True, DARK_PURPLE)
                SCREEN.blit(title_surface, ((window_size[0] - title_surface.get_width())//2, 20))

                pygame.display.flip()
                pygame.time.wait(500)  # Shorter wait before processing

                # Generate prompt and start model processing in a separate thread
                prompt = construct_prompt(current_speaker, conversation_history, models_info, conversation_goal)
                model_thread = start_model_processing(model_name, prompt, model_info.get('options', {}), handle_model_response)
                current_state = STATE_PROCESSING_MODEL

        # Draw background (solid color since backgrounds are disabled)
        SCREEN.fill(DARK_GREY)  # Using dark grey as background color

        # Draw title
        title_surface = fonts['title_font'].render("Team Purple", True, DARK_PURPLE)
        SCREEN.blit(title_surface, ((window_size[0] - title_surface.get_width())//2, 20))

        # Draw chat surface
        chat_position = (int(window_size[0] * 0.1), int(window_size[1] * 0.2))
        chat_rect = chat_surface.get_rect(topleft=chat_position)
        # Ensure chat_scroll is within bounds
        y_offset = display_message(conversation_history, CHARACTER_IMAGES, fonts, chat_surface)
        chat_scroll = max(min(chat_scroll, max(y_offset - chat_box_height, 0)), 0)
        # Blit chat_surface with scroll
        SCREEN.blit(chat_surface, chat_position, area=pygame.Rect(0, chat_scroll, chat_box_width, chat_box_height))

        # Draw input box if waiting for input
        if current_state == STATE_WAITING_FOR_INPUT:
            input_box_width = int(window_size[0] * 0.8)
            input_box_height = int(window_size[1] * 0.05)
            input_box_x = (window_size[0] - input_box_width) // 2
            input_box_y = int(window_size[1] * 0.85)

            # Input box rectangle
            input_rect = pygame.Rect(input_box_x, input_box_y, input_box_width, input_box_height)
            pygame.draw.rect(SCREEN, WHITE, input_rect)
            pygame.draw.rect(SCREEN, BLACK, input_rect, 2)

            # Render prompt above the input box
            prompt_surface = fonts['input_font'].render(input_prompt, True, BLACK)
            SCREEN.blit(prompt_surface, (input_box_x, input_box_y - 30))

            # Render input text
            rendered_text = fonts['input_font'].render(input_text, True, BLACK)
            SCREEN.blit(rendered_text, (input_box_x + 10, input_box_y + 10))

            # Render cursor
            cursor_x = input_box_x + 10 + rendered_text.get_width()
            cursor_y_start = input_box_y + 10
            cursor_y_end = input_box_y + input_box_height - 10
            cursor_timer += CLOCK.get_time()
            if cursor_timer >= cursor_interval:
                cursor_visible = not cursor_visible
                cursor_timer = 0
            if cursor_visible:
                pygame.draw.line(SCREEN, BLACK, (cursor_x, cursor_y_start), (cursor_x, cursor_y_end), 2)

        # Update display
        pygame.display.flip()
        CLOCK.tick(FPS)

# Start the application
if __name__ == "__main__":
    main()
