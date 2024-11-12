import pygame
import subprocess
import json
import os
import sys
import time
import threading
import random

# Initialize Pygame
pygame.init()

# Set initial resolution and make window resizable
INITIAL_WIDTH, INITIAL_HEIGHT = 10000, 5000
SCREEN = pygame.display.set_mode((INITIAL_WIDTH, INITIAL_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Team Purple")

# Clock for controlling frame rate
CLOCK = pygame.time.Clock()
FPS = 60  # Increased for smoother interactions

# Fonts
def get_scaled_fonts(window_width, window_height):
    base_width = 7200
    base_height = 3500
    
    scale_x = window_width / base_width
    scale_y = window_height / base_height
    scale = min(scale_x, scale_y)

    return {
        'font': pygame.font.SysFont("arial", max(12, int(12 * scale))),
        'big_font': pygame.font.SysFont("arial", max(18, int(18 * scale))),
        'title_font': pygame.font.SysFont("arial", max(24, int(24 * scale)), bold=True),
        'message_font': pygame.font.SysFont("arial", max(8, int(8 * scale))),
        'button_font': pygame.font.SysFont("arial", max(15, int(15 * scale)), bold=True),
        'header_font': pygame.font.SysFont("arial", max(20, int(20 * scale)), bold=True),
        'input_font': pygame.font.SysFont("arial", max(14, int(14 * scale)))
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
GOLD = (255, 215, 0)
RED = (255, 0, 0)

def load_sequence():
    """
    Loads the predefined sequence of steps for the conversation.
    
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
        'OmniCall'    # Step 48
    ]
    
def load_models_info():
    """
    Loads the models information as per the application requirements.
    
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
            'model_name': 'llama3.2:1b',  # As specified
            'context_window': 128000,
            'options': {}
        }
    }

def get_user_input(screen, prompt, window_size):
    """
    Displays an input prompt and captures user text input.
    
    Args:
        screen (pygame.Surface): The main screen surface.
        prompt (str): The prompt message to display.
        window_size (tuple): The size of the window (width, height).
    
    Returns:
        str: The user's input.
    """
    input_text = ""
    active = True
    font = fonts['input_font']
    prompt_surf = font.render(prompt, True, WHITE)
    input_box = pygame.Rect(window_size[0]//2 - 200, window_size[1]//2, 400, 50)
    
    while active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    active = False
                    return input_text
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    if len(input_text) < 50:
                        input_text += event.unicode
        
        # Draw the prompt and input box
        screen.fill(DARK_GREY)
        screen.blit(prompt_surf, (window_size[0]//2 - prompt_surf.get_width()//2, window_size[1]//2 - 100))
        
        # Render the current input text
        txt_surface = font.render(input_text, True, WHITE)
        pygame.draw.rect(screen, WHITE, input_box, 2)
        screen.blit(txt_surface, (input_box.x + 10, input_box.y + 10))
        
        pygame.display.flip()
        CLOCK.tick(FPS)
    
    return input_text

# Load images with scaling based on window size
def load_image(path, scale=2000.0):
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
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")

# Scaling factor for avatars based on initial window size
AVATAR_SIZE = (500, 500)  # Increased size for better visibility at higher resolution

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

# Load custom fonts
def load_custom_font(path, size):
    try:
        return pygame.font.Font(path, size)
    except pygame.error as e:
        print(f"Unable to load font at {path}: {e}")
        return pygame.font.SysFont("arial", size)

# Load all custom fonts
CUSTOM_FONTS = {
    'fancy_font': load_custom_font(os.path.join(FONTS_DIR, 'fancy.ttf'), 24)
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
SOUND_NOTIFICATION = load_sound(os.path.join(AUDIO_DIR, 'notification.wav'))
BACKGROUND_MUSIC = os.path.join(AUDIO_DIR, '2022_0810_Looping_Korale_Test_1.mp3')

# Play background music
if os.path.exists(BACKGROUND_MUSIC):
    try:
        pygame.mixer.music.load(BACKGROUND_MUSIC)
        pygame.mixer.music.set_volume(0.9)
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

# Settings Screen Class
class SettingsScreen:
    """
    Represents the settings screen where users can adjust application preferences.
    """
    def __init__(self, screen, window_size):
        self.screen = screen
        self.window_size = window_size
        self.active = False
        self.settings = {
            'volume': 0.5,
            'music_volume': 0.5,
            'show_avatars': True,
            'theme_color': 'DARK_PURPLE'
        }
        self.create_buttons()
        self.create_sliders()
        self.create_toggle_buttons()
        self.back_button = Button(
            text="Back to Setup",
            position=(50, 50),
            size=(200, 60),
            callback=self.deactivate,
            color=LIGHT_PURPLE,
            hover_color=PURPLE
        )

    def create_buttons(self):
        """
        Creates buttons for settings.
        """
        self.buttons = []

    def create_sliders(self):
        """
        Creates sliders for volume settings.
        """
        self.sliders = [
            Slider(
                position=(300, 200),
                size=(400, 50),
                min_val=0.0,
                max_val=1.0,
                initial_val=self.settings['volume'],
                label="Conversation Volume",
                callback=self.update_volume
            ),
            Slider(
                position=(300, 300),
                size=(400, 50),
                min_val=0.0,
                max_val=1.0,
                initial_val=self.settings['music_volume'],
                label="Music Volume",
                callback=self.update_music_volume
            )
        ]

    def create_toggle_buttons(self):
        """
        Creates toggle buttons for settings like showing avatars.
        """
        self.toggle_buttons = [
            ToggleButton(
                position=(300, 400),
                size=(50, 50),
                initial_state=self.settings['show_avatars'],
                label="Show Avatars",
                callback=self.toggle_show_avatars
            )
        ]

    def update_volume(self, value):
        """
        Updates the conversation volume.
        """
        self.settings['volume'] = value
        pygame.mixer.Sound.set_volume(SOUND_SEND, value)
        pygame.mixer.Sound.set_volume(SOUND_RECEIVE, value)
        pygame.mixer.Sound.set_volume(SOUND_SAVE, value)
        pygame.mixer.Sound.set_volume(SOUND_NOTIFICATION, value)

    def update_music_volume(self, value):
        """
        Updates the background music volume.
        """
        self.settings['music_volume'] = value
        pygame.mixer.music.set_volume(value)

    def toggle_show_avatars(self, state):
        """
        Toggles the display of avatars in the chat window.
        """
        self.settings['show_avatars'] = state

    def activate(self):
        """
        Activates the settings screen.
        """
        self.active = True

    def deactivate(self):
        """
        Deactivates the settings screen.
        """
        self.active = False

    def handle_events(self, events):
        """
        Handles events specific to the settings screen.
        """
        for event in events:
            for slider in self.sliders:
                slider.handle_event(event)
            for toggle in self.toggle_buttons:
                toggle.handle_event(event)
            self.back_button.handle_event(event)

    def draw(self):
        """
        Draws the settings screen.
        """
        self.screen.fill(DARK_GREY)

        # Draw title
        title_text = "Settings"
        title_surf = fonts['title_font'].render(title_text, True, WHITE)
        self.screen.blit(title_surf, ((self.window_size[0] - title_surf.get_width())//2, 20))

        # Draw sliders
        for slider in self.sliders:
            slider.draw(self.screen, fonts['font'])

        # Draw toggle buttons
        for toggle in self.toggle_buttons:
            toggle.draw(self.screen, fonts['font'])

        # Draw back button
        self.back_button.draw(self.screen, fonts['button_font'])

        pygame.display.flip()

# Slider Class
class Slider:
    """
    Represents a horizontal slider for adjusting settings.
    """
    def __init__(self, position, size, min_val, max_val, initial_val, label, callback):
        self.rect = pygame.Rect(position, size)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.handle_radius = 15
        self.handle_color = LIGHT_PURPLE
        self.line_color = WHITE
        self.dragging = False
        self.label = label
        self.callback = callback

    def draw(self, surface, font):
        # Draw the line
        pygame.draw.line(surface, self.line_color, (self.rect.x, self.rect.y + self.rect.height//2),
                         (self.rect.x + self.rect.width, self.rect.y + self.rect.height//2), 5)

        # Calculate handle position
        handle_x = self.rect.x + int((self.value - self.min_val) / (self.max_val - self.min_val) * self.rect.width)
        handle_y = self.rect.y + self.rect.height//2

        # Draw the handle
        pygame.draw.circle(surface, self.handle_color, (handle_x, handle_y), self.handle_radius)

        # Draw the label
        label_surf = font.render(f"{self.label}: {int(self.value * 100)}%", True, WHITE)
        surface.blit(label_surf, (self.rect.x, self.rect.y - 30))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            handle_x = self.rect.x + int((self.value - self.min_val) / (self.max_val - self.min_val) * self.rect.width)
            handle_y = self.rect.y + self.rect.height//2
            distance = ((mouse_pos[0] - handle_x)**2 + (mouse_pos[1] - handle_y)**2)**0.5
            if distance <= self.handle_radius:
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                mouse_x = event.pos[0]
                relative_x = mouse_x - self.rect.x
                relative_x = max(0, min(relative_x, self.rect.width))
                self.value = self.min_val + (relative_x / self.rect.width) * (self.max_val - self.min_val)
                self.callback(self.value)

# Toggle Button Class
class ToggleButton:
    """
    Represents a toggle button for binary settings.
    """
    def __init__(self, position, size, initial_state, label, callback):
        self.rect = pygame.Rect(position, size)
        self.state = initial_state
        self.on_color = TEAL
        self.off_color = LIGHT_GREY
        self.label = label
        self.callback = callback

    def draw(self, surface, font):
        color = self.on_color if self.state else self.off_color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)

        # Draw label
        label_surf = font.render(self.label, True, WHITE)
        surface.blit(label_surf, (self.rect.x + self.rect.width + 10, self.rect.y + self.rect.height//2 - label_surf.get_height()//2))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.state = not self.state
                self.callback(self.state)

# Settings Screen Integration in SetupScreen
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
            position=(self.window_size[0]//2 - 150, self.window_size[1] - 200),
            size=(300, 150),
            callback=self.finish_setup,
            color=LIGHT_PURPLE,
            hover_color=PURPLE
        )
        self.settings_button = Button(
            text="Settings",
            position=(self.window_size[0]//2 - 150, self.window_size[1] - 400),
            size=(300, 150),
            callback=self.open_settings,
            color=TEAL,
            hover_color=PURPLE
        )
        self.help_button = Button(
            text="Help & Tutorial",
            position=(self.window_size[0]//2 - 150, self.window_size[1] - 600),
            size=(300, 150),
            callback=self.open_help,
            color=GOLD,
            hover_color=PURPLE
        )
        self.buttons = [self.next_button, self.settings_button, self.help_button]
        self.settings_screen = SettingsScreen(screen, window_size)
        self.help_screen = HelpScreen(screen, window_size)

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
        padding = 600
    
        module_width = 1158
        module_height = 1140
        start_x = padding
        start_y = padding + 150  # Leave space for title

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

    def open_settings(self):
        """
        Opens the settings screen.
        """
        self.settings_screen.activate()

    def open_help(self):
        """
        Opens the help and tutorial screen.
        """
        self.help_screen.activate()

    def handle_events(self, events):
        """
        Handles events specific to the setup screen.
        """
        for event in events:
            for module in self.modules:
                module.handle_event(event)
            for button in self.buttons:
                button.handle_event(event)
        if self.settings_screen.active:
            self.settings_screen.handle_events(events)
        if self.help_screen.active:
            self.help_screen.handle_events(events)

    def update(self):
        """
        Updates the setup screen.
        """
        if self.settings_screen.active:
            self.settings_screen.update()
        if self.help_screen.active:
            self.help_screen.update()

    def draw(self):
        """
        Draws the setup screen.
        """
        self.screen.fill(DARK_PURPLE)  # Dark purple-themed background

        # Draw title
        title_text = "Team Purple Setup"
        title_surf = fonts['title_font'].render(title_text, True, WHITE)
        self.screen.blit(title_surf, ((self.window_size[0] - title_surf.get_width())//2, 20))

        if self.settings_screen.active:
            self.settings_screen.draw()
            return
        if self.help_screen.active:
            self.help_screen.draw()
            return

        # Draw draggable modules
        for module in self.modules:
            module.draw(self.screen)

        # Draw buttons
        for button in self.buttons:
            button.draw(self.screen, fonts['button_font'])

        pygame.display.flip()

# Help Screen Class
class HelpScreen:
    """
    Represents the help and tutorial screen.
    """
    def __init__(self, screen, window_size):
        self.screen = screen
        self.window_size = window_size
        self.active = False
        self.back_button = Button(
            text="Back",
            position=(50, 50),
            size=(150, 60),
            callback=self.deactivate,
            color=RED,
            hover_color=PURPLE
        )
        self.content = [
            "Welcome to Team Purple!",
            "This application allows you to engage in conversations with various personas.",
            "Setup Screen:",
            "- Drag and arrange the personas in the order you want them to participate.",
            "- Click 'Start Conversation' to begin.",
            "Settings:",
            "- Adjust volumes, toggle avatar visibility, and change themes.",
            "Chat Window:",
            "- Scroll through the conversation history.",
            "- Save your conversations for future reference.",
            "Achievements:",
            "- Unlock achievements by reaching milestones in your conversations.",
            "Enjoy your experience!"
        ]

    def activate(self):
        """
        Activates the help screen.
        """
        self.active = True

    def deactivate(self):
        """
        Deactivates the help screen.
        """
        self.active = False

    def handle_events(self, events):
        """
        Handles events specific to the help screen.
        """
        for event in events:
            self.back_button.handle_event(event)

    def draw(self):
        """
        Draws the help screen.
        """
        self.screen.fill(DARK_GREY)

        # Draw title
        title_text = "Help & Tutorial"
        title_surf = fonts['title_font'].render(title_text, True, WHITE)
        self.screen.blit(title_surf, ((self.window_size[0] - title_surf.get_width())//2, 20))

        # Draw content
        y_offset = 100
        for line in self.content:
            text_surf = fonts['message_font'].render(line, True, WHITE)
            self.screen.blit(text_surf, (100, y_offset))
            y_offset += 40

        # Draw back button
        self.back_button.draw(self.screen, fonts['button_font'])

        pygame.display.flip()

# Achievements Manager Class
class AchievementsManager:
        """
        Manages user achievements, tracking milestones and displaying achievement popups.
        """
        def __init__(self, screen, fonts, window_size):
            self.screen = screen
            self.fonts = fonts
            self.window_size = window_size
            self.achievements = {
                'first_message': {
                    'description': 'Sent your first message.',
                    'unlocked': False
                },
                'conversation_started': {
                    'description': 'Started a conversation with all personas.',
                    'unlocked': False
                },
                'save_conversation': {
                    'description': 'Saved a conversation.',
                    'unlocked': False
                },
                'achievement_master': {
                    'description': 'Unlocked all achievements!',
                    'unlocked': False
                }
            }
            self.displaying = False
            self.current_achievement = ""
            self.display_timer = 0
            self.display_duration = 3000  # milliseconds
    
        def check_achievements(self):
            """
            Checks and updates achievements based on conversation history.
            """
            with conversation_lock:
                # Achievement 1: First Message Sent
                if not self.achievements['first_message']['unlocked']:
                    for entry in conversation_history:
                        if entry['speaker'] == 'User':
                            self.achievements['first_message']['unlocked'] = True
                            self.current_achievement = self.achievements['first_message']['description']
                            self.displaying = True
                            SOUND_NOTIFICATION.play() if SOUND_NOTIFICATION else None
                            break
    
                # Achievement 2: Started Conversation with All Personas
                if not self.achievements['conversation_started']['unlocked']:
                    speakers = set(entry['speaker'] for entry in conversation_history if entry['speaker'] not in ['User', 'System', 'ContextModel'])
                    required_speakers = set(models_info.keys()) - {'context_model'}
                    if required_speakers.issubset(speakers):
                        self.achievements['conversation_started']['unlocked'] = True
                        self.current_achievement = self.achievements['conversation_started']['description']
                        self.displaying = True
                        SOUND_NOTIFICATION.play() if SOUND_NOTIFICATION else None
    
                # Achievement 3: Save Conversation
                if not self.achievements['save_conversation']['unlocked']:
                    # This will be triggered externally when saving is successful
                    pass
    
                # Achievement 4: All Achievements Unlocked
                if not self.achievements['achievement_master']['unlocked']:
                    if all(ach['unlocked'] for ach in self.achievements.values()):
                        self.achievements['achievement_master']['unlocked'] = True
                        self.current_achievement = self.achievements['achievement_master']['description']
                        self.displaying = True
                        SOUND_NOTIFICATION.play() if SOUND_NOTIFICATION else None
    
        def trigger_achievement(self, key):
            """
            Manually triggers an achievement.
    
            Args:
                key (str): The key of the achievement to unlock.
            """
            if key in self.achievements and not self.achievements[key]['unlocked']:
                self.achievements[key]['unlocked'] = True
                self.current_achievement = self.achievements[key]['description']
                self.displaying = True
                SOUND_NOTIFICATION.play() if SOUND_NOTIFICATION else None
    
        def display_popup(self):
            """
            Displays the achievement popup if an achievement is being displayed.
            """
            if self.displaying:
                self.display_timer += CLOCK.get_time()
                if self.display_timer <= self.display_duration:
                    # Semi-transparent overlay
                    overlay = pygame.Surface(self.window_size, pygame.SRCALPHA)
                    overlay.fill((0, 0, 0, 180))  # Black with opacity
                    self.screen.blit(overlay, (0, 0))
    
                    # Achievement box
                    box_width, box_height = int(self.window_size[0] * 0.4), int(self.window_size[1] * 0.25)
                    box = pygame.Rect((self.window_size[0] - box_width)//2, (self.window_size[1] - box_height)//2, box_width, box_height)
                    pygame.draw.rect(self.screen, GOLD, box)
                    pygame.draw.rect(self.screen, WHITE, box, 4)
    
                    # Achievement text
                    achievement_font = self.fonts['header_font']
                    text_surface = achievement_font.render("Achievement Unlocked!", True, BLACK)
                    self.screen.blit(text_surface, ((self.window_size[0] - text_surface.get_width())//2, box.y + 30))
    
                    # Description
                    description_font = self.fonts['font']
                    desc_surface = description_font.render(self.current_achievement, True, BLACK)
                    self.screen.blit(desc_surface, ((self.window_size[0] - desc_surface.get_width())//2, box.y + 100))
    
                    pygame.display.flip()
                else:
                    self.displaying = False
                    self.display_timer = 0
        
# Animated Background Class
class AnimatedBackground:
    """
    Represents an animated background using moving shapes.
    """
    def __init__(self, screen, window_size):
        self.screen = screen
        self.window_size = window_size
        self.shapes = []
        self.create_shapes()
    
    def create_shapes(self):
        for _ in range(50):
            shape_type = random.choice(['circle', 'square'])  # Replaced pygame.choice with random.choice
            radius = random.randint(10, 30)                # Replaced pygame.randint with random.randint
            x = random.randint(0, self.window_size[0])     # Replaced pygame.randint with random.randint
            y = random.randint(0, self.window_size[1])     # Replaced pygame.randint with random.randint
            dx = random.uniform(-1, 1)                     # Replaced pygame.uniform with random.uniform
            dy = random.uniform(-1, 1)                     # Replaced pygame.uniform with random.uniform
            color = LIGHT_PURPLE
            self.shapes.append({'type': shape_type, 'pos': [x, y], 'size': radius, 'vel': [dx, dy], 'color': color})
    
    def update(self):
        """
        Updates the positions of the shapes.
        """
        for shape in self.shapes:
            shape['pos'][0] += shape['vel'][0]
            shape['pos'][1] += shape['vel'][1]
    
            # Bounce off the edges
            if shape['pos'][0] < 0 or shape['pos'][0] > self.window_size[0]:
                shape['vel'][0] *= -1
            if shape['pos'][1] < 0 or shape['pos'][1] > self.window_size[1]:
                shape['vel'][1] *= -1
    
    def draw(self):
        """
        Draws the animated shapes onto the screen.
        """
        for shape in self.shapes:
            if shape['type'] == 'circle':
                pygame.draw.circle(self.screen, shape['color'], (int(shape['pos'][0]), int(shape['pos'][1])), shape['size'])
            elif shape['type'] == 'square':
                rect = pygame.Rect(int(shape['pos'][0]), int(shape['pos'][1]), shape['size']*2, shape['size']*2)
                pygame.draw.rect(self.screen, shape['color'], rect)
    
    # Typing Indicator Class
    class TypingIndicator:
        """
        Displays a typing indicator when a model is generating a response.
        """
        def __init__(self, screen, window_size, fonts):
            self.screen = screen
            self.window_size = window_size
            self.fonts = fonts
            self.active = False
            self.animation_frames = [".", "..", "..."]
            self.current_frame = 0
            self.timer = 0
            self.frame_duration = 500  # milliseconds
    
        def activate(self):
            """
            Activates the typing indicator.
            """
            self.active = True
            self.current_frame = 0
            self.timer = 0
    
        def deactivate(self):
            """
            Deactivates the typing indicator.
            """
            self.active = False
    
        def update(self, dt):
            """
            Updates the typing indicator animation.
    
            Args:
                dt (int): Time elapsed since last update in milliseconds.
            """
            if self.active:
                self.timer += dt
                if self.timer >= self.frame_duration:
                    self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
                    self.timer = 0
    
        def draw(self):
            """
            Draws the typing indicator onto the screen.
            """
            if self.active:
                text = "Typing" + self.animation_frames[self.current_frame]
                text_surf = self.fonts['message_font'].render(text, True, WHITE)
                self.screen.blit(text_surf, (int(self.window_size[0] * 0.1) + 10, int(self.window_size[1] * 0.95)))
    
    # Emoji Support
    EMOJI_MAP = {
        ":smile:": "😄",
        ":sad:": "😢",
        ":thumbs_up:": "👍",
        ":heart:": "❤️",
        ":fire:": "🔥",
        ":star:": "⭐",
        ":check:": "✅",
        ":cross:": "❌"
    }
    
    def replace_emojis(text):
        """
        Replaces emoji codes in text with actual emoji characters.
    
        Args:
            text (str): The text containing emoji codes.
    
        Returns:
            str: The text with emoji codes replaced by emoji characters.
        """
        for code, emoji in EMOJI_MAP.items():
            text = text.replace(code, emoji)
        return text
    
    # Enhanced Chat Window Class with Emoji Support and Typing Indicator
    class ChatWindow:
        """
        Represents the scrollable chat window with emoji support and typing indicators.
        """
        def __init__(self, position, size, typing_indicator):
            self.rect = pygame.Rect(position, size)
            self.surface = pygame.Surface(self.rect.size)
            self.surface.fill(DARK_GREY)
            self.scroll = 0
            self.max_scroll = 0
            self.typing_indicator = typing_indicator
    
        def update_chat(self, conversation_history, character_images, fonts, show_avatars=True):
            """
            Updates the chat surface with the latest conversation history.
            """
            self.surface.fill(DARK_GREY)  # Clear previous messages
            padding = 50
            avatar_size = (50, 50)  # Adjusted avatar size
            y_offset = padding
    
            for entry in conversation_history:
                speaker = entry['speaker']
                message = replace_emojis(entry['message'])
                avatar = character_images.get(speaker, character_images['User'])
                if avatar and show_avatars:
                    avatar_scaled = pygame.transform.scale(avatar, avatar_size)
                    self.surface.blit(avatar_scaled, (padding, y_offset))
                # Render message text
                text_x = padding * 2 + avatar_size[0] if (avatar and show_avatars) else padding
                text_y = y_offset + 10
                draw_text(message, fonts['message_font'], WHITE, self.surface, text_x, text_y, self.rect.width - text_x - padding)
                # Calculate the height of the rendered text to adjust y_offset
                lines = message.split('\n')
                text_height = fonts['message_font'].get_linesize() * len(lines) + 5
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
            self.typing_indicator.draw()
    
        def handle_scroll(self, delta):
            """
            Handles scrolling based on user input.
    
            Args:
                delta (int): The amount to scroll.
            """
            self.scroll -= delta
            if self.scroll < 0:
                self.scroll = 0
            elif self.scroll > self.max_scroll:
                self.scroll = self.max_scroll

    # Profile Customization Class
    class ProfileCustomization:
        """
        Allows users to customize the profiles of each persona.
        """
        def __init__(self, screen, window_size, fonts):
            self.screen = screen
            self.window_size = window_size
            self.fonts = fonts
            self.active = False
            self.current_persona = None
            self.input_boxes = {}
            self.save_button = Button(
                text="Save Profile",
                position=(self.window_size[0]//2 - 100, self.window_size[1] - 150),
                size=(200, 60),
                callback=self.save_profile,
                color=GOLD,
                hover_color=PURPLE
            )
            self.back_button = Button(
                text="Back",
                position=(50, 50),
                size=(150, 60),
                callback=self.deactivate,
                color=RED,
                hover_color=PURPLE
            )
            self.create_input_boxes()
    
        def create_input_boxes(self):
            """
            Initializes input boxes for profile customization.
            """
            # Define input fields: nickname and role description
            self.input_fields = ['Nickname', 'Role Description']
            for field in self.input_fields:
                self.input_boxes[field] = InputBox(
                    rect=pygame.Rect(self.window_size[0]//2 - 200, 200 + self.input_fields.index(field)*100, 400, 50),
                    text='',
                    font=self.fonts['input_font']
                )
    
        def activate(self, persona_name):
            """
            Activates the profile customization screen for a specific persona.
        
            Args:
                persona_name (str): The name of the persona to customize.
            """
            self.active = True
            self.current_persona = persona_name
            # Pre-fill input boxes with existing data if available
            persona_info = persona_profiles.get(persona_name, {})
            self.input_boxes['Nickname'].text = persona_info.get('nickname', '')
            self.input_boxes['Role Description'].text = persona_info.get('role_description', '')
    
        def deactivate(self):
            """
            Deactivates the profile customization screen.
            """
            self.active = False
            self.current_persona = None
    
        def save_profile(self):
            """
            Saves the customized profile data for the current persona.
            """
            if self.current_persona:
                nickname = self.input_boxes['Nickname'].text.strip()
                role_description = self.input_boxes['Role Description'].text.strip()
                persona_profiles[self.current_persona] = {
                    'nickname': nickname,
                    'role_description': role_description
                }
                achievement_manager.trigger_achievement('profile_customized')
                self.deactivate()
    
        def handle_events(self, events):
            """
            Handles events specific to the profile customization screen.
            """
            for event in events:
                self.back_button.handle_event(event)
                self.save_button.handle_event(event)
                for box in self.input_boxes.values():
                    box.handle_event(event)
    
        def draw(self):
            """
            Draws the profile customization screen.
            """
            self.screen.fill(DARK_GREY)
    
            # Draw title
            title_text = f"Customize Profile: {self.current_persona.replace('_', ' ').title()}"
            title_surf = self.fonts['title_font'].render(title_text, True, WHITE)
            self.screen.blit(title_surf, ((self.window_size[0] - title_surf.get_width())//2, 50))
    
            # Draw input boxes
            for field, box in self.input_boxes.items():
                # Draw label
                label_surf = self.fonts['font'].render(field + ":", True, WHITE)
                self.screen.blit(label_surf, (box.rect.x, box.rect.y - 30))
                # Draw input box
                box.draw(self.screen)
    
            # Draw buttons
            self.save_button.draw(self.screen, self.fonts['button_font'])
            self.back_button.draw(self.screen, self.fonts['button_font'])
    
            pygame.display.flip()
    
    # Input Box Class
    class InputBox:
        """
        Represents an input box for user text input.
        """
        def __init__(self, rect, text, font):
            self.rect = rect
            self.color_inactive = LIGHT_GREY
            self.color_active = GOLD
            self.color = self.color_inactive
            self.text = text
            self.font = font
            self.txt_surface = self.font.render(text, True, self.color)
            self.active = False
    
        def handle_event(self, event):
            if event.type == pygame.MOUSEBUTTONDOWN:
                # If the user clicked on the input_box rect.
                if self.rect.collidepoint(event.pos):
                    self.active = not self.active
                else:
                    self.active = False
                # Change the current color of the input box.
                self.color = self.color_active if self.active else self.color_inactive
            if event.type == pygame.KEYDOWN:
                if self.active:
                    if event.key == pygame.K_RETURN:
                        pass  # Do nothing on enter
                    elif event.key == pygame.K_BACKSPACE:
                        self.text = self.text[:-1]
                    else:
                        if len(self.text) < 50:
                            self.text += event.unicode
                    # Re-render the text.
                    self.txt_surface = self.font.render(self.text, True, BLACK)
    
        def draw(self, screen):
            # Blit the text.
            screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
            # Blit the rect.
            pygame.draw.rect(screen, self.color, self.rect, 2)
    
    # Achievements Screen Class
    class AchievementsScreen:
        """
        Displays the list of achievements and their statuses.
        """
        def __init__(self, screen, window_size, fonts):
            self.screen = screen
            self.window_size = window_size
            self.fonts = fonts
            self.active = False
            self.back_button = Button(
                text="Back",
                position=(50, 50),
                size=(150, 60),
                callback=self.deactivate,
                color=RED,
                hover_color=PURPLE
            )
    
        def activate(self):
            """
            Activates the achievements screen.
            """
            self.active = True
    
        def deactivate(self):
            """
            Deactivates the achievements screen.
            """
            self.active = False
    
        def handle_events(self, events):
            """
            Handles events specific to the achievements screen.
            """
            for event in events:
                self.back_button.handle_event(event)
    
        def draw(self):
            """
            Draws the achievements screen.
            """
            self.screen.fill(DARK_GREY)
    
            # Draw title
            title_text = "Achievements"
            title_surf = self.fonts['title_font'].render(title_text, True, WHITE)
            self.screen.blit(title_surf, ((self.window_size[0] - title_surf.get_width())//2, 20))
    
            # Draw achievements list
            y_offset = 100
            for key, achievement in achievement_manager.achievements.items():
                status = "Unlocked" if achievement['unlocked'] else "Locked"
                color = GOLD if achievement['unlocked'] else LIGHT_GREY
                text = f"{achievement['description']} - {status}"
                text_surf = self.fonts['font'].render(text, True, color)
                self.screen.blit(text_surf, (100, y_offset))
                y_offset += 40
    
            # Draw back button
            self.back_button.draw(self.screen, self.fonts['button_font'])
    
            pygame.display.flip()
    
    # Multiple Conversation Threads Manager
    class ConversationThreadsManager:
        """
        Manages multiple conversation threads, allowing users to switch between them.
        """
        def __init__(self, screen, window_size, fonts):
            self.screen = screen
            self.window_size = window_size
            self.fonts = fonts
            self.active = False
            self.threads = {'Default': {'sequence': load_sequence(), 'models_info': load_models_info(), 'conversation_goal': '', 'conversation_history': []}}
            self.current_thread = 'Default'
            self.create_buttons()
            self.create_new_thread_button()
    
        def create_buttons(self):
            """
            Creates buttons for switching between threads.
            """
            self.thread_buttons = []
            x_start = 100
            y_start = 200
            for thread_name in self.threads.keys():
                button = Button(
                    text=thread_name,
                    position=(x_start, y_start),
                    size=(200, 60),
                    callback=lambda tn=thread_name: self.switch_thread(tn),
                    color=TEAL,
                    hover_color=PURPLE
                )
                self.thread_buttons.append(button)
                y_start += 80
    
        def create_new_thread_button(self):
            """
            Creates a button to create a new conversation thread.
            """
            self.new_thread_button = Button(
                text="New Thread",
                position=(100, self.window_size[1] - 150),
                size=(200, 60),
                callback=self.create_new_thread,
                color=GOLD,
                hover_color=PURPLE
            )
    
        def switch_thread(self, thread_name):
            """
            Switches the active conversation thread.
        
            Args:
                thread_name (str): The name of the thread to switch to.
            """
            self.current_thread = thread_name
            achievement_manager.check_achievements()
    
        def create_new_thread(self):
            """
            Creates a new conversation thread.
            """
            new_thread_name = get_user_input(self.screen, "Enter name for the new thread:", self.window_size)
            if new_thread_name and new_thread_name not in self.threads:
                self.threads[new_thread_name] = {
                    'sequence': load_sequence(),
                    'models_info': load_models_info(),
                    'conversation_goal': '',
                    'conversation_history': []
                }
                # Create a new button for the thread
                new_button = Button(
                    text=new_thread_name,
                    position=(100, 200 + len(self.thread_buttons)*80),
                    size=(200, 60),
                    callback=lambda tn=new_thread_name: self.switch_thread(tn),
                    color=TEAL,
                    hover_color=PURPLE
                )
                self.thread_buttons.append(new_button)
                achievement_manager.trigger_achievement('new_thread')
    
        def handle_events(self, events):
            """
            Handles events specific to the conversation threads screen.
            """
            for event in events:
                for button in self.thread_buttons:
                    button.handle_event(event)
                self.new_thread_button.handle_event(event)
    
        def draw(self):
            """
            Draws the conversation threads screen.
            """
            self.screen.fill(DARK_GREY)
    
            # Draw title
            title_text = "Conversation Threads"
            title_surf = self.fonts['title_font'].render(title_text, True, WHITE)
            self.screen.blit(title_surf, ((self.window_size[0] - title_surf.get_width())//2, 20))
    
            # Draw thread buttons
            for button in self.thread_buttons:
                button.draw(self.screen, self.fonts['button_font'])
    
            # Draw new thread button
            self.new_thread_button.draw(self.screen, self.fonts['button_font'])
    
            pygame.display.flip()
    
    # Advanced Notification System
    class NotificationSystem:
        """
        Handles advanced notifications within the application.
        """
        def __init__(self, screen, window_size, fonts):
            self.screen = screen
            self.window_size = window_size
            self.fonts = fonts
            self.notifications = []
    
        def add_notification(self, message):
            """
            Adds a new notification to the system.
        
            Args:
                message (str): The notification message.
            """
            self.notifications.append({'message': message, 'timer': 0})
            if SOUND_NOTIFICATION:
                SOUND_NOTIFICATION.play()
    
        def update(self, dt):
            """
            Updates the notification timers and removes expired notifications.
        
            Args:
                dt (int): Time elapsed since last update in milliseconds.
            """
            for notification in self.notifications[:]:
                notification['timer'] += dt
                if notification['timer'] > 5000:  # Display for 5 seconds
                    self.notifications.remove(notification)
    
        def draw(self):
            """
            Draws active notifications onto the screen.
            """
            for i, notification in enumerate(self.notifications):
                # Semi-transparent background
                overlay = pygame.Surface((self.window_size[0] * 0.3, 100), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                self.screen.blit(overlay, (self.window_size[0] * 0.7, 50 + i * 120))
    
                # Notification text
                text_surf = self.fonts['message_font'].render(notification['message'], True, WHITE)
                self.screen.blit(text_surf, (self.window_size[0] * 0.7 + 10, 60 + i * 120))
    
    # Message Reactions
    class MessageReaction:
        """
        Allows users to react to messages with emojis.
        """
        def __init__(self, screen, fonts):
            self.screen = screen
            self.fonts = fonts
            self.active = False
            self.reactions = ['👍', '❤️', '😂', '😮', '😢', '🔥']
            self.selected_message = None
            self.buttons = []
            self.create_reaction_buttons()
    
        def create_reaction_buttons(self):
            """
            Initializes reaction buttons.
            """
            spacing = 80
            start_x = 100
            start_y = 100
            for i, reaction in enumerate(self.reactions):
                button = Button(
                    text=reaction,
                    position=(start_x + i * spacing, start_y),
                    size=(60, 60),
                    callback=lambda r=reaction: self.react(r),
                    color=LIGHT_PURPLE,
                    hover_color=PURPLE
                )
                self.buttons.append(button)
    
        def activate(self, message):
            """
            Activates the reaction selector for a specific message.
        
            Args:
                message (dict): The message dictionary to react to.
            """
            self.active = True
            self.selected_message = message
    
        def deactivate(self):
            """
            Deactivates the reaction selector.
            """
            self.active = False
            self.selected_message = None
    
        def react(self, reaction):
            """
            Adds a reaction to the selected message.
        
            Args:
                reaction (str): The reaction emoji.
            """
            if self.selected_message:
                if 'reactions' not in self.selected_message:
                    self.selected_message['reactions'] = []
                self.selected_message['reactions'].append(reaction)
                notification_system.add_notification(f"Added reaction {reaction} to message.")
                self.deactivate()
    
        def handle_events(self, events):
            """
            Handles events specific to the reaction selector.
            """
            for event in events:
                for button in self.buttons:
                    button.handle_event(event)
    
        def draw(self):
            """
            Draws the reaction selector onto the screen.
            """
            if self.active:
                # Semi-transparent overlay
                overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150))
                self.screen.blit(overlay, (0, 0))
    
                # Reaction box
                box_width = 600
                box_height = 100
                box = pygame.Rect((self.screen.get_width() - box_width)//2, (self.screen.get_height() - box_height)//2, box_width, box_height)
                pygame.draw.rect(self.screen, DARK_GREY, box)
                pygame.draw.rect(self.screen, WHITE, box, 4)
    
                # Draw buttons
                for button in self.buttons:
                    button.draw(self.screen, self.fonts['button_font'])
    
                pygame.display.flip()
    
    # Enhanced Chat Window Class with Message Reactions
    class ChatWindow:
        """
        Represents the scrollable chat window with emoji support, typing indicators, and message reactions.
        """
        def __init__(self, position, size, typing_indicator, message_reaction):
            self.rect = pygame.Rect(position, size)
            self.surface = pygame.Surface(self.rect.size)
            self.surface.fill(DARK_GREY)
            self.scroll = 0
            self.max_scroll = 0
            self.typing_indicator = typing_indicator
            self.message_reaction = message_reaction
        
        def update_chat(self, conversation_history, character_images, fonts, show_avatars=True):
            """
            Updates the chat surface with the latest conversation history.
            """
            self.surface.fill(DARK_GREY)  # Clear previous messages
            padding = 50
            avatar_size = (50, 50)  # Adjusted avatar size
            y_offset = padding
    
            for entry in conversation_history:
                speaker = entry['speaker']
                message = replace_emojis(entry['message'])
                reactions = entry.get('reactions', [])
                avatar = character_images.get(speaker, character_images['User'])
                if avatar and show_avatars:
                    avatar_scaled = pygame.transform.scale(avatar, avatar_size)
                    self.surface.blit(avatar_scaled, (padding, y_offset))
                # Render message text
                text_x = padding * 2 + avatar_size[0] if (avatar and show_avatars) else padding
                text_y = y_offset + 10
                draw_text(message, fonts['message_font'], WHITE, self.surface, text_x, text_y, self.rect.width - text_x - padding)
                # Render reactions
                if reactions:
                    reaction_text = ' '.join(reactions)
                    reaction_surf = fonts['message_font'].render(reaction_text, True, WHITE)
                    self.surface.blit(reaction_surf, (text_x, text_y + fonts['message_font'].get_height() + 5))
                # Calculate the height of the rendered text to adjust y_offset
                lines = message.split('\n')
                text_height = fonts['message_font'].get_linesize() * len(lines) + 5 + (fonts['message_font'].get_height() if reactions else 0)
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
            self.typing_indicator.draw()
            self.message_reaction.draw()
        
        def handle_scroll(self, delta):
            """
            Handles scrolling based on user input.
        
            Args:
                delta (int): The amount to scroll.
            """
            self.scroll -= delta
            if self.scroll < 0:
                self.scroll = 0
            elif self.scroll > self.max_scroll:
                self.scroll = self.max_scroll
    
    # Enhanced Conversation Manager Class with Typing Indicators
    class ConversationManager:
        """
        Manages the conversation flow between personas and the context model with typing indicators.
        """
        def __init__(self, sequence, models_info, conversation_goal, typing_indicator):
            self.sequence = sequence
            self.models_info = models_info
            self.conversation_goal = conversation_goal
            self.turn = 0
            self.total_turns = len(sequence)
            self.active = True
            self.thread = None
            self.typing_indicator = typing_indicator
    
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
            self.typing_indicator.activate()
            model_info = self.models_info.get(speaker, {})
            model_name = model_info.get('model_name')
            if not model_name:
                print(f"No model name specified for '{speaker}'. Skipping.")
                with conversation_lock:
                    conversation_history.append({'speaker': 'System', 'message': f"No model found for {speaker}."})
                self.typing_indicator.deactivate()
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
            achievement_manager.check_achievements()
    
            self.typing_indicator.deactivate()
            self.turn += 1
            self.start_next_turn()
    
        def handle_context_model(self):
            """
            Handles the context/summarization model.
            """
            self.typing_indicator.activate()
            context_model_name = self.models_info['context_model']['model_name']  # As specified
    
            # Generate prompt for context model
            prompt = construct_prompt('context_model', conversation_history, self.models_info, self.conversation_goal)
    
            # Generate summary
            summary = generate_from_model(context_model_name, prompt, self.models_info['context_model'].get('options', {}))
    
            with conversation_lock:
                conversation_history.append({'speaker': 'ContextModel', 'message': summary})
    
            if SOUND_RECEIVE:
                SOUND_RECEIVE.play()
    
            achievement_manager.check_achievements()
    
            self.typing_indicator.deactivate()
            self.turn += 1
            self.start_next_turn()
    
        def run(self):
            """
            Starts the conversation manager.
            """
            self.start_next_turn()
    
    # Achievements Manager Initialization
    achievement_manager = AchievementsManager(SCREEN, fonts, SCREEN.get_size())
    
    # Profile Customization Profiles
    persona_profiles = {}
    
    # Message Reaction Initialization
    message_reaction = MessageReaction(SCREEN, fonts)
    
    # Typing Indicator Initialization
    typing_indicator = TypingIndicator(SCREEN, SCREEN.get_size(), fonts)
    
    # Animated Background Initialization
    animated_background = AnimatedBackground(SCREEN, SCREEN.get_size())
    
    # Notification System Initialization
    notification_system = NotificationSystem(SCREEN, SCREEN.get_size(), fonts)
    
    # Achievements Screen Initialization
    achievements_screen = AchievementsScreen(SCREEN, SCREEN.get_size(), fonts)
    
    # Conversation Threads Manager Initialization
    conversation_threads_manager = ConversationThreadsManager(SCREEN, SCREEN.get_size(), fonts)
    
    # Run the Application
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
                if event.type == pygame.VIDEORESIZE:
                    # Update window size and fonts
                    window_size = event.size
                    SCREEN = pygame.display.set_mode(window_size, pygame.RESIZABLE)
                    fonts = get_scaled_fonts(window_size[0], window_size[1])
                    # Update all components with new window size
                    animated_background = AnimatedBackground(SCREEN, window_size)
                    typing_indicator = TypingIndicator(SCREEN, window_size, fonts)
                    notification_system = NotificationSystem(SCREEN, window_size, fonts)
                    achievements_screen = AchievementsScreen(SCREEN, window_size, fonts)
                    conversation_threads_manager = ConversationThreadsManager(SCREEN, window_size, fonts)
    
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
                notification_system.add_notification("Conversation started.")
    
                # Initialize Conversation Manager
                conversation_manager = ConversationManager(sequence, models_info, conversation_goal, typing_indicator)
                conversation_manager.run()
    
                # Initialize Chat Window
                chat_window = ChatWindow(position=(int(window_size[0] * 0.1), int(window_size[1] * 0.3)),
                                         size=(int(window_size[0] * 0.8), int(window_size[1] * 0.6)),
                                         typing_indicator=typing_indicator,
                                         message_reaction=message_reaction)
    
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
    
                # Create Achievements Button
                achievements_button = Button(
                    text="Achievements",
                    position=(int(window_size[0] * 0.9) - 250, 50),
                    size=(200, 60),
                    callback=achievements_screen.activate,
                    color=GOLD,
                    hover_color=PURPLE
                )
                # Create Profile Customization Button
                profile_button = Button(
                    text="Customize Profiles",
                    position=(int(window_size[0] * 0.9) - 250, 150),
                    size=(200, 60),
                    callback=lambda: profile_customization.activate('project_manager'),  # Example for project_manager
                    color=PURPLE,
                    hover_color=GOLD
                )
                # Create Threads Button
                threads_button = Button(
                    text="Conversation Threads",
                    position=(int(window_size[0] * 0.9) - 250, 250),
                    size=(200, 60),
                    callback=conversation_threads_manager.activate,
                    color=TEAL,
                    hover_color=PURPLE
                )
                control_buttons = [achievements_button, profile_button, threads_button]
            else:
                # Update chat window with latest conversation
                with conversation_lock:
                    chat_window.update_chat(conversation_history, CHARACTER_IMAGES, fonts, show_avatars=achievement_manager.settings.get('show_avatars', True))
    
                # Handle scrolling
                for event in events:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 4:  # Scroll up
                            chat_window.handle_scroll(30)
                        elif event.button == 5:  # Scroll down
                            chat_window.handle_scroll(-30)
    
                # Update animated background
                animated_background.update()
                animated_background.draw()
    
                # Update typing indicator
                typing_indicator.update(CLOCK.get_time())
    
                # Update notification system
                notification_system.update(CLOCK.get_time())
                notification_system.draw()
    
                # Draw the main screen
                # No need to fill since animated background is drawn
                # Draw title
                title_surface = fonts['title_font'].render("Team Purple", True, PURPLE)
                SCREEN.blit(title_surface, ((window_size[0] - title_surface.get_width())//2, 20))
    
                # Draw chat window
                chat_window.draw(SCREEN)
    
                # Draw Save Button
                for button in save_buttons:
                    button.draw(SCREEN, fonts['button_font'])
    
                # Draw Control Buttons
                for button in control_buttons:
                    button.draw(SCREEN, fonts['button_font'])
    
                pygame.display.flip()
    
                # Check for achievements or thread completion
                if not conversation_manager.active and not conversation_manager.thread.is_alive():
                    running = False
    
            # Handle Message Reactions
            if message_reaction.active:
                message_reaction.handle_events(events)
                message_reaction.draw()
    
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
    
        # Draw Control Buttons
        for button in control_buttons:
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
    
    # Message Reaction Callback in Chat Window
    def check_message_reactions(mouse_pos):
        """
        Checks if a message was clicked for adding reactions.
        
        Args:
            mouse_pos (tuple): The (x, y) position of the mouse click.
        """
        for entry in reversed(conversation_history):
            # Simple hit detection; in a real application, you'd calculate message positions
            # Here, we'll assume messages are stacked from top with fixed height
            message_index = conversation_history.index(entry)
            message_y = 100 + message_index * 100 - chat_window.scroll  # Example positioning
            if 100 <= mouse_pos[1] - message_y <= 150:
                message_reaction.activate(entry)
                break
    
    # Enhanced Save Conversation Function with Achievements Trigger
    def save_conversation(conversation_history, fonts, window_size):
        """
        Handles saving the conversation to a file and triggers achievements.
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
            achievement_manager.trigger_achievement('save_conversation')
            notification_system.add_notification(f"Conversation saved to {file_name}")
        except Exception as e:
            error_text = f"Error saving conversation: {e}"
            notification_system.add_notification(error_text)
    
    # Enhancements to SetupScreen for Profile Customization Access
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
                position=(self.window_size[0]//2 - 150, self.window_size[1] - 300),
                size=(300, 150),
                callback=self.finish_setup,
                color=LIGHT_PURPLE,
                hover_color=PURPLE
            )
            self.settings_button = Button(
                text="Settings",
                position=(self.window_size[0]//2 - 150, self.window_size[1] - 500),
                size=(300, 150),
                callback=self.open_settings,
                color=TEAL,
                hover_color=PURPLE
            )
            self.help_button = Button(
                text="Help & Tutorial",
                position=(self.window_size[0]//2 - 150, self.window_size[1] - 700),
                size=(300, 150),
                callback=self.open_help,
                color=GOLD,
                hover_color=PURPLE
            )
            self.buttons = [self.next_button, self.settings_button, self.help_button]
            self.settings_screen = SettingsScreen(screen, window_size)
            self.help_screen = HelpScreen(screen, window_size)
            self.profile_customization = ProfileCustomization(screen, window_size, fonts)
            self.achievements_screen = achievements_screen
    
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
            padding = 600
        
            module_width = 1158
            module_height = 1140
            start_x = padding
            start_y = padding + 150  # Leave space for title
    
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
    
        def open_settings(self):
            """
            Opens the settings screen.
            """
            self.settings_screen.activate()
    
        def open_help(self):
            """
            Opens the help and tutorial screen.
            """
            self.help_screen.activate()
    
        def handle_events(self, events):
            """
            Handles events specific to the setup screen.
            """
            for event in events:
                for module in self.modules:
                    module.handle_event(event)
                for button in self.buttons:
                    button.handle_event(event)
            if self.settings_screen.active:
                self.settings_screen.handle_events(events)
            if self.help_screen.active:
                self.help_screen.handle_events(events)
            if self.profile_customization.active:
                self.profile_customization.handle_events(events)
    
        def update(self):
            """
            Updates the setup screen.
            """
            if self.settings_screen.active:
                self.settings_screen.update()
            if self.help_screen.active:
                self.help_screen.update()
            if self.profile_customization.active:
                pass  # Add any dynamic updates if necessary
    
        def draw(self):
            """
            Draws the setup screen.
            """
            self.screen.fill(DARK_PURPLE)  # Dark purple-themed background
    
            # Draw title
            title_text = "Team Purple Setup"
            title_surf = self.fonts['title_font'].render(title_text, True, WHITE)
            self.screen.blit(title_surf, ((self.window_size[0] - title_surf.get_width())//2, 20))
    
            if self.settings_screen.active:
                self.settings_screen.draw()
                return
            if self.help_screen.active:
                self.help_screen.draw()
                return
            if self.profile_customization.active:
                self.profile_customization.draw()
                return
    
            # Draw draggable modules
            for module in self.modules:
                module.draw(self.screen)
    
            # Draw buttons
            for button in self.buttons:
                button.draw(self.screen, fonts['button_font'])
    
            pygame.display.flip()
    
    # Final Run
    if __name__ == "__main__":
        main()
