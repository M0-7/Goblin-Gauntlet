import pygame
import os
from functools import lru_cache
from variables import WIDTH, HEIGHT  

class Lava:
    def __init__(self, frames_directory, terrain_height, min_size=4, max_size=64, speed=6):
        try:
            # Load all individual frames from the directory
            self.frames = self.load_frames(frames_directory)
            
            # Animation variables
            self.current_frame = 0  # Current frame of the animation
            self.frame_rate = 100  # Time between frames (in milliseconds)
            self.last_update = pygame.time.get_ticks()  # Track the last frame update time

            # Position and movement
            self.tile_width = min_size  # Initial width of each lava tile (scaled from min_size)
            self.tile_height = min_size  # Initial height of each lava tile (scaled from min_size)
            self.max_tile_width = max_size  # Maximum size of tiles
            self.max_tile_height = max_size  # Maximum size of tiles
            self.speed = speed  # Speed at which the lava flows (pixels per frame)
            self.screen_width = WIDTH  # Screen width for resetting position

            # Create multiple lava tiles
            self.tiles = []
            self.create_tiles(terrain_height)
        except Exception as e:
            print(f"Error initializing Lava: {e}")

    @lru_cache(maxsize=None)
    def load_frames(self, frames_directory):
        """Private method to load all individual frames from the specified directory."""
        try:
            frames = []
            frame_files = sorted(os.listdir(frames_directory))
            for file in frame_files:
                if file.endswith(".png"):  # Only load PNG files
                    frame = pygame.image.load(os.path.join(frames_directory, file)).convert_alpha()
                    frames.append(frame)
            return frames
        except Exception as e:
            print(f"Error loading frames from {frames_directory}: {e}")
            return []

    def create_tiles(self, terrain_height):
        """Create multiple lava tiles to cover the screen."""
        try:
            num_tiles = (WIDTH // self.tile_width) + 2  # Number of tiles needed to cover the screen
            for i in range(num_tiles):
                tile_x = i * self.tile_width - WIDTH  # Position tiles starting from the left edge
                # Increase tile size as it moves leftward
                tile_size = self.max_tile_width - int(i * (self.max_tile_width - self.tile_width) / num_tiles)
                tile_y = HEIGHT - terrain_height - tile_size  # Align above the terrain

                # Store tile positions and sizes
                self.tiles.append([tile_x, tile_y, tile_size])
        except Exception as e:
            print(f"Error creating lava tiles: {e}")

    def update(self, camera_x):
        """Update the lava's position and animation."""
        try:
            # Update animation
            now = pygame.time.get_ticks()
            if now - self.last_update > self.frame_rate:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.frames)

            # Move all tiles to the right
            for tile in self.tiles:
                tile[0] += self.speed

            # Reset tiles that move off-screen
            for tile in self.tiles:
                if tile[0] > camera_x + WIDTH:  # Tile goes off-screen to the right
                    tile[0] = camera_x - self.tile_width  # Move tile to the left of the screen
        except Exception as e:
            print(f"Error updating lava: {e}")

    def draw(self, screen, camera_x):
        """Draw the lava tiles on the screen."""
        try:
            frame = self.frames[self.current_frame]
            
            for tile in self.tiles:
                # Adjust the tile size as it moves
                tile_size = tile[2]
                scaled_frame = pygame.transform.scale(frame, (tile_size, tile_size))  # Scale tile
                screen.blit(scaled_frame, (tile[0] - camera_x, tile[1]))
        except Exception as e:
            print(f"Error drawing lava: {e}")