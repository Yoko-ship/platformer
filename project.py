import pygame,sys
import pickle
from os import path
from pygame.locals import *



pygame.init()
pygame.mixer.init()
screen_width = 900
screen_heigth = 900
fps = 60
screen = pygame.display.set_mode((screen_width,screen_heigth))
pygame.display.set_caption("Platformer")
clock = pygame.time.Clock()


#* Level
level = 1
max_level = 7



#*images
sun_image = pygame.image.load("sun.png")
background_image = pygame.image.load("sky.png")
player_image = pygame.image.load("guy1.png")
restart_image = pygame.image.load("restart_btn.png")
start_button_image = pygame.image.load("start_btn.png")
start_button_image = pygame.transform.scale(start_button_image,(100,40))
exit_button_image = pygame.image.load("exit_btn.png")
exit_button_image = pygame.transform.scale(exit_button_image,(100,40))
platformX_image = pygame.image.load("platform_x.png")
platformY_image = pygame.image.load("platform_y.png")


 

#*for score
score = 0
my_text = pygame.font.SysFont("Times New Roman",25)

#* for grid
tile_size = 45 #*Значение можно определить разделив размер экрана на сколько то)

        #* For restart
game_over = 0


def draw_grid():
    for line in range(0,20):
        pygame.draw.line(screen,(255,255,255),(0,line * tile_size),(screen_width,line * tile_size))
        pygame.draw.line(screen,(255,255,255),(line * tile_size,0),(line * tile_size,screen_heigth))


player_speed = 5

#* Sprites:
blob_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
money_group = pygame.sprite.Group()
gate_sprites = pygame.sprite.Group()
platform_sprites = pygame.sprite.Group()


#* resetWorld
def resetWorld(level):
    global player
    player = Player(100,screen_heigth - 130)
    blob_group.empty()
    money_group.empty()
    lava_group.empty()
    gate_sprites.empty()
    platform_sprites.empty()

    if path.exists(f"level{level}_data"):
                    pickle_in = open(f"level{level}_data","rb")
                    world_data = pickle.load(pickle_in)
    world = World(world_data)
    return world

#*creating world
class World:
    def __init__(self,data):
        #*image
        self.tile_list = []
        dirt_image = pygame.image.load("dirt.png")
        #*Добавление других картинок
        grass_image = pygame.image.load("grass.png")
        self.move_direction = 1
        self.coldown = 0

        row_count = 0
        for row in data:
            col_count = 0
            for info in row:
                if info == 1:
                    img = pygame.transform.scale(dirt_image,(tile_size,tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img,img_rect)
                    self.tile_list.append(tile)
                if info == 2:
                    img = pygame.transform.scale(grass_image,(tile_size,tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img,img_rect)
                    self.tile_list.append(tile)
                if info == 3:
                    blob = Enemy(col_count * tile_size,row_count * tile_size + 15)
                    blob_group.add(blob)
                if info == 6:
                    lava = Lava(col_count * tile_size,row_count * tile_size + 30)
                    lava_group.add(lava)

                if info == 7:
                    money = Money(col_count * tile_size + 10,row_count * tile_size + 20)
                    money_group.add(money)
                
                if info == 8:
                    gate = Gate(col_count * tile_size,row_count * tile_size - 30)
                    gate_sprites.add(gate)
                if info == 4:
                    platform = Platform(platformX_image,col_count * tile_size,row_count * tile_size,1,0)
                    platform_sprites.add(platform)
                if info == 5:
                    platform = Platform(platformY_image,col_count * tile_size,row_count * tile_size,0,1)
                    platform_sprites.add(platform)    


                col_count += 1
            row_count += 1
    
    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0],tile[1])
            pygame.draw.rect(screen,(255,255,255),tile[1],2)

class Player:
    def __init__(self, x, y):
        self.counter = 0
        self.images_right = []
        self.images_left = []
        self.direction = 0
        self.img_numbers = 0
        self.in_air = True

        for num in range(1, 5):
            img_right = pygame.image.load(f"guy{num}.png")
            img_right = pygame.transform.scale(img_right, (40, 60))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)

        self.image = self.images_right[self.img_numbers]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vel_y = 0
        self.jumped = False
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self, game_over):
        global level, world
        walk_coldown = 5
        col_thresh = 20
        dx = 0
        dy = 0
        global player_speed
        keys = pygame.key.get_pressed()
        self.dead_image = pygame.image.load("ghost.png")

        if game_over == 0:
            if keys[pygame.K_SPACE] and not self.jumped and not self.in_air:
                self.vel_y = -15
                self.jumped = True
                pygame.mixer.music.load("jump.wav")
                pygame.mixer.music.play(1)
            if not keys[pygame.K_SPACE]:
                self.jumped = False

            if keys[pygame.K_RIGHT]:
                dx += player_speed
                self.counter += 1
                self.direction = 1

            if keys[pygame.K_LEFT]:
                dx -= player_speed
                self.counter += 1
                self.direction = -1
            if keys[pygame.K_DOWN]:
                dy += player_speed

            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y

            if self.counter > walk_coldown:
                self.counter = 0
                self.img_numbers += 1
                if self.img_numbers >= len(self.images_right):
                    self.img_numbers = 0
                if self.direction == 1:
                    self.image = self.images_right[self.img_numbers]
                if self.direction == -1:
                    self.image = self.images_left[self.img_numbers]

            self.in_air = True
            for tile in world.tile_list:
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.in_air = False

            for platform in platform_sprites:
                if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    if abs((self.rect.top + dy) - platform.rect.bottom) < col_thresh:
                        self.vel_y = 0
                        dy = platform.rect.bottom - self.rect.top
                    elif abs((self.rect.bottom + dy) - platform.rect.top) < col_thresh:
                        self.rect.bottom = platform.rect.top - 1
                        self.in_air = False
                        dy = 0
                    if not self.in_air:
                        self.rect.x += platform.move_direction * platform.move_x
                        self.rect.y += platform.move_direction * platform.move_y

            if pygame.sprite.spritecollide(self, blob_group, False):
                game_over = -1
                pygame.mixer.music.load("img_game_over.wav")
                pygame.mixer.music.play(1)

            if pygame.sprite.spritecollide(self, lava_group, False):
                game_over = -1
                pygame.mixer.music.load("img_game_over.wav")
                pygame.mixer.music.play(1)

            if pygame.sprite.spritecollide(self, gate_sprites, False):
                game_over = 1

            self.rect.x += dx
            self.rect.y += dy

            if self.rect.bottom >= screen_heigth - 40:
                self.rect.bottom = screen_heigth - 40
                dy = 0

        elif game_over == -1:
            self.image = self.dead_image
            if self.rect.y > 200:
                self.rect.y -= 5

        screen.blit(self.image, self.rect)
        return game_over

    

class Enemy(pygame.sprite.Sprite):
    def __init__(self,x,y):
        super().__init__()
        self.image = pygame.image.load('blob.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_coldown = 0
    def update(self):
        self.rect.x += self.move_direction
        self.move_coldown += 1
        if abs(self.move_coldown) >= 50:
            self.move_direction *= -1
            self.move_coldown *= -1

class Lava(pygame.sprite.Sprite):
    def __init__(self,x,y):
        super().__init__()
        self.image = pygame.image.load("lava.png")
        self.image = pygame.transform.scale(self.image,(50,20))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Money(pygame.sprite.Sprite):
    def __init__(self,x,y):
        super().__init__()
        self.image = pygame.image.load("coin.png")
        self.image = pygame.transform.scale(self.image,(20,20))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        global score
        if pygame.sprite.spritecollide(player,money_group,True):
            score += 1
            pygame.mixer.music.load("coin.wav")
            pygame.mixer.music.play(1)

        #* For restart
class Button:
    def __init__(self,image,x,y):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.is_clicked = False

    def draw(self):
        action = False

        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.is_clicked == False:
                action = True
                self.is_clicked = True
        
        if pygame.mouse.get_pressed()[0] == 0:
            self.is_clicked = False

        
        screen.blit(self.image,self.rect)
        return action

class Gate(pygame.sprite.Sprite):
    def __init__(self,x,y):
        super().__init__()
        self.image = pygame.image.load("exit.png")
        self.image = pygame.transform.scale(self.image,(50,80))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y



class Platform(pygame.sprite.Sprite):
    def __init__(self,image,x,y,move_x,move_y,):
        super().__init__()
        img = image
        self.image = pygame.transform.scale(img,(tile_size,tile_size //2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.coldown = 0
        self.move_x = move_x
        self.move_y = move_y


    def update(self):
        self.rect.x += self.move_direction * self.move_x
        self.rect.y += self.move_direction * self.move_y
        self.coldown += 1
        if abs(self.coldown) > 50:
            self.move_direction *= -1
            self.coldown *= -1



            
    
 



enemy = Enemy(100,300)
#* Для создание мира 
if path.exists(f"level{level}_data"):
    pickle_in = open(f"level{level}_data","rb")
    world_data = pickle.load(pickle_in)
world = World(world_data)


paused = False


#* Buttons

button_surface = pygame.Surface((150,50))
button_text = my_text.render("Continue",False,(0,0,0))
button_text_rect = button_text.get_rect(center = (button_surface.get_width()/2,button_surface.get_height()/2 ))
button_rect = pygame.Rect(200,600,150,100)

quit_surface = pygame.Surface((150,50))
quit_text = my_text.render("Quit game",False,(0,0,0))
quit_text_rect = quit_text.get_rect(center = (quit_surface.get_width()/2,quit_surface.get_height()/2))
quit_rect = pygame.Rect(400,600,150,100)

# restart_surface = pygame.Surface((150,50))
# restart_text = my_text.render("Restart ",False,(0,0,0))
# restart_text_rect = restart_text.get_rect(center = (restart_surface.get_width()/2,restart_surface.get_height()/2 ))
# restart_rect = pygame.Rect(600,600,150,100)



        


restart_button = Button(restart_image,screen_width // 2 - 50 , screen_heigth // 2 + 100)
start_button = Button(start_button_image,screen_width // 2 - 200,screen_heigth // 2 + 200)
exit_button = Button(exit_button_image,screen_width // 2 + 50,screen_heigth // 2 + 200)

player = Player(100,500)

main_menu = False
while main_menu == False:

    screen.blit(background_image,(0,0))
    screen.blit(sun_image,(80,50))
    world.draw()


    if start_button.draw():
        main_menu = True

    if exit_button.draw():
        pygame.quit()
        sys.exit()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            main_menu = True

    pygame.display.flip()

run = True
while run:
    clock.tick(fps)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                paused = not paused


    if not paused:

        screen.blit(background_image,(0,0))
        screen.blit(sun_image,(80,50))

        score_text = my_text.render(f"Score: {score}",True,(0,0,0))
        screen.blit(score_text,(50,110))
        world.draw()
                #* For restart
        if game_over == 0:
            platform_sprites.update()
            blob_group.update()
        blob_group.draw(screen)
        lava_group.draw(screen)
                #* For restart
        game_over = player.update(game_over)

        money_group.update()
        # draw_grid()
        money_group.draw(screen)
        gate_sprites.draw(screen)
        platform_sprites.draw(screen)

 
        #* For restart and if player died
        if game_over == -1:
            if restart_button.draw():
                world_data = []
                world = resetWorld(level)
                game_over = 0
                score = 0
                

        #* if player completed the level
        if game_over == 1:
            level += 1
            if level <= max_level:
                world_data = []
                world = resetWorld(level)
                game_over = 0
            else:
                if restart_button.draw():
                    level = 1
                    world_data = []
                    world = resetWorld(level)
                    game_over = 0
    else:
        if exit_button.draw():
            pygame.quit()
            sys.exit()

    pygame.display.flip()

pygame.quit()

