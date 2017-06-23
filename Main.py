#Background from Westbeam on OpenGameArt
#Ships, lasers, and wrench credit "Kenney.nl"
#Boss ship from clayster2012 on OpenGameArt
#All sounds from bfxr.net

import pygame
import random
from Sprites import *
from Settings import *
from Definitions import *

#Game initialization
pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")
clock = pygame.time.Clock()

#Loading images
background = pygame.image.load(path.join(images, "back.png")).convert()
background_rect = background.get_rect()
life_image = pygame.image.load(path.join(images, "life.png")).convert()
life_image.set_colorkey(BLACK)
explosion = {"player": [], "small": [], "medium": [], "boss": [], "laser": []}
for i in range(9):
    picture = "regularExplosion0%s.png" % (str(i))
    image = pygame.image.load(path.join(images, picture)).convert()
    image.set_colorkey(BLACK)
    image_player = pygame.transform.scale(image, (60, 60))
    image_small = pygame.transform.scale(image, (65, 65))
    image_medium = pygame.transform.scale(image, (125, 125))
    image_boss = pygame.transform.scale(image, (245, 245))
    image_lasers = pygame.transform.scale(image, (35, 35))
    explosion["player"].append(image_player)
    explosion["small"].append(image_small)
    explosion["medium"].append(image_medium)
    explosion["boss"].append(image_boss)
    explosion["laser"].append(image_lasers)
    
#Loading sound
explosion_sound_player = pygame.mixer.Sound(path.join(sounds, "Explosion.wav"))
explosion_sound_small = pygame.mixer.Sound(path.join(sounds, "Explosion1.wav"))
explosion_sound_medium = pygame.mixer.Sound(path.join(sounds, "Explosion3.wav"))
explosion_sound_boss = pygame.mixer.Sound(path.join(sounds, "Explosion2.wav"))
explosion_sound_lasers = pygame.mixer.Sound(path.join(sounds, "Explosion4.wav"))
player_hit_sound = pygame.mixer.Sound(path.join(sounds, "Hit_Hurt3.wav"))
enemy_hit_sound = pygame.mixer.Sound(path.join(sounds, "Hit_Hurt8.wav"))
repair_sound = pygame.mixer.Sound(path.join(sounds, "Powerup3.wav"))

with open("highscore.txt", "r") as file:
    highscore = int(file.read())


running = True
round_almost_over = False
game_over = True
score = 0

#Game loop
while running:
    clock.tick(FPS)
    
    if game_over:
        if score > highscore:
            highscore = score
            with open("highscore.txt", "w") as file:
                file.write(str(highscore))
        for enemy in enemy_sprites:
            enemy.kill()
        for laser in enemy_laser:
            laser.kill()
        main_screen(background, background_rect, screen, highscore, clock)
        game_over = False
        player = Player()
        sprites.add(player)
        spawn_enemies()
        score = 0
        
    #Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    #Updates
    #If a player bullet collides with an enemy
    hits = pygame.sprite.groupcollide(enemy_sprites, player_laser, False, True)
    for hit in hits:
        if hit.health == 1:
            if hit.ship_type == "small":
                score += 1
                explosion_sound_small.play()
                ship_explosion = ExplosionAnimation(hit.rect.center, explosion["small"], 9)
                sprites.add(ship_explosion)
            if hit.ship_type == "medium":
                score += 3
                explosion_sound_medium.play()
                ship_explosion = ExplosionAnimation(hit.rect.center, explosion["medium"], 9)
                sprites.add(ship_explosion)
            if hit.ship_type == "boss":
                score += 10
                explosion_sound_boss.play()
                ship_explosion = ExplosionAnimation(hit.rect.center, explosion["boss"], 9)
                sprites.add(ship_explosion)
            if random.random() > 0.9:
                wrench = RepairShip(hit.rect.center)
                sprites.add(wrench)
                repair.add(wrench)
        else:
            enemy_hit_sound.play()
        hit.health -= 1
        

    hits = pygame.sprite.spritecollide(player, enemy_laser, True)
    for hit in hits:
        if player.health > 1:
            player_hit_sound.play()
        player.health -=1
    
        if player.health <= 0:
            explosion_sound_player.play()
            player_explosion = ExplosionAnimation(hit.rect.center, explosion["player"], 9)
            sprites.add(player_explosion)
            player.death()
            player.lives -= 1
            player.health = 8

    hits = pygame.sprite.groupcollide(player_laser, enemy_laser, True, True)
    for hit in hits:
        explosion_sound_lasers.play()
        laser_explosion = ExplosionAnimation(hit.rect.center, explosion["laser"], 9)
        sprites.add(laser_explosion)

    hits = pygame.sprite.spritecollide(player, repair, True)
    for hit in hits:
        repair_sound.play()
        if player.health == 7:
            player.health += 1
        if player.health < 7:
            player.health += 2

    hits = pygame.sprite.spritecollide(player, enemy_sprites, False)
    for hit in hits:
        player.heatlh = 0
        explosion_sound_player.play()
        player_explosion = ExplosionAnimation(hit.rect.center, explosion["player"], 9)
        sprites.add(player_explosion)
        hit.health = 0
        if hit.ship_type == "small":
            explosion_sound_small.play()
            ship_explosion = ExplosionAnimation(hit.rect.center, explosion["small"], 9)
            sprites.add(ship_explosion)
        if hit.ship_type == "medium":
            explosion_sound_medium.play()
            ship_explosion = ExplosionAnimation(hit.rect.center, explosion["medium"], 9)
            sprites.add(ship_explosion)
        if hit.ship_type == "boss":
            explosion_sound_boss.play()
            ship_explosion = ExplosionAnimation(hit.rect.center, explosion["boss"], 9)
            sprites.add(ship_explosion)
        player.death()
        player.lives -= 1
        player.health = 8

    if player.lives < 1 and not player_explosion.alive():
        game_over = True
        round_almost_over = False
        player.kill()

    if len(enemy_sprites) == 0 and round_almost_over:
        spawn_enemies()
        for enemy in enemy_sprites:
            enemy.health += 1
        round_almost_over = False

    if len(enemy_sprites) == 0 and not round_almost_over:
        boss = EnemyBig()
        sprites.add(boss)
        enemy_sprites.add(boss)
        round_almost_over = True
 
    sprites.update()
    #Draw
    screen.fill(BLACK)
    screen.blit(background, background_rect)
    sprites.draw(screen)
    draw_text(screen, WIDTH / 2, 10, str(score), 18)
    draw_health_bar(screen, 5, 5, player.health)
    draw_lives(screen, 680, 5, player.lives, life_image)
    pygame.display.flip()


pygame.quit()
