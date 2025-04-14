import pygame
import sys
from visual.lighting import LightingEngine

# Initialize pygame
pygame.init()
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Optimized Lighting Engine")
clock = pygame.time.Clock()

# Create lighting engine with 0.5 resolution factor (half resolution)
lighting = LightingEngine(screen_width, screen_height, resolution_factor=0.5)

# Add some hulls
lighting.hull((100, 100, 200, 50))
lighting.hull((400, 300, 50, 200))
lighting.hull((200, 400, 300, 30))

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                lighting.set_resolution_factor(1.0)  # Full quality
            elif event.key == pygame.K_2:
                lighting.set_resolution_factor(0.5)  # Medium quality
            elif event.key == pygame.K_3:
                lighting.set_resolution_factor(0.25)  # Low quality

    # Clear previous lights (except ambient)
    lighting.lights = []

    # Add a light at mouse position
    mouse_pos = pygame.mouse.get_pos()
    lighting.point_light((150, 200, 255), mouse_pos, 200, 0.6)

    # Add some static lights
    lighting.point_light((255, 150, 100), (200, 150), 120, 0.7)
    lighting.point_light((100, 255, 150), (600, 400), 150, 0.5)

    # Clear the screen
    screen.fill((50, 50, 80))

    # Draw your game objects here (must match hull positions)
    pygame.draw.rect(screen, (255, 0, 0), (100, 100, 200, 50))
    pygame.draw.rect(screen, (0, 255, 0), (400, 300, 50, 200))
    pygame.draw.rect(screen, (0, 0, 255), (200, 400, 300, 30))

    # Update and apply lighting
    lighting.update(screen)

    # Show current resolution factor
    font = pygame.font.SysFont(None, 24)
    text = font.render(f"Resolution Factor: {lighting.resolution_factor} (Press 1-3 to change)", True, (255, 255, 255))
    screen.blit(text, (10, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()