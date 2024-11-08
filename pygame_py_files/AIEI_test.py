import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1200, 800
FPS = 60

# Colors
COLORS = {
    "primary_bg": (30, 0, 46),           # #1E002E
    "primary_button": (255, 0, 124),     # #FF007C
    "secondary_button": (255, 73, 164),  # #FF49A4
    "instruction_label": (92, 0, 114),   # #5C0072
    "input_field_bg": (61, 0, 79),       # #3D004F
    "model_green": (0, 255, 178),        # #00FFB2
    "model_purple": (176, 0, 255),       # #B000FF
    "slider_bg": (42, 0, 54),            # #2A0036
    "persona_upload": (255, 86, 178),    # #FF56B2
    "summarization_text": (255, 102, 204),# #FF66CC
    "accent_dot": (255, 51, 170),        # #FF33AA
    "header_title": (255, 255, 255),     # #FFFFFF
    "hover_bg_primary": (255, 30, 150),  # Lighter shade for hover
    "hover_bg_secondary": (255, 100, 200),# Lighter shade for hover
}

# Fonts
pygame.font.init()
FONT_SMALL = pygame.font.SysFont('Arial', 18)
FONT_MEDIUM = pygame.font.SysFont('Arial', 24)
FONT_LARGE = pygame.font.SysFont('Arial', 32)

# Screen Setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Symphoni Application")
clock = pygame.time.Clock()

# Button Class
class Button:
    def __init__(self, rect, color, hover_color, text, font, action=None):
        self.rect = pygame.Rect(rect)
        self.color = color
        self.hover_color = hover_color
        self.text = text
        self.font = font
        self.action = action
        self.hovered = False

    def draw(self, surface):
        current_color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(surface, current_color, self.rect, border_radius=5)
        text_surf = self.font.render(self.text, True, COLORS["header_title"])
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.hovered and self.action:
                self.action()

# Slider Class
class Slider:
    def __init__(self, x, y, width, min_val, max_val, current_val):
        self.rect = pygame.Rect(x, y, width, 20)
        self.min_val = min_val
        self.max_val = max_val
        self.current_val = current_val
        self.handle_rect = pygame.Rect(0, y - 5, 10, 30)
        self.update_handle_pos()
        self.dragging = False

    def update_handle_pos(self):
        ratio = (self.current_val - self.min_val) / (self.max_val - self.min_val)
        self.handle_rect.centerx = self.rect.x + ratio * self.rect.width

    def draw(self, surface):
        pygame.draw.rect(surface, COLORS["slider_bg"], self.rect)
        pygame.draw.rect(surface, COLORS["summarization_text"], self.handle_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.handle_rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                new_x = max(self.rect.x, min(event.pos[0], self.rect.x + self.rect.width))
                self.handle_rect.centerx = new_x
                ratio = (new_x - self.rect.x) / self.rect.width
                self.current_val = int(self.min_val + ratio * (self.max_val - self.min_val))

# Draggable Item Class
class DraggableItem:
    def __init__(self, name, color, rect):
        self.name = name
        self.color = color
        self.rect = pygame.Rect(rect)
        self.dragging = False
        self.offset = (0, 0)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=5)
        text_surf = FONT_SMALL.render(self.name, True, COLORS["header_title"])
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                mouse_x, mouse_y = event.pos
                self.offset = (self.rect.x - mouse_x, self.rect.y - mouse_y)
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                mouse_x, mouse_y = event.pos
                self.rect.x = mouse_x + self.offset[0]
                self.rect.y = mouse_y + self.offset[1]

# Text Input Class
class TextInput:
    def __init__(self, rect, text=''):
        self.rect = pygame.Rect(rect)
        self.color = COLORS["input_field_bg"]
        self.text = text
        self.txt_surface = FONT_SMALL.render(text, True, COLORS["header_title"])
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Toggle the active variable.
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    self.active = False
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.txt_surface = FONT_SMALL.render(self.text, True, COLORS["header_title"])

    def draw(self, surface):
        # Blit the text.
        surface.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        # Blit the rect.
        pygame.draw.rect(surface, self.color, self.rect, border_radius=5)
        # If the input is active, draw a border.
        if self.active:
            pygame.draw.rect(surface, COLORS["primary_button"], self.rect, 2, border_radius=5)

# Main Interface Class
class SymphoniApp:
    def __init__(self):
        self.current_section = "Persona Setup"
        self.sections = ["Persona Setup", "Instruct Sequence Setup", "Inference Sequence Setup", "Dashboard"]
        self.buttons = []
        self.setup_navbar()
        self.persona_inputs = []
        self.create_persona_inputs()
        self.draggable_models = []
        self.create_draggable_models()
        self.instruct_fields = []
        self.create_instruct_fields()
        self.inference_prompts = []
        self.create_inference_prompts()
        self.start_button = Button((WIDTH - 220, HEIGHT - 60, 100, 40), COLORS["primary_button"], COLORS["hover_bg_primary"], "Start", FONT_MEDIUM, self.start_sequence)
        self.save_button = Button((WIDTH - 110, HEIGHT - 60, 100, 40), COLORS["secondary_button"], COLORS["hover_bg_secondary"], "Save", FONT_MEDIUM, self.save_sequence)

    def setup_navbar(self):
        nav_height = 50
        for i, section in enumerate(self.sections):
            btn = Button((10 + i*200, 10, 180, 30), COLORS["primary_button"], COLORS["hover_bg_primary"], section, FONT_SMALL, lambda s=section: self.change_section(s))
            self.buttons.append(btn)

    def change_section(self, section):
        self.current_section = section

    def create_persona_inputs(self):
        # Create 9 personas
        for i in range(9):
            x = 50 + (i % 3) * 350
            y = 100 + (i // 3) * 200
            name_input = TextInput((x, y, 300, 30))
            adherence_slider = Slider(x, y + 40, 300, 1, 10, 5)
            creativity_slider = Slider(x, y + 80, 300, 1, 10, 5)
            self.persona_inputs.append({
                "name_input": name_input,
                "adherence_slider": adherence_slider,
                "creativity_slider": creativity_slider
            })

    def create_draggable_models(self):
        models = ["Mistral Nemo", "Smol M13B", "Orca Mini 70B"]
        for i, model in enumerate(models):
            x = 50 + i * 150
            y = 100
            draggable = DraggableItem(model, COLORS["model_green"], (x, y, 140, 40))
            self.draggable_models.append(draggable)

    def create_instruct_fields(self):
        # Create 16 instruct fields
        for i in range(16):
            x = 50 + (i % 4) * 275
            y = 200 + (i // 4) * 120
            self.instruct_fields.append(pygame.Rect(x, y, 250, 100))

    def create_inference_prompts(self):
        # Create some inference prompts
        for i in range(3):
            prompt = TextInput((50, 100 + i*150, 800, 80))
            self.inference_prompts.append(prompt)

    def start_sequence(self):
        print("Starting sequence...")
        # Implement your start sequence logic here

    def save_sequence(self):
        print("Saving sequence...")
        # Implement your save sequence logic here

    def handle_events(self, event):
        for button in self.buttons:
            button.handle_event(event)
        self.start_button.handle_event(event)
        self.save_button.handle_event(event)
        for persona in self.persona_inputs:
            persona["name_input"].handle_event(event)
            persona["adherence_slider"].handle_event(event)
            persona["creativity_slider"].handle_event(event)
        for model in self.draggable_models:
            model.handle_event(event)
        for prompt in self.inference_prompts:
            prompt.handle_event(event)

    def draw_navbar(self, surface):
        for button in self.buttons:
            button.draw(surface)

    def draw_persona_setup(self, surface):
        for i, persona in enumerate(self.persona_inputs):
            x = 50 + (i % 3) * 350
            y = 100 + (i // 3) * 200
            # Draw Persona Box
            pygame.draw.rect(surface, COLORS["input_field_bg"], (x, y, 300, 150), border_radius=10)
            # Draw Labels
            label_surf = FONT_SMALL.render(f"Define Persona {i+1}", True, COLORS["instruction_label"])
            surface.blit(label_surf, (x + 10, y + 10))
            # Draw Name Input
            persona["name_input"].draw(surface)
            # Draw Adherence Slider
            adherence_label = FONT_SMALL.render(f"Prompt Adherence: {persona['adherence_slider'].current_val}", True, COLORS["header_title"])
            surface.blit(adherence_label, (x, y + 50))
            persona["adherence_slider"].draw(surface)
            # Draw Creativity Slider
            creativity_label = FONT_SMALL.render(f"Creativity: {persona['creativity_slider'].current_val}", True, COLORS["header_title"])
            surface.blit(creativity_label, (x, y + 90))
            persona["creativity_slider"].draw(surface)

    def draw_instruct_sequence_setup(self, surface):
        # Draw Available Models
        for model in self.draggable_models:
            model.draw(surface)
        # Draw Instruct Fields
        for i, rect in enumerate(self.instruct_fields):
            pygame.draw.rect(surface, COLORS["model_purple"], rect, border_radius=5)
            label_surf = FONT_SMALL.render(f"Instruct Field {i+1}", True, COLORS["header_title"])
            surface.blit(label_surf, (rect.x + 5, rect.y + 5))
        # Draw Start and Save Buttons
        self.start_button.draw(surface)
        self.save_button.draw(surface)

    def draw_inference_sequence_setup(self, surface):
        # Draw Summarization Panel
        summar_rect = pygame.Rect(50, 50, 800, 150)
        pygame.draw.rect(surface, COLORS["input_field_bg"], summar_rect, border_radius=10)
        summary_label = FONT_MEDIUM.render("Summarization & Prompt", True, COLORS["header_title"])
        surface.blit(summary_label, (summar_rect.x + 10, summar_rect.y + 10))
        for prompt in self.inference_prompts:
            prompt.draw(surface)
        # Draw Generate Button
        generate_button = Button((900, 100, 200, 40), COLORS["primary_button"], COLORS["hover_bg_primary"], "Summarize & Generate", FONT_MEDIUM, lambda: print("Summarize clicked"))
        generate_button.draw(surface)

    def draw_dashboard(self, surface):
        # Simple dashboard placeholder
        pygame.draw.rect(surface, COLORS["input_field_bg"], (50, 50, 1100, 700), border_radius=10)
        dashboard_label = FONT_LARGE.render("Dashboard", True, COLORS["header_title"])
        surface.blit(dashboard_label, (WIDTH//2 - dashboard_label.get_width()//2, 100))

    def draw(self, surface):
        surface.fill(COLORS["primary_bg"])
        self.draw_navbar(surface)
        if self.current_section == "Persona Setup":
            self.draw_persona_setup(surface)
        elif self.current_section == "Instruct Sequence Setup":
            self.draw_instruct_sequence_setup(surface)
        elif self.current_section == "Inference Sequence Setup":
            self.draw_inference_sequence_setup(surface)
        elif self.current_section == "Dashboard":
            self.draw_dashboard(surface)
        # Add more sections as needed

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                self.handle_events(event)
            self.draw(screen)
            pygame.display.flip()
            clock.tick(FPS)
        pygame.quit()
        sys.exit()

# Run the application
if __name__ == "__main__":
    app = SymphoniApp()
    app.run()
