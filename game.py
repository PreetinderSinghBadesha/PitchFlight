import pygame as py
from os.path import join
import pyaudio as aud
import numpy as np
from collections import deque

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

player_pos = py.Vector2(screen.get_width() / 2, screen.get_height() / 2)
player_velocity = py.Vector2(0, 0)
GRAVITY = 0.5
MAX_JUMP_STRENGTH = -20  
RMS_THRESHOLD = 70

player_img = py.image.load("assets/bird.png").convert_alpha()
player_rect = player_img.get_rect(center=player_pos)

# Buffer to store the last N RMS values
RMS_BUFFER_SIZE = 10
rms_buffer = deque(maxlen=RMS_BUFFER_SIZE)

def play_damage_music():
    damage_music_path = join("assets", "audio", "death_sound.mp3")
    py.mixer.music.load(damage_music_path)
    py.mixer.music.set_volume(0.7)
    py.mixer.music.play()

def main():
    global running, player_velocity

    while running:
        for event in py.event.get():
            if event.type == py.QUIT:
                running = False
            
            if event.type == py.KEYDOWN:
                if event.key == py.K_SPACE:
                    play_damage_music()
                    player_velocity.y -= 10
        
        try:
            data = stream.read(CHUNK)
            audio_data = np.frombuffer(data, dtype=np.int16)
            rms = np.sqrt(np.mean(audio_data**2))
            
            # Add the latest RMS value to the buffer
            rms_buffer.append(rms)
            
            # Calculate the average RMS over the buffer
            average_rms = np.mean(rms_buffer)

            if average_rms > 50:  
                jump_strength = -average_rms / 2  # Scale down the jump strength
                player_velocity.y = max(player_velocity.y + jump_strength, MAX_JUMP_STRENGTH)

            print(f"Volume Intensity (Average RMS): {average_rms:.2f}, Jump Strength: {player_velocity.y:.2f}")
        
        except KeyboardInterrupt:
            print("Exiting...")
        
        player_velocity.y += GRAVITY
        player_pos.y += player_velocity.y

        if player_pos.y > screen.get_height() - player_rect.height / 2:
            player_pos.y = screen.get_height() - player_rect.height / 2
            player_velocity.y = 0

        if player_pos.y < player_rect.height / 2:
            player_pos.y = player_rect.height / 2
            player_velocity.y = 0

        player_rect.center = player_pos

        screen.fill("white")
        screen.blit(player_img, player_rect)
        
        py.display.flip()
        clock.tick(FPS)
    
    stream.stop_stream()
    stream.close()
    pyAud.terminate()

    py.quit()

if __name__ == "__main__":
    main()
