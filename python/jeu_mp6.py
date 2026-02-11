import pyxel

# tiles coordinates
TILE_FLOOR = [(0, 1), (1, 1), (2, 1), (0, 2), (1, 2), (2, 2), (0, 3), (1, 3), (2, 3), (5, 2), (6, 2), (5, 3), (6, 3)]
TILE_FLOOR_AIR = [(0, 4), (1, 4), (2, 4)]
TILE_STAIR_RIGHT = [(6, 1)]
TILE_STAIR_LEFT = [(5, 1)]
TILE_OBJECT = [(0, 6)]
TILE_DOOR_CLOSE = [(2, 5), (2, 6)]
TILE_DOOR_OPEN = [(1, 5), (1, 6)]
TILE_STAIRS = TILE_STAIR_LEFT + TILE_STAIR_RIGHT
TILE_SOLID = TILE_FLOOR + TILE_FLOOR_AIR
TILE_GROUND = TILE_SOLID + TILE_STAIR_LEFT + TILE_STAIR_RIGHT

WORLD_COORDINATES = [(0, 304), (0, 168)]

##### _____ App _____ ######

class App:
    def __init__(self):
        pyxel.init(
            128,
            128,
            title="TNSI_projet_6",
            fps=60
        )
        pyxel.fullscreen(True)


        pyxel.load('4.pyxres')
        self.physic = Physic()
        self.player = Player(self.physic, 15, 15)
        self.camera = Camera()
        self.ui = UI(self)
        self.start_menu = StartMenu()
        self.whereami = "start menu"
        pyxel.run(self.update, self.draw)


    def update(self):
        if self.whereami == "game":
            self.player.update()
            self.camera.update(self.player.x, self.player.y)
            self.ui.update()
        elif self.whereami == "start menu":
            self.whereami = self.start_menu.update()


    def draw(self):
        if self.whereami == "game":
            self.camera.draw()
            self.player.draw()
            self.ui.draw()
        if self.whereami == "start menu":
            self.start_menu.draw()








##### _____ Physics _____ #####

class Physic:
    def __init__(self):
        self.gravity = 0.5

    
    def get_tile(self, x:int, y:int):
        if x < 0 or y < 0:
            return (0, 0)
        tile_x = x // 8
        tile_y = y // 8
        return pyxel.tilemaps[0].pget(tile_x, tile_y)









##### _____ Player _____ #####

class Player:
    def __init__(self, physic:Physic, x:int=15, y:int=15):
        self.physic = physic
        self.x = x
        self.y = y
        self.direction = 1
        self.SPEED_X = 1
        self.SPEED_Y = 1
        self.jump_speed = 3
        self.gravity = 0.2
        self.have_key = False
        self.world = 0
        self.coins = 0
        self.life = 5



    def update(self):
        self.move = False

        tile_player = self.physic.get_tile(self.x, self.y)
        tile_left = self.physic.get_tile(self.x-1, self.y)
        tile_right = self.physic.get_tile(self.x+8, self.y)
        tile_under = self.physic.get_tile(self.x, self.y+8)
        tile_under_right = self.physic.get_tile(self.x+8, self.y+8)
        tile_over = self.physic.get_tile(self.x, self.y-1)
        tile_over_right = self.physic.get_tile(self.x+8, self.y-1)

        
        # player's mouvemnt

        if pyxel.btn(pyxel.KEY_D):
            new_x = self.x
            for _ in range(self.SPEED_X):
                new_x = self.x + 1

                if new_x < WORLD_COORDINATES[0][1]:
                    if tile_right in TILE_STAIR_RIGHT or tile_under_right in TILE_STAIR_RIGHT:
                        self.y -= 1
                        self.x = new_x
                        self.move = True

                    elif tile_under in TILE_STAIR_LEFT:
                        self.y += 1
                        self.x = new_x
                        self.move = True
                    
                    elif tile_right in TILE_SOLID:
                        break

                    else:
                        self.x = new_x
                        self.move = True

                else:
                    break
                
            self.direction = 1


        if pyxel.btn(pyxel.KEY_Q):
            new_x = self.x
            for _ in range(self.SPEED_X):
                new_x = self.x - 1

                if new_x > WORLD_COORDINATES[0][0]:
                    if tile_left in TILE_STAIR_LEFT or tile_under in TILE_STAIR_LEFT:
                        self.y -= 1
                        self.x = new_x
                        self.move = True

                    elif tile_under_right in TILE_STAIR_RIGHT:
                        self.y += 1
                        self.x = new_x
                        self.move = True
                    
                    elif tile_left in TILE_SOLID:
                        break

                    else:
                        self.x = new_x
                        self.move = True

                else:
                    break
            
            self.direction = -1


        # gravity
        if tile_under in TILE_GROUND or tile_under_right in TILE_GROUND:
            if self.SPEED_Y > 0:
                self.SPEED_Y = 0

        else:
            self.SPEED_Y += self.gravity

        if tile_under in TILE_SOLID or tile_under_right in TILE_SOLID:
            if not tile_left in TILE_STAIRS and not tile_right in TILE_STAIRS:
                self.y = self.y //8 *8


        if pyxel.btnp(pyxel.KEY_SPACE):
            if tile_under in TILE_GROUND or tile_under_right in TILE_GROUND:
                self.SPEED_Y -= self.jump_speed



        # if we jump
        if self.SPEED_Y < 0:
            for _ in range(abs(round(self.SPEED_Y))):
                new_y = self.y - 1

                if tile_over in TILE_GROUND or tile_over_right in TILE_GROUND:
                    self.y = new_y
                    self.SPEED_Y = 0
                    break

                if new_y < WORLD_COORDINATES[1][0]:
                    self.SPEED_Y = 0
                    break

                self.y = new_y


        # if we fall
        elif self.SPEED_Y > 0:
            for _ in range(round(self.SPEED_Y * 10)):
                new_y = self.y + 0.1

                if tile_under in TILE_GROUND or tile_under_right in TILE_GROUND:
                    self.SPEED_Y = 0
                    self.y = new_y
                    break

                if self.y > WORLD_COORDINATES[1][1]:
                    self.y = 15
                    self.SPEED_Y = 0
                    break

                self.y = new_y


        
        # grab an object
        tm = pyxel.tilemaps[self.world]
        if tile_player in TILE_OBJECT:
            tm.set(
                int(self.x //8),
                int(self.y //8),
                ["0000"]
            )
            if tile_player == (0, 6):
                self.have_key = True

        
        # use an object
        if pyxel.btnp(pyxel.KEY_E):
            if tile_player in TILE_DOOR_CLOSE or tile_right in TILE_DOOR_CLOSE:
                if self.have_key:
                    for y in range(WORLD_COORDINATES[1][1] - WORLD_COORDINATES[1][0]):
                        for x in range(WORLD_COORDINATES[0][1] - WORLD_COORDINATES[0][0]):
                            tile = tm.pget(x, y)
                            if tile == (2, 5):
                                tm.set(x, y, ["0105"])
                            elif tile == (2, 6):
                                tm.set(x, y, ["0106"])
                    self.have_key = False
    




    
    def draw(self):
        list_pos = [(0, 72), (0, 80), (0, 88), (8, 72), (8, 80), (8, 88)]
        pos = list_pos[(self.number(len(list_pos)) if self.move else 0)]

        pyxel.blt(
            self.x,
            self.y,
            0,
            pos[0],
            pos[1],
            8 * self.direction,
            8,
            5
        )

    
    def number(self, number):
        return pyxel.frame_count // 3 % number








##### _____ Camera _____ #####

class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.map = 0


    def update(self, p_x:int, p_y:int):
        # for x
        if WORLD_COORDINATES[0][0] + 54 < p_x < WORLD_COORDINATES[0][1] - 46:
            self.x = p_x - 54
        
        # for y
        if WORLD_COORDINATES[1][0] + 64 < p_y < WORLD_COORDINATES[1][1] - 56:
            self.y = p_y - 64


        pyxel.camera(self.x, self.y)


    def draw(self):
        pyxel.cls(0)
        pyxel.bltm(
            self.x,
            self.y,
            self.map,
            self.x,
            self.y,
            128,
            128
        )










##### _____ UI _____ #####
class UI:
    def __init__(self, app:App):
        self.app = app
        self.list_objects = []
        self.life = 5
        self.coins = 0
        self.x = self.app.camera.x + 98
        self.y = self.app.camera.y
        self.pos_objects = [(3, 12)]


    def update(self):
        # for the key
        if self.app.player.have_key and "key" not in self.list_objects:
            self.list_objects.append("key")
        if not self.app.player.have_key and "key" in self.list_objects:
            self.list_objects.remove("key")
        
        self.life = self.app.player.life
        self.coins = self.app.player.coins
        self.x = self.app.camera.x + 98
        self.y = self.app.camera.y


    
    def draw(self):
        pyxel.rect(
            self.x,
            self.y,
            30,
            128,
            0
        )
        pyxel.text(
            self.x + 3,
            self.y + 3,
            f"Vie: {self.life}",
            4
        )
        for i, objet in enumerate(self.list_objects):
            if objet == "key":
                pyxel.blt(
                    self.x + self.pos_objects[i][0],
                    self.y + self.pos_objects[i][1],
                    0,
                    0,
                    48,
                    8,
                    8,
                    5
                )








##### _____ Start Menu _____ #####

class StartMenu:
    def __init__(self):
        self.play = False
        self.bouton_play = Button(30, 10, "jouer")

    
    def update(self):
        if self.bouton_play.update():
            return "play"
        

        return "start menu"
        

    def draw(self):
        self.bouton_play.draw()
        







### ___ subclass Button ___ ###

class Button:
    def __init__(self, x:int, y:int, text:str):
        self.x = x
        self.y = y
        self.text = text
        self.w = 50
        self.h = 16
        self.border = 2

    def update(self) -> bool:
        if pyxel.MOUSE_BUTTON_LEFT:
            if self.x <= pyxel.mouse_x <= self.x + self.w:
                if self.y <= pyxel.mouse_y <= self.y + self.h:
                    return True
        return False

    def draw(self) -> None:
        pyxel.rect(
            self.x,
            self.y,
            self.w,
            self.h,
            2
        )
        pyxel.rect(
            self.x + self.border,
            self.y + self.border,
            self.w - self.border*2,
            self.h - self.border*2,
            11
        )
        pyxel.text(
            self.x + self.border + 2,
            self.y + self.border + 3,
            self.text,
            0
        )



App()

