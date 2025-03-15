import pygame
import random
from database import Database

class Music:
    def __init__(self):
        try:
            pygame.mixer.init()
            self.tracks = {
                "menu": "./assets/Sounds/Music/menu-music.mp3",
                "play": "./assets/Sounds/Music/play-music.mp3",
            }
        except Exception as e:
            print(f"Failed to start music. Error: {e}")
            exit()
    
    def play_music(self, track_name):
        """Play a specific music track."""
        if track_name in self.tracks:
            pygame.mixer.music.stop()  # Stop current music
            pygame.mixer.music.load(self.tracks[track_name])
            pygame.mixer.music.set_volume(0.2)
            pygame.mixer.music.play(-1)  # Loop indefinitely

## Sound effects for the game
class Effects:
    def __init__(self):
        try:
            pygame.mixer.init()
            self.effects = {
                "jump": {"file": "./assets/Sounds/Effects/jump.mp3", "volume": 1.0},
                "bbq": {"file": "./assets/Sounds/Effects/bbq.mp3", "volume": 1.0},
                "chicken": {"file": "./assets/Sounds/Effects/chicken.mp3", "volume": 0.5},
                "rino": {"file": "./assets/Sounds/Effects/rino.mp3", "volume": 0.5},
                "bee": {"file": "./assets/Sounds/Effects/bee.mp3", "volume": 0.2},
                "bunny": {"file": "./assets/Sounds/Effects/bunny.mp3", "volume": 0.5},
                "bat": {"file": "./assets/Sounds/Effects/bat.mp3", "volume": 0.3},
            }
            self.state = ""
        except Exception as e:
            print(f"Error setting up effects. Error: {e}")
            exit()
    
    def __update_state(self):
        try:
            with Database() as db:
                self.state = db.getEffectsState()
        except Exception:
            print(f"Error accessing databse. Error: {e}")

    def play_effect(self, effect_name):
        self.__update_state()
        chance = random.randint(1,5)
        if chance != 5 and effect_name != "jump":
            return
        elif self.state.lower() == "n" and effect_name != "jump":
            return
        try:
            sound = pygame.mixer.Sound(self.effects[effect_name]["file"])
            sound.set_volume(self.effects[effect_name]["volume"])
            sound.play()
        except:
            print("Sound effect not found")
    
    def kill_effects(self):
        pygame.mixer.stop()