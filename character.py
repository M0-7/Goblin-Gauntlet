import pygame
import os
from variables import WIDTH, HEIGHT, FPS  # Import game settings (screen width, height, and FPS)
from database import Database  # Import the Database class for fetching character data

# Character class
class Character:
    def __init__(self,action_paths):
        # Load the sprite sheets for each action and store them in a dictionary
        self.sprites = {
            action: self.__load_sprites(path)  # Call __load_sprites to load each sprite sheet
            for action, path in action_paths.items()  # Loop over all actions and paths
        }

        # Initialize character's current action and animation frame
        self.current_action = "idle"  # Default action
        self.current_frame = 0  # Start with the first frame
        # Frame delays define how fast each animation action plays (idle, run, jump, double_jump)
        self.frame_delays = {"idle": 8, "run": 7, "jump": 8, "double_jump": 6}
        self.frame_delay = self.frame_delays[self.current_action]  # Set delay for current action
        self.frame_count = 0  # Counter to track frames
        # Default position (center of the screen, adjusted for character height)
        self.position = [WIDTH // 2, HEIGHT - 220]
        self.facing_left = False  # Boolean flag for character's facing direction
        self.damage_timer = 0  # Timer to track duration of damage effect
        self.immunity = False  # Immunity flag to show if character is invulnerable
        self.speed_cooldown = False  # Speed boost cooldown flag

    def draw(self, screen, position):
        """Draw the character on the screen with any effects applied."""
        # Get the current frame based on the action
        frame = self.sprites[self.current_action][self.current_frame]
        
        # Flip the sprite horizontally if the character is facing left
        if self.facing_left:
            frame = pygame.transform.flip(frame, True, False)

        # Apply effects based on timers (red for damage, green for immunity, blue for speed boost)
        if self.damage_timer > 0:  
            if self.immunity:  # Apply green tint effect when immune
                green_tinted = frame.copy()
                green_tinted.fill((0, 255, 0, 50), special_flags=pygame.BLEND_RGBA_MULT)
                screen.blit(green_tinted, position)
            else:  # Apply red tint effect when damaged
                red_tinted = frame.copy()
                red_tinted.fill((255, 0, 0, 50), special_flags=pygame.BLEND_RGBA_MULT)
                screen.blit(red_tinted, position)
        elif self.speed_cooldown:  # Apply blue tint effect when speed boost is active
            blue_tinted = frame.copy()
            blue_tinted.fill((0, 0, 255, 50), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(blue_tinted, position)
        else:
            # If no effects, just draw the normal frame
            screen.blit(frame, position)

    def __load_sprites(self, image_path):
        """Load a sprite sheet from an image and split it into individual frames."""
        try:
            sheet = pygame.image.load(image_path).convert_alpha()  # Load the image and keep transparency
            sprite_width = 32  # Original sprite width (assumed size for character)
            sprite_height = 32  # Original sprite height
            scale_factor = 2  # Scale the sprites to make them bigger
            scaled_sprites = []  # List to store scaled sprites

            # Loop through the sprite sheet and extract individual sprites
            for y in range(sheet.get_height() // sprite_height):  # Loop through rows
                for x in range(sheet.get_width() // sprite_width):  # Loop through columns
                    rect = pygame.Rect(x * sprite_width, y * sprite_height, sprite_width, sprite_height)
                    sprite = sheet.subsurface(rect)  # Extract individual sprite
                    # Scale the sprite and add it to the list
                    scaled_sprite = pygame.transform.scale(sprite, (sprite_width * scale_factor, sprite_height * scale_factor))
                    scaled_sprites.append(scaled_sprite)

            return scaled_sprites  # Return the list of scaled sprites
        except Exception as e:
            print(f"Error loading character; {e}")  # Print any errors if loading fails
            exit()

    def set_action(self, action):
        """Change the character's current action (animation)."""
        if action != self.current_action:  # If the action is different from the current one
            # Don't change if the double jump animation is still playing
            if self.current_action == "double_jump" and self.current_frame < len(self.sprites["double_jump"]) - 1:
                return  # Don't change action until double jump animation finishes

            self.current_action = action  # Change to the new action
            self.current_frame = 0  # Start from the first frame of the new action
            self.frame_count = 0  # Reset the frame count
            self.frame_delay = self.frame_delays[action]  # Set the correct frame delay for the new action

    def update(self):
        """Update the character's animation frame."""
        self.frame_count += 1  # Increment frame count
        if self.frame_count >= self.frame_delay:  # If it's time to change frame
            self.frame_count = 0  # Reset the frame count
            self.current_frame += 1  # Move to the next frame

            # If we exceed the last frame, reset to 0 (looping animation)
            if self.current_frame >= len(self.sprites[self.current_action]):
                if self.current_action == "double_jump":
                    self.set_action("idle")  # Only reset AFTER double jump animation finishes
                else:
                    self.current_frame = 0  # Loop other animations

        # Handle damage and immunity timers
        if self.damage_timer > 0:
            self.damage_timer -= 1  # Decrease damage timer
            if self.damage_timer == 0:
                self.immunity = False  # End immunity after the timer finishes

    def take_damage_effect(self, duration=20):
        """Trigger the red damage effect for a short duration."""
        self.damage_timer = duration  # Set the damage effect duration

    def take_immunity_effect(self, duration=20):
        """Trigger the green immunity effect for a short duration."""
        self.damage_timer = duration  # Set the immunity effect duration
        self.immunity = True  # Enable immunity effect
