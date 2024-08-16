import pygame
import math
import random

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 540
WINDOW_HEIGHT = 960
FPS = 60
CIRCLE_RADIUS = 20
BOUNDING_BOX_RADIUS = 270
SHADOW_OFFSET = 5  # Offset of the shadow from the ball
SPEED = 5
ASPECT_RATIO = WINDOW_WIDTH / WINDOW_HEIGHT
INITIAL_GRAVITY = 0.5
UPDATED_GRAVITY = 0.3
GRAVITY_CHANGE_TIME = 5000  # Time in milliseconds to change gravity
INITIAL_BOUNCE = -1.005
UPDATED_BOUNCE = -1.02

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PALE_CALMING_BLUE = (173, 216, 230)  # Hex #ADD8E6
SHADOW_COLOR = (50, 50, 50)  # Dark gray for shadow

# Load images
diamond_image = pygame.image.load("diamond.png")
emerald_image = pygame.image.load("emerald.png")
background_image = pygame.image.load("dirt.png")
stone_image = pygame.image.load("stone.jpg")

# Load sound effects
diamond_bounce_sound = pygame.mixer.Sound("pling.wav")  # Replace with the appropriate sound file
emerald_bounce_sound = pygame.mixer.Sound("harp.wav")   # Replace with the appropriate sound file

# Adjust volume of the pling sound to be 50% quieter
diamond_bounce_sound.set_volume(0.5)

# Scale images to the size of the circle
diamond_image = pygame.transform.scale(diamond_image, (CIRCLE_RADIUS * 2, CIRCLE_RADIUS * 2))
emerald_image = pygame.transform.scale(emerald_image, (CIRCLE_RADIUS * 2, CIRCLE_RADIUS * 2))

# Scale the background to fit the window size
background_image = pygame.transform.scale(background_image, (WINDOW_WIDTH, WINDOW_HEIGHT))

# Create screen
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Bouncing Balls")

# Function to generate random horizontal momentum
def random_horizontal_momentum():
    return random.uniform(0, SPEED)

# List of balls
balls = [
    {"pos": [WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 41], "vel": [-random_horizontal_momentum(), -SPEED], "image": diamond_image, "gravity": INITIAL_GRAVITY, "bounces": 0},
    {"pos": [WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 40], "vel": [random_horizontal_momentum(), SPEED], "image": emerald_image, "gravity": -INITIAL_GRAVITY, "bounces": 0}
]

# Function to draw everything
def draw_screen():
    screen.blit(background_image, (0, 0))  # Draw the background image

    # Draw the bounding circle with stone texture
    mask_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    pygame.draw.circle(mask_surface, (0, 0, 0, 255), (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2), BOUNDING_BOX_RADIUS, 10)
    mask = pygame.mask.from_surface(mask_surface)
    stone_texture = pygame.transform.scale(stone_image, (BOUNDING_BOX_RADIUS * 2, BOUNDING_BOX_RADIUS * 2))
    mask_surf = mask.to_surface(setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0))
    mask_surf.blit(stone_texture, (WINDOW_WIDTH // 2 - BOUNDING_BOX_RADIUS, WINDOW_HEIGHT // 2 - BOUNDING_BOX_RADIUS), special_flags=pygame.BLEND_RGBA_MULT)
    screen.blit(mask_surf, (0, 0))

    for ball in balls:
        # Draw drop shadow
        shadow_pos = (ball["pos"][0] - CIRCLE_RADIUS + SHADOW_OFFSET, ball["pos"][1] - CIRCLE_RADIUS + SHADOW_OFFSET)
        pygame.draw.circle(screen, SHADOW_COLOR, shadow_pos, CIRCLE_RADIUS)
        
        # Draw the ball
        screen.blit(ball["image"], (ball["pos"][0] - CIRCLE_RADIUS, ball["pos"][1] - CIRCLE_RADIUS))
    
    pygame.display.flip()

# Function to reset the simulation
def reset_simulation():
    global balls, start_time, BOUNCE
    balls = [
        {"pos": [WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 41], "vel": [-random_horizontal_momentum(), -SPEED], "image": diamond_image, "gravity": INITIAL_GRAVITY, "bounces": 0},
        {"pos": [WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 40], "vel": [random_horizontal_momentum(), SPEED], "image": emerald_image, "gravity": -INITIAL_GRAVITY, "bounces": 0}
    ]
    BOUNCE = INITIAL_BOUNCE
    start_time = pygame.time.get_ticks()

# Main loop
running = True
game_started = False
clock = pygame.time.Clock()
start_time = None
BOUNCE = INITIAL_BOUNCE

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LCTRL:
                game_started = True
                start_time = pygame.time.get_ticks()
            elif event.key == pygame.K_RCTRL and game_started:
                reset_simulation()
            elif event.key == pygame.K_SPACE and game_started:
                reset_simulation()
            elif event.key == pygame.K_ESCAPE:
                running = False

    if game_started:
        # Change gravity after 5 seconds
        current_time = pygame.time.get_ticks()
        if current_time - start_time > GRAVITY_CHANGE_TIME:
            for ball in balls:
                ball["gravity"] = UPDATED_GRAVITY if ball["gravity"] > 0 else -UPDATED_GRAVITY
            BOUNCE = UPDATED_BOUNCE

        # Apply gravity and update positions
        new_balls = []
        for ball in balls:
            ball["vel"][1] += ball["gravity"]
            ball["pos"][0] += ball["vel"][0]
            ball["pos"][1] += ball["vel"][1]

            # Check for collision with bounding box
            distance_from_center = math.sqrt(
                (ball["pos"][0] - WINDOW_WIDTH // 2) ** 2 + (ball["pos"][1] - WINDOW_HEIGHT // 2) ** 2
            )

            if distance_from_center + CIRCLE_RADIUS > BOUNDING_BOX_RADIUS:
                # Calculate the normal at the collision point
                normal_angle = math.atan2(ball["pos"][1] - WINDOW_HEIGHT // 2, ball["pos"][0] - WINDOW_WIDTH // 2)
                
                # Calculate the reflection angle
                angle = math.atan2(ball["vel"][1], ball["vel"][0])
                reflection_angle = 2 * normal_angle - angle
                
                # Reflect the velocity vector
                speed = math.sqrt(ball["vel"][0]**2 + ball["vel"][1]**2) * BOUNCE
                ball["vel"][0] = speed * math.cos(reflection_angle)
                ball["vel"][1] = speed * math.sin(reflection_angle)

                # Play sound effect on bounce
                if ball["image"] == diamond_image:
                    diamond_bounce_sound.play()
                elif ball["image"] == emerald_image:
                    emerald_bounce_sound.play()

                # Ensure the ball is pushed out of the bounding box to avoid getting stuck
                overlap = distance_from_center + CIRCLE_RADIUS - BOUNDING_BOX_RADIUS
                ball["pos"][0] -= overlap * math.cos(normal_angle)
                ball["pos"][1] -= overlap * math.sin(normal_angle)

                # Increment the bounce count
                ball["bounces"] += 1

                # Duplicate the ball every fifth bounce
                if ball["bounces"] % 5 == 0:
                    new_ball = {
                        "pos": ball["pos"][:],
                        "vel": [-ball["vel"][0], -ball["vel"][1]],
                        "image": ball["image"],
                        "gravity": ball["gravity"],
                        "bounces": 0
                    }
                    new_balls.append(new_ball)

        # Add new balls to the list
        balls.extend(new_balls)

        # Detect and handle collisions between balls
        to_remove = set()
        for i, ball1 in enumerate(balls):
            for j, ball2 in enumerate(balls):
                if i < j and ball1["image"] != ball2["image"]:  # Only check for collisions between different types
                    dist = math.sqrt((ball1["pos"][0] - ball2["pos"][0])**2 + (ball1["pos"][1] - ball2["pos"][1])**2)
                    if dist < 2 * CIRCLE_RADIUS:
                        to_remove.add(i)
                        to_remove.add(j)

        # Remove collided balls
        balls = [ball for k, ball in enumerate(balls) if k not in to_remove]

    draw_screen()
    clock.tick(FPS)

pygame.quit()
