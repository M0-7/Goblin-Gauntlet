import pygame
import random
from gameMusic import Effects
from variables import HEIGHT,TERRAIN,WIDTH
from database import Database
from functools import lru_cache

effects = Effects()

previous_land_enemy = None
previous_air_enemy = None

class LandEnemy:
    def __init__(self, x, y, sprite_sheet,name, frame_width, frame_height):
        self.sprite_sheets = sprite_sheet
        self.current_animation = "run"
        # Setting frame width and height
        self.frame_width = frame_width
        self.frame_height = frame_height 
        self.type = name
        self.frames = self.load_frames(self.sprite_sheets[self.current_animation])
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = random.randint(2, 4)
        self.camera_speed = 1

        self.last_frame_time = pygame.time.get_ticks()
        self.frame_rate = 100  # Time between frames (in milliseconds)

        # Die logic
        self.is_hit = False
        self.is_visible = True
        self.hit_duration = 2000  # Duration of the hit animation in milliseconds
        self.hit_start_time = 0  # Time when the hit animation starts

    @lru_cache(maxsize=None)
    def load_frames(self, sprite_sheet_path):
        """Extract individual frames from a sprite sheet and scale them up."""
        sprite_sheet = pygame.image.load(sprite_sheet_path).convert_alpha()
        frames = []
        for i in range(sprite_sheet.get_width() // self.frame_width):
            frame = sprite_sheet.subsurface(pygame.Rect(i * self.frame_width, 0, self.frame_width, self.frame_height))
            # Scale up the frame
            scaled_frame = pygame.transform.scale(frame, (self.frame_width * 2, self.frame_height * 2))
            frames.append(scaled_frame)
        return frames
    
    def take_damage(self):
        """Trigger the hit animation."""
        self.is_hit = True
        self.hit_start_time = pygame.time.get_ticks()  # Record the time when hit
        self.set_animation("hit")  # Set the animation to hit
        self.rect.y -= 2 # Ensures enemy sprite stays on top of the terrain as the hit animation goes downwards

    def update(self, camera_x):
        """Move enemy from right to left and update animation."""
        now = pygame.time.get_ticks()

        # Check if the enemy is in the hit state
        if self.is_hit:
            # Check if the hit animation duration has passed
            if now - self.hit_start_time >= self.hit_duration:
                self.is_visible = False  # Make the enemy invisible
            else:
                # If still in hit state, use the hit frames
                self.set_animation("hit")

        # Update animation frame every 'frame_rate' milliseconds
        if now - self.last_frame_time >= self.frame_rate and self.is_visible:
            self.last_frame_time = now
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]  # Update the image here

        # Move the enemy
        if self.is_visible and not self.is_hit:
            self.rect.x -= self.speed
            if self.rect.right - camera_x < 0:
                self.rect.x = random.randint(800, 1200) + camera_x  # Respawn off-screen

    def draw(self, screen, camera_x, lava_tiles):
        if self.is_visible:
            player_rect = pygame.Rect(self.rect.x, self.rect.y, self.image.get_width(), self.image.get_height())
            for tile in lava_tiles:
                lava_rect = pygame.Rect(tile[0], tile[1], 32, 32)
                if player_rect.colliderect(lava_rect):
                    effects.play_effect("bbq")
                    return  # don't draw the enemy if it's colliding with lava
            screen.blit(self.image, (self.rect.x - camera_x, self.rect.y))

    def check_collision(self, player_rect):
        """Check if enemy collides with the player."""
        return self.rect.colliderect(player_rect)

    def set_animation(self, animation):
        """Change the current animation state."""
        if animation in self.sprite_sheets and animation != self.current_animation:
            self.current_animation = animation
            self.frames = self.load_frames(self.sprite_sheets[self.current_animation])
            self.current_frame = 0
            self.last_frame_time = pygame.time.get_ticks()

class Chicken(LandEnemy):
    def __init__(self,x,y,name="Chicken",frame_width=32,frame_height=34):
        sprite_sheets = {
            "idle": "./assets/Enemies/Chicken/Idle (32x34).png",
            "run": "./assets/Enemies/Chicken/Run (32x34).png",
            "hit": "./assets/Enemies/Chicken/Hit (32x34).png"
        }
        super().__init__(x, y, sprite_sheets,name,frame_width,frame_height)
        effects.play_effect("chicken")
    
    def spawn(camera_x):
        """Spawn a Chicken at a random x position and a fixed y position."""
        x = camera_x + WIDTH + random.randint(100, 500)  # Random x position
        y = HEIGHT - TERRAIN  # Fixed y position for Chicken (adjust as needed)
        return Chicken(x, y)

class Rino(LandEnemy):
    def __init__(self,x,y,name="Rino",frame_width=52,frame_height=34):
        sprite_sheets = {
            "idle": "./assets/Enemies/Rino/Idle (52x34).png",
            "run": "./assets/Enemies/Rino/Run (52x34).png",
            "hit": "./assets/Enemies/Rino/Hit (52x34).png"
        }
        super().__init__(x, y, sprite_sheets,name,frame_width,frame_height)
        self.speed = 5
        effects.play_effect("rino")
    
    def spawn(camera_x):
        """Spawn a Rino at a random x position and a fixed y position."""
        x = camera_x + WIDTH + random.randint(100, 500)  # Random x position
        y = HEIGHT - TERRAIN  # Fixed y position for Rino (adjust as needed)
        return Rino(x, y)

class Bunny(LandEnemy):
    def __init__(self,x,y,name="Bunny",frame_width=34,frame_height=44):
        sprite_sheets = {
            "idle": "./assets/Enemies/Bunny/Idle (34x44).png",
            "run": "./assets/Enemies/Bunny/Run (34x44).png",
            "hit": "./assets/Enemies/Bunny/Hit (34x44).png",
            "jump": "./assets/Enemies/Bunny/Jump.png"  # Use the uploaded jump sprite
        }
        super().__init__(x, y, sprite_sheets,name,frame_width,frame_height)
        effects.play_effect("bunny")

        # Jump logic
        self.is_jumping = False
        self.jump_start_time = pygame.time.get_ticks()
        self.jump_cooldown = 3000  # Jump every 3 seconds
        self.jump_velocity = -10
        self.gravity = 0.5
        self.vertical_speed = 0
    
    def spawn(camera_x):
        """Spawn a Bunny at a random x position and a fixed y position."""
        x = camera_x + random.randint(800, 1200)
        y = HEIGHT - TERRAIN - 21
        return Bunny(x, y)
    
    def update(self, camera_x):
        """Move enemy from right to left, update animation, and handle jumping."""
        now = pygame.time.get_ticks()

        # Check if the bunny is in the hit state
        if self.is_hit:
            # Check if the hit animation duration has passed
            if now - self.hit_start_time >= self.hit_duration:
                self.is_visible = False  # Reset to run animation or any other state
            else:
                # If still in hit state, use the hit frames
                self.set_animation("hit")
                #return  # Skip the r# Check if the hit animation duration has passed
            if now - self.hit_start_time >= self.hit_duration:
                self.set_animation("run")  # Reset to run animation or any other state
            else:
                # If still in hit state, use the hit frames
                self.set_animation("hit")
                #return  # Skip the rest of the update if in hit statest of the update if in hit state

        # Update animation frame every 'frame_rate' milliseconds
        if now - self.last_frame_time >= self.frame_rate and self.is_visible:
            self.last_frame_time = now
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]

        # Move left
        #if not self.set_animation == "hit":
        if self.is_visible and not self.is_hit:
            self.rect.x -= self.speed
            if self.rect.right - camera_x < 0:
                self.rect.x = random.randint(800, 1200) + camera_x

        # Handle jumping
        if now - self.jump_start_time >= self.jump_cooldown and self.is_visible and not self.is_hit:
            self.is_jumping = True
            self.vertical_speed = self.jump_velocity
            self.set_animation("jump")
            self.jump_start_time = now  # Reset timer

        if self.is_jumping and self.is_visible:
            self.rect.y += self.vertical_speed
            self.vertical_speed += self.gravity
            if self.rect.y >= HEIGHT - TERRAIN - 21:
                self.rect.y = HEIGHT - TERRAIN - 21
                self.is_jumping = False
                self.set_animation("run")

class AirEnemy:
    def __init__(self, x, y, sprite_sheet,name, frame_width, frame_height):
        self.sprite_sheets = sprite_sheet
        self.current_animation = "fly"
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.type = name
        self.frames = self.load_frames(self.sprite_sheets[self.current_animation], self.frame_width, self.frame_height)
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = random.randint(1, 3)  # Enemy moves slower
        self.camera_speed = 1
        self.direction = random.choice([-1, 1])  # Random vertical movement direction

        self.last_frame_time = pygame.time.get_ticks()
        self.frame_rate = 100  # Time between frames (in milliseconds)

        # Die logic
        self.is_hit = False
        self.is_visible = True
        self.hit_duration = 2000  # Duration of the hit animation in milliseconds
        self.hit_start_time = 0  # Time when the hit animation starts
    
    def take_damage(self):
        """Trigger the hit animation."""
        self.is_hit = True
        self.hit_start_time = pygame.time.get_ticks()  # Record the time when hit
        self.set_animation("hit")  # Set the animation to hit

    @lru_cache(maxsize=None)
    def load_frames(self, sprite_sheet_path, frame_width, frame_height):
        """Extract individual frames from a sprite sheet and scale them up."""
        sprite_sheet = pygame.image.load(sprite_sheet_path)
        frames = []
        for i in range(sprite_sheet.get_width() // frame_width):
            frame = sprite_sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
            # Scale up the frame
            scaled_frame = pygame.transform.scale(frame, (frame_width * 2, frame_height * 2))
            frames.append(scaled_frame)
        return frames

    def update(self, camera_x):
        """Move the enemy from right to left with vertical movement and update animation."""
        now = pygame.time.get_ticks()

        if self.is_hit:
        # Check if the hit animation duration has passed
            if now - self.hit_start_time >= self.hit_duration:
                self.is_visible = False  # Make the enemy invisible
            else:
                # If still in hit state, use the hit frames
                self.set_animation("hit")
                self.rect.y += 2 

        # Update animation frame every 'frame_rate' milliseconds
        if now - self.last_frame_time >= self.frame_rate and self.is_visible:
            self.last_frame_time = now
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]  # Update the image here

        # Move the enemy in a "flying" path (horizontal movement with slight vertical oscillation)
        self.rect.x -= self.speed
        self.rect.y += self.direction  # Moves slightly up or down

        # Move the enemy in a "flying" path (horizontal movement with slight vertical oscillation)
        if self.is_visible and not self.is_hit:
            self.rect.x -= self.speed
            self.rect.y += self.direction  # Moves slightly up or down

            # Change direction randomly
            if random.randint(0, 50) == 0:
                self.direction *= -1

            if self.rect.right - camera_x < 0:
                self.rect.x = random.randint(800, 1200) + camera_x  # Respawn off-screen
                self.rect.y = random.randint(100, 300)  # Reset y position
                self.set_animation("fly")  # Reset to flying animation

    def draw(self, screen, camera_x, lava_tiles):
        if self.is_visible:
            player_rect = pygame.Rect(self.rect.x, self.rect.y, self.image.get_width(), self.image.get_height())
            for tile in lava_tiles:
                lava_rect = pygame.Rect(tile[0], tile[1], self.frame_height, self.frame_width)
                if player_rect.colliderect(lava_rect):
                    effects.play_effect("bbq")
                    return  # Don't draw the enemy if it's colliding with lava
            screen.blit(self.image, (self.rect.x - camera_x, self.rect.y))

    def check_collision(self, player_rect):
        """Check if enemy collides with the player."""
        return self.rect.colliderect(player_rect)

    def set_animation(self, animation):
        """Change the current animation state."""
        if animation in self.sprite_sheets and animation != self.current_animation:
            self.current_animation = animation
            self.frames = self.load_frames(self.sprite_sheets[self.current_animation], self.frame_width, self.frame_height)
            self.current_frame = 0
            self.last_frame_time = pygame.time.get_ticks()

class BlueBird(AirEnemy):
    def __init__(self,x,y,name="BlueBird",frame_width=32,frame_height=32):
        sprite_sheets = {
            "fly": "./assets/Enemies/BlueBird/Flying (32x32).png",
            "hit": "./assets/Enemies/BlueBird/Hit (32x32).png"
        }
        super().__init__(x, y, sprite_sheets,name,frame_width,frame_height)
        effects.play_effect("bat")
    
    def spawn(camera_x):
        """Spawn a Bird at a random x position and a fixed y position."""
        x = camera_x + WIDTH + random.randint(100, 500)
        y = ((HEIGHT - TERRAIN) // 2) + random.randint(10,50)
        return BlueBird(x, y)

class Bat(AirEnemy):
    def __init__(self,x,y,name="Bat",frame_width=46,frame_height=30):
        sprite_sheets = {
            "idle": "./assets/Enemies/Bat/Idle (46x30).png",
            "fly": "./assets/Enemies/Bat/Flying (46x30).png",
            "hit": "./assets/Enemies/Bat/Hit (46x30).png"
        }
        super().__init__(x, y, sprite_sheets,name,frame_width,frame_height)
        effects.play_effect("bat")
    
    def spawn(camera_x):
        """Spawn a Bat at a random x position and a fixed y position."""
        x = camera_x + WIDTH + random.randint(100, 500)
        y = ((HEIGHT - TERRAIN) // 2) + random.randint(10,50)
        return Bat(x, y)

class Bee(AirEnemy):
    def __init__(self,x,y,name="Bee",frame_width=36,frame_height=34):
        sprite_sheets = {
            "fly": "./assets/Enemies/Bee/Idle (36x34).png",
            "attack": "./assets/Enemies/Bee/Attack (36x34).png",
            "hit": "./assets/Enemies/Bee/Hit (36x34).png"
        }
        super().__init__(x, y, sprite_sheets,name,frame_width,frame_height)
        effects.play_effect("bee")
    
    def spawn(camera_x):
        """Spawn a Bee at a random x position and a fixed y position."""
        x = camera_x + WIDTH + random.randint(100, 500) 
        y = ((HEIGHT - TERRAIN) // 2) + random.randint(10,50)
        return Bee(x, y)

enemy_land = [Bunny,Chicken,Rino]
enemy_air = [Bee,Bat,BlueBird]

def generate_random_enemy(camera_x):
    """Generate a random enemy while blacklisting the previously chosen one."""
    global previous_land_enemy, previous_air_enemy

    # Filter available enemies to exclude the previous one
    available_land_enemies = [enemy for enemy in enemy_land if enemy != previous_land_enemy]
    available_air_enemies = [enemy for enemy in enemy_air if enemy != previous_air_enemy]

    # Pick a random enemy from the filtered lists
    land_enemy = random.choice(available_land_enemies)
    air_enemy = random.choice(available_air_enemies)

    # Update blacklist (store the current choices for next time)
    previous_land_enemy = land_enemy
    previous_air_enemy = air_enemy

    # Return different amounts of enemies depending on user's choice in settings
    with Database() as db:
        number = db.getNumberofEnemies()
    
    match number:
        case 1:
            available_air_enemies.extend(available_land_enemies)
            return [random.choice(available_air_enemies).spawn(camera_x)]
        case 2:
            return [land_enemy.spawn(camera_x),air_enemy.spawn(camera_x)]
        case 3:
            spawning_list = [
                land_enemy.spawn(camera_x),
                air_enemy.spawn(camera_x)
            ]
            available_land_enemies.remove(land_enemy)
            available_air_enemies.remove(air_enemy)
            available_air_enemies.extend(available_air_enemies)
            spawning_list.append(random.choice(available_air_enemies).spawn(camera_x))
        case 4:
            spawning_list = [
                land_enemy.spawn(camera_x),
                air_enemy.spawn(camera_x)
            ]
            available_land_enemies.remove(land_enemy)
            available_air_enemies.remove(air_enemy)
            spawning_list.append(random.choice(available_air_enemies).spawn(camera_x))
            spawning_list.append(random.choice(available_land_enemies).spawn(camera_x))

    return spawning_list