import pygame
from Sprites import *

pygame.init()

def spawn_enemies():
    for i in range(1, 7):
        for j in range(0, 3):
            enemy = EnemySmall(120 * i, 0.50 - (0.08 * j), -10 - (64 * j))
            sprites.add(enemy)
            enemy_sprites.add(enemy)
    for i in range(1, 5):
        enemy = EnemyMedium(164 * i, 0.50 - (0.08 * 3), -10 - (64 * 3))
        sprites.add(enemy)
        enemy_sprites.add(enemy)
    for i in range(1, 7):
        enemy = EnemySmall(120 * i, 0.13, -300)
        sprites.add(enemy)
        enemy_sprites.add(enemy)

def draw_text(screen, x, y, text, size):
    font_name = pygame.font.match_font("arial")
    font = pygame.font.Font(font_name, size)
    textbox = font.render(text, True, WHITE)
    textbox_rect = textbox.get_rect()
    textbox_rect.midtop = (x, y)
    screen.blit(textbox, textbox_rect)

def draw_health_bar(screen, x, y, health):
    if health < 0:
        health = 0
    bar_length = 100
    bar_height = 10
    inside = (health / 8) * bar_length
    outside_rect = pygame.Rect(x, y, bar_length, bar_height)
    inside_rect = pygame.Rect(x, y, inside, bar_height)
    pygame.draw.rect(screen, LIGHT_BLUE, inside_rect)
    pygame.draw.rect(screen, WHITE, outside_rect, 2)

def draw_lives(screen, x, y, lives, image):
    for i in range(lives):
        image_rect = image.get_rect()
        image_rect.x = x + 40 * i
        image_rect.y = y
        screen.blit(image, image_rect)

def main_screen(background, background_rect, screen, highscore, clock):
    screen.blit(background, background_rect)
    draw_text(screen, WIDTH / 2, 20, "High Score: %d" % (highscore), 16)
    draw_text(screen, WIDTH/ 2, HEIGHT * 0.25,  "Space Shooter", 50)
    draw_text(screen, WIDTH / 2, HEIGHT / 2, "Use the arrow keys to move and the space bar to shoot", 20)
    draw_text(screen, WIDTH / 2, HEIGHT * 0.75,  "Press any key to begin", 16)
    pygame.display.flip()
    in_main_screen = True
    while in_main_screen:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                in_main_screen = False
