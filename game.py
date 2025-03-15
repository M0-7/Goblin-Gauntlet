import pygame
import time
import random
from gameMusic import Effects
from database import Database
from character import Character
from variables import WIDTH,HEIGHT,FPS,BG_COLOR,BIG_FONT_COLOR,BIG_FONT_SIZE
from lava import Lava
from gameOver import GameOver
from enemies import generate_random_enemy
from fruits import Fruit
from traps import generate_random_trap
from functools import lru_cache

# Initialize pygame and music
pygame.init()
effects = Effects()

# Play class
class Play:
    def __init__(self,menu,music):
        self.menu = menu
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Play")
        # Music
        self.music = music
        self.music.play_music("play")
        self.startgame()

    # Load the selected character from file
    def startgame(self):
        with Database() as db:
            selected_character = db.getCharacter()

        # Define the paths to the character's sprite sheets for different actions
        action_paths = {
            "idle": f"./assets/MainCharacters/{selected_character}/idle.png",  # Path to idle sprite sheet
            "run": f"./assets/MainCharacters/{selected_character}/run.png",  # Path to run sprite sheet
            "jump": f"./assets/MainCharacters/{selected_character}/jump.png",  # Path to jump sprite sheet
            "double_jump": f"./assets/MainCharacters/{selected_character}/double_jump.png"  # Path to double jump sprite sheet
        }
        self.player = Character(action_paths)
        self.background_image = self.load_background("./assets/Background/2.jpg")
        self.terrain_image = self.load_background("./assets/Background/blue.png")
        self.terrain_tiles = []
        self.init_terrain()
        self.camera_x = 0
        self.gravity = 0.5
        self.velocity_y = 0
        self.on_ground = False
        self.jump_count = 0
        self.first_jump_strength = -10
        self.second_jump_strength = -12
        self.last_jump_time = 0
        self.double_jump_delay = 0.2
        # Distance
        self.score = 0  # Initialize distance traveled
        self.last_position_x = self.player.position[0]  # Track the last x position
        self.pixels_per_meter = 100
        self.speed = 6
        self.speed_cooldown = False
        # Health System
        self.max_health = 100
        self.current_health = 100  # Player starts with full health
        self.immunity = False
        # Lava
        self.lava = Lava(frames_directory="./assets/Lava",terrain_height=self.terrain_image.get_height())
        self.last_damage_time = 0  # Track last time the player took lava damage
        self.lava_damage = 20
        self.damage_interval = 0.8  # Seconds before taking damage again
        # Enemies
        self.enemies = []
        self.spawn_timer = 0  # Timer to control enemy spawning
        self.spawn_interval = 3000  # Time in milliseconds between spawns
        self.last_collision_time = 0
        self.collision_delay = 1000  # 1 second delay
        # Fruit
        self.fruit_system = Fruit("./assets/Fruits/", frame_count=14, frame_width=32, frame_height=32)
        # Traps
        self.last_trap_hit_time = 0  # Track last time the player hit a trap
        self.trap_hit_cooldown = 1.0  # 1 second cooldown before taking damage again
        # Traps
        self.trap_spawn_timer = 0  # Timer to control trap spawning
        self.trap_spawn_interval = 8000  # Time in milliseconds between trap spawns
        self.traps = []  # List to hold active traps

    def draw_health_bar(self):
        """Draws hearts in the top-right corner to represent health."""
        heart_sheet = pygame.image.load("./assets/Health/heart.png").convert_alpha()  # Load the heart sprite sheet
        heart_full = heart_sheet.subsurface((0, 0, 32, 32))  # Full heart image
        heart_half = heart_sheet.subsurface((32, 0, 32, 32))  # Half heart image
        heart_empty = heart_sheet.subsurface((64, 0, 32, 32))  # Empty heart image
        
        heart_size = 32  # Adjust heart size
        spacing = 3  # Space between hearts
        max_hearts = 5  # Total hearts available
        hearts_to_display = self.current_health // 20  # 20 HP per heart

        for i in range(max_hearts):
            x = WIDTH - (heart_size + spacing) * (max_hearts - i) - 20
            y = 20  # Align at the top

            if i < hearts_to_display:
                self.screen.blit(pygame.transform.scale(heart_full, (heart_size, heart_size)), (x, y))
            elif i == hearts_to_display and self.current_health % 20 != 0:
                self.screen.blit(pygame.transform.scale(heart_half, (heart_size, heart_size)), (x, y))
            else:
                self.screen.blit(pygame.transform.scale(heart_empty, (heart_size, heart_size)), (x, y))

    def take_damage(self, amount):
        """Reduces health and triggers red flash effect"""
        self.player.speed_cooldown = False
        if self.immunity == True:
            self.immunity = False
            self.player.take_immunity_effect()
            self.speed = 8
        else:
            self.current_health = max(0, self.current_health - amount)
            self.speed = 6
            self.player.take_damage_effect()  # Activate red highlight
        if self.current_health <= 0:
            game_over_screen = GameOver(self.menu,self,self.score)
            effects.kill_effects()
            self.music.play_music("menu")
            game_over_screen.run()
    
    def add_health(self, amount, fruit="yes"):
        if self.current_health >= 100:
            if fruit == "yes":
                if self.speed_cooldown == True:
                    self.speed_cooldown = False
                    self.speed = 8
                    self.immunity = False
                    self.player.speed_cooldown = False
                elif self.speed_cooldown == False:
                    self.speed = 10
                    self.score += 10
                    self.speed_cooldown = True
                    self.immunity = True
                    self.player.speed_cooldown = True
        else:
            self.current_health += amount
        self.score += 10

    def load_background(self, image_path):
        try:
            return pygame.image.load(image_path).convert()
        except FileNotFoundError:
            print("Background image file not found")
            exit()
    
    def init_terrain(self):
        for i in range(WIDTH // self.terrain_image.get_width() + 1):
            self.terrain_tiles.append(i * self.terrain_image.get_width())

    def generate_terrain(self):
        last_tile = self.terrain_tiles[-1]
        if last_tile < self.camera_x + WIDTH:
            self.terrain_tiles.append(last_tile + self.terrain_image.get_width())

    def apply_gravity(self):
        self.velocity_y += self.gravity
        self.player.position[1] += self.velocity_y

        sprite_height = 64
        if self.player.position[1] + sprite_height >= HEIGHT - self.terrain_image.get_height():
            self.player.position[1] = HEIGHT - self.terrain_image.get_height() - sprite_height
            self.velocity_y = 0
            self.on_ground = True
            self.jump_count = 0
        else:
            self.on_ground = False

    def handle_input(self):
        keys = pygame.key.get_pressed()
        current_time = time.time()

        # Store the current position before moving
        current_position_x = self.player.position[0]

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.position[0] -= self.speed
            self.player.set_action("run")
            self.player.facing_left = True
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.position[0] += self.speed
            self.player.set_action("run")
            self.player.facing_left = False

            # Update distance traveled
            distance_moved = abs(current_position_x - self.player.position[0])
            self.score += distance_moved / self.pixels_per_meter
        else:
            self.player.set_action("idle")

        if keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]:
            if self.on_ground:
                effects.play_effect("jump")
                self.velocity_y = self.first_jump_strength
                self.jump_count = 1
                self.player.set_action("jump")
                self.last_jump_time = current_time
            elif not self.on_ground and self.jump_count == 1 and current_time - self.last_jump_time >= self.double_jump_delay:
                effects.play_effect("jump")
                self.velocity_y = self.second_jump_strength
                self.jump_count = 2
                if self.player.current_action != "double_jump" or self.player.current_frame >= len(self.player.sprites["double_jump"]) - 1:  # Only set if not already in double jump animation
                    self.player.set_action("double_jump")
                self.last_jump_time = current_time
        
        if keys[pygame.K_q]:
            self.menu.run()
            effects.kill_effects()

        self.player.position[0] = max(0, self.player.position[0])
    
    def draw_distance_counter(self):
        font = pygame.font.SysFont("JetBrains Mono", 25, bold=True)  # You can adjust the font size
        distance_text = f"Score: {int(self.score)}"  # Format to 2 decimal places
        text_surface = font.render(distance_text, True, (255, 255, 255))  # White color
        self.screen.blit(text_surface, (20, 20))  # Position it at the top-left corner
    
    def damage_jump(self, current_time):
        self.velocity_y = self.first_jump_strength
        self.jump_count = 2
        self.player.set_action("jump")
        self.last_jump_time = current_time

    def check_lava_collision(self):
        """Check if the player collides with the lava and apply damage with a cooldown."""
        player_rect = pygame.Rect(self.player.position[0], self.player.position[1], 64, 64)

        for tile in self.lava.tiles:
            lava_rect = pygame.Rect(tile[0], tile[1], self.lava.tile_width, self.lava.tile_height)
            if player_rect.colliderect(lava_rect):
                current_time = time.time()
                if current_time - self.last_damage_time > self.damage_interval:
                    self.take_damage(self.lava_damage)
                    self.damage_jump(current_time)
                    self.last_damage_time = current_time  # Reset cooldown timer
                    self.speed = 7
                break

    def draw_fruits(self):
        for fruit in self.fruit.fruits:
            fruit_image = pygame.image.load(fruit[0]).convert_alpha()  # Load the fruit image
            self.screen.blit(fruit_image, (fruit[1] - self.camera_x, fruit[2]))  # Draw the fruit
        
    def draw(self):
        self.screen.fill(BG_COLOR)
    
        # Draw the background
        background_width = self.background_image.get_width()
        background_height = self.background_image.get_height()
        for x in range(self.camera_x // background_width, (self.camera_x + WIDTH) // background_width + 1):
            for y in range(HEIGHT // background_height + 1):  # Tile vertically across the screen
                self.screen.blit(self.background_image, (x * background_width - self.camera_x, y * background_height))
    
        # Draw the terrain
        for x in self.terrain_tiles:
            self.screen.blit(self.terrain_image, (x - self.camera_x, HEIGHT - self.terrain_image.get_height()))
    
        # Draw the player
        self.player.update()
        self.player.draw(self.screen, (self.player.position[0] - self.camera_x, self.player.position[1]))

        # Draw lava
        self.lava.draw(self.screen, self.camera_x)

        # Draw the health bar
        self.draw_health_bar()

        # Draw the distance counter
        self.draw_distance_counter()

        # Draws the fruit on the screen
        self.fruit_system.draw(self.screen, self.camera_x)

        # Enemy
        # Draw all enemies
        for enemy in self.enemies:
            enemy.draw(self.screen, self.camera_x, self.lava.tiles)

        # Traps
        # Draw traps
        # Draw traps
        for trap in self.traps:
            trap.draw(self.screen, self.camera_x)

        pygame.display.flip()

    def run(self):
        while True:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            self.handle_input()
            self.apply_gravity()
            self.check_lava_collision()

            # Player position for checking collision
            player_rect = pygame.Rect(self.player.position[0], self.player.position[1], 64, 64)

            # Update camera position
            self.camera_x = max(0, self.player.position[0] - WIDTH // 2)

            # Update lava
            self.lava.update(self.camera_x)

            self.generate_terrain()
            self.draw()

            # Draw lava
            self.lava.draw(self.screen, self.camera_x)

            # Update enemy postion
            # Spawn new enemies if needed
            current_time = pygame.time.get_ticks()
            if (current_time - self.spawn_timer > self.spawn_interval) and len(self.enemies) < 1:
                self.enemies.extend(generate_random_enemy(self.camera_x))  # Add new enemies to the list
                self.spawn_timer = current_time  # Reset the spawn timer

            # Update all enemies
            for enemy in self.enemies[:]:
                enemy.update(self.camera_x)

                # Check if the enemy is off-screen and remove it
                if enemy.rect.left < self.camera_x: 
                    self.enemies.remove(enemy)  # Remove the enemy from the list
                
                if enemy.is_visible == False:
                    self.enemies.remove(enemy)

            # Fruit updates and collison detection
            self.fruit_system.update(HEIGHT - self.terrain_image.get_height(),self.camera_x)            
            if self.fruit_system.check_collision(player_rect):
                self.add_health(10,fruit="yes")
            
            # Collision detetction with enemy
            for enemy in self.enemies:
                if enemy.check_collision(player_rect):
                    current_time = pygame.time.get_ticks()

                    # Check if the collision is from above
                    if (player_rect.bottom > enemy.rect.top and player_rect.top < enemy.rect.top) and self.velocity_y > 0:
                        if not enemy.is_hit:
                            enemy.take_damage()
                        self.damage_jump(current_time)
                        self.speed = 7
                        self.last_collision_time = current_time
                    else:
                        if current_time - self.last_collision_time > self.collision_delay:
                            with Database() as db:
                                self.take_damage(db.getDamageEnemy(enemy.type))  # Take damage if there is a collision
                            self.damage_jump(current_time)
                            self.last_collision_time = current_time  # Reset collision timer
            
            ## Spawn new traps if needed
            current_time = pygame.time.get_ticks()
            if (current_time - self.trap_spawn_timer > self.trap_spawn_interval):
                self.traps.append(generate_random_trap())  # Call the method to spawn traps
                self.trap_spawn_timer = current_time  # Reset the spawn timer
            
            for trap in self.traps[:]:
                trap.update(HEIGHT - self.terrain_image.get_height(), self.camera_x)

                if trap.trap_position:  # Only create a rect if the trap has been spawned
                    trap_rect = pygame.Rect(trap.trap_position[0], trap.trap_position[1], trap.trap_width, trap.trap_height)

                    # Check if the trap is off-screen and remove it
                    if trap_rect.left < self.camera_x: 
                        self.traps.remove(trap)  # Remove the trap from the list

            # Check for trap collisions
            current_time = time.time()
            for trap in self.traps:
                if trap.check_collision(player_rect):
                    if current_time - self.last_trap_hit_time > self.trap_hit_cooldown:
                        with Database() as db:
                            self.take_damage(db.getDamageTrap(trap.type))
                        self.damage_jump(current_time)
                        self.last_trap_hit_time = current_time

            pygame.display.flip()