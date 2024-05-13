import pygame , sys
from os import listdir
from os.path import join ,isfile

WIDTH ,HEIGHT = 1024 , 640
FPS = 120

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
        self.rect = pygame.Rect(x,y,64,64)
        self.animation_count = 0
        self.direction = "right"
        self.jump_count = 0
        self.dy= 0
        self.hit = False
        self.hit_timer = 0

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

        #Timer for hit sprites
        if self.hit and self.hit_timer <= 0:
            self.hit = False
        elif self.hit_timer > 0:
            self.hit_timer -= 1

        self.handle_sprites(x_vel , y_vel)

        #move the player
        self.rect.x += x_vel
        self.rect.y += y_vel

    def draw_player(self):
        screen.blit(self.sprite, self.rect)
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

class World():
    SAW_SPRITES = load_sprites("Traps","Saw",38,False)
    ANIMATION_DELAY = 7
    def __init__(self , data):
        block_image = pygame.image.load("assets/Terrain/terrain.png").convert_alpha()
        dirt_image = pygame.image.load("assets/Terrain/dirt.png").convert_alpha()
        self.sprite = self.SAW_SPRITES["Off"][0]
        self.saw_images = self.SAW_SPRITES["On"]
        self.tile_list = []
        self.saw_list = []
        self.plat_list = []
        self.animation_count = 0
        for i,row  in enumerate(data):
            for j,col in enumerate(row):
                if col in [1 , 2] :
                    if col == 1 :
                        img = pygame.transform.scale(block_image,(64,64))
                    else:
                        img = pygame.transform.scale(dirt_image,(64,64))
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

world_data =[[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, 1],
             [0,0,0,0,5,0,0,0,0,0,0,0,0,0,0,0, 1],
             [0,0,0,0,1,1,0,3,1,1,1,4,0,0,1,1, 1],
             [0,0,0,0,0,0,0,0,0,0,0,4,0,0,0,0, 1],
             [0,1,0,0,0,0,0,4,0,0,0,0,0,0,0,0, 1],
             [0,2,1,0,0,0,0,0,0,0,0,0,0,0,0,0, 1],
             [0,2,2,1,3,0,1,1,1,6,0,0,0,0,0,0, 1],
             [0,0,0,0,0,0,0,0,0,0,0,1,7,0,3,3, 1],
             [0,0,0,0,0,0,0,0,0,0,1,2,0,0,0,0, 1],
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