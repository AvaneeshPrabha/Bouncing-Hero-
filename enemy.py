import math
import random
import pygame

pygame.init() 

width = 800 
height = 600 
enemy_size = 40
fps = 60 
spawn_gap = 1.0

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Ground and Air Enemies")
clock = pygame.time.Clock()

enemies = []
spawn_timer = 0
running = True 

# Define ground level position
ground_y = height - 100

while running: 
    distance = clock.tick(fps) / 1000.0

    for event in pygame.event.get(): 
        if event.type == pygame.QUIT: 
            running = False

    spawn_timer += distance
    while spawn_timer >= spawn_gap:
        spawn_timer -= spawn_gap
        
        # Randomly choose between a ground enemy and an air enemy
        enemy_type = random.choice(["ground", "air"])
        
        if enemy_type == "ground":
            enemies.append({
                "type": "ground",
                "x": width,
                "y": ground_y - enemy_size,
                "speed": random.uniform(180, 260),
                "color": (50, 210, 100)  # Green for ground enemy
            })
        else:
            enemies.append({
                "type": "air",
                "x": width,
                "y": random.randint(100, ground_y - 220),
                "speed": random.uniform(220, 340),
                "phase": random.uniform(0, 2 * math.pi),
                "color": (230, 60, 70)   # Red for air enemy
            })
        
    screen.fill((25, 25, 35))

    # Draw the ground floor line
    pygame.draw.line(screen, (100, 100, 120), (0, ground_y), (width, ground_y), 4)

    for enemy in enemies:
        enemy["x"] -= enemy["speed"] * distance
        
        # Apply floating bob motion only to air enemies
        if enemy["type"] == "air":
            enemy["phase"] += 6 * distance
            bob = math.sin(enemy["phase"]) * 12
            draw_y = enemy["y"] + bob
        else:
            draw_y = enemy["y"]

        pygame.draw.rect(screen, enemy["color"], (round(enemy["x"]), round(draw_y), enemy_size, enemy_size))
        
    # Remove enemies that have moved off the left side of the screen
    enemies = [enemy for enemy in enemies if enemy["x"] + enemy_size > 0]

    pygame.display.flip()

pygame.quit()