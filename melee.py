import math
import random
import pygame

pygame.init()

clock = pygame.time.Clock()
width = 1400
height = 850
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Bouncing Jumper")

radius = 40
ball_image_orig = pygame.image.load("art.png").convert_alpha()
ball_image_orig = pygame.transform.scale(ball_image_orig, (radius * 2, radius * 2))

x = 100.0
y = float(height - radius)
velocity_x = 0.0
velocity_y = 0.0
rotation_angle = 0.0

gravity = 1800.0
jump_speed = 1020.0
move_acceleration = 1200.0
max_horizontal_speed = 620.0
ground_friction = 3.0
wall_bounce = 0.9
ground_bounce = 0.72

grounded = True
running = True
jump_requested = False
aiming = False

# Enemies and projectiles use world coordinates.
enemies = []
projectiles = []
enemy_spawn_timer = 0.0
enemy_spawn_interval = 1.5
projectile_speed = 900.0
projectile_radius = 7
enemy_size = 34

font = pygame.font.SysFont(None, 26)


def fire_projectile(target):
    direction = pygame.Vector2(target) - pygame.Vector2(x, y)

    # Ignore a shot if the cursor is exactly on the ball.
    if direction.length_squared() == 0:
        return

    direction = direction.normalize()
    projectiles.append({"pos": pygame.Vector2(x, y),"velocity": direction * projectile_speed,})


while running:
    real_dt = min(clock.tick(60) / 1000.0, 0.05)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                jump_requested = True

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            aiming = True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
            if aiming:
                fire_projectile(event.pos)
            aiming = False

    game_dt = real_dt * (0.25 if aiming else 1.0)

    keys = pygame.key.get_pressed()
    jump_held = (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w])
    move_right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
    move_left = keys[pygame.K_LEFT] or keys[pygame.K_a]
    direction = int(move_right) - int(move_left)

    velocity_x += direction * move_acceleration * game_dt
    if direction == 0:
        velocity_x *= max(0.0, 1.0 - ground_friction * game_dt)
    velocity_x = max(-max_horizontal_speed,min(max_horizontal_speed, velocity_x),)

    landed = False
    velocity_y += gravity * game_dt
    x += velocity_x * game_dt
    y += velocity_y * game_dt

    rotation_angle -= (velocity_x * game_dt / radius) * (180.0 / math.pi)

    if x - radius < 0:
        x = float(radius)
        velocity_x = abs(velocity_x) * wall_bounce
    elif x + radius > width:
        x = float(width - radius)
        velocity_x = -abs(velocity_x) * wall_bounce

    if y - radius < 0:
        y = float(radius)
        velocity_y = abs(velocity_y) * wall_bounce

    if y + radius > height:
        y = float(height - radius)
        landed = True
        if abs(velocity_y) > 100.0:
            velocity_y = -abs(velocity_y) * ground_bounce
            grounded = False
        else:
            velocity_y = 0.0
            grounded = True

    if (jump_requested or jump_held) and (grounded or landed):
        velocity_y = -jump_speed
        grounded = False
        jump_requested = False


    enemy_spawn_timer += game_dt
    while enemy_spawn_timer >= enemy_spawn_interval:
        enemy_spawn_timer -= enemy_spawn_interval
        enemies.append({"pos": pygame.Vector2(width + enemy_size, random.randint(80, height - 80),),"speed": random.uniform(140.0, 230.0),})

    for enemy in enemies:
        enemy["pos"].x -= enemy["speed"] * game_dt

    enemies = [enemy for enemy in enemies if enemy["pos"].x + enemy_size > 0]
    for projectile in projectiles[:]:
        projectile["pos"] += projectile["velocity"] * game_dt

        hit_enemy = None
        for enemy in enemies:
            if projectile["pos"].distance_to(enemy["pos"]) < (
                projectile_radius + enemy_size / 2
            ):
                hit_enemy = enemy
                break

        if hit_enemy is not None:
            enemies.remove(hit_enemy)
            projectiles.remove(projectile)
        elif (
            projectile["pos"].x < 0
            or projectile["pos"].x > width
            or projectile["pos"].y < 0
            or projectile["pos"].y > height
        ):
            projectiles.remove(projectile)

    screen.fill((20, 20, 80))

    for enemy in enemies:
        enemy_rect = pygame.Rect(0, 0, enemy_size, enemy_size)
        enemy_rect.center = (round(enemy["pos"].x),round(enemy["pos"].y),)
        pygame.draw.rect(screen, (230, 70, 70), enemy_rect)

    # Draw projectiles.
    for projectile in projectiles:
        pygame.draw.circle(screen,(255, 220, 80),(round(projectile["pos"].x),round(projectile["pos"].y),),projectile_radius,)

    if aiming:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        pygame.draw.line(screen,(255, 230, 100),(round(x), round(y)),(mouse_x, mouse_y),3,)

    rotated_ball = pygame.transform.rotate(ball_image_orig, rotation_angle)
    ball_rect = rotated_ball.get_rect(center=(round(x), round(y)))
    screen.blit(rotated_ball, ball_rect.topleft)

    instructions = font.render("Move: A/D or arrows   Jump: Space   Aim: hold right mouse, release to fire", True, (255, 255, 255),)
    screen.blit(instructions, (16, 16))

    if aiming:
        slowmo_text = font.render("AIMING - SLOW MOTION", True, (255, 230, 100))
        screen.blit(slowmo_text, (16, 48))

    pygame.display.flip()

pygame.quit()