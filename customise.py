import pygame
import os
from database import Database
from character import Character
from button import Button
from variables import WIDTH, HEIGHT, FPS

class Customise:
    def __init__(self, menu):
        # Initialize the customisation screen
        self.menu = menu  # The main menu object to return to when exiting
        self.clock = pygame.time.Clock()  # Clock to control the frame rate
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))  # Set the screen size for the window
        pygame.display.set_caption("Customisation")  # Set the window title to "Customisation"

        # Load background image for the customisation screen
        self.background_image = self.__load_background("./assets/Background/fire.png")

        # Get the list of character directories available in the assets folder
        self.character_directories = self.__get_character_directories("./assets/MainCharacters")

        # Load the saved character from the database, if it exists
        with Database() as db:
            saved_character = db.getCharacter()  # Retrieve the saved character from the database
        # Set the selected character to the saved one, or default to the first one if none saved
        self.selected_character = self.character_directories.index(saved_character) if saved_character in self.character_directories else 0

        # Create the player character with the loaded sprites for the selected character
        self.player = Character(self.__load_character_sprites(self.character_directories[self.selected_character]))

        # Create buttons for navigating between characters and exiting to the menu
        self.button_left = Button("<", 150, HEIGHT // 2, 50, 50, self.__previous_character)  # Left button to go to the previous character
        self.button_right = Button(">", WIDTH - 200, HEIGHT // 2, 50, 50, self.__next_character)  # Right button to go to the next character
        self.button_back = Button("Save & Exit", WIDTH // 2 - 100, HEIGHT - 100, 200, 50, self.__back_to_menu)  # Save and exit button

    def __load_background(self, image_path):
        """Load and scale the background image to fit the screen."""
        try:
            image = pygame.image.load(image_path)  # Try to load the background image
            return pygame.transform.scale(image, (WIDTH, HEIGHT))  # Scale image to fit screen size
        except FileNotFoundError:
            print("Background image file not found")  # Handle missing background image
            exit()  # Exit the program if the background file is missing
    
    def __get_character_directories(self, base_path):
        """Fetch all directories (character folders) from the given base path."""
        return [f for f in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, f))]
    
    def __load_character_sprites(self, character_name):
        """Load the sprite paths for a given character from its directory."""
        base_path = f"./assets/MainCharacters/{character_name}"  # Construct base path to character's sprite folder
        return {
            "idle": f"{base_path}/idle.png",
            "run": f"{base_path}/run.png",
            "jump": f"{base_path}/jump.png",
            "double_jump": f"{base_path}/double_jump.png"
        }
    
    def __previous_character(self):
        """Switch to the previous character in the list."""
        # Update selected character index to the previous one, looping back to the last character if needed
        self.selected_character = (self.selected_character - 1) % len(self.character_directories)
        # Reload the player character with new sprites based on selected character
        self.player = Character(self.__load_character_sprites(self.character_directories[self.selected_character]))
    
    def __next_character(self):
        """Switch to the next character in the list."""
        # Update selected character index to the next one, looping to the first character if needed
        self.selected_character = (self.selected_character + 1) % len(self.character_directories)
        # Reload the player character with new sprites based on selected character
        self.player = Character(self.__load_character_sprites(self.character_directories[self.selected_character]))
    
    def __back_to_menu(self):
        """Save the selected character and return to the main menu."""
        with Database() as db:
            # Update the database with the selected character's name
            db.updateCharacter(self.character_directories[self.selected_character])
        self.menu.run()  # Return to the main menu by calling the `run` method of the menu
    
    def draw(self):
        """Draw everything on the screen."""
        self.screen.blit(self.background_image, (0, 0))  # Draw the background image on the screen
        # Draw all buttons on the screen (left, right, and save & exit)
        self.button_left.draw(self.screen)
        self.button_right.draw(self.screen)
        self.button_back.draw(self.screen)

        self.player.update()  # Update the player's animation state
        
        # Get the current frame of the character's animation
        original_frame = self.player.sprites[self.player.current_action][self.player.current_frame]
        # Enlarge the character sprite to make it more visible for selection
        enlarged_frame = pygame.transform.scale(original_frame, (96, 96))  # Scale sprite to a larger size
        # Draw the enlarged sprite in the center of the screen
        self.screen.blit(enlarged_frame, (WIDTH // 2 - 48, HEIGHT // 2 - 96))

        pygame.display.flip()  # Update the display with the drawn elements
    
    def run(self):
        """Main loop to run the customisation screen."""
        while True:
            self.clock.tick(FPS)  # Control the frame rate of the game loop
            for event in pygame.event.get():  # Loop through all events (key presses, mouse clicks, etc.)
                if event.type == pygame.QUIT:  # If the window is closed
                    pygame.quit()  # Quit pygame
                    exit()  # Exit the program

                if event.type == pygame.KEYDOWN:  # If a key is pressed down
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:  # Left arrow or 'A' to go to previous character
                        self.__previous_character()
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:  # Right arrow or 'D' to go to next character
                        self.__next_character()
                    elif event.key == pygame.K_q:  # 'Q' key to save the character and return to the main menu
                        with Database() as db:
                            db.updateCharacter(self.character_directories[self.selected_character])  # Save selected character
                        self.menu.run()  # Go back to the main menu

                # Handle all button events (clicks, mouse movements, etc.)
                self.button_left.handle_event(event)
                self.button_right.handle_event(event)
                self.button_back.handle_event(event)

            self.draw()  # Draw all elements on the screen after handling events
