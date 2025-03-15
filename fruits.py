import pygame
import time
import random
import os
from variables import WIDTH

class Fruit:
    def __init__(self, fruit_folder, frame_count, frame_width, frame_height):
        try:
            # Load all fruit sprite sheets
            self.fruit_sheets = [os.path.join(fruit_folder, f) for f in os.listdir(fruit_folder) if f.endswith('.png')]

            # Load collected animation
            self.__load_collected_animation("./assets/Fruits/Other/Collected.png", 6, 32, 32)  # Update frame count & size

            # Pick a random fruit sprite sheet
            self.__load_random_fruit(frame_count, frame_width, frame_height)

            # Animation & state variables
            self.current_frame = 0
            self.animation_speed = 0.1  # Seconds per frame
            self.last_animation_time = time.time()

            self.fruit_position = None  # Store fruit position as (x, y)
            self.last_spawn_time = time.time()
            self.spawn_delay = 3  # Time in seconds before a new fruit can spawn

            self.collected = False  # Track if fruit is collected
            self.collection_start_time = None
        except Exception as e:
            print(f"Error in setting up the fruit. Error: {e}")

    def __load_random_fruit(self, frame_count, frame_width, frame_height):
        """Load a random fruit sprite sheet and extract frames."""
        sprite_sheet_path = random.choice(self.fruit_sheets)
        self.sprite_sheet = pygame.image.load(sprite_sheet_path).convert_alpha()

        # Define scaling factor
        scale_factor = 2
        self.fruit_width = frame_width * scale_factor
        self.fruit_height = frame_height * scale_factor

        # Extract and scale frames
        self.frames = [
            pygame.transform.scale(
                self.sprite_sheet.subsurface((i * frame_width, 0, frame_width, frame_height)),
                (self.fruit_width, self.fruit_height)
            )
            for i in range(frame_count)
        ]

    def __load_collected_animation(self, path, frame_count, frame_width, frame_height):
        """Loads the animation frames for when a fruit is collected."""
        self.collected_sprite_sheet = pygame.image.load(path).convert_alpha()
        self.collected_frames = [
            pygame.transform.scale(
                self.collected_sprite_sheet.subsurface((i * frame_width, 0, frame_width, frame_height)),
                (frame_width * 2, frame_height * 2)
            ) for i in range(frame_count)
        ]

    def spawn_fruit(self, terrain_height, camera_x):
        """Spawns a fruit if the spawn delay has passed and there isn't one already."""
        current_time = time.time()
        if current_time - self.last_spawn_time >= self.spawn_delay and self.fruit_position is None:
            x_position = camera_x + WIDTH + random.randint(50, 200)
            y_position = terrain_height - self.fruit_height + random.randint(-200, 10)
            self.fruit_position = (x_position, y_position)
            self.last_spawn_time = current_time
            self.__load_random_fruit(len(self.frames), self.fruit_width // 2, self.fruit_height // 2)

    def check_collision(self, player_rect):
        """Triggers collection animation if the player touches the fruit."""
        if self.fruit_position and not self.collected:
            fruit_rect = pygame.Rect(self.fruit_position[0], self.fruit_position[1], self.fruit_width, self.fruit_height)
            if player_rect.colliderect(fruit_rect):
                self.collected = True  # Mark as collected
                self.collection_start_time = time.time()
                self.current_frame = 0  # Reset animation
                return True  
        return False

    def update(self, terrain_height, camera_x):
        """Handles normal fruit animation & collected animation when needed."""
        if self.collected:
            current_time = time.time()
            if current_time - self.last_animation_time > self.animation_speed:
                self.current_frame += 1
                self.last_animation_time = current_time
                
                # If animation finished, remove fruit
                if self.current_frame >= len(self.collected_frames):
                    self.fruit_position = None
                    self.collected = False
                    self.current_frame = 0
            return  
        
        self.spawn_fruit(terrain_height, camera_x)
        
        if self.fruit_position:
            current_time = time.time()
            if current_time - self.last_animation_time > self.animation_speed:
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.last_animation_time = current_time

    def draw(self, screen, camera_x):
        """Draws the normal fruit or the collected animation if triggered."""
        if self.fruit_position:
            if self.collected:
                frame = self.collected_frames[min(self.current_frame, len(self.collected_frames) - 1)]
            else:
                frame = self.frames[self.current_frame]
            
            screen.blit(frame, (self.fruit_position[0] - camera_x, self.fruit_position[1]))