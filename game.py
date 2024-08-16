# import pygame as py
# from os.path import join
# import pyaudio as aud
# import numpy as np
# from collections import deque
import random

# py.init()
# screen = py.display.set_mode((1200, 720))
# clock = py.time.Clock()
# running = True
# FPS = 60

# # Initialize PyAudio
# pyAud = aud.PyAudio()
# FORMAT = aud.paInt16
# CHANNELS = 1  
# RATE = 44100
# CHUNK = 1024
# stream = pyAud.open(format=FORMAT,
#                     channels=CHANNELS,
#                     rate=RATE,
#                     input=True,
#                     frames_per_buffer=CHUNK)
# Constants
GRAVITY = 0.5
MAX_JUMP_STRENGTH = -20
RMS_THRESHOLD = 70
PIPE_GAP = 200
PIPE_SPEED = 5
PIPE_FREQUENCY = 1500  # Time in milliseconds between pipes

# player_pos = py.Vector2(screen.get_width() / 2, screen.get_height() / 2)
# player_velocity = py.Vector2(0, 0)
# player_img = py.image.load("assets/bird.png").convert_alpha()
# player_rect = player_img.get_rect(center=player_pos)
# Obstacle
pipe_img = py.image.load("assets/pipe.png").convert_alpha()

# Background
background_img = py.image.load("assets/background.jpeg").convert()
background_img = py.transform.scale(background_img, screen.get_size())

# Scoring
font = py.font.Font(None, 36)
score = 0

# # Buffer to store the last N RMS values
# RMS_BUFFER_SIZE = 10
# rms_buffer = deque(maxlen=RMS_BUFFER_SIZE)
# Events
SPAWNPIPE = py.USEREVENT
py.time.set_timer(SPAWNPIPE, PIPE_FREQUENCY)

class Pipe:
    def __init__(self):
        self.x = screen.get_width()
        self.gap_start = random.randint(150, screen.get_height() - 150 - PIPE_GAP)
        self.top_rect = pipe_img.get_rect(midbottom=(self.x, self.gap_start))
        self.bottom_rect = pipe_img.get_rect(midtop=(self.x, self.gap_start + PIPE_GAP))

    def move(self):
        self.top_rect.x -= PIPE_SPEED
        self.bottom_rect.x -= PIPE_SPEED

    def draw(self):
        screen.blit(pipe_img, self.top_rect)
        screen.blit(pipe_img, self.bottom_rect)

    def is_off_screen(self):
        return self.top_rect.x < -pipe_img.get_width()

    def check_collision(self, player_rect):
        return (self.top_rect.colliderect(player_rect) or
                self.bottom_rect.colliderect(player_rect))
# def play_damage_music():
#     damage_music_path = join("assets", "audio", "death_sound.mp3")
#     py.mixer.music.load(damage_music_path)
#     py.mixer.music.set_volume(0.7)
#     py.mixer.music.play()
def update_pipes():
    global score
    for pipe in pipes:
        pipe.move()
        if pipe.is_off_screen():
            pipes.remove(pipe)
            score += 1
        if pipe.check_collision(player_rect):
            game_over()

def draw():
    # Draw the background
    screen.blit(background_img, (0, 0))

    # Draw the pipes
    for pipe in pipes:
        pipe.draw()

    # Draw the player
    screen.blit(player_img, player_rect)

    # Draw the score
    score_text = font.render(f"Score: {score}", True, (0, 0, 0))
    screen.blit(score_text, (10, 10))

    # Update the display
    py.display.flip()

def game_over():
    global running
    running = False
    print("Game Over!")
    play_damage_music()

# def main():
#     global running, player_velocity

#     while running:
#         for event in py.event.get():
#             if event.type == py.QUIT:
#                 running = False
            
#             if event.type == py.KEYDOWN:
#                 if event.key == py.K_SPACE:
#                     play_damage_music()
#                     player_velocity.y -= 10
        
#         try:
#             data = stream.read(CHUNK)
#             audio_data = np.frombuffer(data, dtype=np.int16)
#             rms = np.sqrt(np.mean(audio_data**2))
            
#             # Add the latest RMS value to the buffer
#             rms_buffer.append(rms)
            
#             # Calculate the average RMS over the buffer
#             average_rms = np.mean(rms_buffer)

#             if average_rms > 50:  
#                 jump_strength = -average_rms / 2  # Scale down the jump strength
#                 player_velocity.y = max(player_velocity.y + jump_strength, MAX_JUMP_STRENGTH)

#             print(f"Volume Intensity (Average RMS): {average_rms:.2f}, Jump Strength: {player_velocity.y:.2f}")
        
#         except KeyboardInterrupt:
#             print("Exiting...")
        
#         player_velocity.y += GRAVITY
#         player_pos.y += player_velocity.y

#         if player_pos.y > screen.get_height() - player_rect.height / 2:
#             player_pos.y = screen.get_height() - player_rect.height / 2
#             player_velocity.y = 0

#         if player_pos.y < player_rect.height / 2:
#             player_pos.y = player_rect.height / 2
#             player_velocity.y = 0

#         player_rect.center = player_pos

#         screen.fill("white")
#         screen.blit(player_img, player_rect)
        
#         py.display.flip()
#         clock.tick(FPS)
    
#     stream.stop_stream()
#     stream.close()
#     pyAud.terminate()

#     py.quit()

# if __name__ == "__main__":
pipes = []  
#     main()
import pygame as py
from os.path import join
import pyaudio as aud
import numpy as np
from collections import deque
import random

# Initialize Pygame and screen
py.init()
screen = py.display.set_mode((1200, 720))
clock = py.time.Clock()
running = True
FPS = 60

# Initialize PyAudio
pyAud = aud.PyAudio()
FORMAT = aud.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
stream = pyAud.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

# Constants
GRAVITY = 0.5
MAX_JUMP_STRENGTH = -20
RMS_THRESHOLD = 50
PIPE_GAP = 200
PIPE_SPEED = 5
PIPE_FREQUENCY = 1500  # Time in milliseconds between pipes
# Player
player_img = py.image.load("assets/bird.png").convert_alpha()
player_pos = py.Vector2(screen.get_width() / 2, screen.get_height() / 2)
player_velocity = py.Vector2(0, 0)
player_rect = player_img.get_rect(center=player_pos)

# Obstacle
pipe_img = py.image.load("assets/pipe.png").convert_alpha()

# Background
background_img = py.image.load("assets/background.jpeg").convert()
background_img = py.transform.scale(background_img, screen.get_size())

# Scoring
font = py.font.Font(None, 36)
score = 0

# Buffer to store the last N RMS values
RMS_BUFFER_SIZE = 10
rms_buffer = deque(maxlen=RMS_BUFFER_SIZE)

# Events
SPAWNPIPE = py.USEREVENT
py.time.set_timer(SPAWNPIPE, PIPE_FREQUENCY)

class Pipe:
    def __init__(self):
        self.x = screen.get_width()
        self.gap_start = random.randint(150, screen.get_height() - 150 - PIPE_GAP)
        self.top_rect = pipe_img.get_rect(midbottom=(self.x, self.gap_start))
        self.bottom_rect = pipe_img.get_rect(midtop=(self.x, self.gap_start + PIPE_GAP))

    def move(self):
        self.top_rect.x -= PIPE_SPEED
        self.bottom_rect.x -= PIPE_SPEED

    def draw(self):
        screen.blit(pipe_img, self.top_rect)
        screen.blit(pipe_img, self.bottom_rect)

    def is_off_screen(self):
        return self.top_rect.x < -pipe_img.get_width()

    def check_collision(self, player_rect):
        return (self.top_rect.colliderect(player_rect) or
                self.bottom_rect.colliderect(player_rect))

def play_damage_music():
    damage_music_path = join("assets", "audio", "death_sound.mp3")
    py.mixer.music.load(damage_music_path)
    py.mixer.music.set_volume(0.7)
    py.mixer.music.play()

def handle_audio_input():
    try:
        data = stream.read(CHUNK, exception_on_overflow=False)
        audio_data = np.frombuffer(data, dtype=np.int16)
        rms = np.sqrt(np.mean(audio_data ** 2))
        rms_buffer.append(rms)
        average_rms = np.mean(rms_buffer)
        return average_rms
    except IOError as e:
        print(f"Error reading audio stream: {e}")
        return 0

def process_events():
    global running, player_velocity
    for event in py.event.get():
        if event.type == py.QUIT:
            running = False
        elif event.type == py.KEYDOWN:
            if event.key == py.K_SPACE:
                play_damage_music()
                player_velocity.y -= 10
        elif event.type == SPAWNPIPE:
            pipes.append(Pipe())

def update_player(average_rms):
    global player_velocity, player_pos
    if average_rms > RMS_THRESHOLD:
        jump_strength = -average_rms / 2
        player_velocity.y = max(player_velocity.y + jump_strength, MAX_JUMP_STRENGTH)
    player_velocity.y += GRAVITY
    player_pos.y += player_velocity.y

    # Ensure the player stays within the screen bounds
    if player_pos.y > screen.get_height() - player_rect.height / 2:
        player_pos.y = screen.get_height() - player_rect.height / 2
        player_velocity.y = 0
    if player_pos.y < player_rect.height / 2:
        player_pos.y = player_rect.height / 2
        player_velocity.y = 0

    player_rect.center = player_pos

def update_pipes():
    global score
    for pipe in pipes:
        pipe.move()
        if pipe.is_off_screen():
            pipes.remove(pipe)
            score += 1
        if pipe.check_collision(player_rect):
            game_over()

def draw():
    # Draw the background
    screen.blit(background_img, (0, 0))

    # Draw the pipes
    for pipe in pipes:
        pipe.draw()

    # Draw the player
    screen.blit(player_img, player_rect)

    # Draw the score
    score_text = font.render(f"Score: {score}", True, (0, 0, 0))
    screen.blit(score_text, (10, 10))

    # Update the display
    py.display.flip()

def game_over():
    global running
    running = False
    print("Game Over!")
    play_damage_music()

def main():
    global running
    while running:
        process_events()
        average_rms = handle_audio_input()
        update_player(average_rms)
        update_pipes()
        draw()
        clock.tick(FPS)

    # Clean up
    stream.stop_stream()
    stream.close()
    pyAud.terminate()
    py.quit()

if __name__ == "__main__":
    # Initialize pipes list
    pipes = []
    main()
  