import pygame
import random
from variables import WIDTH
from functools import lru_cache

# Use lru_cache to cache loaded images
@lru_cache(maxsize=None)  # This decorator caches the result of the load_image function
def load_image(image_path, scale_factor):
    """Load an image and scale it, using a cache to avoid reloading."""
    try:
        # Load the image from the specified path
        image = pygame.image.load(image_path).convert_alpha()
        # Scale the image by the given factor
        scaled_image = pygame.transform.scale(image, (image.get_width() * scale_factor, image.get_height() * scale_factor))
        return scaled_image
    except pygame.error as e:
        print(f"Error loading image {image_path}: {e}")
        return None  # Return None if there was an error

class Trap:
    def __init__(self, trap_image_path, name, scale_factor):
        self.trap_image = self._load_trap_image(trap_image_path, scale_factor)
        self.type = name
        self.trap_width = self.trap_image.get_width()
        self.trap_height = self.trap_image.get_height()
        self.trap_position = None  

    def _load_trap_image(self, trap_image_path, scale_factor):
        """Private method to load the trap image and handle errors."""
        try:
            # Use the cached load_image function to load and scale the image
            trap_image = load_image(trap_image_path, scale_factor)
            if trap_image is None:
                raise ValueError("Failed to load trap image.")
            return trap_image
        except Exception as e:
            print(f"Error initializing trap image {trap_image_path}: {e}")
            return None  # Return None if there's an error in loading the image

    def spawn_trap(self, terrain_height, camera_x):
        """Spawns a trap at a random position on the screen if it hasn't been spawned yet."""
        try:
            if self.trap_position is None:  # Check if trap has not been spawned
                x_position = camera_x + WIDTH + random.randint(50, 200)
                y_position = terrain_height - self.trap_height
                self.trap_position = (x_position, y_position)
        except Exception as e:
            print(f"Error spawning trap: {e}")

    def check_collision(self, player_rect):
        """Checks if the player collides with the trap."""
        try:
            if self.trap_position:
                trap_rect = pygame.Rect(self.trap_position[0], self.trap_position[1], self.trap_width, self.trap_height)
                if player_rect.colliderect(trap_rect):
                    return True
            return False
        except Exception as e:
            print(f"Error checking collision: {e}")
            return False

    def update(self, terrain_height, camera_x):
        """Updates the trap's position and checks if it should be spawned."""
        try:
            self.spawn_trap(terrain_height, camera_x)
        except Exception as e:
            print(f"Error updating trap: {e}")

    def draw(self, screen, camera_x):
        """Draws the trap on the screen at its current position."""
        try:
            if self.trap_position:
                screen.blit(self.trap_image, (self.trap_position[0] - camera_x, self.trap_position[1]))
        except Exception as e:
            print(f"Error drawing trap: {e}")

class Spikes(Trap):
    def __init__(self, trap_image_path="./assets/Traps/Spikes/Idle.png", name="Spikes", scale_factor=4):
        super().__init__(trap_image_path, name, scale_factor)

class Ball(Trap):
    def __init__(self, trap_image_path="./assets/Traps/Spiked Ball/Idle.png", name="Ball", scale_factor=2):
        super().__init__(trap_image_path, name, scale_factor)

class Head(Trap):
    def __init__(self, trap_image_path="./assets/Traps/Spike Head/Idle.png", name="Head", scale_factor=2):
        super().__init__(trap_image_path, name, scale_factor)

    def spawn_trap(self, terrain_height, camera_x):
        """Spawns a Head trap slightly lower than the default position."""
        try:
            if self.trap_position is None:
                x_position = camera_x + WIDTH + random.randint(50, 200)
                y_position = terrain_height - self.trap_height + 10
                self.trap_position = (x_position, y_position)
        except Exception as e:
            print(f"Error spawning Head trap: {e}")

# List of traps
traps = [Spikes, Ball, Head]

# Function to randomly generate a trap from the predefined list
def generate_random_trap():
    try:
        return random.choice(traps)()
    except Exception as e:
        print(f"Error generating random trap: {e}")
        return []