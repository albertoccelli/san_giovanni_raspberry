import curses
import yaml

# Save yaml
def save_yaml(config):
    with open('config.yaml', 'w') as yaml_file:
        yaml.dump(config, yaml_file, default_flow_style=False)

# Modify parameter
def modify_param(param_name, config):
    curses.echo()
    stdscr.clear()
    stdscr.addstr(0, 0, f"Modify {param_name}: ")
    stdscr.refresh()
    value = stdscr.getstr(1, 0).decode('utf-8')
    config[param_name] = value
    curses.noecho()

# Load YAML
with open('config.yaml', 'r') as yaml_file:
    config = yaml.safe_load(yaml_file)

# Initialize curses
stdscr = curses.initscr()
curses.noecho()
curses.cbreak()
stdscr.keypad(1)

# Create menu
menu_items = list(config.keys())
menu_items.append("Salva e Esci")
current_row = 1
current_item = 0

while True:
    stdscr.clear()
    stdscr.addstr(0, 0, "Main menu")

    for i, item in enumerate(menu_items):
        x = 1
        y = i + 1
        if i == current_item:
            stdscr.addstr(y, x, item, curses.A_REVERSE)
        else:
            stdscr.addstr(y, x, item)

    stdscr.refresh()

    key = stdscr.getch()

    if key == curses.KEY_UP and current_item > 0:
        current_item -= 1
    elif key == curses.KEY_DOWN and current_item < len(menu_items) - 1:
        current_item += 1
    elif key == 10:  # Enter key
        if current_item == len(menu_items) - 1:
            # Save
            save_yaml(config)
            break
        else:
            # Modify parameter
            param_name = menu_items[current_item]
            modify_param(param_name, config)

# Close
curses.endwin()
