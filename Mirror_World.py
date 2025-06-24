# Mirror World 
# Features: Emotion-Based Maze + Level Progression + Anti-Idle Timeout

import pygame
import random
import time
import sys
from textblob import TextBlob

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 600, 400
GRID = 40
COLS, ROWS = WIDTH // GRID, HEIGHT // GRID
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🧠 Mirror World – Level Edition")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 32)

# Player setup
light_player = [1, 1]
shadow_player = [1, ROWS - 2]

def get_emotion_gui():
    user_input = ""
    active = True
    while active:
        screen.fill((0, 0, 0))
        prompt = font.render("💬 How do you feel today? Type & press Enter:", True, (255, 255, 255))
        input_text = font.render(user_input, True, (0, 255, 0))
        screen.blit(prompt, (40, 100))
        screen.blit(input_text, (40, 150))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    active = False
                elif event.key == pygame.K_BACKSPACE:
                    user_input = user_input[:-1]
                else:
                    user_input += event.unicode

    blob = TextBlob(user_input)
    polarity = blob.sentiment.polarity
    if polarity < -0.3:
        return "sad"
    elif polarity > 0.3:
        return "happy"
    else:
        return "neutral"

def generate_obstacles(level, emotion):
    base = 5 if emotion == "sad" else 15 if emotion == "happy" else 10
    count = base + (level - 1) * 3
    obs = []
    while len(obs) < count:
        x, y = random.randint(0, COLS - 1), random.randint(0, ROWS // 2 - 2)
        if [x, y] != light_player and [x, y] not in obs:
            obs.append([x, y])
    return obs

def draw_block(pos, color):
    x, y = pos
    pygame.draw.rect(screen, color, (x * GRID, y * GRID, GRID, GRID))

def show_message(text, color):
    screen.fill((0, 0, 0))
    msg = font.render(text, True, color)
    screen.blit(msg, (WIDTH // 2 - 120, HEIGHT // 2 - 20))
    pygame.display.update()
    pygame.time.wait(2000)

def play_level(level, emotion):
    global light_player, shadow_player
    light_player = [1, 1]
    shadow_player = [1, ROWS - 2]
    ghost_path = []

    light_obstacles = generate_obstacles(level, emotion)
    shadow_obstacles = [[x, ROWS - y - 1] for x, y in light_obstacles]

    start_time = time.time()
    last_move_time = time.time()
    game_duration = 30
    speed = min(15, 10 + level - 1)
    prev_position = tuple(light_player)

    while True:
        screen.fill((0, 0, 0))
        clock.tick(speed)
        elapsed = int(time.time() - start_time)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        moved = False
        if keys[pygame.K_UP]:
            light_player[1] -= 1; shadow_player[1] += 1; moved = True
        if keys[pygame.K_DOWN]:
            light_player[1] += 1; shadow_player[1] -= 1; moved = True
        if keys[pygame.K_LEFT]:
            light_player[0] -= 1; shadow_player[0] -= 1; moved = True
        if keys[pygame.K_RIGHT]:
            light_player[0] += 1; shadow_player[0] += 1; moved = True

        for p in [light_player, shadow_player]:
            p[0] = max(0, min(p[0], COLS - 1))
            p[1] = max(0, min(p[1], ROWS - 1))

        # Check for idle timeout
        if tuple(light_player) != prev_position:
            last_move_time = time.time()
            prev_position = tuple(light_player)
        elif time.time() - last_move_time > 3:
            show_message(f"🛑 Inactive too long! Level {level} failed.", (255, 100, 0))
            return False

        for obs in light_obstacles:
            if light_player == obs:
                show_message(f"💥 Light bot hit obstacle! Level {level} failed.", (255, 0, 0))
                return False
        for obs in shadow_obstacles:
            if shadow_player == obs:
                show_message(f"💥 Shadow bot hit obstacle! Level {level} failed.", (255, 0, 0))
                return False

        if elapsed >= game_duration:
            show_message(f"✅ Level {level} complete!", (0, 255, 0))
            return True

        for obs in light_obstacles:
            draw_block(obs, (255, 0, 0))
        for obs in shadow_obstacles:
            draw_block(obs, (255, 0, 0))
        draw_block(light_player, (0, 0, 255))
        draw_block(shadow_player, (0, 0, 255))

        pygame.draw.line(screen, (255, 255, 255), (0, HEIGHT // 2), (WIDTH, HEIGHT // 2), 2)
        timer = font.render(f"Level {level} | Time: {elapsed}s", True, (255, 255, 0))
        screen.blit(timer, (10, 10))

        pygame.display.update()

# Game starts
emotion = get_emotion_gui()
level = 1
while True:
    result = play_level(level, emotion)
    if result:
        level += 1
    else:
        break

pygame.quit()
sys.exit()