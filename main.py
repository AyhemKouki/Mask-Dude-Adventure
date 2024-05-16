import pygame , sys
from os import listdir
from os.path import join ,isfile
from Levels import all_levels

WIDTH ,HEIGHT = 1024 , 640
FPS = 120

pygame.font.init()
font = pygame.font.SysFont(None, 40)

clock = pygame.time.Clock()
pygame.display.set_caption("Mask Dude Adventure")
screen = pygame.display.set_mode((WIDTH, HEIGHT))

def load_sprites(folder1 , folder2 , x , test_direction):
    path = join("assets",folder1,folder2)
    images = [file for file in listdir(path) if isfile(join (path , file))]
    sprite_sheets = {}
    for image in images:
        sprite_sheet = pygame.image.load(join(path , image)).convert_alpha()
        sprites = []
        for i in range(sprite_sheet.get_width()//x):
            surface = pygame.Surface((x ,x),pygame.SRCALPHA,32)
            rect = pygame.Rect(i*x, 0 , x, x)
            surface.blit(sprite_sheet,(0,0),rect)
            sprites.append(pygame.transform.scale(surface,(64,64)))
        if test_direction:
            sprite_sheets[image.replace(".png","")+"_right"] = sprites
            sprite_sheets[image.replace(".png","")+"_left"] = [pygame.transform.flip(sprite,True,False) for sprite in sprites]
        else:
            sprite_sheets[image.replace(".png","")] = sprites
    return sprite_sheets

def get_background():
    background_image = pygame.image.load("assets/Background/Brown.png")
    _,_,width,height = background_image.get_rect()
    positions=[]
    for i in range(WIDTH//width + 1):
        for j in range(HEIGHT//height + 1):
            pos=(i*width ,j*height)
            positions.append(pos)
    return positions , background_image

def draw_background():
    positions , back_image = get_background()
    for position in positions:
        screen.blit(back_image , position)

class Player():
    SPRITES = load_sprites("Main Characters","Mask Dude",32,True)
    ANIMATION_DELAY = 5
    GRAVITY = 0.1 
    MAX_FALL_SPEED = 3 
    def __init__(self , x ,y):
        self.score_img = Fruit.FRUIT_SPRITES["Apple"][0]
        self.rect = pygame.Rect(x,y,64,64)
        self.animation_count = 0
        self.direction = "right"
        self.jump_count = 0
        self.dy= 0
        self.hit = False
        self.hit_timer = 0
        self.score = 0
        self.score_message = font.render(f"{self.score}", True, (255,255,255))
        self.score_message_rect = self.score_message.get_rect(center=(60, 32))
        self.level_counter = 1

    def handle_sprites(self, x_vel , y_vel):
        if self.hit and self.hit_timer > 0:
            if self.direction == "right" :
                images = self.SPRITES["Hit_right"]
            elif self.direction == "left" :
                images = self.SPRITES["Hit_left"]
        elif y_vel < 0 and self.direction == "right"  :
            images = self.SPRITES["jump_right"]
        elif y_vel < 0 and self.direction == "left":
            images = self.SPRITES["jump_left"]
        elif y_vel > 0 and self.direction == "right" :
            images = self.SPRITES["Fall_right"]
        elif y_vel > 0  and self.direction == "left" :
            images = self.SPRITES["Fall_left"]
        elif x_vel == 0 and self.direction == "right":
            images = self.SPRITES["idle_right"]
        elif x_vel == 0 and self.direction == "left":
            images = self.SPRITES["idle_left"]
        elif x_vel == 2 :
            images = self.SPRITES["Run_right"]
        elif x_vel == -2:
            images = self.SPRITES["Run_left"]
        elif y_vel == 0 and  self.direction == "right":
            images = self.SPRITES["idle_right"]
        elif y_vel == 0 and  self.direction == "left":
            images = self.SPRITES["idle_left"]
        
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(images)
        self.sprite = images[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x,self.rect.y))
        #to adjust a little the player collision with other rects
        self.rect.width = 54

    def move_player(self):
        x_vel , y_vel = 0 , 0
        press = pygame.key.get_pressed()
        if press[pygame.K_d]:
            self.direction = "right"
            x_vel= 2
        elif press[pygame.K_q]:
            self.direction = "left"
            x_vel = -2
        if press[pygame.K_SPACE] and self.jump_count == 0:
            self.jump_count = 1
            self.dy = -5.2

        #GRAVITY   
        self.dy += self.GRAVITY
        if self.dy > self.MAX_FALL_SPEED:
            self.dy = self.MAX_FALL_SPEED
        y_vel =+ self.dy
        
        #check collision with ground
        for tile in world.tile_list:
            if tile[1].colliderect(self.rect.x + x_vel, self.rect.y , 60 ,64):
                x_vel = 0
            if tile[1].colliderect(self.rect.x , self.rect.y + y_vel , 60 ,64):
                if y_vel > 0 :
                    y_vel =  tile[1].top - self.rect.bottom
                    self.jump_count = 0
                elif y_vel < 0 :
                    y_vel = tile[1].bottom - self.rect.top
                    self.dy = 0
        self.test = False
        #check collision with moving platforms
        for plat in world.plat_list:
            if plat.img_rect.colliderect(self.rect.x + x_vel, self.rect.y , 60 ,64):
                x_vel = 0
            if plat.img_rect.colliderect(self.rect.x , self.rect.y + y_vel , 60 ,64):
                if y_vel >= 0 :
                    #we have to check first if we are above the platformer, max y_vel when falling = 3 so max diff = 4 because platformer is moving up by 1 pixel
                    if abs((self.rect.bottom + y_vel)-plat.img_rect.top)<= 4 :
                        #diminuer 1 pixel pour ne pas activer la condition de x_vel = 0
                        self.rect.bottom = plat.img_rect.top - 1
                        y_vel = 0 
                        self.jump_count = 0
                        if x_vel == 0:
                            x_vel = plat.move_x
                #consider that y_vel= -5.2 and platformer height=19 so max diff between them will be 14
                elif y_vel < 0 :
                    if abs((self.rect.top + y_vel)-plat.img_rect.bottom)< 14.2:
                        self.dy = 0
                        y_vel = plat.img_rect.bottom - self.rect.top  
        #check collision with spike balls
        if pygame.sprite.spritecollide(self,trap_group,False):
            self.hit = True
            self.hit_timer = 120    
        #collision with saws
        for saw in world.saw_list:
            if self.rect.colliderect(saw[1]):
                self.hit = True
                self.hit_timer = 120
        #collision with enemy
        for enemy in world.enemy_list:
            if self.rect.colliderect(enemy.img_rect):
                self.hit = True
                self.hit_timer = 120
        #collision with fruits
        for fruit in world.fruit_list:
            if self.rect.colliderect(fruit.img_rect):
                self.score += 1
                world.fruit_list.remove(fruit)
                self.score_message = font.render(f"{self.score}", True, (255,255,255))
        
        if self.win_round():
            world.checkpoint_list.clear()
            world.tile_list.clear()
            world.enemy_list.clear()
            world.fruit_list.clear()
            world.plat_list.clear()
            world.saw_list.clear()
            self.level_counter +=1
            world.build_world(all_levels[self.level_counter])

        #Timer for hit sprites
        if self.hit and self.hit_timer <= 0:
            self.hit = False
        elif self.hit_timer > 0:
            self.hit_timer -= 1

        self.handle_sprites(x_vel , y_vel)

        #move the player
        self.rect.x += x_vel
        self.rect.y += y_vel

    def win_round(self):
        for checkpoint in world.checkpoint_list:
            if self.rect.colliderect(checkpoint.img_rect):
                return True
        return False

    def draw_player(self):
        screen.blit(self.sprite, self.rect)
        screen.blit(self.score_img, (0,0))
        screen.blit(self.score_message , self.score_message_rect)
        #draw rect arround the player:
        #pygame.draw.rect(screen, (255, 0, 0), self.rect, 2)

class Trap(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load("assets/Traps/Spiked Ball/SpikedBall.png").convert_alpha()
        self.image = pygame.transform.scale2x(img)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Moving_Platform():
    SPRITES_PLAT = load_sprites("Traps","Falling Platforms" ,32 , False)
    ANIMATION_DELAY = 17
    sprite = SPRITES_PLAT["On"]
    def __init__(self,x,y,move_x , move_y,block_num):
        self.img = self.SPRITES_PLAT["Off"][0]
        self.img_rect = self.img.get_rect()
        self.img_rect.height = 19
        self.img_rect.x = x
        self.img_rect.y = y
        self.move_x = move_x
        self.move_y = move_y
        self.count_distance = 0
        self.animation_count = 0
        self.block_num = block_num
    def move_plat(self):
        if self.count_distance < 64 * self.block_num:
            self.img_rect.x += self.move_x
            self.img_rect.y -= self.move_y
            self.count_distance +=1
        else:
            self.move_x *= -1
            self.move_y *= -1
            self.count_distance = 0
    def draw(self):
        self.move_plat()
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(self.SPRITES_PLAT["On"])
        self.img = self.sprite[sprite_index]
        self.animation_count += 1
        screen.blit(self.img ,self.img_rect)
        #pygame.draw.rect(screen, (255, 255, 255), self.img_rect, 1)

class Enemy():
    ENEMIES_SPRITES = load_sprites("Enemies","Slime",44,True)
    sprite = ENEMIES_SPRITES["Run_left"]
    ANIMATION_DELAY = 6
    def __init__(self,x,y,move_x,block_num):
        self.img = self.ENEMIES_SPRITES["Run_right"][0]
        self.img_rect = pygame.Rect(x,y+20,50,50)
        self.move_x = move_x
        self.count_distance = 0
        self.animation_count = 0
        self.block_num = block_num
    def move_enemy(self):
        if self.count_distance < 64 * self.block_num:
            self.img_rect.x += self.move_x
            self.count_distance +=1
        else:
            self.move_x *= -1
            self.count_distance = 0
    def handle_sprites(self):
        if self.move_x>=0:
            self.sprite = self.ENEMIES_SPRITES["Run_left"]
        else:
            self.sprite = self.ENEMIES_SPRITES["Run_right"]
    def draw(self):
        self.move_enemy()
        self.handle_sprites()
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(self.ENEMIES_SPRITES["Run_right"])
        self.img = self.sprite[sprite_index]
        self.animation_count += 1
        screen.blit(self.img ,self.img_rect)
        #pygame.draw.rect(screen, (255, 255, 255), self.img_rect, 1)
        
class Fruit:
    FRUIT_SPRITES = load_sprites("items","Fruits",32,False)
    sprite = FRUIT_SPRITES["Apple"]
    ANIMATION_DELAY = 6
    def __init__(self,x,y):
        self.img = self.FRUIT_SPRITES["Apple"][0]
        self.img_rect = pygame.Rect(x,y,32,32)
        self.animation_count = 0
    def draw(self):
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(self.FRUIT_SPRITES["Apple"])
        self.img = self.sprite[sprite_index]
        self.animation_count += 1
        screen.blit(self.img ,(self.img_rect.x - 16 , self.img_rect.y -16))
        #pygame.draw.rect(screen, (255, 255, 255), self.img_rect, 1)

class Checkpoint:
    CHECK_POINT_SPRITES = load_sprites("items","Checkpoint",64,False)
    sprite = CHECK_POINT_SPRITES["Checkpoint"]
    ANIMATION_DELAY = 6
    def __init__(self , x, y):
        self.img = self.CHECK_POINT_SPRITES["Checkpoint"][0]
        self.img_rect = pygame.Rect(x,y+16,32,48)
        self.animation_count = 0
    def draw(self):
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(self.CHECK_POINT_SPRITES["Checkpoint"])
        self.img = self.sprite[sprite_index]
        self.animation_count += 1
        screen.blit(self.img ,(self.img_rect.x - 16 , self.img_rect.y - 16))
        #pygame.draw.rect(screen, (255, 255, 255), self.img_rect, 1)

class World():
    SAW_SPRITES = load_sprites("Traps","Saw",38,False)
    ANIMATION_DELAY = 7
    def __init__(self , data):
        self.block_image = pygame.image.load("assets/Terrain/terrain.png").convert_alpha()
        self.dirt_image = pygame.image.load("assets/Terrain/dirt.png").convert_alpha()
        self.sprite = self.SAW_SPRITES["Off"][0]
        self.saw_images = self.SAW_SPRITES["On"]
        self.tile_list = []
        self.saw_list = []
        self.plat_list = []
        self.enemy_list = []
        self.fruit_list = []
        self.checkpoint_list = []
        self.animation_count = 0
        self.build_world(data)
    def build_world(self, data):
        for i,row  in enumerate(data):
            for j,col in enumerate(row):
                if col in [1 , 2] :
                    if col == 1 :
                        img = pygame.transform.scale(self.block_image,(64,64))
                    else:
                        img = pygame.transform.scale(self.dirt_image,(64,64))
                    img_rect = img.get_rect()
                    img_rect.topleft = ( j * 64 , i * 64)
                    img_rect.width = 54
                    tile =(img , img_rect)
                    self.tile_list.append(tile)
                if col == 3:
                    trap = Trap( j * 64 , i * 64)
                    trap_group.add(trap)
                if col == 4:
                    img = pygame.transform.scale(self.sprite , (64,62))
                    img_rect = img.get_rect()
                    img_rect.topleft = ( j * 64 , i * 64)
                    tile= [img,img_rect]
                    self.saw_list.append(tile)
                if col == 5:
                    #moving platform in x direction
                    plat = Moving_Platform(j * 64 , i * 64 ,1,0, 2)
                    self.plat_list.append(plat)
                if col == 6:
                    #moving platform in y direction
                    plat = Moving_Platform(j * 64 , i * 64 ,0,1, 2)
                    self.plat_list.append(plat)
                if col == 7:
                    #moving platform in x and y directions
                    plat = Moving_Platform(j * 64 , i * 64 ,1,1, 2)
                    self.plat_list.append(plat)
                if col == 8:
                    enemy = Enemy(j * 64 , i * 64 ,1 , 2)
                    self.enemy_list.append(enemy)
                if col == 9:
                    fruit = Fruit(j * 64 , i * 64)
                    self.fruit_list.append(fruit)
                if col == 10:
                    checkpoint = Checkpoint(j * 64 , i * 64)
                    self.checkpoint_list.append(checkpoint)

    def draw(self):
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(self.saw_images)
        self.sprite = self.saw_images[sprite_index]
        self.animation_count += 1
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
            #show rects of terrain
            #pygame.draw.rect(screen, (255, 255, 255), tile[1], 1)
        for saw in self.saw_list:
            saw[0]= self.sprite
            screen.blit(saw[0], saw[1])
            #show rects of saws
            #pygame.draw.rect(screen, (255, 255, 255), saw[1], 1) 
        for plat in self.plat_list:
            plat.draw()
        for enemy in self.enemy_list:
            enemy.draw()
        for fruit in self.fruit_list:
            fruit.draw()
        for checkpoint in self.checkpoint_list:
            checkpoint.draw()

world_data =[[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, 1],
             [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,10, 1],
             [0,0,0,0,1,1,0,0,1,1,1,0,0,0,1,1, 1],
             [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, 1],
             [0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0, 1],
             [9,2,1,0,0,0,0,0,0,0,0,0,0,0,0,0, 1],
             [0,2,2,1,0,0,1,1,1,0,0,0,0,0,0,0, 1],
             [0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0, 1],
             [0,0,0,0,0,0,9,0,0,0,1,2,0,0,9,9, 1],
             [1,1,1,1,1,1,1,1,1,1,2,2,1,1,1,1, 1]]

player = Player(50 , HEIGHT - 64)
trap_group = pygame.sprite.Group()
world = World(world_data)
def run():
    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    player.animation_count = 0
                if event.key == pygame.K_q:
                    player.animation_count = 0
        draw_background()
        trap_group.draw(screen)
        world.draw()
        player.move_player()
        player.draw_player()
        pygame.display.update()
if __name__ == "__main__":
    run()