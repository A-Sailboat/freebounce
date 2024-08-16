import  pygame
import math
import random
import os
from pygame_sdl2.sdl2 import sdlimage

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
GRAVITY = 0.5
BOUNCE = -1.005

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PALE_CALMING_BLUE = (173, 216, 230)  # Hex #ADD8E6
SHADOW_COLOR = (200, 200, 200)  # Light gray for shadow
BACKGROUND_COLOR = (240, 248, 255)  # Alice Blue

# Richest countries and their codes
countries = [
    "US", "CN", "JP", "DE", "IN", "GB", "FR", "IT", "BR", "CA", 
    "RU", "KR", "AU", "ES", "MX", "ID", "NL", "SA", "TR", "CH",
    "TW", "SE", "PL", "BE", "TH", "AR", "NG", "AT", "IR", "AE",
    "IL", "NO", "IE", "HK", "MY", "SG", "PH", "PK", "CL", "FI",
    "EG", "VN", "PT", "CZ", "RO", "PE", "NZ", "GR", "IQ", "QA"
]

# Create screen
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Bouncing Balls")

# Function to generate random horizontal momentum
def random_horizontal_momentum():
    return random.uniform(0, SPEED)

# Function to load and scale SVG flags
def load_svg_image(filepath, scale_to_width, scale_to_height):
    raw_image = sdlimage.IMG_Load(filepath.encode())
    texture = pygame.Texture.from_surface(screen, raw_image)
    w, h = raw_image.w, raw_image.h
    return pygame.transform.smoothscale(texture, (scale_to_width, scale_to_height))

# List of balls
balls = []
for i, country in enumerate(countries):
    angle = i * (2 * math.pi / len(countries))
    x = WINDOW_WIDTH // 2 + BOUNDING_BOX_RADIUS * math.cos(angle)
    y = WINDOW_HEIGHT // 2 + BOUNDING_BOX_RADIUS * math.sin(angle)
    flag_path = os.path.join("4x3", f"{country}.svg")
    flag_image = load_svg_image(flag_path, CIRCLE_RADIUS * 2, CIRCLE_RADIUS * 2)
    balls.append({"pos": [x, y], "vel": [random_horizontal_momentum(), random_horizontal_momentum()], "flag": flag_image, "country": country})

# Function to draw everything
def draw_screen():
    screen.fill(BACKGROUND_COLOR)  # Fill the background with a calm color

    # Draw the bounding circle with a simple outline
    pygame.draw.circle(screen, PALE_CALMING_BLUE, (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2), BOUNDING_BOX_RADIUS, 10)

    for ball in balls:
        # Draw drop shadow
        shadow_pos = (ball["pos"][0] + SHADOW_OFFSET, ball["pos"][1] + SHADOW_OFFSET)
        pygame.draw.circle(screen, SHADOW_COLOR, shadow_pos, CIRCLE_RADIUS)
        
        # Draw the ball
        ball_rect = ball["flag"].get_rect(center=(ball["pos"][0], ball["pos"][1]))
        screen.blit(ball["flag"], ball_rect)
        
    pygame.display.flip()

# Main loop
running = True
game_started = False
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LCTRL:
                game_started = True
            elif event.key == pygame.K_ESCAPE:
                running = False

    if game_started:
        # Apply gravity and update positions
        for ball in balls:
            ball["vel"][1] += GRAVITY
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

                # Ensure the ball is pushed out of the bounding box to avoid getting stuck
                overlap = distance_from_center + CIRCLE_RADIUS - BOUNDING_BOX_RADIUS
                ball["pos"][0] -= overlap * math.cos(normal_angle)
                ball["pos"][1] -= overlap * math.sin(normal_angle)

    draw_screen()
    clock.tick(FPS)

pygame.quit()
