import math
import random
import pygame

pygame.init()
clock = pygame.time.Clock()
width = 1400
height = 850
screen = pygame.display.set_mode([width, height])
pygame.display.set_caption("Bouncing Jumper - Fixed Sprites")

radius = 40
diameter = radius * 2
ball_image_orig = pygame.image.load("art.png").convert_alpha()
ball_image_orig = pygame.transform.scale(ball_image_orig, (diameter, diameter))

bird_sheet = pygame.image.load("pixil-frame-0.png").convert_alpha()
wolf_black_sheet = pygame.image.load("wolf_black_full.png").convert_alpha()
wolf_brown_sheet = pygame.image.load("wolf_brown_full.png").convert_alpha()
wolf_gray_sheet = pygame.image.load("wolf_gray_full.png").convert_alpha()

wolf_sheets = [wolf_black_sheet, wolf_brown_sheet, wolf_gray_sheet]

def extract_frames(sheet, frame_width, frame_height, row, start_col, count, scale_factor):
    frames = []
    for i in range(count):
        rect = pygame.Rect((start_col + i) * frame_width, row * frame_height, frame_width, frame_height)
        frame = sheet.subsurface(rect).copy()
        new_w = int(frame_width * scale_factor)
        new_h = int(frame_height * scale_factor)
        frames.append(pygame.transform.scale(frame, (new_w, new_h)))
    return frames

bird_fly_frames = extract_frames(bird_sheet, 32, 32, 1, 0, 8, 2.5)

wolf_variations = []
for sheet in wolf_sheets:
    variation_frames = extract_frames(sheet, 32, 32, 1, 0, 6, 4.5)
    wolf_variations.append(variation_frames)

x = 100.0
y = float(height - radius)
velocity_x = 0.0
velocity_y = 0.0
rotation_angle = 0.0

health = 100
energy_charges = 8
max_energy_charges = 8
damage_cooldown = 0.0

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

enemies = []
spawn_timer = 0
spawn_gap = 1.2
ground_y = height

try:
    hud_font = pygame.font.SysFont("Courier New", 18, bold=True)
except:
    hud_font = pygame.font.SysFont(None, 20)

def draw_info_bar(screen, health, energy_charges, spell_images):
    panel = pygame.Rect(16, 16, 460, 160)
    pygame.draw.rect(screen, (10, 10, 15), panel)
    pygame.draw.rect(screen, (200, 200, 220), panel, 4)

    ball_box_x = 28
    ball_box_y = 28
    ball_box_size = 72
    pygame.draw.rect(screen, (30, 30, 40), (ball_box_x, ball_box_y, ball_box_size, ball_box_size))
    pygame.draw.rect(screen, (100, 100, 120), (ball_box_x, ball_box_y, ball_box_size, ball_box_size), 2)

    hb_surf = pygame.transform.scale(ball_image_orig, (64, 64))
    hb_grey = hb_surf.copy()
    for px in range(64):
        for py in range(64):
            color = hb_surf.get_at((px, py))
            gray = int(0.299 * color.r + 0.587 * color.g + 0.114 * color.b)
            hb_grey.set_at((px, py), (gray, gray, gray, color.a))

    if health > 0:
        color_height = int(64 * (health / 100.0))
        source_y = 64 - color_height
        rect_to_blit = pygame.Rect(0, source_y, 64, color_height)
        hb_grey.blit(hb_surf, (0, source_y), area=rect_to_blit)

    screen.blit(hb_grey, (ball_box_x + 4, ball_box_y + 4))

    screen.blit(hud_font.render("ENERGY", True, (255, 255, 255)), (115, 28))
    
    for i in range(max_energy_charges):
        seg_x = 115 + (i * 32)
        seg_y = 52
        seg_w = 28
        seg_h = 24
        
        pygame.draw.rect(screen, (30, 30, 40), (seg_x, seg_y, seg_w, seg_h))
        pygame.draw.rect(screen, (80, 90, 110), (seg_x, seg_y, seg_w, seg_h), 2)
        
        if i < energy_charges:
            pygame.draw.rect(screen, (40, 140, 255), (seg_x + 3, seg_y + 3, seg_w - 6, seg_h - 6))

    screen.blit(hud_font.render("ABILITIES", True, (255, 255, 255)), (115, 92))
    for index, image in enumerate(spell_images):
        slot_rect = pygame.Rect(115 + index * 54, 112, 44, 40)
        pygame.draw.rect(screen, (100, 100, 120), slot_rect, 2)
        screen.fill((30, 30, 40), slot_rect.inflate(-4, -4))
        screen.blit(image, (slot_rect.x + 4, slot_rect.y + 2))

spell_images = []
for color in [(220, 80, 80), (80, 200, 100), (80, 140, 240)]:
    surf = pygame.Surface((36, 36))
    surf.fill(color)
    pygame.draw.rect(surf, (255, 255, 255), surf.get_rect(), 2)
    spell_images.append(surf)

while running:
    distance = min(clock.tick(60) / 1000.0, 0.05)

    if damage_cooldown > 0:
        damage_cooldown -= distance

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                jump_requested = True
            elif event.key == pygame.K_e:
                energy_charges = max(0, energy_charges - 1)
            elif event.key == pygame.K_r:
                energy_charges = min(max_energy_charges, energy_charges + 1)

    keys = pygame.key.get_pressed()
    jump_held = keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]
    move_right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
    move_left = keys[pygame.K_LEFT] or keys[pygame.K_a]
    direction = int(move_right) - int(move_left)

    velocity_x += direction * move_acceleration * distance
    if direction == 0:
        velocity_x *= max(0.0, 1.0 - ground_friction * distance)
    velocity_x = max(-max_horizontal_speed, min(max_horizontal_speed, velocity_x))

    landed = False
    velocity_y += gravity * distance
    x += velocity_x * distance
    y += velocity_y * distance

    rotation_angle -= (velocity_x * distance / radius) * (180.0 / math.pi)

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

    spawn_timer += distance
    while spawn_timer >= spawn_gap:
        spawn_timer -= spawn_gap
        enemy_type = random.choice(["ground", "air"])
        if enemy_type == "ground":
            chosen_variation = random.choice(wolf_variations)
            wolf_h = chosen_variation[0].get_height()
            enemies.append({
                "type": "ground",
                "x": width,
                "y": ground_y - wolf_h,
                "speed": random.uniform(180, 260),
                "frames": chosen_variation,
                "anim_timer": 0.0
            })
        else:
            bird_h = bird_fly_frames[0].get_height()
            enemies.append({
                "type": "air",
                "x": width,
                "y": random.randint(150, ground_y - 300),
                "speed": random.uniform(220, 340),
                "phase": random.uniform(0, 2 * math.pi),
                "frames": bird_fly_frames,
                "anim_timer": 0.0
            })

    player_rect = pygame.Rect(x - radius, y - radius, diameter, diameter)
    for enemy in enemies:
        enemy["x"] -= enemy["speed"] * distance
        enemy["anim_timer"] += distance * 10.0

        if enemy["type"] == "air":
            enemy["phase"] += 6 * distance
            enemy["draw_y"] = enemy["y"] + math.sin(enemy["phase"]) * 12
        else:
            enemy["draw_y"] = enemy["y"]

        current_sprite = enemy["frames"][int(enemy["anim_timer"]) % len(enemy["frames"])]
        s_w, s_h = current_sprite.get_size()
        enemy_rect = pygame.Rect(enemy["x"], enemy["draw_y"], s_w, s_h)

        if player_rect.colliderect(enemy_rect) and damage_cooldown <= 0:
            health = max(0, health - 20)
            damage_cooldown = 1.0

    enemies = [e for e in enemies if e["x"] + 200 > 0]

    screen.fill((15, 15, 25))

    for enemy in enemies:
        frame_list = enemy["frames"]
        frame_idx = int(enemy["anim_timer"]) % len(frame_list)
        current_sprite = frame_list[frame_idx]
        screen.blit(current_sprite, (round(enemy["x"]), round(enemy["draw_y"])))

    rotated_ball = pygame.transform.rotate(ball_image_orig, rotation_angle)
    rect = rotated_ball.get_rect(center=(round(x), round(y)))
    screen.blit(rotated_ball, rect.topleft)

    draw_info_bar(screen, health, energy_charges, spell_images)

    pygame.display.flip()

pygame.quit()