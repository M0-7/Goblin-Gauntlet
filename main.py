import pygame
from gameMusic import Music
from button import Button
from settings import Settings
from customise import Customise
from game import Play
from variables import WIDTH, HEIGHT, FPS, BIG_FONT_COLOR, BIG_FONT_SIZE

# Initialize pygame
pygame.init()

# Menu class
class Menu:
    def __init__(self):
        # Initialize clock for FPS control
        self.clock = pygame.time.Clock()
        
        # Create the game window
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Main Menu")

        # Load background image
        self.background_image = self._load_background("./assets/Background/fire.png")

        # Buttons for the menu (text, x, y, width, height, callback function)
        self.button1 = Button("Play", 300, 220, 300, 70, self.play_button)
        self.button2 = Button("Customise", 300, 300, 300, 70, self.customise_button)
        self.button3 = Button("Settings", 300, 380, 300, 70, self.settings_button)
        
        # Initialize and play menu music
        self.music = Music()
        self.music.play_music("menu")

    def _load_background(self, image_path):
        """Private method to load and scale the background image."""
        try:
            image = pygame.image.load(image_path).convert()  # .convert() loads the image in an ideal format for pygame
            return pygame.transform.scale(image, (WIDTH, HEIGHT))
        except FileNotFoundError:
            print(f"Background image file not found: {image_path}")
            exit()
        except pygame.error as e:
            print(f"Error loading background image: {e}")
            exit()

    # Button callback functions
    def play_button(self):
        """Starts the game when 'Play' is clicked."""
        game = Play(menu, self.music)
        game.run()

    def customise_button(self):
        """Opens the customization menu."""
        customise = Customise(menu)
        customise.run()

    def settings_button(self):
        """Opens the settings menu."""
        setting = Settings(menu)
        setting.run()

    def draw_big_text(self, text):
        """Draws large text at a given y-coordinate."""
        font = pygame.font.SysFont("JetBrains Mono", BIG_FONT_SIZE, bold=True)
        text_surface = font.render(text, True, BIG_FONT_COLOR)
        text_rect = text_surface.get_rect(center=(WIDTH // 2, 120))
        self.screen.blit(text_surface, text_rect)

    def draw(self):
        """Draws the menu screen elements."""
        try:
            self.screen.blit(self.background_image, (0, 0))
            self.draw_big_text("Lava Rush")
            self.button1.draw(self.screen)
            self.button2.draw(self.screen)
            self.button3.draw(self.screen)
            pygame.display.flip()  # Updates the display
        except Exception as e:
            print(f"Error drawing the menu: {e}")

    def run(self):
        """Main loop for the menu."""
        while True:
            self.clock.tick(FPS)  # Limit frame rate
            
            # Event handling loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                
                # Handle button interactions
                self.button1.handle_event(event)
                self.button2.handle_event(event)
                self.button3.handle_event(event)
            
            # Draw everything on the screen
            self.draw()

# Run the menu if this script is executed directly
if __name__ == "__main__":
    menu = Menu()
    menu.run()