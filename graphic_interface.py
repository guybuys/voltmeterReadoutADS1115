import pygame
from pygame.locals import *
from colors import SCOPE_BG, BLACK, GREEN
from collections import deque  # for ScopeSignal class


class Slider:
    def __init__(self, x, y, width, height, min_value, max_value, initial_value, steps, slot_color=pygame.Color(200, 200, 200),
                 slider_color=pygame.Color(100, 100, 100)):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value
        self.prev_value = initial_value
        self.steps = steps
        self.step_size = (max_value - min_value) / (steps - 1)
        self.dragging = False
        self.prev_mouse_x = 0  # Previous mouse x position
        self.slider_pos = int(
            (self.value - self.min_value) / (self.max_value - self.min_value) * (self.width - 20)) + self.x
        self.slot_color = slot_color
        self.slider_color = slider_color

    def draw(self, screen):
        # Draw slider track
        pygame.draw.rect(screen, self.slot_color, (self.x, self.y + self.height // 3, self.width, self.height // 3))

        # Ensure slider position stays within bounds
        self.slider_pos = max(self.x, min(self.x + self.width - 20, self.slider_pos))

        # Draw slider button
        pygame.draw.rect(screen, self.slider_color, (self.slider_pos, self.y, 20, self.height))

    def update_value(self, new_value):
        # Quantize the value to the nearest step
        quantized_value = round(new_value / self.step_size) * self.step_size
        # Update the value and ensure it stays within bounds
        self.value = max(self.min_value, min(self.max_value, quantized_value))

    def increase_value(self):
        # Increase the value by one step if within range
        new_value = min(self.max_value, self.value + self.step_size)
        if new_value != self.value:
            self.update_value(new_value)
            self.update_slider_position()

    def decrease_value(self):
        # Decrease the value by one step if within range
        new_value = max(self.min_value, self.value - self.step_size)
        if new_value != self.value:
            self.update_value(new_value)
            self.update_slider_position()

    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            slider_rect = pygame.Rect(self.slider_pos, self.y, 20, self.height)
            if slider_rect.collidepoint(mouse_pos):
                self.dragging = True
                self.prev_mouse_x = mouse_pos[0]  # Store previous mouse x position
        elif event.type == MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == MOUSEMOTION:
            if self.dragging:
                mouse_x, _ = event.pos
                delta_x = mouse_x - self.prev_mouse_x  # Change in mouse x position
                self.prev_mouse_x = mouse_x  # Update previous mouse x position

                # Calculate new slider position
                self.slider_pos += delta_x
                self.slider_pos = max(self.x, min(self.x + self.width - 20, self.slider_pos))

                # Calculate new value based on slider position
                new_value = ((self.slider_pos - self.x) / (self.width - 20)) * (self.max_value - self.min_value) + self.min_value
                self.update_value(new_value)

                # Quantize the slider position to the nearest step
                quantized_value = round(self.value / self.step_size) * self.step_size
                self.update_value(quantized_value)
                self.update_slider_position()
        elif event.type == KEYDOWN and pygame.key.get_focused():
            if self.is_mouse_over():
                if event.key == K_LEFT:
                    self.decrease_value()
                elif event.key == K_RIGHT:
                    self.increase_value()

    def is_mouse_over(self):
        # Check if the mouse is over the slider
        mouse_pos = pygame.mouse.get_pos()
        return self.x <= mouse_pos[0] <= self.x + self.width and self.y <= mouse_pos[1] <= self.y + self.height

    def get_value(self):
        return self.value

    def is_moved(self):
        if self.value != self.prev_value:
            self.prev_value = self.value
            return True
        return False

    def increase_value(self):
        # Increase the value by one step if within range
        new_value = min(self.max_value, self.value + self.step_size)
        if new_value != self.value:
            self.update_value(new_value)
            self.update_slider_position()

    def decrease_value(self):
        # Decrease the value by one step if within range
        new_value = max(self.min_value, self.value - self.step_size)
        if new_value != self.value:
            self.update_value(new_value)
            self.update_slider_position()

    def update_slider_position(self):
        # Update the slider position based on the current value
        self.slider_pos = int(
            (self.value - self.min_value) / (self.max_value - self.min_value) * (self.width - 20)) + self.x

class PushButtonPic:
    def __init__(self, x, y, on_image, off_image, text, font=None, font_size=20, font_color=BLACK,callback=None):
        self.x = x
        self.y = y
        self.on_image = pygame.image.load(on_image)
        self.off_image = pygame.image.load(off_image)
        self.image = self.off_image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.text = text
        self.font = pygame.font.SysFont(font, font_size) if font else pygame.font.Font(None, font_size)
        self.font_color = font_color
        self.state = False
        self.callback = callback

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        # Render and draw text on button
        text_surface = self.font.render(self.text, True, self.font_color)
        text_rect = text_surface.get_rect(center=(self.x + self.image.get_width() / 2, self.y +
                                                  (self.image.get_height() - self.font.get_height() / 2) / 2))
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos):
                self.state = not self.state
                if self.state:
                    self.image = self.on_image
                else:
                    self.image = self.off_image
                if self.callback:
                    self.callback(self.state)

    def toggle(self):
        self.state = not self.state
        if self.state:
            self.image = self.on_image
        else:
            self.image = self.off_image

    def set_state(self, state):
        self.state = state
        if self.state:
            self.image = self.on_image
        else:
            self.image = self.off_image

    def get_state(self):
        return self.state


class PushButton:
    def __init__(self, x, y, width, height, text, on_color, off_color, font=None, font_size=20, callback=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.on_color = on_color
        self.off_color = off_color
        self.font = pygame.font.SysFont(font, font_size) if font else pygame.font.Font(None, font_size)
        self.state = False  # Initial state
        self.callback = callback

    def draw(self, screen):
        # Draw button outline
        pygame.draw.rect(screen, (0, 0, 0), (self.x, self.y, self.width, self.height), 2)

        # Draw button background based on state
        color = self.on_color if self.state else self.off_color
        pygame.draw.rect(screen, color, (self.x + 2, self.y + 2, self.width - 4, self.height - 4))

        # Render and draw text on button
        text_surface = self.font.render(self.text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(self.x + self.width / 2, self.y + self.height / 2))
        screen.blit(text_surface, text_rect)

    def update(self):
        # Implement button update logic here
        pass

    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if self.x < mouse_pos[0] < self.x + self.width and self.y < mouse_pos[1] < self.y + self.height:
                self.state = not self.state
                if self.callback:
                    self.callback(self.state)

    def toggle(self):
        self.state = not self.state

    def set(self, state):
        self.state = state

    def get(self):
        if self.state:
            return "1"
        return "0"


class TextField:
    def __init__(self, x, y, width, height, font=None, font_size=20, editable=False, rect_color=(200, 200, 200),
                 background_color=(100, 200, 0), active_text_color=(0, 0, 0), passive_text_color=(64, 64, 64),
                 callback=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.value = 0.0  # Initial value
        self.prev_valid_value = 0.0
        self.editable = editable  # Whether the value is editable
        # """
        if font:
            self.font = pygame.font.Font(font, font_size)
        else:
            self.font = pygame.font.SysFont(font, font_size)
        # """
        # self.font = pygame.font.SysFont(font, font_size) if font else pygame.font.Font(None, font_size)
        self.active = False
        self.text = ""
        self.rect_color = rect_color
        self.active_text_color = active_text_color
        self.passive_text_color = passive_text_color
        self.background_color = background_color
        self.callback = callback

    def draw(self, screen):
        # Draw the text field rectangle
        pygame.draw.rect(screen, self.background_color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, self.rect_color, (self.x, self.y, self.width, self.height), 2)

        # Render the text
        if self.active:
            color = self.active_text_color
        else:
            color = self.passive_text_color
        # text_surface = self.font.render(self.text, True, color)
        custom_font = self.font
        text_surface = custom_font.render(self.text, True, color)

        text_rect = text_surface.get_rect(center=(self.x + self.width / 2, self.y + self.height / 2))
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN:
            if self.is_mouse_over(pygame.mouse.get_pos()):
                self.active = True
            else:
                self.active = False
        elif event.type == KEYDOWN:
            if self.active:
                if event.key == K_BACKSPACE:
                    self.text = self.text[:-1]
                elif event.key == K_RETURN:
                    try:
                        new_value = float(self.text)
                        if new_value != self.value:
                            self.value = new_value
                            self.prev_valid_value = new_value  # Update previous valid value
                            # Notify main loop about the new value
                            if self.callback:
                                self.callback(self.value)
                    except ValueError:
                        # If the value is not a valid float, restore the previous valid value
                        self.text = str(self.prev_valid_value)
                    """
                    try:
                        self.value = float(self.text)
                    except ValueError:
                        pass
                    self.active = False
                    """
                else:
                    self.text += event.unicode

    def change_colors(self, active_text_color=None, passive_text_color=None, background_color=None):
        if active_text_color:
            self.active_text_color = active_text_color
        if passive_text_color:
            self.passive_text_color = passive_text_color
        if background_color:
            self.background_color = background_color

    def update(self):
        pass

    def is_mouse_over(self, pos):
        return self.x <= pos[0] <= self.x + self.width and self.y <= pos[1] <= self.y + self.height

    def get_value(self):
        return self.value

    def set_value(self, value):
        self.value = value
        self.text = str(value)

    def is_editable(self):
        return self.editable

    def set_editable(self, editable):
        self.editable = editable


class TerminalWindow:
    def __init__(self, x, y, width, height, background_color=pygame.Color('white')):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.background_color = background_color
        self.text_lines = []  # Buffer for terminal text
        self.font = pygame.font.SysFont('Consolas', 20)  # You can adjust the font size as needed

    def draw(self, screen):
        pygame.draw.rect(screen, self.background_color, (self.x, self.y, self.width, self.height))
        y_offset = self.y
        for line in self.text_lines:
            text_surface = self.font.render(line['text'], True, line['color'])
            screen.blit(text_surface, (self.x + 5, y_offset + 5))  # Adjust the padding as needed
            y_offset += text_surface.get_height() + 5  # Adjust the spacing between lines

    def add_message(self, message, color=pygame.Color('black')):
        self.text_lines.append({'text': message, 'color': color})
        # Trim excess lines if necessary to fit within the window
        while len(self.text_lines) * (self.font.get_height() + 5) > self.height:
            self.text_lines.pop(0)


class Label:
    def __init__(self, x, y, text, font_size=24, color=(255, 255, 255), font=None):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.font_size = font_size
        # self.font = pygame.font.SysFont(font, font_size) if font else pygame.font.Font(None, font_size)
        if font:
            self.font = pygame.font.Font(font, font_size)
        else:
            self.font = pygame.font.SysFont(font, font_size)

        self.rendered_text = self.font.render(text, True, color)

    def set_text(self, text):
        self.text = text
        self.rendered_text = self.font.render(text, True, self.color)

    def draw(self, screen):
        screen.blit(self.rendered_text, (self.x, self.y))


class Scope:
    def __init__(self, x, y, width, height, bg_color=SCOPE_BG, dev_per_quad_x=5, dev_per_quad_y=4):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.dev_per_quad_x = dev_per_quad_x
        self.dev_per_quad_y = dev_per_quad_y
        self.time_scale = 0
        self.delta_t = None
        self.signals = []

    def update(self, screen):
        self.draw(screen)

    def set_time_scale(self, time_scale):
        self.time_scale = time_scale

    def draw(self, screen):
        # draw background
        pygame.draw.rect(screen, self.bg_color, (self.x, self.y, self.width, self.height))

        # draw signal(s)
        self.draw_signals(screen)

        # draw raster
        self.draw_raster(screen)

    def draw_raster(self, screen, raster_color=BLACK):
        # draw center lines
        pygame.draw.line(screen, raster_color, (self.width / 2 + self.x, self.y),
                         (self.width / 2 + self.x, self.y + self.height), 2)
        pygame.draw.line(screen, raster_color, (self.x, self.height / 2 + self.y),
                         (self.x + self.width, self.height / 2 + self.y), 2)

        y_start = (self.width / 2 + self.x - 3, self.width / 2 + self.x + 4,
                   self.height / (5 * (2 * self.dev_per_quad_y)), self.height / (2 * self.dev_per_quad_y))
        x_start = (self.height / 2 + self.y - 3, self.height / 2 + self.y + 4,
                   self.width / (5 * (2 * self.dev_per_quad_x)), self.width / (2 * self.dev_per_quad_x))

        for i in range(5 * (2 * self.dev_per_quad_y)):
            pygame.draw.line(screen, raster_color, (y_start[0], self.y + y_start[2] * i),
                             (y_start[1], self.y + y_start[2] * i), 1)

        for i in range(5 * (2 * self.dev_per_quad_x)):
            pygame.draw.line(screen, raster_color, (self.x + x_start[2] * i, x_start[0]),
                             (self.x + x_start[2] * i, x_start[1]), 1)

        for i in range(2 * self.dev_per_quad_y):
            pygame.draw.line(screen, raster_color, (self.x, self.y + y_start[3] * i),
                             (self.x + self.width, self.y + y_start[3] * i), 1)
        for i in range(2 * self.dev_per_quad_x):
            pygame.draw.line(screen, raster_color, (self.x + x_start[3] * i, self.y),
                             (self.x + x_start[3] * i, self.y + self.height), 1)

    def y_val_2_pixel(self, signal, y):
        return round(-y / signal.val_per_division * self.height / (2 * self.dev_per_quad_y) - signal.offset *
                     self.height / (2 * self.dev_per_quad_y) + self.y + self.height / 2)

    def draw_signals(self, screen):
        for idx, signal in enumerate(self.signals):
            if self.time_scale > 0:
                min_nr = 2 * 2 ** self.time_scale
            else:
                min_nr = 2
            if len(signal.values) >= min_nr:
                # Draw lines between data points
                if self.time_scale == 0:
                    nr_of_steps = min(self.width, len(signal.values))
                    iterator_scale = 1
                    zoom_scale = 1
                elif self.time_scale > 0:
                    nr_of_steps = min(self.width, len(signal.values)) // 2 ** self.time_scale
                    iterator_scale = 2 ** self.time_scale
                    zoom_scale = 1
                else:  # self.time_scale < 0
                    nr_of_steps = min(self.width // 2 ** -self.time_scale, len(signal.values))
                    iterator_scale = 1
                    zoom_scale = 2 ** -self.time_scale

                for j in range(1, nr_of_steps):  #
                    i = j * iterator_scale
                    y0 = self.y_val_2_pixel(signal, float(signal.values[-i]))
                    y1 = self.y_val_2_pixel(signal, float(signal.values[-(i + 1)]))
                    start_point = (self.x + self.width - i * zoom_scale, int(y0))
                    end_point = (self.x + self.width - i * zoom_scale - 1, int(y1))
                    if not (start_point[1] < self.y or start_point[1] > (self.y + self.height) and
                            end_point[1] < self.y or end_point[1] > (self.y + self.height)):
                        if start_point[1] < self.y:
                            start_point = (start_point[0], self.y)
                        if start_point[1] > (self.y + self.height):
                            start_point = (start_point[0], self.y + self.height)
                        if end_point[1] < self.y:
                            end_point = (end_point[0], self.y)
                        if end_point[1] > (self.y + self.height):
                            end_point = (end_point[0], self.y + self.height)

                        pygame.draw.line(screen, signal.color, start_point, end_point, 4)

    def add_signal(self, offset, val_per_division=100, color=GREEN):
        new_signal = ScopeSignal(offset, val_per_division, color, max_length=self.width * 4)
        self.signals.append(new_signal)

    def add_data_to_signal(self, signal_index, value):
        if signal_index < len(self.signals):
            self.signals[signal_index].add_value(value)
        else:
            print("Invalid signal index")


class ScopeSignal:
    def __init__(self, offset, val_per_division, color, max_length=100):
        self.offset = offset
        self.val_per_division = val_per_division
        self.color = color
        self.values = deque(maxlen=max_length)  # Use deque with a fixed maximum length
        self.active = True

    def add_value(self, value):
        self.values.append(value)


class SerialPlotter:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        # Add attributes for data visualization

    def draw(self, screen):
        # Implement serial plotter drawing logic here
        pass

    def update(self):
        # Implement serial plotter update logic here
        pass
