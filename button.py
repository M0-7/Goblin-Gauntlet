import pygame
from variables import BUTTON_COLOR, FONT_SIZE, FONT_COLOR, BUTTON_HOVER_COLOR

class Button:
    def __init__(self, text, x, y, width, height, action):
        """Initializes a button with text, position, size, and an action callback."""
        self.rect = pygame.Rect(x, y, width, height)  # Define button rectangle
        self.color = BUTTON_COLOR  # Default button color
        self.hover_color = BUTTON_HOVER_COLOR  # Color when hovered
        self.text = text  # Button text

        # Set up font and render text
        self.font = pygame.font.SysFont("JetBrains Mono", FONT_SIZE, bold=True)
        self.text_surface = self.font.render(self.text, True, FONT_COLOR)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center) # Center text

        self.action = action  # Function to call when button is clicked

    def draw(self, screen):
        """Draws the button with hover effect."""
        mouse_pos = pygame.mouse.get_pos()  # Get current mouse position
        
        # Change color if mouse is over the button
        color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color

        # Draw the button with rounded corners
        pygame.draw.rect(screen, color, self.rect, border_radius=10)

        # Draw the text on the button
        screen.blit(self.text_surface, self.text_rect) # Text surface is the text, text rect is the destination

    def handle_event(self, event):
        """Handles mouse click events to trigger the button action."""
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.action()  # Call the assigned action function when clicked
