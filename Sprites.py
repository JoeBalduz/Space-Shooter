import pygame
import random
from Settings import *

#Initializing sound
pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.mixer.init()

#Loading sounds
player_shoot_sound = pygame.mixer.Sound(path.join(sounds, "Laser_Shoot.wav"))
enemy_shoot_sound = pygame.mixer.Sound(path.join(sounds, "Laser_Shoot2.wav"))

#Groups for sprites
sprites = pygame.sprite.Group()
enemy_sprites = pygame.sprite.Group()
player_laser = pygame.sprite.Group()
enemy_laser = pygame.sprite.Group()
check_laser = pygame.sprite.Group()
repair = pygame.sprite.Group()

#User controls this sprite
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        player_image = pygame.image.load(path.join(images, "player.png")).convert()
        self.image = pygame.transform.scale(player_image, (50, 38))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 20
        self.speedx = 0
        self.health = 8
        self.lives = 3
        self.dead = False
        self.death_timer = pygame.time.get_ticks()

    #Creates a laser
    def shoot(self):
        #Only one player laser can be on screen at any time
        if len(player_laser) == 0:
            pLaser = PlayerLaser(self.rect.centerx, self.rect.centery)
            sprites.add(pLaser)
            player_laser.add(pLaser)
            player_shoot_sound.play()

    #Moves the player offscreen all health is depleated
    def death(self):
        self.dead = True
        self.death_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH + 100, HEIGHT + 100)

    def update(self):
        #Keeps the player offsceen for 1.5 seconds
        if self.dead and pygame.time.get_ticks() - self.death_timer > 1500:
            self.dead = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 20
        
        #Control the player using arrow keys and shoot using space
        self.speedx = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speedx = -3
        if keystate[pygame.K_RIGHT]:
            self.speedx= 3
        if keystate[pygame.K_LEFT] and keystate[pygame.K_RIGHT]:
            self.speedx = 0
        if keystate[pygame.K_SPACE]:
            self.shoot()
        self.rect.centerx += self.speedx

        #Wall boundries
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

#Laser shot by the user
class PlayerLaser(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        player_laser_image = pygame.image.load(path.join(images, "laserGreen.png"))
        self.image = player_laser_image
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -10

    def update(self):
        self.rect.centery += self.speedy
        if self.rect.bottom < 0:
            self.kill()

#Laser shot by enemy ships
class EnemyLaser(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        enemy_laser_image = pygame.image.load(path.join(images, "laserRed.png")).convert()
        self.image = enemy_laser_image
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y
        self.speedy = 10

    def update(self):
        self.rect.centery += self.speedy
        if self.rect.top > HEIGHT:
            self.kill()

#Used to check if an enemy should be allowed to shoot
class ShootCheck(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((10, 400))
        self.image.fill(BLUE)
        self.image.set_colorkey(BLUE)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y
        self.speedy = 5

    def update(self):
        self.rect.centery += self.speedy
        if self.rect.top > HEIGHT:
            self.kill()

#Small sized enemy ships
class EnemySmall(pygame.sprite.Sprite):
    def __init__(self, x, y, start):
        pygame.sprite.Sprite.__init__(self)
        enemy_image_small = pygame.image.load(path.join(images, "sampleShip3.png")).convert()
        self.image = pygame.transform.scale(enemy_image_small, (60, 34))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = start
        self.speedx = 0
        self.speedy = 1
        self.last_move = pygame.time.get_ticks()
        self.y_pct = y
        self.full_health = 1
        self.health = 1
        self.drop_not_complete = True
        self.last_shot = pygame.time.get_ticks()
        self.can_shoot = False
        self.last_check = pygame.time.get_ticks()
        self.ship_type = "small"

    def update(self):
        now = pygame.time.get_ticks()
        self.rect.centery += self.speedy

        #Stops the ship from continuing to move down
        if not self.drop_not_complete:
            self.speedy = 0

        #Makes the enemy ships move slower
        if now - self.last_move > 30:
            self.last_move = now
            self.rect.centerx += self.speedx
        
        #Ship is only allowed to move down until it reaches a certain point
        if self.rect.bottom > HEIGHT * self.y_pct and self.drop_not_complete:
            self.drop_not_complete = False
            self.speedy = 0
            self.rect.bottom = HEIGHT * self.y_pct
            self.speedx = 1

        #Moves the ships right and left
        if self.rect.left < 0:
            for ship in (enemy_sprites.sprites()):
                ship.speedx = 1
                ship.speedy = 5
        if self.rect.right > WIDTH:
            for ship in (enemy_sprites.sprites()):
                ship.speedx = -1
                ship.speedy = 5

        #Checks to see if it is allowed to shoot
        if now - self.last_check > 900 and not self.can_shoot:
            self.last_check = now
            self.check_shoot()
            hits = pygame.sprite.groupcollide(enemy_sprites, check_laser, False, True)
            if len(hits) < 1:
                self.can_shoot = True

        hits = []
        
        #Shoots every 1-5 seconds
        if now - self.last_shot > random.randint(1000, 5000) and self.can_shoot:
            self.last_shot = now
            self.shoot()
                
        if self.health < 1:
            self.kill()
            
    def shoot(self):
        eLaser = EnemyLaser(self.rect.centerx, self.rect.centery)
        sprites.add(eLaser)
        enemy_laser.add(eLaser)
        enemy_shoot_sound.play()

    def check_shoot(self):
        cLaser = ShootCheck(self.rect.centerx, self.rect.centery + 20)
        sprites.add(cLaser)
        check_laser.add(cLaser)

#Medium sized enemy ships
class EnemyMedium(pygame.sprite.Sprite):
    def __init__(self, x, y, start):
        pygame.sprite.Sprite.__init__(self)
        enemy_image_medium = pygame.image.load(path.join(images, "enemyShip.png")).convert()
        self.image = pygame.transform.scale(enemy_image_medium, (120, 61))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = start
        self.speedx = 0
        self.speedy = 1
        self.last_move = pygame.time.get_ticks()
        self.y_pct = y
        self.health = 3
        self.drop_not_complete = True
        self.last_shot = pygame.time.get_ticks()
        self.can_shoot = False
        self.last_check = pygame.time.get_ticks()
        self.ship_type = "medium"

    def update(self):
        now = pygame.time.get_ticks()
        self.rect.centery += self.speedy

        #Stops the ship from moving down after a certain point
        if not self.drop_not_complete:
            self.speedy = 0

        #Makes the enemy ships move slower
        if now - self.last_move > 30:
            self.last_move = now
            self.rect.centerx += self.speedx
        
        #Stops the ship from moving down after a certain point
        if self.rect.bottom > HEIGHT * self.y_pct and self.drop_not_complete:
            self.drop_not_complete = False
            self.speedy = 0
            self.rect.bottom = HEIGHT * self.y_pct
            self.speedx = 1

        #Moves the ships right and left
        if self.rect.left < 0:
            for ship in (enemy_sprites.sprites()):
                ship.speedx = 1
                ship.speedy = 5
        if self.rect.right > WIDTH:
            for ship in (enemy_sprites.sprites()):
                ship.speedx = -1
                ship.speedy = 5
                
        #Checks to see if the ship can shoot
        if now - self.last_check > 900 and not self.can_shoot:
            self.last_check = now
            self.check_shoot()
            hits = pygame.sprite.groupcollide(enemy_sprites, check_laser, False, True)
            if len(hits) < 1:
                self.can_shoot = True

        hits = []

        #Ship shoots every 1-5 seconds
        if now - self.last_shot > random.randint(1000, 5000) and self.can_shoot:
            self.last_shot = now
            self.shoot()

        if self.health < 1:
            self.kill()

    def shoot(self):
        eLaser1 = EnemyLaser(self.rect.centerx - 40, self.rect.centery)
        eLaser2 = EnemyLaser(self.rect.centerx + 40, self.rect.centery)
        sprites.add(eLaser1)
        sprites.add(eLaser2)
        enemy_laser.add(eLaser1)
        enemy_laser.add(eLaser2)
        enemy_shoot_sound.play()

    def check_shoot(self):
        cLaser1 = ShootCheck(self.rect.centerx - 40, self.rect.centery + 45)
        cLaser2 = ShootCheck(self.rect.centerx + 40, self.rect.centery + 45)
        sprites.add(cLaser1)
        sprites.add(cLaser2)
        check_laser.add(cLaser1)
        check_laser.add(cLaser2)


#Boss ship
class EnemyBig(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        boss_image = pygame.image.load(path.join(images, "gala.png")).convert()
        self.image = pygame.transform.scale(boss_image, (240, 204))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH / 2, -300)
        self.speedy = 1
        self.speedx = 0
        self.health = 15
        self.drop_not_complete = True
        self.ship_type = "boss"
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        now = pygame.time.get_ticks()
        
        self.rect.centerx += self.speedx
        self.rect.centery += self.speedy

        #Stops the ship from moving down after a certain point
        if not self.drop_not_complete:
            self.speedy = 0
        
        #Stops the ship from moving down after a certain point
        if self.rect.bottom > HEIGHT * 0.25 and self.drop_not_complete:
            self.drop_not_complete = False
            self.speedy = 0
            self.rect.bottom = HEIGHT * 0.25
            self.speedx = 2

        #Moves ship left and right
        if self.rect.left < 0:
            self.speedx = 2
            self.speedy = 5
        if self.rect.right > WIDTH:
            self.speedx = -2
            self.speedy = 5

        #Ship shoots every 1-3 seconds
        if now - self.last_shot > random.randint(1000, 3000):
            self.last_shot = now
            self.shoot()

        if self.health < 1:
            self.kill()

    def shoot(self):
        eLaser1 = EnemyLaser(self.rect.centerx - 55, self.rect.bottom - 20)
        eLaser2 = EnemyLaser(self.rect.centerx + 55, self.rect.bottom - 20)
        eLaser3 = EnemyLaser(self.rect.centerx - 105, self.rect.bottom - 20)
        eLaser4 = EnemyLaser(self.rect.centerx + 105, self.rect.bottom - 20)
        sprites.add(eLaser1)
        sprites.add(eLaser2)
        sprites.add(eLaser3)
        sprites.add(eLaser4)
        enemy_laser.add(eLaser1)
        enemy_laser.add(eLaser2)
        enemy_laser.add(eLaser3)
        enemy_laser.add(eLaser4)
        enemy_shoot_sound.play()

#Explosion animation
class ExplosionAnimation(pygame.sprite.Sprite):
    def __init__(self, center, explosion, length):
        pygame.sprite.Sprite.__init__(self)
        self.length = length
        self.explosion = explosion
        self.image = self.explosion[0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.image_number = 1
        self.last_update = pygame.time.get_ticks()
        self.speed = 65

    #Goes though every picture in the explosion list to have it animated
    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.speed:
            self.last_update = now
            self.image_number += 1
            if self.image_number == self.length:
                self.kill()
            else:
                center = self.rect.center
                self.image = self.explosion[self.image_number]
                self.rect = self.image.get_rect()
                self.rect.center = center

#Adds health to the player
class RepairShip(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        wrench = pygame.image.load(path.join(images, "genericItem_color_007.png")).convert()
        self.image = pygame.transform.scale(wrench, (38, 60))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 3

    def update(self):
        self.rect.centery += self.speedy
        if self.rect.top >= HEIGHT:
            self.kill()











            
