import pygame
import subprocess
import json
import os
import sys
import time
import threading

# Initialize Pygame
pygame.init()

# Set initial resolution and make window resizable
INITIAL_WIDTH, INITIAL_HEIGHT = 2880, 1620
SCREEN = pygame.display.set_mode((INITIAL_WIDTH, INITIAL_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Team Purple")

# Clock for controlling frame rate
CLOCK = pygame.time.Clock()
FPS = 60  # Increased for smoother interactions

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
        'button_font': pygame.font.SysFont("arial", max(30, int(30 * scale)), bold=True)
    }

# Initial font setup
fonts = get_scaled_fonts(INITIAL_WIDTH, INITIAL_HEIGHT)

# Colors - Dark Mode Purple-Themed Palette
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_GREY = (30, 30, 30)
LIGHT_GREY = (50, 50, 50)
PURPLE = (75, 0, 130)
LIGHT_PURPLE = (138, 43, 226)
DARK_PURPLE = (48, 25, 52)
TEAL = (0, 128, 128)
PINK = (255, 105, 180)

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
    'project_manager': load_image(os.path.join(IMAGES_DIR, 'project_manager.png'), scale=1.5),
    'musicologist': load_image(os.path.join(IMAGES_DIR, 'musicologist.png'), scale=1.5),
    'neuroscientist': load_image(os.path.join(IMAGES_DIR, 'neuroscientist.png'), scale=1.5),
    'data_scientist': load_image(os.path.join(IMAGES_DIR, 'data_scientist.png'), scale=1.5),
    'technical_researcher': load_image(os.path.join(IMAGES_DIR, 'technical_researcher.png'), scale=1.5),
    'ux_ui_designer': load_image(os.path.join(IMAGES_DIR, 'ux_ui_designer.png'), scale=1.5),
    'ethicist': load_image(os.path.join(IMAGES_DIR, 'ethicist.png'), scale=1.5),
    'qa_engineer': load_image(os.path.join(IMAGES_DIR, 'qa_engineer.png'), scale=1.5),
    'philosophical_writer': load_image(os.path.join(IMAGES_DIR, 'philosophical_writer.png'), scale=1.5),
    'OmniCall': load_image(os.path.join(IMAGES_DIR, 'omnicall.png'), scale=1.5),
    'User': load_image(os.path.join(IMAGES_DIR, 'user.png'), scale=1.5)
}

# Sound Effects
def load_sound(path):
    if os.path.exists(path):
        try:
            return pygame.mixer.Sound(path)
        except pygame.error as e:
            print(f"Unable to load sound at {path}: {e}")
            return None
    else:
        print(f"Sound file not found at {path}")
        return None

SOUND_SEND = load_sound(os.path.join(AUDIO_DIR, 'send.wav'))
SOUND_RECEIVE = load_sound(os.path.join(AUDIO_DIR, 'receive.wav'))
SOUND_SAVE = load_sound(os.path.join(AUDIO_DIR, 'save.mp3'))
BACKGROUND_MUSIC = os.path.join(AUDIO_DIR, '2022_0810_Looping Korale Test_1.mp3')

# Play background music
if os.path.exists(BACKGROUND_MUSIC):
    try:
        pygame.mixer.music.load(BACKGROUND_MUSIC)
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)  # Loop indefinitely
    except pygame.error as e:
        print(f"Unable to load background music at {BACKGROUND_MUSIC}: {e}")
else:
    print(f"Background music file not found at {BACKGROUND_MUSIC}")

# Conversation history and lock for thread safety
conversation_history = []
conversation_lock = threading.Lock()

# Model Generation Function
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

# Prompt Construction Function
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

# Text Drawing Function
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

# Draggable Module Class
class DraggableModule:
    """
    Represents a draggable module (persona) in the setup screen.
    """
    def __init__(self, name, image, position, size):
        self.name = name
        self.image = image
        self.rect = pygame.Rect(position, size)
        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0

    def draw(self, surface):
        if self.image:
            surface.blit(self.image, self.rect.topleft)
        else:
            # Placeholder for missing images
            pygame.draw.rect(surface, PURPLE, self.rect)
            text_surf = fonts['font'].render(self.name.replace('_', ' ').title(), True, WHITE)
            surface.blit(text_surf, (self.rect.x + 10, self.rect.y + self.rect.height // 2 - text_surf.get_height() // 2))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                mouse_x, mouse_y = event.pos
                self.offset_x = self.rect.x - mouse_x
                self.offset_y = self.rect.y - mouse_y
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                mouse_x, mouse_y = event.pos
                self.rect.x = mouse_x + self.offset_x
                self.rect.y = mouse_y + self.offset_y

# Button Class
class Button:
    """
    Represents a clickable button.
    """
    def __init__(self, text, position, size, callback, color=LIGHT_PURPLE, hover_color=PURPLE, text_color=WHITE):
        self.text = text
        self.rect = pygame.Rect(position, size)
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.callback = callback
        self.hovered = False

    def draw(self, surface, font):
        current_color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(surface, current_color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        text_surf = font.render(self.text, True, self.text_color)
        surface.blit(text_surf, (self.rect.x + (self.rect.width - text_surf.get_width()) // 2,
                                 self.rect.y + (self.rect.height - text_surf.get_height()) // 2))

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.hovered and event.button == 1:
                self.callback()

# Setup Screen Class
class SetupScreen:
    """
    Represents the setup screen where users arrange personas and script the conversation.
    """
    def __init__(self, screen, window_size):
        self.screen = screen
        self.window_size = window_size
        self.modules = []
        self.create_modules()
        self.done = False
        self.next_button = Button(
            text="Start Conversation",
            position=(self.window_size[0]//2 - 150, self.window_size[1] - 100),
            size=(300, 60),
            callback=self.finish_setup,
            color=LIGHT_PURPLE,
            hover_color=PURPLE
        )
        self.buttons = [self.next_button]

    def create_modules(self):
        """
        Initializes the draggable modules.
        """
        module_names = [
            'project_manager',
            'musicologist',
            'neuroscientist',
            'data_scientist',
            'technical_researcher',
            'ux_ui_designer',
            'ethicist',
            'qa_engineer',
            'philosophical_writer'
        ]
        padding = 20
        module_width = 200
        module_height = 200
        start_x = padding
        start_y = padding + 100  # Leave space for title

        for i, name in enumerate(module_names):
            position = (start_x + i * (module_width + padding), start_y)
            size = (module_width, module_height)
            module = DraggableModule(name, CHARACTER_IMAGES.get(name), position, size)
            self.modules.append(module)

    def finish_setup(self):
        """
        Marks the setup as done and transitions to the main conversation.
        """
        self.done = True

    def handle_events(self, events):
        """
        Handles events specific to the setup screen.
        """
        for event in events:
            for module in self.modules:
                module.handle_event(event)
            for button in self.buttons:
                button.handle_event(event)

    def update(self):
        """
        Updates the setup screen.
        """
        pass  # Currently, no dynamic updates required

    def draw(self):
        """
        Draws the setup screen.
        """
        self.screen.fill(DARK_PURPLE)  # Dark purple-themed background

        # Draw title
        title_text = "Team Purple Setup"
        title_surf = fonts['title_font'].render(title_text, True, WHITE)
        self.screen.blit(title_surf, ((self.window_size[0] - title_surf.get_width())//2, 20))

        # Draw draggable modules
        for module in self.modules:
            module.draw(self.screen)

        # Draw buttons
        for button in self.buttons:
            button.draw(self.screen, fonts['button_font'])

        pygame.display.flip()

# Chat Window Class
class ChatWindow:
    """
    Represents the scrollable chat window.
    """
    def __init__(self, position, size):
        self.rect = pygame.Rect(position, size)
        self.surface = pygame.Surface(self.rect.size)
        self.surface.fill(DARK_GREY)
        self.scroll = 0
        self.max_scroll = 0

    def update_chat(self, conversation_history, character_images, fonts):
        """
        Updates the chat surface with the latest conversation history.
        """
        self.surface.fill(DARK_GREY)  # Clear previous messages
        padding = 20
        avatar_size = (100, 100)  # Adjusted avatar size
        y_offset = padding

        for entry in conversation_history:
            speaker = entry['speaker']
            message = entry['message']
            avatar = character_images.get(speaker, character_images['User'])
            if avatar:
                avatar_scaled = pygame.transform.scale(avatar, avatar_size)
                self.surface.blit(avatar_scaled, (padding, y_offset))
            # Render message text
            text_x = padding * 2 + avatar_size[0]
            text_y = y_offset + 10
            draw_text(message, fonts['message_font'], WHITE, self.surface, text_x, text_y, self.rect.width - text_x - padding)
            # Calculate the height of the rendered text to adjust y_offset
            lines = message.split('\n')
            text_height = fonts['message_font'].get_linesize() * len(lines) + 20
            y_offset += max(avatar_size[1], text_height)

        # Update max_scroll
        if y_offset > self.rect.height:
            self.max_scroll = y_offset - self.rect.height
        else:
            self.max_scroll = 0

        # Auto-scroll to the bottom
        self.scroll = self.max_scroll

    def draw(self, screen):
        """
        Draws the chat window onto the main screen.
        """
        screen.blit(self.surface, self.rect.topleft, area=pygame.Rect(0, self.scroll, self.rect.width, self.rect.height))

    def handle_scroll(self, delta):
        """
        Handles scrolling based on user input.
        """
        self.scroll -= delta
        if self.scroll < 0:
            self.scroll = 0
        elif self.scroll > self.max_scroll:
            self.scroll = self.max_scroll

# Achievement Display Function
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
    overlay.fill((0, 0, 0, 180))  # Black with opacity
    screen.blit(overlay, (0, 0))

    # Achievement box
    box_width, box_height = int(window_size[0] * 0.3), int(window_size[1] * 0.2)
    box = pygame.Rect((window_size[0] - box_width)//2, (window_size[1] - box_height)//2, box_width, box_height)
    pygame.draw.rect(screen, LIGHT_PURPLE, box)
    pygame.draw.rect(screen, WHITE, box, 4)

    # Achievement text
    achievement_font = fonts['title_font']
    text_surface = achievement_font.render("Achievement Unlocked!", True, DARK_PURPLE)
    screen.blit(text_surface, ((window_size[0] - text_surface.get_width())//2, box.y + 20))

    # Description
    description_font = fonts['font']
    desc_surface = description_font.render(achievement_text, True, BLACK)
    screen.blit(desc_surface, ((window_size[0] - desc_surface.get_width())//2, box.y + 100))

    pygame.display.flip()
    pygame.time.wait(2000)  # Display for 2 seconds

# Button Click Callback Function
def save_conversation(conversation_history, fonts, window_size):
    """
    Handles saving the conversation to a file.
    """
    default_file_name = "conversation.txt"
    file_name = get_user_input(SCREEN, "Enter file name (default 'conversation.txt'):", window_size)
    if not file_name:
        file_name = default_file_name
    try:
        with open(file_name, 'w', encoding='utf-8') as f:
            for entry in conversation_history:
                f.write(f"{entry['speaker']}: {entry['message']}\n")
        if SOUND_SAVE:
            SOUND_SAVE.play()
        achievement_text = f"Conversation saved to {file_name}"
        display_achievement(SCREEN, achievement_text, fonts, window_size)
    except Exception as e:
        error_text = f"Error saving conversation: {e}"
        display_achievement(SCREEN, error_text, fonts, window_size)

# User Input Function
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
    input_box_width = int(window_size[0] * 0.6)
    input_box_height = int(window_size[1] * 0.07)
    input_box_x = (window_size[0] - input_box_width) // 2
    input_box_y = int(window_size[1] * 0.4)

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
                input_box_width = int(window_size[0] * 0.6)
                input_box_height = int(window_size[1] * 0.07)
                input_box_x = (window_size[0] - input_box_width) // 2
                input_box_y = int(window_size[1] * 0.4)
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
        screen.fill(DARK_PURPLE)  # Dark purple background

        # Draw prompt
        prompt_surf = fonts['big_font'].render(prompt_text, True, WHITE)
        screen.blit(prompt_surf, ((window_size[0] - prompt_surf.get_width())//2, int(window_size[1] * 0.2)))

        # Draw input box
        input_box = pygame.Rect(input_box_x, input_box_y, input_box_width, input_box_height)
        pygame.draw.rect(screen, LIGHT_GREY, input_box)
        pygame.draw.rect(screen, WHITE, input_box, 2)

        # Render text
        draw_text(input_text, fonts['font'], BLACK, screen, input_box_x + 10, input_box_y + 10, input_box_width - 20)

        # Draw cursor
        if cursor_visible:
            cursor_x = input_box_x + 10 + fonts['font'].size(input_text)[0]
            cursor_y_start = input_box_y + 10
            cursor_y_end = input_box_y + input_box_height - 10
            pygame.draw.line(screen, BLACK, (cursor_x, cursor_y_start), (cursor_x, cursor_y_end), 2)

        pygame.display.flip()

    return input_text.strip()

# Button Click Callback Function
def start_conversation_callback(setup_screen, sequence, models_info, conversation_goal):
    """
    Callback function to start the conversation after setup.
    """
    setup_screen.done = True

# Conversation Manager Class
class ConversationManager:
    """
    Manages the conversation flow between personas and the context model.
    """
    def __init__(self, sequence, models_info, conversation_goal):
        self.sequence = sequence
        self.models_info = models_info
        self.conversation_goal = conversation_goal
        self.turn = 0
        self.total_turns = len(sequence)
        self.active = True
        self.thread = None

    def start_next_turn(self):
        """
        Initiates the next turn in the conversation.
        """
        if self.turn >= self.total_turns:
            self.active = False
            return

        current_speaker = self.sequence[self.turn]
        if current_speaker == 'context_model':
            # Handle context/summarization
            threading.Thread(target=self.handle_context_model).start()
        else:
            # Handle persona response
            threading.Thread(target=self.handle_persona_response, args=(current_speaker,)).start()

    def handle_persona_response(self, speaker):
        """
        Handles the response generation for a persona.
        """
        model_info = self.models_info.get(speaker, {})
        model_name = model_info.get('model_name')
        if not model_name:
            print(f"No model name specified for '{speaker}'. Skipping.")
            with conversation_lock:
                conversation_history.append({'speaker': 'System', 'message': f"No model found for {speaker}."})
            self.turn += 1
            self.start_next_turn()
            return

        # Generate prompt
        prompt = construct_prompt(speaker, conversation_history, self.models_info, self.conversation_goal)

        # Generate response
        response = generate_from_model(model_name, prompt, model_info.get('options', {}))

        with conversation_lock:
            conversation_history.append({'speaker': speaker, 'message': response})

        if SOUND_RECEIVE:
            SOUND_RECEIVE.play()

        # Check for achievements or milestones if needed

        self.turn += 1
        self.start_next_turn()

    def handle_context_model(self):
        """
        Handles the context/summarization model.
        """
        context_model_name = 'phi3:14b-medium-128k-instruct-fp16'  # As specified

        # Generate prompt for context model
        prompt = construct_prompt('context_model', conversation_history, self.models_info, self.conversation_goal)

        # Generate summary
        summary = generate_from_model(context_model_name, prompt)

        with conversation_lock:
            conversation_history.append({'speaker': 'ContextModel', 'message': summary})

        if SOUND_RECEIVE:
            SOUND_RECEIVE.play()

        self.turn += 1
        self.start_next_turn()

    def run(self):
        """
        Starts the conversation manager.
        """
        self.start_next_turn()

# Setup Screen Function
def setup_screen_handler(setup_screen, screen, window_size):
    """
    Handles the setup screen events and drawing.
    """
    events = pygame.event.get()
    setup_screen.handle_events(events)
    setup_screen.draw()
    return setup_screen.done

# Main Function
def main():
    global fonts, SCREEN  # Declare as global to modify within functions

    # Load models info and sequence
    models_info = load_models_info()
    sequence = load_sequence()

    # Insert context_model at every other position in the sequence
    enhanced_sequence = []
    for i, persona in enumerate(sequence):
        enhanced_sequence.append(persona)
        enhanced_sequence.append('context_model')  # Add context model after each persona
    sequence = enhanced_sequence
    total_turns = len(sequence)

    # Create Setup Screen
    setup_screen_obj = SetupScreen(SCREEN, SCREEN.get_size())

    # Main Loop Flag
    running = True

    # Conversation Manager and Chat Window Initialization
    conversation_manager = None
    chat_window = None

    while running:
        window_size = SCREEN.get_size()
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

        if not setup_screen_obj.done:
            # Handle setup screen
            setup_screen_obj.handle_events(events)
            setup_screen_obj.draw()
            continue  # Skip the rest until setup is done

        if conversation_manager is None:
            # Get conversation goal and initial message
            conversation_goal = get_user_input(SCREEN, "Enter the overarching goal or topic for the conversation (optional):", window_size)
            initial_message = get_user_input(SCREEN, "Enter your initial message to start the conversation:", window_size)

            if not initial_message:
                print("No initial message provided. Exiting.")
                pygame.quit()
                sys.exit()

            # Initialize conversation history
            with conversation_lock:
                conversation_history.append({'speaker': 'User', 'message': initial_message})
            if SOUND_SEND:
                SOUND_SEND.play()

            # Initialize Conversation Manager
            conversation_manager = ConversationManager(sequence, models_info, conversation_goal)
            conversation_manager.run()

            # Initialize Chat Window
            chat_window = ChatWindow(position=(int(window_size[0] * 0.1), int(window_size[1] * 0.3)),
                                     size=(int(window_size[0] * 0.8), int(window_size[1] * 0.6)))

            # Create Save Button
            save_button = Button(
                text="Save Conversation",
                position=(int(window_size[0] * 0.1), int(window_size[1] * 0.95)),
                size=(200, 50),
                callback=lambda: save_conversation(conversation_history, fonts, window_size),
                color=TEAL,
                hover_color=PINK
            )
            save_buttons = [save_button]
        else:
            # Update chat window with latest conversation
            with conversation_lock:
                chat_window.update_chat(conversation_history, CHARACTER_IMAGES, fonts)

            # Handle scrolling
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 4:  # Scroll up
                        chat_window.handle_scroll(30)
                    elif event.button == 5:  # Scroll down
                        chat_window.handle_scroll(-30)

            # Draw the main screen
            SCREEN.fill(DARK_GREY)  # Solid dark grey background

            # Draw title
            title_surface = fonts['title_font'].render("Team Purple", True, PURPLE)
            SCREEN.blit(title_surface, ((window_size[0] - title_surface.get_width())//2, 20))

            # Draw chat window
            chat_window.draw(SCREEN)

            # Draw Save Button
            for button in save_buttons:
                button.draw(SCREEN, fonts['button_font'])

            pygame.display.flip()

            # Check if conversation is over
            if not conversation_manager.active and not conversation_manager.thread.is_alive():
                running = False

        CLOCK.tick(FPS)

    # Conversation ended
    # Final Draw
    SCREEN.fill(DARK_GREY)

    # Draw title
    title_surface = fonts['title_font'].render("Team Purple", True, PURPLE)
    SCREEN.blit(title_surface, ((window_size[0] - title_surface.get_width())//2, 20))

    # Draw chat window
    chat_window.draw(SCREEN)

    # Draw Save Button
    for button in save_buttons:
        button.draw(SCREEN, fonts['button_font'])

    pygame.display.flip()
    pygame.time.wait(1000)

    # Option to save the conversation
    save_conversation(conversation_history, fonts, window_size)

    # Exit message
    with conversation_lock:
        conversation_history.append({'speaker': 'System', 'message': 'Thank you for using Team Purple! Goodbye.'})
    chat_window.update_chat(conversation_history, CHARACTER_IMAGES, fonts)

    # Final Draw with exit message
    SCREEN.fill(DARK_GREY)
    title_surface = fonts['title_font'].render("Team Purple", True, PURPLE)
    SCREEN.blit(title_surface, ((window_size[0] - title_surface.get_width())//2, 20))
    chat_window.draw(SCREEN)
    pygame.display.flip()
    pygame.time.wait(3000)

    pygame.quit()
    sys.exit()

# Conversation Manager Class (Revised)
class ConversationManager:
    """
    Manages the conversation flow between personas and the context model.
    """
    def __init__(self, sequence, models_info, conversation_goal):
        self.sequence = sequence
        self.models_info = models_info
        self.conversation_goal = conversation_goal
        self.turn = 0
        self.total_turns = len(sequence)
        self.active = True
        self.thread = None

    def start_next_turn(self):
        """
        Initiates the next turn in the conversation.
        """
        if self.turn >= self.total_turns:
            self.active = False
            return

        current_speaker = self.sequence[self.turn]
        if current_speaker == 'context_model':
            # Handle context/summarization
            self.thread = threading.Thread(target=self.handle_context_model)
            self.thread.start()
        else:
            # Handle persona response
            self.thread = threading.Thread(target=self.handle_persona_response, args=(current_speaker,))
            self.thread.start()

    def handle_persona_response(self, speaker):
        """
        Handles the response generation for a persona.
        """
        model_info = self.models_info.get(speaker, {})
        model_name = model_info.get('model_name')
        if not model_name:
            print(f"No model name specified for '{speaker}'. Skipping.")
            with conversation_lock:
                conversation_history.append({'speaker': 'System', 'message': f"No model found for {speaker}."})
            self.turn += 1
            self.start_next_turn()
            return

        # Generate prompt
        prompt = construct_prompt(speaker, conversation_history, self.models_info, self.conversation_goal)

        # Generate response
        response = generate_from_model(model_name, prompt, model_info.get('options', {}))

        with conversation_lock:
            conversation_history.append({'speaker': speaker, 'message': response})

        if SOUND_RECEIVE:
            SOUND_RECEIVE.play()

        self.turn += 1
        self.start_next_turn()

    def handle_context_model(self):
        """
        Handles the context/summarization model.
        """
        context_model_name = 'phi3:14b-medium-128k-instruct-fp16'  # As specified

        # Generate prompt for context model
        prompt = construct_prompt('context_model', conversation_history, self.models_info, self.conversation_goal)

        # Generate summary
        summary = generate_from_model(context_model_name, prompt)

        with conversation_lock:
            conversation_history.append({'speaker': 'ContextModel', 'message': summary})

        if SOUND_RECEIVE:
            SOUND_RECEIVE.play()

        self.turn += 1
        self.start_next_turn()

    def run(self):
        """
        Starts the conversation manager.
        """
        self.start_next_turn()

# Model Information Loader Function
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
        },
        'context_model': {
            'nickname': 'The Summarizer',
            'role': 'Context-Keeping Model',
            'model_name': 'phi3:14b-medium-128k-instruct-fp16',  # As specified
            'context_window': 128000,
            'options': {}
        }
    }

# Conversation Sequence Loader Function
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

# Conversation Manager Class (Revised)
class ConversationManager:
    """
    Manages the conversation flow between personas and the context model.
    """
    def __init__(self, sequence, models_info, conversation_goal):
        self.sequence = sequence
        self.models_info = models_info
        self.conversation_goal = conversation_goal
        self.turn = 0
        self.total_turns = len(sequence)
        self.active = True
        self.thread = None

    def start_next_turn(self):
        """
        Initiates the next turn in the conversation.
        """
        if self.turn >= self.total_turns:
            self.active = False
            return

        current_speaker = self.sequence[self.turn]
        if current_speaker == 'context_model':
            # Handle context/summarization
            self.thread = threading.Thread(target=self.handle_context_model)
            self.thread.start()
        else:
            # Handle persona response
            self.thread = threading.Thread(target=self.handle_persona_response, args=(current_speaker,))
            self.thread.start()

    def handle_persona_response(self, speaker):
        """
        Handles the response generation for a persona.
        """
        model_info = self.models_info.get(speaker, {})
        model_name = model_info.get('model_name')
        if not model_name:
            print(f"No model name specified for '{speaker}'. Skipping.")
            with conversation_lock:
                conversation_history.append({'speaker': 'System', 'message': f"No model found for {speaker}."})
            self.turn += 1
            self.start_next_turn()
            return

        # Generate prompt
        prompt = construct_prompt(speaker, conversation_history, self.models_info, self.conversation_goal)

        # Generate response
        response = generate_from_model(model_name, prompt, model_info.get('options', {}))

        with conversation_lock:
            conversation_history.append({'speaker': speaker, 'message': response})

        if SOUND_RECEIVE:
            SOUND_RECEIVE.play()

        self.turn += 1
        self.start_next_turn()

    def handle_context_model(self):
        """
        Handles the context/summarization model.
        """
        context_model_name = self.models_info['context_model']['model_name']  # As specified

        # Generate prompt for context model
        prompt = construct_prompt('context_model', conversation_history, self.models_info, self.conversation_goal)

        # Generate summary
        summary = generate_from_model(context_model_name, prompt, self.models_info['context_model'].get('options', {}))

        with conversation_lock:
            conversation_history.append({'speaker': 'ContextModel', 'message': summary})

        if SOUND_RECEIVE:
            SOUND_RECEIVE.play()

        self.turn += 1
        self.start_next_turn()

    def run(self):
        """
        Starts the conversation manager.
        """
        self.start_next_turn()

# Save Conversation Function
def save_conversation(conversation_history, fonts, window_size):
    """
    Handles saving the conversation to a file.
    """
    default_file_name = "conversation.txt"
    file_name = get_user_input(SCREEN, "Enter file name (default 'conversation.txt'):", window_size)
    if not file_name:
        file_name = default_file_name
    try:
        with open(file_name, 'w', encoding='utf-8') as f:
            for entry in conversation_history:
                f.write(f"{entry['speaker']}: {entry['message']}\n")
        if SOUND_SAVE:
            SOUND_SAVE.play()
        achievement_text = f"Conversation saved to {file_name}"
        display_achievement(SCREEN, achievement_text, fonts, window_size)
    except Exception as e:
        error_text = f"Error saving conversation: {e}"
        display_achievement(SCREEN, error_text, fonts, window_size)

# Run the Application
if __name__ == "__main__":
    main()
