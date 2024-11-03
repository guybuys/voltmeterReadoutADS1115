import pygame
from graphic_interface import Slider, PushButtonPic, TextField, TerminalWindow, Label, Scope
from serial_manager import SerialManager
from parameter_manager import ParameterManager
from colors import BLACK, RED, YELLOW, BLUE, GREEN, MAGENTA, GRAY, BACKGROUNDCOLOR, DARKGREEN, SCREENGREEN
import os
import json

CHANNEL_COLORS = [GREEN, YELLOW, RED, MAGENTA]
CHANNEL_NAMES = ["Jef", "Du Bin", "Ward", "Schoeters"]

# Functie om parameters uit een bestand te lezen
def read_parameters(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)


# Functie om parameters naar een bestand te schrijven
def write_parameters(file_path, parameters):
    with open(file_path, 'w') as file:
        json.dump(parameters, file, indent=4)


# Get the current directory of the Python file
current_dir = os.path.dirname(__file__)

# Specify the name of the folder containing images
image_folder = 'images'

# Construct the path to the image files
on_image_path = os.path.join(current_dir, image_folder, 'SSL_Button_ON.png')
off_image_path = os.path.join(current_dir, image_folder, 'SSL_Button_OFF.png')

# Set the path to your font file
lcd_font_path = "C:/Users/guy.buys/PycharmProjects/SerialCommunicationDisplay/fonts/LCD-Solid/LCD_Solid.ttf"
led_font_path = "C:/Users/guy.buys/PycharmProjects/SerialCommunicationDisplay/fonts/ds_digital/DS-DIGII.TTF"
# ls7_font_path = "C:/Users/guy.buys/PycharmProjects/SerialCommunicationDisplay/fonts/Segment7/Segment7Standard.otf"
# dymo_font_path = ("C:/Users/guy.buys/PycharmProjects/SerialCommunicationDisplay/fonts/dymo_grunge_bubble"
#                  "/Dymo Grunge Bubble.ttf")
sharpie_font_path = ("C:/Users/guy.buys/PycharmProjects/SerialCommunicationDisplay/fonts/permanent-marker-font"
                     "/PermanentMarker-x99j.ttf")
serial_connected = False

# Define constants for window dimensions
# WINDOW_WIDTH = 1120
# WINDOW_HEIGHT = 800

# Define constants for interface
PID_TARGET_OFFSET = 1
TOLERANCE_RANGE = 1


def get_param_value(name, pm, ttx, trx):
    parameter_name, parameter_value = pm.get_parameter(name)
    ttx.add_message(name, color=DARKGREEN)
    trx.add_message(parameter_name + " " + parameter_value, color=DARKGREEN)
    try:
        return float(parameter_value)
    except ValueError:
        return float('nan')


def create_slider_group(origin_x, origin_y, label_text, slider_min, slider_max, slider_initial, slider_steps, font_path, font_size, label_color, slot_color, slider_color, text_field_rect_color, text_field_bg_color, text_field_passive_color, text_field_font_path, text_field_font_size):
    label = Label(origin_x, origin_y, label_text, font=font_path, font_size=font_size, color=label_color)
    slider = Slider(origin_x, origin_y + 45, 64, 30, slider_min, slider_max, slider_initial, slider_steps, slot_color=slot_color, slider_color=slider_color)
    text_field = TextField(origin_x + 100, origin_y + 35, 100, 40, rect_color=text_field_rect_color, background_color=text_field_bg_color, passive_text_color=text_field_passive_color, font=text_field_font_path, font_size=text_field_font_size)
    return label, slider, text_field


def main():
    pygame.init()
    # -----
    # Get display information
    display_info = pygame.display.Info()

    # Get maximum resolution
    max_resolution = (display_info.current_w, display_info.current_h)

    # 150% => (1280, 720) event.w = 1280, event.h = 649
    # 125% => (1536, 864) event.w = 1536, event.h = 793
    # 100% => (1920, 1080) event.w = 1920, event.h = 1009

    print("Maximum resolution:", max_resolution)
    window_width, window_height = max_resolution

    window_height = round(window_height * .9)

    serial_manager = SerialManager()
    parameter_manager = ParameterManager(serial_manager)
    # Open serial connection
    parameter_manager.open_serial_connection()

    pygame.display.set_caption("Arduino Serial Interface " + parameter_manager.get_serial_connection_name())

    # Set screen to maximum resolution (90% in height)
    screen = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE)

    # Bestandspad voor gain and offset parameters
    parameters_file_path = 'parameters.json'

    # Lees de parameters bij het starten van het programma
    parameters = read_parameters(parameters_file_path)

    serial_manager = SerialManager()
    parameter_manager = ParameterManager(serial_manager)
    # Open serial connection
    parameter_manager.open_serial_connection()

    pygame.display.set_caption("Arduino Serial Interface " + parameter_manager.get_serial_connection_name())

    clock = pygame.time.Clock()
    running = True
    scope = False

    # Initialize adc variables
    adc0 = 0
    adc1 = 0
    adc2 = 0
    adc3 = 0

    # callback functions
    def button_callback(state):
        if state:
            value = 1
            switch_scope_run.set_state(True)
        else:
            value = 0
        terminal_tx_window.add_message("meter " + str(value), color=DARKGREEN)
        parameter_manager.set_parameter("meter", value)

    def button_fast_callback(state):
        if state:
            my_scope.set_time_scale(-1)
        else:
            my_scope.set_time_scale(0)

    def rate_callback(value):
        terminal_tx_window.add_message("rate " + str(value), color=DARKGREEN)
        parameter_manager.set_parameter("rate", value)

    # Callback-functie voor tekstvelden
    def parameter_callback(name, value, parameters, file_path):
        parameters[name] = value
        write_parameters(file_path, parameters)
        terminal_tx_window.add_message(f"{name} {value}", color=GREEN)
        # parameter_manager.set_parameter(name, value)

    # Create UI elements
    switch_on = PushButtonPic(50, 25, on_image_path, off_image_path, "meter", callback=button_callback)

    switch_scope_run = PushButtonPic(1200, 800, on_image_path, off_image_path, "Scope")

    switch_scope_speed = PushButtonPic(1300, 800, on_image_path, off_image_path, "Time x2",
                                       callback=button_fast_callback)

    label_adc0 = Label(170, 2, 'ADC0', font=sharpie_font_path, font_size=28, color=(0, 0, 0))
    label_adc1 = Label(370, 2, 'ADC1', font=sharpie_font_path, font_size=28, color=(0, 0, 0))
    label_adc2 = Label(570, 2, 'ADC2', font=sharpie_font_path, font_size=28, color=(0, 0, 0))
    label_adc3 = Label(770, 2, 'ADC3', font=sharpie_font_path, font_size=28, color=(0, 0, 0))

    label_res0 = Label(170, 302, CHANNEL_NAMES[0], font=sharpie_font_path, font_size=28, color=CHANNEL_COLORS[0])
    label_res1 = Label(370, 302, CHANNEL_NAMES[1], font=sharpie_font_path, font_size=28, color=CHANNEL_COLORS[1])
    label_res2 = Label(570, 302, CHANNEL_NAMES[2], font=sharpie_font_path, font_size=28, color=CHANNEL_COLORS[2])
    label_res3 = Label(770, 302, CHANNEL_NAMES[3], font=sharpie_font_path, font_size=28, color=CHANNEL_COLORS[3])

    # (Tijdelijke) labels voor gain en rate
    '''label_gain = Label(60, 390, 'Gain', font=sharpie_font_path, font_size=28, color=(0, 0, 0))
    slider_gain = Slider(50, 435, 64, 30, 0, 5, 1, 6,  # 6 steps from 0 to 5
                         slot_color=BLACK, slider_color=GRAY)
    text_field_gain = TextField(150, 425, 100, 40, rect_color=BLACK, background_color=BLACK,
                                passive_text_color=RED, font=led_font_path, font_size=40)

    '''

    # Voorbeeld van het aanmaken van de objecten met een oorsprong
    label_gain, slider_gain, text_field_gain = create_slider_group(
        50, 100, 'Gain', 0, 5, 1, 6, sharpie_font_path,
        28, (0, 0, 0), BLACK, GRAY, BLACK, BLACK, RED, led_font_path, 40
    )

    label_rate, slider_rate, text_field_rate = create_slider_group(
        50, 200, 'Rate', 0, 7, 4, 8, sharpie_font_path,
        28, (0, 0, 0), BLACK, GRAY, BLACK, BLACK, RED, led_font_path, 40
    )

    '''
    label_rate = Label(60, 520, 'Rate', font=sharpie_font_path, font_size=28, color=(0, 0, 0))
    slider_rate = Slider(50, 575, 64, 30, 0, 7, 4, 8,  # 8 steps from 0 to 7
                     slot_color=BLACK, slider_color=GRAY)
    text_field_rate = TextField(200, 525, 100, 40, rect_color=BLACK, background_color=BLACK,
                                passive_text_color=RED, font=led_font_path, font_size=40)
    '''

    # Create a dictionary to store ADC text fields
    adc_text_fields = {}
    adc_x = 150
    adc_y = 40
    adc_width = 120
    adc_height = 45
    adc_y_offset = 200

    # Use a loop to create and initialize each TextField instance
    for i in range(4):
        adc_name = f"adc{i}"
        adc_text_fields[adc_name] = TextField(
            adc_x + i * adc_y_offset, adc_y, adc_width, adc_height,
            rect_color=BLACK, background_color=BLACK,
            passive_text_color=RED, font=led_font_path, font_size=40
        )

    # Create a dictionary to store the result text fields
    res_text_fields = {}
    res_x = 150
    res_y = 340
    res_width = 120
    res_height = 45
    res_y_offset = 200

    # Use a loop to create and initialize each TextField instance
    for i in range(4):
        res_name = f"res{i}"
        res_text_fields[res_name] = TextField(
            res_x + i * res_y_offset, res_y, res_width, res_height,
            rect_color=BLACK, background_color=BLACK,
            passive_text_color=RED, font=led_font_path, font_size=40
        )

    # Maak de tekstvelden dynamisch aan
    lcd_x = 350
    lcd_y = 100
    lcd_a_offset = 20
    lcd_b_offset = 140
    lcd_y_offset = 50

    text_fields = {}
    for i in range(4):
        a_name = f"a{i}"
        b_name = f"b{i}"
        text_fields[a_name] = TextField(
            lcd_x + lcd_a_offset, lcd_y + i * lcd_y_offset, 100, 45,
            rect_color=(100, 200, 0), font=lcd_font_path, font_size=30,
            editable=True,
            callback=lambda value, name=a_name: parameter_callback(name, value, parameters, parameters_file_path)
        )
        text_fields[b_name] = TextField(
            lcd_x + lcd_b_offset, lcd_y + i * lcd_y_offset, 100, 45,
            rect_color=(100, 200, 0), font=lcd_font_path, font_size=30,
            editable=True,
            callback=lambda value, name=b_name: parameter_callback(name, value, parameters, parameters_file_path)
        )

    # Stel de waarden van de tekstvelden in op basis van de parameters
    for name, text_field in text_fields.items():
        text_field.set_value(parameters.get(name, 0))


    terminal_tx_window = TerminalWindow(50, 620, 500, 270, background_color=SCREENGREEN)
    terminal_rx_window = TerminalWindow(575, 620, 500, 270, background_color=SCREENGREEN)

    my_scope = Scope(1125, 20, 750, 600, dev_per_quad_x=5, dev_per_quad_y=4)
    my_scope.add_signal(offset=0, val_per_division=10, color=CHANNEL_COLORS[0])
    my_scope.add_signal(offset=-3, val_per_division=2, color=CHANNEL_COLORS[1])
    my_scope.add_signal(offset=-3, val_per_division=2, color=CHANNEL_COLORS[2])
    my_scope.add_signal(offset=-3, val_per_division=2, color=CHANNEL_COLORS[3])
    scope_frame_complete = False

    # Get values from device with parameter manager
    switch_on.set_state(get_param_value("meter", parameter_manager, terminal_tx_window, terminal_rx_window))

    '''
    slider_gain.update_value(get_param_value("gain", parameter_manager, terminal_tx_window, terminal_rx_window))
    slider_gain.update_slider_position()
    slider_rate.update_value(get_param_value("rate", parameter_manager, terminal_tx_window, terminal_rx_window))
    slider_rate.update_slider_position()
    '''

    # --------------------------
    # Define text_field_lcd
    text_field_lcd = TextField(
        lcd_x, lcd_y - 2, 320, 4 * lcd_y_offset + 1,
        rect_color=BLACK, font=lcd_font_path, font_size=30
    )

    # Drawing loop
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            switch_on.handle_event(event)
            switch_scope_run.handle_event(event)
            switch_scope_speed.handle_event(event)
            for name, text_field in text_fields.items():
                text_field.handle_event(event)
            for name, text_field in adc_text_fields.items():
                text_field.handle_event(event)
            slider_gain.handle_event(event)
            slider_rate.handle_event(event)

        text_field_gain.set_value(int(slider_gain.get_value()))
        text_field_rate.set_value(int(slider_rate.get_value()))

        screen.fill(BACKGROUNDCOLOR)
        slider_gain.draw(screen)
        slider_rate.draw(screen)
        switch_on.draw(screen)
        switch_scope_run.draw(screen)
        switch_scope_speed.draw(screen)
        label_gain.draw(screen)
        label_rate.draw(screen)
        text_field_gain.draw(screen)
        text_field_rate.draw(screen)

        label_adc0.draw(screen)
        label_adc1.draw(screen)
        label_adc2.draw(screen)
        label_adc3.draw(screen)

        label_res0.draw(screen)
        label_res1.draw(screen)
        label_res2.draw(screen)
        label_res3.draw(screen)

        for name, text_field in adc_text_fields.items():
            text_field.draw(screen)
        for name, text_field in res_text_fields.items():
            text_field.draw(screen)
        text_field_lcd.draw(screen)  # Draw text_field_lcd
        for name, text_field in text_fields.items():
            text_field.draw(screen)
        terminal_tx_window.draw(screen)
        terminal_rx_window.draw(screen)
        if scope_frame_complete:
            scope_frame_complete = False
            if switch_scope_run.get_state():
                if 'adc0' in locals():
                    my_scope.add_data_to_signal(0, adc0)
                if 'adc1' in locals():
                    my_scope.add_data_to_signal(1, adc1)
                if 'adc2' in locals():
                    my_scope.add_data_to_signal(2, adc2)
                if 'adc3' in locals():
                    my_scope.add_data_to_signal(3, adc3)
        my_scope.draw(screen)
        pygame.display.flip()

        if slider_gain.is_moved():
            slider_gain_val_str = str(int(slider_gain.get_value()))
            print("Current slider_gain value: " + slider_gain_val_str)
            parameter_manager.set_parameter("gain", slider_gain_val_str)
            terminal_tx_window.add_message("gain " + slider_gain_val_str, color=DARKGREEN)

        if slider_rate.is_moved():
            slider_rate_val_str = str(int(slider_rate.get_value()))
            print("Current slider_rate value: " + slider_rate_val_str)
            parameter_manager.set_parameter("rate", slider_rate_val_str)
            terminal_tx_window.add_message("rate " + slider_rate_val_str, color=DARKGREEN)

        update_list = parameter_manager.check_parameter_updates()
        if update_list:
            for item in update_list:
                parameter_name, parameter_value = item
                terminal_rx_window.add_message(parameter_name + " " + parameter_value, color=DARKGREEN)
                if parameter_name == "meter":
                    if parameter_value != switch_on.get_state():
                        if parameter_value == "1":
                            switch_on.set_state(True)
                        else:
                            switch_on.set_state(False)

                for i in range(4):
                    adc_name = f"adc{i}"
                    if parameter_name == adc_name:
                        res_name = f"res{i}"
                        a_name = f"a{i}"
                        b_name = f"b{i}"
                        globals()[adc_name] = int(parameter_value)
                        adc_text_fields[adc_name].set_value(parameter_value)
                        # Bereken scaled_value
                        a_value = parameters.get(a_name, 1)
                        b_value = parameters.get(b_name, 0)
                        scaled_value = (globals()[adc_name] - b_value)/ a_value

                        res_text_fields[res_name].set_value(round(scaled_value, 2))
                        if i == 3:
                            scope_frame_complete = True
                        break

        clock.tick(1000)

    # --------------------------

    pygame.quit()
    # Close the serial connection when done
    parameter_manager.close_serial_connection()


if __name__ == "__main__":
    main()
