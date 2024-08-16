import pygame as py
from os.path import join
import pyaudio as aud
import numpy as np
from collections import deque
import random

# Initialize Pygame and screen
py.init()
py.mixer.init()  # Initialize the mixer module
screen = py.display.set_mode((1200, 720))
clock = py.time.Clock()
running = True
FPS = 60

# Initialize PyAudio
try:
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
except Exception as e:
    print(f"Error initializing audio stream: {e}")
    running = False

# Constants
GRAVITY = 0.5
MAX_JUMP_STRENGTH = -20
RMS_THRESHOLD = 50
PIPE_GAP = 200
PIPE_SPEED = 5
PIPE_FREQUENCY = 1500  # Time in milliseconds between pipes

# Resource Loading with Error Handling
try:
    player_img = py.image.load("assets/bird.png").convert_alpha()
    pipe_img = py.image.load("assets/pipe.png").convert_alpha()
    background_img = py.image.load("assets/background.jpeg").convert()
    background_img = py.transform.scale(background_img, screen.get_size())
except py.error as e:
    print(f"Error loading resources: {e}")
    running = False

# Player
player_pos = py.Vector2(screen.get_width() / 2, screen.get_height() / 2)
player_velocity = py.Vector2(0, 0)
player_rect = player_img.get_rect(center=player_pos)

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
    """Class representing each pipe obstacle in the game."""

    def __init__(self):
        """Initialize pipe at the right side of the screen with a random gap."""
        self.x = screen.get_width()
        self.gap_start = random.randint(150, screen.get_height() - 150 - PIPE_GAP)
        self.top_rect = pipe_img.get_rect(midbottom=(self.x, self.gap_start))
        self.bottom_rect = pipe_img.get_rect(midtop=(self.x, self.gap_start + PIPE_GAP))

    def move(self):
        """Move the pipe to the left."""
        self.top_rect.x -= PIPE_SPEED
        self.bottom_rect.x -= PIPE_SPEED

    def draw(self):
        """Draw the pipe on the screen."""
        screen.blit(pipe_img, self.top_rect)
        screen.blit(pipe_img, self.bottom_rect)

    def is_off_screen(self):
        """Check if the pipe has moved off the screen."""
        return self.top_rect.x < -pipe_img.get_width()

    def check_collision(self, player_rect):
        """Check for collision with the player."""
        return (self.top_rect.colliderect(player_rect) or
                self.bottom_rect.colliderect(player_rect))

def play_damage_music():
    """Play the damage music when the player hits a pipe."""
    try:
        damage_music_path = join("assets", "audio", "death_sound.mp3")
        py.mixer.music.load(damage_music_path)
        py.mixer.music.set_volume(0.7)
        py.mixer.music.play()
    except py.error as e:
        print(f"Error playing damage music: {e}")

def main():
    global running, player_velocity, score

    # Initialize pipes list
    pipes = []

    while running:
        # Event handling
        for event in py.event.get():
            if event.type == py.QUIT:
                running = False
            
            if event.type == py.KEYDOWN:
                if event.key == py.K_SPACE:
                    player_velocity.y = -10  # Temporarily set a fixed jump velocity
                    print("Spacebar pressed: Jump initiated.")

            if event.type == SPAWNPIPE:
                pipes.append(Pipe())
        
        # Audio processing and player control
        try:
            data = stream.read(CHUNK, exception_on_overflow=False)
            audio_data = np.frombuffer(data, dtype=np.int16)
            rms = np.sqrt(np.mean(audio_data**2))
            
            # Add the latest RMS value to the buffer
            rms_buffer.append(rms)
            
            # Calculate the average RMS over the buffer
            average_rms = np.mean(rms_buffer)
            audio_level_percent = min((average_rms / RMS_THRESHOLD) * 100, 100)  # Calculate audio level as a percentage

            if average_rms > RMS_THRESHOLD:  
                jump_strength = -average_rms / 2  # Scale down the jump strength
                player_velocity.y = max(player_velocity.y + jump_strength, MAX_JUMP_STRENGTH)

            print(f"Audio Data Read: RMS = {rms:.2f}, Average RMS = {average_rms:.2f}, Player Velocity Y = {player_velocity.y:.2f}")
        
        except IOError as e:
            print(f"Audio processing error: {e}")
            continue
        
        # Update player position
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

        # Draw everything
        screen.blit(background_img, (0, 0))

        # Draw pipes and handle collisions
        for pipe in pipes[:]:  # Iterate over a copy of the list to avoid modification issues
            pipe.move()
            pipe.draw()
            if pipe.is_off_screen():
                pipes.remove(pipe)
            if pipe.check_collision(player_rect):
                game_over()
                return

        # Draw player
        screen.blit(player_img, player_rect)

        # Draw score
        score_text = font.render(f"Score: {score}", True, (0, 0, 0))
        screen.blit(score_text, (10, 10))

        # Draw audio level percentage
        audio_level_text = font.render(f"Audio Level: {audio_level_percent:.0f}%", True, (0, 0, 0))
        audio_level_rect = audio_level_text.get_rect(topright=(screen.get_width() - 10, 10))
        screen.blit(audio_level_text, audio_level_rect)

        # Update display and tick clock
        py.display.flip()
        clock.tick(FPS)

    # Clean up on exit
    stream.stop_stream()
    stream.close()
    pyAud.terminate()
    py.quit()

def game_over():
    """End the game and play the damage music."""
    global running, score
    running = False
    print("Game Over!")
    play_damage_music()
    print(f"Final Score: {score}")

if __name__ == "__main__":
    main()
