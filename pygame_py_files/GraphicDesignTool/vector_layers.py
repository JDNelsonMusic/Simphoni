import pygame
import sys
import json
from pygame.locals import *
from collections import OrderedDict

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1400, 900
TOOLBAR_WIDTH, LAYERPANEL_WIDTH, PROPERTIES_WIDTH = 200, 200, 250
CANVAS_WIDTH = SCREEN_WIDTH - TOOLBAR_WIDTH - LAYERPANEL_WIDTH - PROPERTIES_WIDTH
CANVAS_HEIGHT = SCREEN_HEIGHT
FPS = 60

# Colors
WHITE = (255, 255, 255)
LIGHT_GREY = (220, 220, 220)
GREY = (180, 180, 180)
DARK_GREY = (100, 100, 100)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (160, 32, 240)
CYAN = (0, 255, 255)
PINK = (255, 192, 203)
BROWN = (165, 42, 42)

STROKE_COLORS = [BLACK, RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE, CYAN]
FILL_COLORS = [WHITE, RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE, CYAN, PINK, BROWN]

# Fonts
pygame.font.init()
FONT = pygame.font.SysFont('Arial', 16)
BIG_FONT = pygame.font.SysFont('Arial', 20, bold=True)

# Tool Constants
TOOL_SELECT = 'Select'
TOOL_LINE = 'Line'
TOOL_RECT = 'Rectangle'
TOOL_CIRCLE = 'Circle'
TOOL_ELLIPSE = 'Ellipse'
TOOL_FREEHAND = 'Freehand'
TOOL_TEXT = 'Text'
TOOL_POLYGON = 'Polygon'

TOOLS = [TOOL_SELECT, TOOL_LINE, TOOL_RECT, TOOL_CIRCLE, TOOL_ELLIPSE, TOOL_POLYGON, TOOL_FREEHAND, TOOL_TEXT]

# Helper Functions
def draw_text(surface, text, pos, color=BLACK, font=FONT):
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, pos)

def get_mouse_pos_canvas(pos):
    x, y = pos
    return (x - TOOLBAR_WIDTH, y)

# Vector Object Classes
class VectorObject:
    def __init__(self, obj_type, properties):
        self.type = obj_type
        self.properties = properties  # Dictionary containing properties like color, position, etc.
        self.selected = False

    def draw(self, surface):
        if self.type == 'line':
            pygame.draw.line(surface, self.properties['stroke_color'],
                             self.properties['start_pos'], self.properties['end_pos'],
                             self.properties['stroke_width'])
            if self.selected:
                self.draw_selection(surface, [self.properties['start_pos'], self.properties['end_pos']])
        elif self.type == 'rectangle':
            rect = pygame.Rect(self.properties['start_pos'], (self.properties['width'], self.properties['height']))
            if self.properties['fill']:
                pygame.draw.rect(surface, self.properties['fill_color'], rect)
            pygame.draw.rect(surface, self.properties['stroke_color'], rect, self.properties['stroke_width'])
            if self.selected:
                self.draw_selection(surface, [self.properties['start_pos'],
                                               (self.properties['start_pos'][0] + self.properties['width'],
                                                self.properties['start_pos'][1] + self.properties['height'])])
        elif self.type == 'circle':
            if self.properties['fill']:
                pygame.draw.circle(surface, self.properties['fill_color'],
                                   self.properties['center'], self.properties['radius'])
            pygame.draw.circle(surface, self.properties['stroke_color'],
                               self.properties['center'], self.properties['radius'],
                               self.properties['stroke_width'])
            if self.selected:
                self.draw_selection(surface, [self.properties['center'],
                                               (self.properties['center'][0] + self.properties['radius'],
                                                self.properties['center'][1] + self.properties['radius'])])
        elif self.type == 'ellipse':
            rect = pygame.Rect(self.properties['start_pos'],
                               (self.properties['width'], self.properties['height']))
            if self.properties['fill']:
                pygame.draw.ellipse(surface, self.properties['fill_color'], rect)
            pygame.draw.ellipse(surface, self.properties['stroke_color'], rect,
                                self.properties['stroke_width'])
            if self.selected:
                self.draw_selection(surface, [self.properties['start_pos'],
                                               (self.properties['start_pos'][0] + self.properties['width'],
                                                self.properties['start_pos'][1] + self.properties['height'])])
        elif self.type == 'freehand':
            if len(self.properties['points']) > 1:
                pygame.draw.lines(surface, self.properties['stroke_color'],
                                  False, self.properties['points'],
                                  self.properties['stroke_width'])
            if self.selected:
                self.draw_selection(surface, self.properties['points'])
        elif self.type == 'text':
            text_surface = FONT.render(self.properties['text'], True, self.properties['stroke_color'])
            surface.blit(text_surface, self.properties['position'])
            if self.selected:
                text_rect = text_surface.get_rect(topleft=self.properties['position'])
                pygame.draw.rect(surface, RED, text_rect, 2)
        elif self.type == 'polygon':
            if self.properties['fill']:
                pygame.draw.polygon(surface, self.properties['fill_color'],
                                    self.properties['points'])
            pygame.draw.polygon(surface, self.properties['stroke_color'],
                                self.properties['points'],
                                self.properties['stroke_width'])
            if self.selected:
                pygame.draw.polygon(surface, RED, self.properties['points'], 2)

    def draw_selection(self, surface, points):
        if isinstance(points, list):
            for point in points:
                pygame.draw.circle(surface, RED, point, 5)

    def is_clicked(self, pos):
        if self.type == 'line':
            # Simplistic line click detection
            start = self.properties['start_pos']
            end = self.properties['end_pos']
            distance = self.point_to_line_distance(pos, start, end)
            return distance <= self.properties['stroke_width'] + 3
        elif self.type == 'rectangle' or self.type == 'ellipse':
            rect = pygame.Rect(self.properties['start_pos'],
                               (self.properties['width'], self.properties['height']))
            return rect.collidepoint(pos)
        elif self.type == 'circle':
            distance = ((pos[0] - self.properties['center'][0]) ** 2 +
                        (pos[1] - self.properties['center'][1]) ** 2) ** 0.5
            return distance <= self.properties['radius']
        elif self.type == 'freehand':
            for i in range(len(self.properties['points']) - 1):
                distance = self.point_to_line_distance(pos,
                                                       self.properties['points'][i],
                                                       self.properties['points'][i + 1])
                if distance <= self.properties['stroke_width'] + 3:
                    return True
            return False
        elif self.type == 'text':
            text_surface = FONT.render(self.properties['text'], True, self.properties['stroke_color'])
            text_rect = text_surface.get_rect(topleft=self.properties['position'])
            return text_rect.collidepoint(pos)
        elif self.type == 'polygon':
            return self.point_in_polygon(pos, self.properties['points'])
        return False

    @staticmethod
    def point_to_line_distance(point, start, end):
        # Calculate the distance from a point to a line segment
        px, py = point
        x1, y1 = start
        x2, y2 = end

        dx = x2 - x1
        dy = y2 - y1

        if dx == dy == 0:
            return ((px - x1)**2 + (py - y1)**2) ** 0.5

        t = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)

        t = max(0, min(1, t))
        nearest_x = x1 + t * dx
        nearest_y = y1 + t * dy

        distance = ((px - nearest_x)**2 + (py - nearest_y)**2) ** 0.5
        return distance

    @staticmethod
    def point_in_polygon(point, polygon):
        # Ray casting algorithm for point in polygon
        x, y = point
        n = len(polygon)
        inside = False

        px1, py1 = polygon[0]
        for i in range(n + 1):
            px2, py2 = polygon[i % n]
            if y > min(py1, py2):
                if y <= max(py1, py2):
                    if x <= max(px1, px2):
                        if py1 != py2:
                            xinters = (y - py1) * (px2 - px1) / (py2 - py1) + px1
                        if px1 == px2 or x <= xinters:
                            inside = not inside
            px1, py1 = px2, py2
        return inside

    def to_dict(self):
        return {
            'type': self.type,
            'properties': self.properties
        }

    @staticmethod
    def from_dict(data):
        return VectorObject(data['type'], data['properties'])

# Layer Class
class Layer:
    def __init__(self, name):
        self.name = name
        self.visible = True
        self.objects = []

    def draw(self, surface):
        if not self.visible:
            return
        for obj in self.objects:
            obj.draw(surface)

    def to_dict(self):
        return {
            'name': self.name,
            'visible': self.visible,
            'objects': [obj.to_dict() for obj in self.objects]
        }

    @staticmethod
    def from_dict(data):
        layer = Layer(data['name'])
        layer.visible = data['visible']
        layer.objects = [VectorObject.from_dict(obj_data) for obj_data in data['objects']]
        return layer

# History Manager for Undo/Redo
class HistoryManager:
    def __init__(self):
        self.undo_stack = []
        self.redo_stack = []

    def save_state(self, layers):
        # Deep copy layers
        state = json.dumps([layer.to_dict() for layer in layers.values()])
        self.undo_stack.append(state)
        self.redo_stack.clear()

    def undo(self, layers):
        if not self.undo_stack:
            return
        state = self.undo_stack.pop()
        self.redo_stack.append(json.dumps([layer.to_dict() for layer in layers.values()]))
        loaded_layers = json.loads(state)
        layers.clear()
        for layer_data in loaded_layers:
            layer = Layer.from_dict(layer_data)
            layers[layer.name] = layer

    def redo(self, layers):
        if not self.redo_stack:
            return
        state = self.redo_stack.pop()
        self.undo_stack.append(json.dumps([layer.to_dict() for layer in layers.values()]))
        loaded_layers = json.loads(state)
        layers.clear()
        for layer_data in loaded_layers:
            layer = Layer.from_dict(layer_data)
            layers[layer.name] = layer

# Toolbar Class
class Toolbar:
    def __init__(self, rect):
        self.rect = rect
        self.tools = TOOLS
        self.tool_buttons = []
        self.stroke_palette = STROKE_COLORS
        self.fill_palette = FILL_COLORS
        self.current_tool = TOOL_SELECT
        self.current_stroke_color = BLACK
        self.current_fill_color = WHITE
        self.fill_enabled = False
        self.stroke_width = 2

        # Initialize tool buttons
        self.init_tool_buttons()

    def init_tool_buttons(self):
        padding = 10
        button_height = 40
        for index, tool in enumerate(self.tools):
            button_rect = pygame.Rect(self.rect.x + 10,
                                      self.rect.y + 10 + index * (button_height + padding),
                                      self.rect.width - 20, button_height)
            self.tool_buttons.append({'tool': tool, 'rect': button_rect})

    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN:
            pos = event.pos
            for button in self.tool_buttons:
                if button['rect'].collidepoint(pos):
                    self.current_tool = button['tool']
                    # Reset fill toggle if tool changes
                    if self.current_tool != TOOL_RECT and self.current_tool != TOOL_ELLIPSE and self.current_tool != TOOL_POLYGON:
                        self.fill_enabled = False
                    return
            # Handle stroke color selection
            self.handle_stroke_color_selection(pos)
            # Handle fill color selection
            self.handle_fill_color_selection(pos)
            # Handle fill toggle
            self.handle_fill_toggle(pos)

    def handle_stroke_color_selection(self, pos):
        # Define stroke color palette area
        palette_start_y = self.rect.y + 10 + len(self.tools) * 50 + 20
        for index, color in enumerate(self.stroke_palette):
            color_rect = pygame.Rect(self.rect.x + 10,
                                     palette_start_y + index * 30,
                                     30, 30)
            if color_rect.collidepoint(pos):
                self.current_stroke_color = color
                break

    def handle_fill_color_selection(self, pos):
        # Define fill color palette area
        palette_start_y = self.rect.y + 10 + len(self.tools) * 50 + 20
        palette_start_y += len(self.stroke_palette) * 40 + 20
        for index, color in enumerate(self.fill_palette):
            color_rect = pygame.Rect(self.rect.x + 10,
                                     palette_start_y + index * 30,
                                     30, 30)
            if color_rect.collidepoint(pos):
                self.current_fill_color = color
                self.fill_enabled = True
                break

    def handle_fill_toggle(self, pos):
        # Define fill toggle area
        palette_start_y = self.rect.y + 10 + len(self.tools) * 50 + 20
        palette_start_y += len(self.stroke_palette) * 40 + 20 + len(self.fill_palette) * 40 + 20
        fill_toggle_rect = pygame.Rect(self.rect.x + 10, palette_start_y, 30, 30)
        if fill_toggle_rect.collidepoint(pos):
            self.fill_enabled = not self.fill_enabled

    def render(self, surface):
        # Draw toolbar background
        pygame.draw.rect(surface, GREY, self.rect)

        # Draw tool buttons
        for button in self.tool_buttons:
            color = DARK_GREY if self.current_tool == button['tool'] else LIGHT_GREY
            pygame.draw.rect(surface, color, button['rect'])
            draw_text(surface, button['tool'], (button['rect'].x + 5, button['rect'].y + 10),
                      WHITE if self.current_tool == button['tool'] else BLACK)

        # Draw stroke color palette
        palette_start_y = self.rect.y + 10 + len(self.tools) * 50 + 20
        draw_text(surface, "Stroke Colors:", (self.rect.x + 10, palette_start_y - 20))
        for index, color in enumerate(self.stroke_palette):
            color_rect = pygame.Rect(self.rect.x + 10,
                                     palette_start_y + index * 30,
                                     30, 30)
            pygame.draw.rect(surface, color, color_rect)
            if self.current_stroke_color == color:
                pygame.draw.rect(surface, RED, color_rect, 3)

        # Draw fill color palette
        palette_start_y += len(self.stroke_palette) * 40 + 20
        draw_text(surface, "Fill Colors:", (self.rect.x + 10, palette_start_y - 20))
        for index, color in enumerate(self.fill_palette):
            color_rect = pygame.Rect(self.rect.x + 10,
                                     palette_start_y + index * 30,
                                     30, 30)
            pygame.draw.rect(surface, color, color_rect)
            if self.current_fill_color == color and self.fill_enabled:
                pygame.draw.rect(surface, RED, color_rect, 3)

        # Draw fill toggle
        palette_start_y += len(self.fill_palette) * 40 + 20
        fill_toggle_rect = pygame.Rect(self.rect.x + 10, palette_start_y, 30, 30)
        pygame.draw.rect(surface, DARK_GREY if self.fill_enabled else LIGHT_GREY, fill_toggle_rect)
        draw_text(surface, "Fill", (fill_toggle_rect.x + 5, fill_toggle_rect.y + 5),
                  WHITE if self.fill_enabled else BLACK)

    def toggle_fill(self):
        self.fill_enabled = not self.fill_enabled

# Layer Panel Class
class LayerPanel:
    def __init__(self, rect):
        self.rect = rect
        self.layers = OrderedDict()
        self.layers['Background'] = Layer('Background')
        self.active_layer = 'Background'

        self.button_height = 30
        self.padding = 10
        self.init_buttons()

    def init_buttons(self):
        # Initialize layer control buttons
        self.add_layer_button = pygame.Rect(self.rect.x + 10, self.rect.y + 10,
                                            self.rect.width - 20, self.button_height)
        self.up_button = pygame.Rect(self.rect.x + 10, self.rect.y + 50,
                                     (self.rect.width - 30) // 2, self.button_height)
        self.down_button = pygame.Rect(self.rect.x + self.rect.width // 2 + 10, self.rect.y + 50,
                                       (self.rect.width - 30) // 2, self.button_height)

    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN:
            pos = event.pos
            if self.add_layer_button.collidepoint(pos):
                self.add_layer()
                return
            elif self.up_button.collidepoint(pos):
                self.move_layer_up()
                return
            elif self.down_button.collidepoint(pos):
                self.move_layer_down()
                return
            else:
                # Check if a layer was clicked
                for index, layer_name in enumerate(reversed(self.layers.keys())):
                    layer_rect = pygame.Rect(self.rect.x + 10, self.rect.y + 100 + index * (self.button_height + 10),
                                             self.rect.width - 20, self.button_height)
                    if layer_rect.collidepoint(pos):
                        self.active_layer = layer_name
                        return
                    # Check visibility toggle
                    vis_rect = pygame.Rect(layer_rect.x + layer_rect.width - 25, layer_rect.y + 5, 20, 20)
                    if vis_rect.collidepoint(pos):
                        self.toggle_visibility(layer_name)
                        return

    def add_layer(self):
        new_layer_name = f'Layer {len(self.layers)}'
        self.layers[new_layer_name] = Layer(new_layer_name)
        self.active_layer = new_layer_name

    def move_layer_up(self):
        keys = list(self.layers.keys())
        index = keys.index(self.active_layer)
        if index < len(keys) - 1:
            keys[index], keys[index + 1] = keys[index + 1], keys[index]
            self.layers = OrderedDict((k, self.layers[k]) for k in keys)

    def move_layer_down(self):
        keys = list(self.layers.keys())
        index = keys.index(self.active_layer)
        if index > 0:
            keys[index], keys[index - 1] = keys[index - 1], keys[index]
            self.layers = OrderedDict((k, self.layers[k]) for k in keys)

    def toggle_visibility(self, layer_name):
        self.layers[layer_name].visible = not self.layers[layer_name].visible

    def render(self, surface):
        # Draw layer panel background
        pygame.draw.rect(surface, GREY, self.rect)

        # Draw Add Layer Button
        pygame.draw.rect(surface, DARK_GREY, self.add_layer_button)
        draw_text(surface, "Add Layer", (self.add_layer_button.x + 10, self.add_layer_button.y + 5),
                  WHITE)

        # Draw Move Up and Move Down Buttons
        pygame.draw.rect(surface, DARK_GREY, self.up_button)
        draw_text(surface, "Up", (self.up_button.x + 10, self.up_button.y + 5), WHITE)
        pygame.draw.rect(surface, DARK_GREY, self.down_button)
        draw_text(surface, "Down", (self.down_button.x + 10, self.down_button.y + 5), WHITE)

        # Draw Layers List
        for index, layer_name in enumerate(reversed(self.layers.keys())):
            layer = self.layers[layer_name]
            layer_rect = pygame.Rect(self.rect.x + 10, self.rect.y + 100 + index * (self.button_height + 10),
                                     self.rect.width - 20, self.button_height)
            color = DARK_GREY if self.active_layer == layer_name else LIGHT_GREY
            pygame.draw.rect(surface, color, layer_rect)
            draw_text(surface, layer_name, (layer_rect.x + 5, layer_rect.y + 5),
                      WHITE if self.active_layer == layer_name else BLACK)
            # Draw visibility toggle
            vis_rect = pygame.Rect(layer_rect.x + layer_rect.width - 25, layer_rect.y + 5, 20, 20)
            pygame.draw.rect(surface, GREEN if layer.visible else DARK_GREY, vis_rect)
            visibility_icon = "V" if layer.visible else "X"
            draw_text(surface, visibility_icon,
                      (vis_rect.x + 5, vis_rect.y + 2), WHITE)

    def to_dict(self):
        return {
            'layers': [layer.to_dict() for layer in self.layers.values()],
            'active_layer': self.active_layer
        }

    def from_dict(self, data):
        self.layers.clear()
        for layer_data in data['layers']:
            layer = Layer.from_dict(layer_data)
            self.layers[layer.name] = layer
        self.active_layer = data.get('active_layer', 'Background')

# Properties Panel Class
class PropertiesPanel:
    def __init__(self, rect):
        self.rect = rect
        self.selected_object = None
        self.stroke_width = 2
        self.opacity = 255  # Not implemented in VectorObject

    def handle_event(self, event):
        if self.selected_object:
            if event.type == KEYDOWN:
                if event.key == K_UP:
                    self.stroke_width += 1
                    self.selected_object.properties['stroke_width'] = self.stroke_width
                elif event.key == K_DOWN:
                    self.stroke_width = max(1, self.stroke_width - 1)
                    self.selected_object.properties['stroke_width'] = self.stroke_width
                elif event.key == K_LEFT:
                    # Placeholder for opacity or other properties
                    pass
                elif event.key == K_RIGHT:
                    pass

    def render(self, surface):
        # Draw properties panel background
        pygame.draw.rect(surface, GREY, self.rect)

        # Display properties of the selected object
        if self.selected_object:
            draw_text(surface, f"Selected: {self.selected_object.type}", (self.rect.x + 10, self.rect.y + 10),
                      BIG_FONT)
            draw_text(surface, f"Stroke Width: {self.stroke_width}", (self.rect.x + 10, self.rect.y + 50))
            draw_text(surface, "Use Up/Down arrows to adjust", (self.rect.x + 10, self.rect.y + 80))
            # Additional properties can be added here
        else:
            draw_text(surface, "No object selected", (self.rect.x + 10, self.rect.y + 10),
                      BIG_FONT)

# Canvas Class
class Canvas:
    def __init__(self, rect, layers, history_manager, toolbar):
        self.rect = rect
        self.layers = layers
        self.history_manager = history_manager
        self.toolbar = toolbar
        self.current_tool = TOOL_SELECT
        self.drawing = False
        self.start_pos = None
        self.current_obj = None
        self.selected_obj = None
        self.dragging = False
        self.offset = (0, 0)

    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN:
            pos = event.pos
            if not self.rect.collidepoint(pos):
                return
            canvas_pos = get_mouse_pos_canvas(pos)
            if self.toolbar.current_tool == TOOL_SELECT:
                self.select_object(canvas_pos)
                if self.selected_obj:
                    self.dragging = True
                    obj_pos = self.get_object_position(self.selected_obj)
                    self.offset = (canvas_pos[0] - obj_pos[0], canvas_pos[1] - obj_pos[1])
            else:
                self.drawing = True
                self.start_pos = canvas_pos
                self.create_new_object(canvas_pos)

        elif event.type == MOUSEBUTTONUP:
            if self.drawing:
                self.drawing = False
                self.current_obj = None
                self.history_manager.save_state(self.layers)
            if self.dragging:
                self.dragging = False
                self.history_manager.save_state(self.layers)

        elif event.type == MOUSEMOTION:
            if self.drawing and self.current_tool != TOOL_SELECT:
                self.update_drawing(get_mouse_pos_canvas(event.pos))
            if self.dragging and self.selected_obj:
                self.move_object(get_mouse_pos_canvas(event.pos))

    def select_object(self, pos):
        # Iterate from topmost layer to bottom
        for layer in reversed(self.layers.values()):
            if not layer.visible:
                continue
            for obj in reversed(layer.objects):
                if obj.is_clicked(pos):
                    if self.selected_obj:
                        self.selected_obj.selected = False
                    self.selected_obj = obj
                    obj.selected = True
                    return
        # If no object is clicked
        if self.selected_obj:
            self.selected_obj.selected = False
        self.selected_obj = None

    def move_object(self, pos):
        obj_pos = self.get_object_position(self.selected_obj)
        new_pos = (pos[0] - self.offset[0], pos[1] - self.offset[1])
        if self.selected_obj.type == 'line':
            dx = new_pos[0] - obj_pos[0]
            dy = new_pos[1] - obj_pos[1]
            self.selected_obj.properties['start_pos'] = (self.selected_obj.properties['start_pos'][0] + dx,
                                                        self.selected_obj.properties['start_pos'][1] + dy)
            self.selected_obj.properties['end_pos'] = (self.selected_obj.properties['end_pos'][0] + dx,
                                                      self.selected_obj.properties['end_pos'][1] + dy)
        elif self.selected_obj.type in ['rectangle', 'ellipse']:
            self.selected_obj.properties['start_pos'] = new_pos
        elif self.selected_obj.type == 'circle':
            self.selected_obj.properties['center'] = new_pos
        elif self.selected_obj.type == 'freehand':
            # Basic implementation: shift all points
            dx = pos[0] - self.selected_obj.properties['points'][0][0] - self.offset[0]
            dy = pos[1] - self.selected_obj.properties['points'][0][1] - self.offset[1]
            self.selected_obj.properties['points'] = [(x + dx, y + dy) for (x, y) in self.selected_obj.properties['points']]
        elif self.selected_obj.type == 'text':
            self.selected_obj.properties['position'] = new_pos
        elif self.selected_obj.type == 'polygon':
            dx = new_pos[0] - obj_pos[0]
            dy = new_pos[1] - obj_pos[1]
            self.selected_obj.properties['points'] = [(x + dx, y + dy) for (x, y) in self.selected_obj.properties['points']]

    def get_object_position(self, obj):
        if obj.type == 'line':
            return obj.properties['start_pos']
        elif obj.type in ['rectangle', 'ellipse']:
            return obj.properties['start_pos']
        elif obj.type == 'circle':
            return obj.properties['center']
        elif obj.type == 'freehand':
            return obj.properties['points'][0]
        elif obj.type == 'text':
            return obj.properties['position']
        elif obj.type == 'polygon':
            return obj.properties['points'][0]
        return (0, 0)

    def create_new_object(self, pos):
        props = {
            'stroke_color': self.toolbar.current_stroke_color,
            'stroke_width': self.toolbar.stroke_width,
            'fill': self.toolbar.fill_enabled,
            'fill_color': self.toolbar.current_fill_color
        }
        tool = self.toolbar.current_tool
        if tool == TOOL_LINE:
            props['start_pos'] = pos
            props['end_pos'] = pos
            obj = VectorObject('line', props)
        elif tool == TOOL_RECT:
            props['start_pos'] = pos
            props['width'] = 0
            props['height'] = 0
            obj = VectorObject('rectangle', props)
        elif tool == TOOL_CIRCLE:
            props['center'] = pos
            props['radius'] = 0
            obj = VectorObject('circle', props)
        elif tool == TOOL_ELLIPSE:
            props['start_pos'] = pos
            props['width'] = 0
            props['height'] = 0
            obj = VectorObject('ellipse', props)
        elif tool == TOOL_FREEHAND:
            props['points'] = [pos]
            obj = VectorObject('freehand', props)
        elif tool == TOOL_TEXT:
            text = self.get_text_input(pos)
            if text:
                props['text'] = text
                props['position'] = pos
                obj = VectorObject('text', props)
            else:
                return
        elif tool == TOOL_POLYGON:
            props['points'] = [pos]
            obj = VectorObject('polygon', props)
        else:
            obj = None

        if obj:
            self.layers[self.layers.active_layer].objects.append(obj)
            self.current_obj = obj

    def update_drawing(self, pos):
        tool = self.toolbar.current_tool
        if tool == TOOL_LINE:
            self.current_obj.properties['end_pos'] = pos
        elif tool == TOOL_RECT:
            width = pos[0] - self.start_pos[0]
            height = pos[1] - self.start_pos[1]
            self.current_obj.properties['width'] = width
            self.current_obj.properties['height'] = height
        elif tool == TOOL_CIRCLE:
            radius = int(((pos[0] - self.current_obj.properties['center'][0])**2 +
                          (pos[1] - self.current_obj.properties['center'][1])**2)**0.5)
            self.current_obj.properties['radius'] = radius
        elif tool == TOOL_ELLIPSE:
            width = pos[0] - self.start_pos[0]
            height = pos[1] - self.start_pos[1]
            self.current_obj.properties['width'] = width
            self.current_obj.properties['height'] = height
        elif tool == TOOL_FREEHAND:
            self.current_obj.properties['points'].append(pos)
        elif tool == TOOL_POLYGON:
            self.current_obj.properties['points'].append(pos)

    def get_text_input(self, pos):
        input_box = pygame.Rect(pos[0] + TOOLBAR_WIDTH, pos[1], 200, 30)
        pygame.draw.rect(screen, WHITE, input_box)
        pygame.draw.rect(screen, BLACK, input_box, 2)
        pygame.display.flip()
        user_text = ''
        done = False
        while not done:
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_RETURN:
                        done = True
                        break
                    elif event.key == K_BACKSPACE:
                        user_text = user_text[:-1]
                    else:
                        user_text += event.unicode
                elif event.type == QUIT:
                    pygame.quit()
                    sys.exit()
            # Redraw input box with current text
            pygame.draw.rect(screen, WHITE, input_box)
            pygame.draw.rect(screen, BLACK, input_box, 2)
            draw_text(screen, user_text, (input_box.x + 5, input_box.y + 5))
            pygame.display.flip()
        return user_text

    def render(self, surface):
        # Draw canvas background
        pygame.draw.rect(surface, WHITE, self.rect)

        # Draw all layers
        for layer in self.layers.values():
            layer.draw(surface.subsurface(self.rect))

    def save_to_history(self):
        self.history_manager.save_state(self.layers)

# Main Application Class
class VectorLayersApp:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("VectorLayers.py - Enhanced")
        self.clock = pygame.time.Clock()
        self.running = True

        # Initialize UI Components
        self.toolbar_rect = pygame.Rect(0, 0, TOOLBAR_WIDTH, SCREEN_HEIGHT)
        self.layerpanel_rect = pygame.Rect(SCREEN_WIDTH - LAYERPANEL_WIDTH - PROPERTIES_WIDTH, 0, LAYERPANEL_WIDTH, SCREEN_HEIGHT)
        self.properties_rect = pygame.Rect(SCREEN_WIDTH - PROPERTIES_WIDTH, 0, PROPERTIES_WIDTH, SCREEN_HEIGHT)
        self.canvas_rect = pygame.Rect(TOOLBAR_WIDTH, 0, CANVAS_WIDTH, CANVAS_HEIGHT)

        self.toolbar = Toolbar(self.toolbar_rect)
        self.layerpanel = LayerPanel(self.layerpanel_rect)
        self.properties_panel = PropertiesPanel(self.properties_rect)
        self.history_manager = HistoryManager()
        self.canvas = Canvas(self.canvas_rect, self.layerpanel.layers, self.history_manager, self.toolbar)

        # Initialize history
        self.history_manager.save_state(self.layerpanel.layers)

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.render()
        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            # Global Quit Event
            if event.type == QUIT:
                self.running = False

            # Handle Keyboard Shortcuts
            if event.type == KEYDOWN:
                if event.mod & pygame.KMOD_CTRL:
                    if event.key == K_z:
                        if event.mod & pygame.KMOD_SHIFT:
                            self.history_manager.redo(self.layerpanel.layers)
                        else:
                            self.history_manager.undo(self.layerpanel.layers)
                    elif event.key == K_s:
                        self.save_project()
                    elif event.key == K_o:
                        self.load_project()
                    elif event.key == K_e:
                        self.export_image()

            # Pass event to Toolbar
            self.toolbar.handle_event(event)

            # Pass event to Layer Panel
            self.layerpanel.handle_event(event)

            # Pass event to Canvas
            self.canvas.handle_event(event)

            # Pass event to Properties Panel
            self.properties_panel.handle_event(event)

            # Update selected object in Properties Panel
            if event.type == MOUSEBUTTONDOWN:
                if self.canvas.selected_obj:
                    self.properties_panel.selected_object = self.canvas.selected_obj
                    self.properties_panel.stroke_width = self.canvas.selected_obj.properties.get('stroke_width', 2)
                else:
                    self.properties_panel.selected_object = None

        # Update current tool
        self.canvas.current_tool = self.toolbar.current_tool

    def render(self):
        # Fill Background
        self.screen.fill(LIGHT_GREY)

        # Render Toolbar
        self.toolbar.render(self.screen)

        # Render Layer Panel
        self.layerpanel.render(self.screen)

        # Render Properties Panel
        self.properties_panel.render(self.screen)

        # Render Canvas
        self.canvas.render(self.screen)

        # Update Display
        pygame.display.flip()

    def save_project(self):
        project_data = self.layerpanel.to_dict()
        with open('project.json', 'w') as f:
            json.dump(project_data, f)
        print("Project saved to project.json")

    def load_project(self):
        try:
            with open('project.json', 'r') as f:
                project_data = json.load(f)
            self.layerpanel.from_dict(project_data)
            self.history_manager.save_state(self.layerpanel.layers)
            print("Project loaded from project.json")
        except Exception as e:
            print(f"Failed to load project: {e}")

    def export_image(self):
        export_surface = pygame.Surface((CANVAS_WIDTH, CANVAS_HEIGHT))
        export_surface.fill(WHITE)
        for layer in self.layerpanel.layers.values():
            layer.draw(export_surface)
        pygame.image.save(export_surface, 'export.png')
        print("Canvas exported to export.png")

# Run the Application
if __name__ == "__main__":
    app = VectorLayersApp()
    app.run()
