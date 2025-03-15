import pygame
from variables import WIDTH, HEIGHT, BG_COLOR, FONT_COLOR, FONT_SIZE
from button import Button  
from database import Database

class Settings:
    def __init__(self, menu):
        self.__menu = menu
        self.__clock = pygame.time.Clock()  # Clock to control the frame rate
        self.__screen = pygame.display.set_mode((WIDTH, HEIGHT))  # Set the display size
        pygame.display.set_caption("Settings")  # Set the window title
        
        # Load background image for settings screen
        self.__background_image = self.__load_background("./assets/Background/fire.png")  # Path to background image
        
        # Initialize the 'Back' button that returns to the main menu
        self.__back_button = Button("Back", WIDTH // 2 - 50, HEIGHT - 100, 100, 50, self.__back_to_menu)

        # Fetch number of enemies and sound effects state from the database
        try:
            with Database() as db:
                self.__num_enemies = db.getNumberofEnemies()  # Get the current number of enemies
                self.__sound_effects = db.getEffectsState()  # Get the current state of sound effects
        except Exception as e:
            print(f"Error accessing database: {e}")
            self.__num_enemies = 3  # Default value in case of error
            self.__sound_effects = "y"  # Default value in case of error

        # Initialize the buttons to increase or decrease the number of enemies
        self.__plus_button = Button("+", WIDTH - 345, 40, 50, 50, self.__increase_enemies)
        self.__minus_button = Button("-", WIDTH - 400, 40, 50, 50, self.__decrease_enemies)

        # Initialize the button to toggle sound effects
        self.__sound_button = Button("Toggle", WIDTH - 400, 120, 110, 50, self.__toggle_sound_effects)

    def __load_background(self, image_path):
        """Load and return the background image, scaling it to fit the screen size."""
        try:
            image = pygame.image.load(image_path).convert()  # Load the image and optimize it
            return pygame.transform.scale(image, (WIDTH, HEIGHT))  # Scale the image to match screen size
        except FileNotFoundError:
            print(f"Background image not found at {image_path}")  # Print error message if file is missing
            exit()

    def __draw(self):
        """Draw the entire settings screen, including background, buttons, and text."""
        try:
            if self.__background_image:
                self.__screen.blit(self.__background_image, (0, 0))  # Fill the screen with the background
            else:
                self.__screen.fill(BG_COLOR)  # Fallback: Fill with a solid background color

            # Draw the UI elements (buttons)
            self.__back_button.draw(self.__screen)
            self.__plus_button.draw(self.__screen)
            self.__minus_button.draw(self.__screen)
            self.__sound_button.draw(self.__screen)

            # Display text for current settings
            font = pygame.font.SysFont("JetBrains Mono", FONT_SIZE, bold=True)
            text = font.render(f"Number of Enemies: {self.__num_enemies}", True, (255, 255, 255))  # White color for text
            self.__screen.blit(text, (30, 50))  # Position the number of enemies text

            # Display the sound effects state text
            sound_text = font.render(f"Sound Effects: {self.__sound_effects}", True, (255, 255, 255))  # White color for text
            self.__screen.blit(sound_text, (30, 120))  # Position the sound effects text

            pygame.display.flip()  # Update the screen with everything that was drawn
        except Exception as e:
            print(f"Error drawing screen: {e}")

    def __handle_events(self):
        """Handle user input events (such as button clicks)."""
        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()  # Quit the game if the window is closed
                    exit()
                
                # Handle button events (clicks)
                self.__back_button.handle_event(event)
                self.__plus_button.handle_event(event)
                self.__minus_button.handle_event(event)
                self.__sound_button.handle_event(event)
        except Exception as e:
            print(f"Error handling events: {e}")

    def __back_to_menu(self):
        """Save current settings and return to the main menu."""
        try:
            with Database() as db:
                db.updateNumberofEnemies(self.__num_enemies)  # Save number of enemies to database
                db.updateEffectsState(self.__sound_effects)  # Save sound effects state to database
            self.__menu.run()  # Return to the main menu screen
        except Exception as e:
            print(f"Error saving settings to database: {e}")

    def __increase_enemies(self):
        """Increase the number of enemies, if not already at max value."""
        try:
            if self.__num_enemies == 4:  # Prevent going above the maximum
                return
            self.__num_enemies += 1  # Increase number of enemies by 1
        except Exception as e:
            print(f"Error increasing enemies: {e}")

    def __decrease_enemies(self):
        """Decrease the number of enemies, if not already at minimum value."""
        try:
            if self.__num_enemies == 1:  # Prevent going below the minimum
                return
            self.__num_enemies -= 1  # Decrease number of enemies by 1
        except Exception as e:
            print(f"Error decreasing enemies: {e}")

    def __toggle_sound_effects(self):
        """Toggle the sound effects state between 'on' and 'off'."""
        try:
            if self.__sound_effects == "y":
                self.__sound_effects = "n"  # Set to 'off'
            else:
                self.__sound_effects = "y"  # Set to 'on'
            self.__sound_button.text = self.__sound_effects  # Update button text with the current state
        except Exception as e:
            print(f"Error toggling sound effects: {e}")

    def run(self):
        """Main loop for running the settings screen."""
        while True:
            try:
                self.__clock.tick(60)  # Limit the game loop to 60 frames per second
                self.__handle_events()  # Check for and handle any events
                self.__draw()  # Draw the updated screen
            except Exception as e:
                print(f"Error in the main loop: {e}")
                break  # Exit the loop if there's an error