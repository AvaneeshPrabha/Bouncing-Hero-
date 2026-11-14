import pygame


pygame.init()


width = 1400
height = 850
screen = pygame.display.set_mode((width, height))


pygame.display.set_caption("Bouncing Hero")


background_color = (18, 35, 75)
text_color = (255, 255, 255)


title_font = pygame.font.SysFont(None, 76)
button_font = pygame.font.SysFont(None, 40)


play_button = pygame.Rect(550, 600, 300, 70)
quit_button = pygame.Rect(550, 690, 300, 70)


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if play_button.collidepoint(mouse_pos):
                import sourceCode
                sourceCode.main()
            elif quit_button.collidepoint(mouse_pos):
                running = False


        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if play_button.collidepoint(mouse_pos):
                print("Play clicked")
            elif quit_button.collidepoint(mouse_pos):
                running = False
    screen.fill(background_color)


    title = title_font.render("BOUNCING HERO", True, text_color)
    screen.blit(title, title.get_rect(center=(700, 160)))


    pygame.draw.rect(screen, (40, 120, 200), play_button, border_radius=12)
    play_text = button_font.render("PLAY", True, text_color)
    screen.blit(play_text, play_text.get_rect(center=play_button.center))


    art_area = pygame.Rect(500, 240, 400, 300)
    pygame.draw.rect(screen, (100, 200, 220), art_area, width=3)

