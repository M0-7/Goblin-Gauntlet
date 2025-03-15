import pygame
from button import Button
from variables import WIDTH, HEIGHT, BIG_FONT_COLOR, BIG_FONT_SIZE, FONT_COLOR, FONT_SIZE

class GameOver:
    def __init__(self, menu, play, score):
        self.menu = menu
        self.play = play
        self.score = score
        self.clock = pygame.time.Clock()
        
        # Initialize the screen and set the window caption
        try:
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
            pygame.display.set_caption("Game Over")
        except Exception as e:
            print(f"Error initializing the screen: {e}")

        # Load background
        self.background_image = self.load_background("./assets/Background/fire.png")

        # Button to play again and return to main menu 
        try:
            self.play_again_button = Button("Play Again", WIDTH // 2 - 150, HEIGHT - 200, 300, 70, self.play_again)
            self.main_menu_button = Button("Main Menu", WIDTH // 2 - 150, HEIGHT - 120, 300, 70, self.return_to_menu)
        except Exception as e:
            print(f"Error initializing buttons: {e}")
            exit()

    def load_background(self, image_path):
        """Load the background image."""
        try:
            image = pygame.image.load(image_path).convert()
            return pygame.transform.scale(image, (WIDTH, HEIGHT))
        except Exception as e:
            print(f"Error loading background image: {e}")
            exit()

    def return_to_menu(self):
        """Return to the main menu."""
        try:
            self.menu.run()
        except Exception as e:
            print(f"Error returning to the menu: {e}")
            exit()
    
    def play_again(self):
        """Start a new game."""
        try:
            self.play.startgame()
            self.play.run()
        except Exception as e:
            print(f"Error starting a new game: {e}")
            exit()

    def draw_text(self, text, y, size, color):
        """Draw text on the screen."""
        try:
            font = pygame.font.SysFont("JetBrains Mono", size, bold=True)
            text_surface = font.render(text, True, color)
            text_rect = text_surface.get_rect(center=(WIDTH // 2, y))
            self.screen.blit(text_surface, text_rect)
        except Exception as e:
            print(f"Error rendering text: {e}")

    def draw(self):
        """Draw all elements on the screen."""
        try:
            self.screen.blit(self.background_image, (0, 0))
            self.draw_text("You Died", HEIGHT // 3, BIG_FONT_SIZE, BIG_FONT_COLOR)
            self.draw_text(f"Final Score: {int(self.score)}", HEIGHT // 2, FONT_SIZE, (255, 255, 255))  # White color
            self.play_again_button.draw(self.screen)
            self.main_menu_button.draw(self.screen)
            pygame.display.flip()
        except Exception as e:
            print(f"Error drawing elements on the screen: {e}")

    def run(self):
        """Main loop for the Game Over screen."""
        while True:
            try:
                self.clock.tick(60)  # Limit frame rate to 60 FPS
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()
                    self.main_menu_button.handle_event(event)
                    self.play_again_button.handle_event(event)

                self.draw()
            except Exception as e:
                print(f"Error in game loop: {e}")
                exit()

