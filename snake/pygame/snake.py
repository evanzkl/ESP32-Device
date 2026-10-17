
import random
import sys

import pygame

try:
    import serial
    import serial.tools.list_ports
except ImportError:
    serial = None

CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 25

WIDTH = GRID_WIDTH * CELL_SIZE
HEIGHT = GRID_HEIGHT * CELL_SIZE

FPS = 10
SERIAL_PORT = "COM3" 
BAUD_RATE = 115200

BLACK = (18, 18, 24)
WHITE = (240, 240, 240)
GREEN = (65, 210, 100)
DARK_GREEN = (35, 150, 70)
RED = (240, 75, 75)
GRAY = (100, 100, 115)
YELLOW = (245, 210, 80)

DIRECTIONS = {
    "UP": (0, -1),
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
    "RIGHT": (1, 0),
}

OPPOSITE = {
    "UP": "DOWN",
    "DOWN": "UP",
    "LEFT": "RIGHT",
    "RIGHT": "LEFT",
}

KEYS = {
    pygame.K_UP: "UP",
    pygame.K_DOWN: "DOWN",
    pygame.K_LEFT: "LEFT",
    pygame.K_RIGHT: "RIGHT",
}

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ESP32 Snake")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 32)
small_font = pygame.font.Font(None, 24)

esp32 = None

if serial is not None:
    try:
        esp32 = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0)
        print(f"Connected to ESP32 on {SERIAL_PORT}")
    except (serial.SerialException, OSError) as error:
        print(f"ESP32 not connected: {error}")
        print("You can still play using the keyboard.")


def new_food(snake):
    empty_cells = [
        (x, y)
        for x in range(GRID_WIDTH)
        for y in range(GRID_HEIGHT)
        if (x, y) not in snake
    ]
    return random.choice(empty_cells) if empty_cells else None


def reset_game():
    snake = [
        (GRID_WIDTH // 2, GRID_HEIGHT // 2),
        (GRID_WIDTH // 2 - 1, GRID_HEIGHT // 2),
        (GRID_WIDTH // 2 - 2, GRID_HEIGHT // 2),
    ]
    return snake, "RIGHT", "RIGHT", new_food(snake), 0, False


def change_direction(new_direction):
    global direction, next_direction

    if new_direction != OPPOSITE[direction]:
        next_direction = new_direction


def read_esp32():
    """Read newline-terminated direction commands from the ESP32."""
    if esp32 is None:
        return

    try:
        while esp32.in_waiting:
            command = esp32.readline().decode(
                "utf-8", errors="ignore"
            ).strip().upper()

            if command in DIRECTIONS:
                change_direction(command)

    except (serial.SerialException, OSError):
        print("Lost connection to ESP32.")
        esp32.close()


def draw_text(text, font_obj, color, x, y, center=True):
    surface = font_obj.render(text, True, color)
    rect = surface.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(surface, rect)


def draw_game(snake, food, score, game_over):
    screen.fill(BLACK)

    if food is not None:
        food_rect = pygame.Rect(
            food[0] * CELL_SIZE,
            food[1] * CELL_SIZE,
            CELL_SIZE,
            CELL_SIZE,
        )
        pygame.draw.rect(screen, RED, food_rect, border_radius=5)

    for index, (x, y) in enumerate(snake):
        rect = pygame.Rect(
            x * CELL_SIZE + 1,
            y * CELL_SIZE + 1,
            CELL_SIZE - 2,
            CELL_SIZE - 2,
        )
        color = GREEN if index == 0 else DARK_GREEN
        pygame.draw.rect(screen, color, rect, border_radius=4)

    draw_text(f"Score: {score}", small_font, WHITE, 10, 8, center=False)

    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        screen.blit(overlay, (0, 0))

        draw_text("GAME OVER", font, RED, WIDTH // 2, HEIGHT // 2 - 35)
        draw_text(
            "Press SPACE to restart",
            small_font,
            WHITE,
            WIDTH // 2,
            HEIGHT // 2 + 5,
        )
        draw_text(
            "Press ESC to quit",
            small_font,
            GRAY,
            WIDTH // 2,
            HEIGHT // 2 + 35,
        )

    pygame.display.flip()

snake, direction, next_direction, food, score, game_over = reset_game()

running = True

while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            elif event.key == pygame.K_SPACE and game_over:
                snake, direction, next_direction, food, score, game_over = (
                    reset_game()
                )

            elif event.key in KEYS and not game_over:
                change_direction(KEYS[event.key])

    if not game_over:
        read_esp32()

    if not game_over:
        direction = next_direction
        dx, dy = DIRECTIONS[direction]

        head_x, head_y = snake[0]
        new_head = (head_x + dx, head_y + dy)

        if (
            new_head[0] < 0
            or new_head[0] >= GRID_WIDTH
            or new_head[1] < 0
            or new_head[1] >= GRID_HEIGHT
        ):
            game_over = True

        else:
            eating = new_head == food
            body_to_check = snake if eating else snake[:-1]

            if new_head in body_to_check:
                game_over = True

            else:
                snake.insert(0, new_head)

                if eating:
                    score += 1
                    food = new_food(snake)

                    if food is None:
                        game_over = True
                else:
                    snake.pop()

    draw_game(snake, food, score, game_over)

pygame.quit()

sys.exit()
