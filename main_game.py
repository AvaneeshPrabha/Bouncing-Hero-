import math
import random
import pygame

pygame.init()
pygame.mixer.init()

intro_sound_path = "02 Wonderin.mp3"
main_sound_path = "main.mp3"

pygame.mixer.music.load(intro_sound_path)
pygame.mixer.music.set_volume(0.74)
pygame.mixer.music.play(-1)

music_switched = False

clock = pygame.time.Clock()

width = 1400
height = 850
screen = pygame.display.set_mode([width, height])
pygame.display.set_caption("Bouncing Hero")

radius = 40
diameter = radius * 2
ball_image_orig = pygame.image.load("art.png").convert_alpha()
ball_image_orig = pygame.transform.scale(ball_image_orig, (diameter, diameter))

title_logo_orig = pygame.image.load("Bouncing-Hero-11-14-2026.png").convert_alpha()
logo_w = 720
logo_h = int(title_logo_orig.get_height() * (logo_w / title_logo_orig.get_width()))
title_logo_orig = pygame.transform.scale(title_logo_orig, (logo_w, logo_h))

hud_ball_size = 32
hud_ball_color = pygame.transform.scale(ball_image_orig, (hud_ball_size, hud_ball_size))
hud_ball_grey = hud_ball_color.copy()
for px in range(hud_ball_size):
    for py in range(hud_ball_size):
        color = hud_ball_color.get_at((px, py))
        gray = int(0.299 * color.r + 0.587 * color.g + 0.114 * color.b)
        hud_ball_grey.set_at((px, py), (gray, gray, gray, color.a))

explosion_frames = []
for i in range(1, 11):
    exp_surf = pygame.image.load(f"Explosion_two_colors{i}.png").convert_alpha()
    exp_surf = pygame.transform.scale(exp_surf, (450, 450))
    explosion_frames.append(exp_surf)

castle_orig = pygame.image.load("art-3.png").convert_alpha()
castle_w, castle_h = 250, 220
castle_img = pygame.transform.scale(castle_orig, (castle_w, castle_h))

bg_orig = pygame.image.load("background.jpg").convert()
bg_img = pygame.transform.scale(bg_orig, (width, height))
ground_y = 668

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

wolf_variations = []
for sheet in wolf_sheets:
    variation_frames = extract_frames(sheet, 32, 32, 1, 0, 6, 4.5)
    wolf_variations.append(variation_frames)

hud_font = pygame.font.SysFont("Arial", 14, bold=True)
mid_font = pygame.font.SysFont("Arial", 18, bold=True)
big_font = pygame.font.SysFont("Arial", 30, bold=True)

hud_panel = pygame.Rect(16, 16, 490, 168)
pause_btn = pygame.Rect(width - 230, 16, 100, 40)
restart_btn = pygame.Rect(width - 118, 16, 102, 40)
menu_start_btn = pygame.Rect(width // 2 - 140, height // 2 + 120, 280, 64)
controls_continue_btn = pygame.Rect(width // 2 - 160, height - 90, 320, 50)

spell_images = []
s1 = pygame.Surface((16, 16))
s1.fill((36, 32, 48))
pygame.draw.rect(s1, (255, 215, 75), (2, 11, 12, 3))
pygame.draw.circle(s1, (225, 55, 45), (8, 7), 4)
spell_images.append(pygame.transform.scale(s1, (36, 36)))

s2 = pygame.Surface((16, 16))
s2.fill((36, 32, 48))
pygame.draw.rect(s2, (85, 195, 240), (4, 3, 8, 9), 2)
pygame.draw.rect(s2, (255, 215, 75), (6, 5, 4, 5))
spell_images.append(pygame.transform.scale(s2, (36, 36)))

s3 = pygame.Surface((16, 16))
s3.fill((36, 32, 48))
pygame.draw.rect(s3, (235, 125, 195), (5, 4, 6, 8), 2)
pygame.draw.rect(s3, (255, 215, 75), (7, 6, 2, 4))
spell_images.append(pygame.transform.scale(s3, (36, 36)))

slomo_overlay = pygame.Surface((width, height), pygame.SRCALPHA)
slomo_overlay.fill((25, 85, 190, 32))
pygame.draw.rect(slomo_overlay, (80, 200, 255, 110), (0, 0, width, height), 12)

def reset_game(skip_to_play=False):
    return {
        "state": "TUTORIAL" if skip_to_play else "MENU",
        "menu_time": 0.0,
        "story_timer": 0.0,
        "castle_hold_timer": 0.0,
        "castle_x": 18.0,
        "paused": False,
        "x": 340.0,
        "y": float(ground_y - radius),
        "velocity_x": 0.0,
        "velocity_y": 0.0,
        "rotation_angle": 0.0,
        "grounded": True,
        "jump_requested": False,
        "health": 100,
        "castle_hp": 100,
        "energy_charges": 8,
        "energy_regen": 0.0,
        "damage_cooldown": 0.0,
        "slomo": False,
        "aiming": False,
        "aim_start": (0, 0),
        "aim_curr": (0, 0),
        "charge_time": 0.0,
        "dashing": False,
        "super_dash": False,
        "unlocked_super_dash": False,
        "cd_dash": 0.0,
        "max_cd_dash": 2.0,
        "cd_shield": 0.0,
        "max_cd_shield": 8.0,
        "cd_pulse": 0.0,
        "max_cd_pulse": 7.0,
        "shield_timer": 0.0,
        "shockwaves": [],
        "explosions": [],
        "bg_scroll": 0.0,
        "banner_text": "",
        "banner_timer": 0.0,
        "enemies": [],
        "spawn_timer": 0.0,
        "tutorial_step": 0,
        "tutorial_spawned": False,
        "game_over_type": "",
        "trail": [],
        "shake_timer": 0.0,
    }

g = reset_game(skip_to_play=False)

gravity = 1800.0
jump_speed = 1040.0
move_acceleration = 1300.0
max_horizontal_speed = 620.0
ground_friction = 3.2
wall_bounce = 0.85
ground_bounce = 0.65
max_energy_charges = 8

def start_main_music():
    global music_switched
    if not music_switched:
        pygame.mixer.music.load(main_sound_path)
        pygame.mixer.music.set_volume(0.58)
        pygame.mixer.music.play(-1)
        music_switched = True

def toggle_pause():
    g["paused"] = not g["paused"]
    if g["paused"]:
        pygame.mixer.music.pause()
    else:
        pygame.mixer.music.unpause()

def draw_info_bar(screen):
    pygame.draw.rect(screen, (24, 24, 32), hud_panel)

    ball_box_x = 28
    ball_box_y = 28
    ball_box_size = 72
    pygame.draw.rect(screen, (34, 34, 46), (ball_box_x, ball_box_y, ball_box_size, ball_box_size))

    hb_small = hud_ball_grey.copy()
    if g["health"] > 0:
        color_height = int(hud_ball_size * (g["health"] / 100.0))
        source_y = hud_ball_size - color_height
        rect_to_blit = pygame.Rect(0, source_y, hud_ball_size, color_height)
        hb_small.blit(hud_ball_color, (0, source_y), area=rect_to_blit)
    hb_scaled = pygame.transform.scale(hb_small, (64, 64))
    screen.blit(hb_scaled, (ball_box_x + 4, ball_box_y + 4))

    screen.blit(hud_font.render(f"CASTLE {g['castle_hp']}%", True, (255, 220, 80)), (22, 110))
    c_bar = pygame.Rect(28, 132, 76, 16)
    pygame.draw.rect(screen, (40, 20, 20), c_bar)
    if g["castle_hp"] > 0:
        cw = int((c_bar.w - 4) * (g["castle_hp"] / 100.0))
        pygame.draw.rect(screen, (220, 50, 50), (c_bar.x + 2, c_bar.y + 2, cw, c_bar.h - 4))

    slomo_label = "ENERGY [SLO-MO ACTIVE]" if g["slomo"] else "ENERGY [E: SLO-MO]"
    screen.blit(hud_font.render(slomo_label, True, (255, 255, 255)), (118, 26))
    for i in range(max_energy_charges):
        seg_x = 118 + (i * 44)
        seg_y = 50
        seg_w = 38
        seg_h = 22
        pygame.draw.rect(screen, (34, 34, 46), (seg_x, seg_y, seg_w, seg_h))
        if i < g["energy_charges"]:
            pygame.draw.rect(screen, (40, 140, 255), (seg_x + 2, seg_y + 2, seg_w - 4, seg_h - 4))

    screen.blit(hud_font.render("ABILITIES", True, (255, 255, 255)), (118, 86))
    cds = [g["cd_dash"], g["cd_shield"], g["cd_pulse"]]
    max_cds = [g["max_cd_dash"], g["max_cd_shield"], g["max_cd_pulse"]]
    keys_txt = ["RMB", "[2]", "[3]"]
    unlocked = [g["unlocked_super_dash"], True, True]

    for index, image in enumerate(spell_images):
        slot_x = 118 + index * 120
        slot_y = 108
        pygame.draw.rect(screen, (34, 34, 46), (slot_x, slot_y, 44, 44))

        if unlocked[index]:
            screen.blit(image, (slot_x + 4, slot_y + 4))
        else:
            screen.blit(hud_font.render("?", True, (130, 130, 140)), (slot_x + 16, slot_y + 14))

        if cds[index] > 0:
            ratio = cds[index] / max_cds[index]
            overlay_h = int(40 * ratio)
            pygame.draw.rect(screen, (14, 14, 20), (slot_x + 2, slot_y + 2 + (40 - overlay_h), 40, overlay_h))
            cd_num = hud_font.render(f"{cds[index]:.1f}", True, (255, 95, 95))
            screen.blit(cd_num, (slot_x + 6, slot_y + 15))
            status_surf = hud_font.render("WAIT", True, (255, 95, 95))
        else:
            status_surf = hud_font.render(keys_txt[index], True, (120, 230, 140))

        screen.blit(status_surf, (slot_x + 48, slot_y + 15))

    pygame.draw.rect(screen, (30, 34, 48), pause_btn)
    p_label = "RESUME" if g["paused"] else "PAUSE"
    screen.blit(hud_font.render(p_label, True, (255, 255, 255)), (pause_btn.x + 16, pause_btn.y + 14))

    pygame.draw.rect(screen, (52, 26, 32), restart_btn)
    screen.blit(hud_font.render("RESTART", True, (255, 255, 255)), (restart_btn.x + 12, restart_btn.y + 14))

running = True
while running:
    real_dt = min(clock.tick(60) / 1000.0, 0.05)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if g["state"] == "MENU":
                if menu_start_btn.collidepoint(event.pos):
                    g["state"] = "CONTROLS"
            elif g["state"] == "CONTROLS":
                if controls_continue_btn.collidepoint(event.pos):
                    g["state"] = "STORY"
                    g["story_timer"] = 0.0
            elif pause_btn.collidepoint(event.pos) and g["state"] in ("TUTORIAL", "PLAYING"):
                toggle_pause()
            elif restart_btn.collidepoint(event.pos) and g["state"] in ("TUTORIAL", "PLAYING", "GAMEOVER"):
                if g["paused"]:
                    pygame.mixer.music.unpause()
                g = reset_game(skip_to_play=True)
                start_main_music()

        elif event.type == pygame.KEYDOWN:
            if g["state"] == "MENU" and event.key in (pygame.K_SPACE, pygame.K_RETURN):
                g["state"] = "CONTROLS"
            elif g["state"] == "CONTROLS" and event.key in (pygame.K_SPACE, pygame.K_RETURN):
                g["state"] = "STORY"
                g["story_timer"] = 0.0
            elif g["state"] == "STORY" and event.key == pygame.K_SPACE:
                g["state"] = "TUTORIAL"
                start_main_music()
            elif event.key == pygame.K_p and g["state"] in ("TUTORIAL", "PLAYING"):
                toggle_pause()
            elif g["state"] == "GAMEOVER" and event.key == pygame.K_r:
                if g["game_over_type"] == "player":
                    g["health"] = 100
                    g["damage_cooldown"] = 2.0
                    g["state"] = "PLAYING"
                else:
                    g = reset_game(skip_to_play=True)
                    start_main_music()

            elif not g["paused"] and g["state"] in ("TUTORIAL", "PLAYING"):
                if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                    g["jump_requested"] = True
                elif event.key == pygame.K_e:
                    g["slomo"] = not g["slomo"]
                    if g["slomo"]:
                        g["shake_timer"] = 0.15
                elif event.key == pygame.K_2 and g["energy_charges"] >= 3 and g["cd_shield"] <= 0:
                    g["energy_charges"] -= 3
                    g["shield_timer"] = 4.0
                    g["cd_shield"] = g["max_cd_shield"]
                    g["banner_text"] = "SHIELD ACTIVE"
                    g["banner_timer"] = 1.4
                elif event.key == pygame.K_3 and g["energy_charges"] >= 4 and g["cd_pulse"] <= 0:
                    g["energy_charges"] -= 4
                    g["cd_pulse"] = g["max_cd_pulse"]
                    g["damage_cooldown"] = max(g["damage_cooldown"], 1.6)
                    for e in g["enemies"]:
                        if abs(e["x"] - g["x"]) <= 250:
                            e["hp"] -= 1
                            e["x"] += 65
                    g["enemies"] = [e for e in g["enemies"] if e["hp"] > 0]
                    g["banner_text"] = "GUST PULSE"
                    g["banner_timer"] = 1.4

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            if not g["paused"] and g["state"] in ("TUTORIAL", "PLAYING") and not g["grounded"] and g["cd_dash"] <= 0:
                g["aiming"] = True
                g["aim_start"] = event.pos
                g["aim_curr"] = event.pos
                g["charge_time"] = 0.0

        elif event.type == pygame.MOUSEMOTION and g["aiming"]:
            g["aim_curr"] = event.pos

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 3 and g["aiming"]:
            g["aiming"] = False
            drag_vec = pygame.Vector2(g["aim_curr"]) - pygame.Vector2(g["aim_start"])
            if drag_vec.length() > 15:
                launch_dir = drag_vec.normalize()
                is_super = g["unlocked_super_dash"] and g["charge_time"] >= 2.0
                launch_speed = 1120.0 if is_super else 840.0
                g["velocity_x"] = launch_dir.x * launch_speed
                g["velocity_y"] = launch_dir.y * launch_speed
                g["dashing"] = True
                g["super_dash"] = is_super
                g["cd_dash"] = g["max_cd_dash"]
                g["damage_cooldown"] = 1.1
                g["shake_timer"] = 0.2

    # 1. MAIN MENU SCREEN
    if g["state"] == "MENU":
        g["menu_time"] += real_dt
        screen.blit(bg_img, (0, 0))
        screen.blit(castle_img, (18, ground_y - castle_h + 10))

        tilt_angle = math.sin(g["menu_time"] * 2.2) * 5.0
        tilted_logo = pygame.transform.rotozoom(title_logo_orig, tilt_angle, 1.0)
        logo_rect = tilted_logo.get_rect(center=(width // 2, height // 2 - 110))
        screen.blit(tilted_logo, logo_rect.topleft)

        pygame.draw.rect(screen, (24, 24, 32), menu_start_btn)
        pygame.draw.rect(screen, (255, 220, 80), menu_start_btn, 3)
        start_txt = big_font.render("PLAY", True, (255, 220, 80))
        screen.blit(start_txt, start_txt.get_rect(center=menu_start_btn.center))

        pygame.display.flip()
        continue

    # 2. CONTROLS PAGE
    if g["state"] == "CONTROLS":
        screen.blit(bg_img, (0, 0))
        screen.blit(castle_img, (18, ground_y - castle_h + 10))

        panel_rect = pygame.Rect(width // 2 - 520, height // 2 - 350, 1040, 600)
        pygame.draw.rect(screen, (24, 24, 32), panel_rect)
        pygame.draw.rect(screen, (80, 200, 255), panel_rect, 3)

        header = big_font.render("CONTROLS", True, (255, 220, 80))
        screen.blit(header, header.get_rect(center=(width // 2, panel_rect.top + 38)))

        controls_list = [
            ("MOVE LEFT / RIGHT", "[A] / [D] or [LEFT] / [RIGHT]"),
            ("JUMP", "[SPACE] or [W] or [UP]"),
            ("SLO-MO", "[E] (Uses Energy)"),
            ("AIR DASH & SLAM", "In mid-air: Hold [RIGHT-CLICK] & drag toward target, release to launch"),
            ("SUPER DASH", "Hold air aim for 2 seconds (Unlocked after tutorial)"),
            ("SHIELD ABILITY", "[2] (Blocks wolf hits for 4 seconds)"),
            ("GUST PULSE ABILITY", "[3] (Knocks back and damages nearby wolves)"),
            ("PAUSE", "[P] or Top-Right Button"),
        ]

        y_offset = panel_rect.top + 90
        for action, desc in controls_list:
            act_surf = mid_font.render(action + ":", True, (120, 230, 140))
            desc_surf = mid_font.render(desc, True, (255, 255, 255))
            screen.blit(act_surf, (panel_rect.left + 45, y_offset))
            screen.blit(desc_surf, (panel_rect.left + 300, y_offset))
            y_offset += 46

        pygame.draw.rect(screen, (24, 24, 32), controls_continue_btn)
        pygame.draw.rect(screen, (120, 230, 140), controls_continue_btn, 3)
        cont_txt = mid_font.render("CLICK TO CONTINUE", True, (120, 230, 140))
        screen.blit(cont_txt, cont_txt.get_rect(center=controls_continue_btn.center))

        pygame.display.flip()
        continue

    # 3. INTRO STORY SCREEN
    if g["state"] == "STORY":
        g["story_timer"] += real_dt
        screen.fill((10, 10, 14))
        lines = [
            "THE KINGDOM IS UNDER ATTACK.",
            "YOU ARE THE LAST GUARD OF THE CASTLE.",
            "PROTECT THE GATES.",
        ]
        total_dur = 11.5
        if g["story_timer"] >= total_dur:
            g["state"] = "TUTORIAL"
            start_main_music()
        else:
            t = g["story_timer"]
            for i, line in enumerate(lines):
                line_start = 1.0 + i * 2.8
                if t > line_start:
                    line_age = t - line_start
                    alpha = min(255, int(255 * (line_age / 1.4)))
                    if t > 9.5:
                        alpha = int(alpha * max(0.0, (total_dur - t) / 2.0))
                    surf = mid_font.render(line, True, (240, 235, 225))
                    surf.set_alpha(alpha)
                    screen.blit(surf, surf.get_rect(center=(width // 2, height // 2 - 60 + i * 56)))
            skip = hud_font.render("[SPACE TO SKIP]", True, (130, 130, 150))
            screen.blit(skip, skip.get_rect(center=(width // 2, height - 60)))
        pygame.display.flip()
        continue

    # 4. GAMEPLAY UPDATE
    if not g["paused"] and g["state"] in ("TUTORIAL", "PLAYING"):
        is_slow = g["slomo"] or g["aiming"]
        time_scale = 0.28 if is_slow else 1.0
        distance = real_dt * time_scale

        if g["damage_cooldown"] > 0:
            g["damage_cooldown"] -= real_dt
        if g["shield_timer"] > 0:
            g["shield_timer"] -= real_dt
        if g["banner_timer"] > 0:
            g["banner_timer"] -= real_dt
        if g["shake_timer"] > 0:
            g["shake_timer"] -= real_dt
        if g["cd_dash"] > 0:
            g["cd_dash"] = max(0.0, g["cd_dash"] - real_dt)
        if g["cd_shield"] > 0:
            g["cd_shield"] = max(0.0, g["cd_shield"] - real_dt)
        if g["cd_pulse"] > 0:
            g["cd_pulse"] = max(0.0, g["cd_pulse"] - real_dt)

        if g["aiming"]:
            g["charge_time"] += real_dt

        if g["energy_charges"] < max_energy_charges:
            g["energy_regen"] += distance
            if g["energy_regen"] >= 2.5:
                g["energy_regen"] = 0.0
                g["energy_charges"] += 1

        if g["state"] == "PLAYING":
            g["castle_hold_timer"] += distance

        if g["state"] == "PLAYING" and g["castle_hold_timer"] >= 5.0:
            forward_speed = 115.0 + max(0.0, g["velocity_x"] * 0.25)
            g["bg_scroll"] = (g["bg_scroll"] - forward_speed * distance) % width
            if g["castle_x"] > -castle_w - 40:
                g["castle_x"] -= forward_speed * distance
        else:
            forward_speed = 0.0

        keys = pygame.key.get_pressed()
        jump_held = keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]
        move_right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        move_left = keys[pygame.K_LEFT] or keys[pygame.K_a]
        direction = int(move_right) - int(move_left)

        g["velocity_x"] += direction * move_acceleration * distance
        if direction == 0 and not g["dashing"]:
            g["velocity_x"] *= max(0.0, 1.0 - ground_friction * distance)
        if not g["dashing"]:
            g["velocity_x"] = max(-max_horizontal_speed, min(max_horizontal_speed, g["velocity_x"]))

        g["velocity_y"] += gravity * distance
        g["x"] += g["velocity_x"] * distance
        g["y"] += g["velocity_y"] * distance
        g["rotation_angle"] -= ((g["velocity_x"] + forward_speed) * distance / radius) * (180.0 / math.pi)

        if is_slow or g["dashing"]:
            g["trail"].append((g["x"], g["y"], g["rotation_angle"], 180))
        new_trail = []
        for tx, ty, tang, ta in g["trail"]:
            ta -= int(280 * real_dt)
            if ta > 0:
                new_trail.append((tx, ty, tang, ta))
        g["trail"] = new_trail[-16:]

        if g["x"] - radius < 0:
            g["x"] = float(radius)
            g["velocity_x"] = abs(g["velocity_x"]) * wall_bounce
        elif g["x"] + radius > width:
            g["x"] = float(width - radius)
            g["velocity_x"] = -abs(g["velocity_x"]) * wall_bounce

        if g["y"] - radius < 0:
            g["y"] = float(radius)
            g["velocity_y"] = abs(g["velocity_y"]) * wall_bounce

        hud_bounds = hud_panel.inflate(8, 8)
        ball_box = pygame.Rect(g["x"] - radius, g["y"] - radius, diameter, diameter)
        if ball_box.colliderect(hud_bounds):
            overlap_bottom = hud_bounds.bottom - ball_box.top
            overlap_right = hud_bounds.right - ball_box.left
            if overlap_bottom < overlap_right:
                g["y"] = float(hud_bounds.bottom + radius)
                if g["velocity_y"] < 0:
                    g["velocity_y"] = abs(g["velocity_y"]) * 0.6
            else:
                g["x"] = float(hud_bounds.right + radius)
                if g["velocity_x"] < 0:
                    g["velocity_x"] = abs(g["velocity_x"]) * 0.6

        landed = False
        if g["y"] + radius >= ground_y:
            g["y"] = float(ground_y - radius)
            landed = True

            if g["dashing"]:
                slam_radius = 290 if g["super_dash"] else 165
                slam_dmg = 3 if g["super_dash"] else 1

                g["explosions"].append({
                    "x": g["x"],
                    "y": ground_y,
                    "frame_idx": 0.0,
                })
                g["damage_cooldown"] = max(g["damage_cooldown"], 0.6)
                g["shake_timer"] = 0.25

                for e in g["enemies"]:
                    wolf_center_x = e["x"] + e["frames"][0].get_width() / 2
                    if abs(wolf_center_x - g["x"]) <= slam_radius:
                        e["hp"] -= slam_dmg
                        e["x"] += 85 if g["super_dash"] else 40

                g["enemies"] = [e for e in g["enemies"] if e["hp"] > 0]
                g["dashing"] = False
                g["super_dash"] = False

            if abs(g["velocity_y"]) > 120.0:
                g["velocity_y"] = -abs(g["velocity_y"]) * ground_bounce
                g["grounded"] = False
            else:
                g["velocity_y"] = 0.0
                g["grounded"] = True

        if (g["jump_requested"] or jump_held) and (g["grounded"] or landed):
            g["velocity_y"] = -jump_speed
            g["grounded"] = False
            g["jump_requested"] = False
            g["aiming"] = False

        if g["state"] == "TUTORIAL":
            if not g["tutorial_spawned"]:
                chosen_variation = random.choice(wolf_variations)
                wolf_h = chosen_variation[0].get_height()
                g["enemies"].append({
                    "x": float(width),
                    "y": float(ground_y - wolf_h),
                    "speed": 115.0,
                    "frames": chosen_variation,
                    "anim_timer": 0.0,
                    "hp": 1,
                })
                g["tutorial_spawned"] = True
                g["tutorial_step"] = 1

            if g["tutorial_step"] == 1 and not g["grounded"]:
                g["tutorial_step"] = 2

            if len(g["enemies"]) == 0 and g["tutorial_spawned"]:
                g["unlocked_super_dash"] = True
                g["state"] = "PLAYING"
                g["castle_hold_timer"] = 0.0
                g["banner_text"] = "SUPER DASH UNLOCKED (HOLD AIR AIM 2S)"
                g["banner_timer"] = 3.5

        elif g["state"] == "PLAYING":
            g["spawn_timer"] += distance
            if g["spawn_timer"] >= 1.55:
                g["spawn_timer"] = 0.0
                chosen_variation = random.choice(wolf_variations)
                wolf_h = chosen_variation[0].get_height()
                g["enemies"].append({
                    "x": float(width),
                    "y": float(ground_y - wolf_h),
                    "speed": random.uniform(160, 215),
                    "frames": chosen_variation,
                    "anim_timer": 0.0,
                    "hp": 1,
                })

        player_rect = pygame.Rect(g["x"] - radius + 8, g["y"] - radius + 8, diameter - 16, diameter - 16)
        castle_gate_x = g["castle_x"] + castle_w - 45

        for e in g["enemies"][:]:
            e["x"] -= (e["speed"] + forward_speed * 0.4) * distance
            e["anim_timer"] += distance * 10.0

            current_sprite = e["frames"][int(e["anim_timer"]) % len(e["frames"])]
            s_w, s_h = current_sprite.get_size()
            enemy_rect = pygame.Rect(e["x"] + 20, e["y"] + 20, s_w - 40, s_h - 30)

            if player_rect.colliderect(enemy_rect):
                if g["dashing"]:
                    e["hp"] -= (3 if g["super_dash"] else 1)
                    g["damage_cooldown"] = max(g["damage_cooldown"], 0.6)
                elif g["shield_timer"] > 0:
                    e["x"] += 150
                elif g["damage_cooldown"] <= 0:
                    g["health"] = max(0, g["health"] - 20)
                    g["damage_cooldown"] = 1.1
                    g["shake_timer"] = 0.2

            if g["state"] == "TUTORIAL":
                if e["x"] <= castle_gate_x:
                    e["x"] = float(width)
            else:
                if g["castle_x"] > -castle_w and e["x"] <= castle_gate_x:
                    g["castle_hp"] = max(0, g["castle_hp"] - 15)
                    g["shake_timer"] = 0.2
                    g["enemies"].remove(e)
                elif e["x"] + s_w <= 0:
                    g["castle_hp"] = max(0, g["castle_hp"] - 15)
                    g["shake_timer"] = 0.2
                    g["enemies"].remove(e)

        g["enemies"] = [e for e in g["enemies"] if e["hp"] > 0]

        for ex in g["explosions"][:]:
            ex["frame_idx"] += real_dt * 22.0
            if ex["frame_idx"] >= len(explosion_frames):
                g["explosions"].remove(ex)

        if g["health"] <= 0:
            g["state"] = "GAMEOVER"
            g["game_over_type"] = "player"
        elif g["castle_hp"] <= 0:
            g["state"] = "GAMEOVER"
            g["game_over_type"] = "castle"

    ox = random.randint(-5, 5) if g["shake_timer"] > 0 else 0
    oy = random.randint(-5, 5) if g["shake_timer"] > 0 else 0

    # Restored the beautiful grass background during gameplay!
    scroll_x = int(g["bg_scroll"])
    screen.blit(bg_img, (scroll_x + ox, oy))
    screen.blit(bg_img, (scroll_x - width + ox, oy))

    if g["castle_x"] > -castle_w - 20:
        screen.blit(castle_img, (round(g["castle_x"]) + ox, ground_y - castle_h + 10 + oy))

    for ex in g["explosions"]:
        f_idx = int(ex["frame_idx"])
        if f_idx < len(explosion_frames):
            exp_surf = explosion_frames[f_idx]
            erect = exp_surf.get_rect(center=(round(ex["x"]) + ox, round(ex["y"]) - 80 + oy))
            screen.blit(exp_surf, erect.topleft)

    for e in g["enemies"]:
        frame_list = e["frames"]
        frame_idx = int(e["anim_timer"]) % len(frame_list)
        current_sprite = frame_list[frame_idx]
        screen.blit(current_sprite, (round(e["x"]) + ox, round(e["y"]) + oy))

    for tx, ty, tang, ta in g["trail"]:
        ghost = pygame.transform.rotate(ball_image_orig, tang)
        ghost.set_alpha(ta)
        g_rect = ghost.get_rect(center=(round(tx) + ox, round(ty) + oy))
        screen.blit(ghost, g_rect.topleft)

    if g["aiming"]:
        drag_vec = pygame.Vector2(g["aim_curr"]) - pygame.Vector2(g["aim_start"])
        if drag_vec.length() > 10:
            direction = drag_vec.normalize()
            is_super = g["unlocked_super_dash"] and g["charge_time"] >= 2.0
            arrow_len = min(180, max(60, drag_vec.length()))
            end_pos = pygame.Vector2(g["x"], g["y"]) + direction * arrow_len
            arrow_col = (255, 220, 80) if is_super else (240, 80, 70)

            pygame.draw.line(screen, arrow_col, (round(g["x"]) + ox, round(g["y"]) + oy), (round(end_pos.x) + ox, round(end_pos.y) + oy), 6)
            pygame.draw.circle(screen, arrow_col, (round(end_pos.x) + ox, round(end_pos.y) + oy), 10)

            if g["unlocked_super_dash"]:
                pct = min(1.0, g["charge_time"] / 2.0)
                cb = pygame.Rect(round(g["x"] - 35) + ox, round(g["y"] - 62) + oy, 70, 10)
                pygame.draw.rect(screen, (20, 20, 30), cb)
                pygame.draw.rect(screen, (255, 255, 255), cb, 2)
                pygame.draw.rect(screen, arrow_col, (cb.x + 2, cb.y + 2, int((cb.w - 4) * pct), cb.h - 4))

    show_ball = True
    if g["damage_cooldown"] > 0 and not g["dashing"]:
        show_ball = (int(g["damage_cooldown"] * 18) % 2 == 0)

    if show_ball:
        rotated_ball = pygame.transform.rotate(ball_image_orig, g["rotation_angle"])
        rect = rotated_ball.get_rect(center=(round(g["x"]) + ox, round(g["y"]) + oy))
        screen.blit(rotated_ball, rect.topleft)

    if g["shield_timer"] > 0:
        pygame.draw.circle(screen, (90, 210, 255), (round(g["x"]) + ox, round(g["y"]) + oy), radius + 10, 4)

    if g["slomo"] or g["aiming"]:
        screen.blit(slomp_overlay if 'slomp_overlay' in locals() else slomo_overlay, (0, 0))

    draw_info_bar(screen)

    if g["state"] == "TUTORIAL":
        p_box = pygame.Rect(width // 2 - 330, 195, 660, 68)
        pygame.draw.rect(screen, (24, 24, 32), p_box)
        if g["tutorial_step"] == 1:
            t1 = "WOLF INCOMING - PRESS [SPACE] TO JUMP"
            t2 = "PRESS [E] FOR SLO-MO"
        else:
            t1 = "IN MID-AIR: HOLD [RIGHT-CLICK] & DRAG TOWARD THE WOLF"
            t2 = "RELEASE TO DASH & SLAM THE WOLF"
        screen.blit(hud_font.render(t1, True, (255, 255, 255)), (p_box.x + 18, p_box.y + 12))
        screen.blit(hud_font.render(t2, True, (255, 220, 80)), (p_box.x + 18, p_box.y + 38))

    if g["banner_timer"] > 0:
        b_surf = hud_font.render(g["banner_text"], True, (255, 220, 80))
        b_rect = b_surf.get_rect(center=(width // 2, 215))
        bg_r = b_rect.inflate(24, 14)
        pygame.draw.rect(screen, (24, 24, 32), bg_r)
        screen.blit(b_surf, b_rect)

    if g["paused"]:
        p_box = pygame.Rect(width // 2 - 140, height // 2 - 40, 280, 80)
        pygame.draw.rect(screen, (24, 24, 32), p_box)
        p_surf = big_font.render("PAUSED", True, (255, 255, 255))
        screen.blit(p_surf, p_surf.get_rect(center=p_box.center))

    if g["state"] == "GAMEOVER":
        go_box = pygame.Rect(width // 2 - 340, height // 2 - 80, 680, 160)
        pygame.draw.rect(screen, (24, 24, 32), go_box)
        if g["game_over_type"] == "player":
            go_screen_text = "YOU DIED IN BATTLE"
            sub_screen_text = "PRESS [R] TO RESPAWN"
        else:
            go_screen_text = "YOU FAILED TO PROTECT THE CASTLE"
            sub_screen_text = "PRESS [R] OR CLICK RESTART"
        go_surf = big_font.render(go_screen_text, True, (230, 60, 60))
        sub_surf = hud_font.render(sub_screen_text, True, (255, 255, 255))
        screen.blit(go_surf, go_surf.get_rect(center=(width // 2, height // 2 - 25)))
        screen.blit(sub_surf, sub_surf.get_rect(center=(width // 2, height // 2 + 30)))

    pygame.display.flip()

pygame.quit()