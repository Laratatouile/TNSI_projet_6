import pyxel
import random





# tiles coordinates
TILE_FLOOR = [(0, 1), (1, 1), (2, 1), (0, 2), (1, 2), (2, 2), (0, 3), (1, 3), (2, 3), (5, 2), (6, 2), (5, 3), (6, 3)]
TILE_FLOOR_AIR = [(0, 4), (1, 4), (2, 4)]
TILE_STAIR_RIGHT = [(6, 1)]
TILE_STAIR_LEFT = [(5, 1)]
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

        # variables
        self.pos_monsters = {
            0: [],
            1: [(104, 80)]
        }
        self.pos_objects = {
            0: {},
            1: {
                "key" : [(248, 32)]
            }
        }

        pos_player = (15, 15)
        self.whereami = "start menu"
        self.world = 0      # the tilemap

        # instances objects
        self.physic = Physic(pos_player, self.world)
        self.objects = Objects(self.pos_objects ,self.physic, self.world)
        self.player = Player(self.physic, pos_player, self.world, self.objects)
        self.camera = Camera(self.world, self.physic)
        self.ui = UI(self)
        self.fake_player = FakePlayer(self.world)
        self.start_menu = StartMenu()
        self.monsters = Monsters(self.pos_monsters[self.world], self.physic)
        self.pause = False
        
        # run the app
        pyxel.run(self.update, self.draw)




    def update(self):
        # if we put pause
        if pyxel.btnp(pyxel.KEY_P):
            self.pause = not self.pause


        # if we are in the game
        if self.whereami == "game" and not self.pause:
            self.objects.update()
            self.player.update()
            # detect if the player is dead
            if self.player.life == 0:
                self.whereami = "death menu"
            
            self.camera.update(self.player.x, self.player.y)
            self.monsters.update()
            self.ui.update()
        

        # if we are in the start menu
        elif self.whereami == "start menu":
            self.whereami, self.world = self.start_menu.update()
            self.fake_player.update()

            # update the world variable
            self.player.world = self.physic.world = self.camera.world = self.objects.world = self.world
            
            self.monsters = Monsters(self.pos_monsters[self.world], self.physic)

        elif self.whereami == "death menu":
            pyxel.cls(0)





    def draw(self):
        # if we are in the game
        if self.whereami == "game":
            self.camera.draw()
            self.objects.draw()
            self.player.draw()
            self.monsters.draw()
            self.ui.draw()


        # if we are in the menu
        elif self.whereami == "start menu":
            self.camera.draw()
            self.start_menu.draw()
            self.fake_player.draw()


        return None










##### _____ Physics _____ #####

class Physic:
    """ this class is used to have things ralative to many things """

    def __init__(self, pos_player:tuple, world:int) -> None:
        """ initialise the class """
        self.pos_player = pos_player
        self.world = world
        self.dict_pos_monsters = {}

    
    def get_tile(self, x:int, y:int) -> tuple:
        """ return the position of the tile at this position """
        if x < 0 or y < 0:
            return (0, 0)
        tile_x = x // 8
        tile_y = y // 8
        return pyxel.tilemaps[self.world].pget(tile_x, tile_y)
    
    
    def side_player(self, x:int) -> int:
        """ return 0 if the player is at the left of the position
        or 1 if the player is at right """
        return (0 if self.pos_player[0] < x else 1)
    

    def stair_under(self, x:int, y:int) -> int:
        """ return the position y if we are over a stair """
        y = y //8 *8

        # verify if we are on a stair
        tile_left = self.get_tile(x, y+8)
        tile_right = self.get_tile(x+8, y+8)

        if tile_right in TILE_STAIR_RIGHT:
            return y + 8 - (x % 8)

        elif tile_left in TILE_STAIR_LEFT:
            return y + x % 8
        
        return y
    

    def add_monster(self, id_m:int, pos:tuple) -> None:
        """ add the monster in the physic class """
        self.dict_pos_monsters[id_m] = pos

    def del_monster(self, id_m:int) -> None:
        """ delete a monster """
        del self.dict_pos_monsters[id_m]


    def on_monster(self, x:int, y:int) -> bool:
        """ return if we are on a monster """
        for pos_monster in self.dict_pos_monsters.values():
            if pos_monster[1]-7 < y < pos_monster[1]+7:
                if pos_monster[0]-7 < x < pos_monster[0]+7:
                    return True
        return False
    

    def over_monster(self, x:int, y:int) -> None:
        """ search if we are over a monster and kill it """
        for id_m, pos_monster in self.dict_pos_monsters.items():
            if pos_monster[1]-8 < y < pos_monster[1]-4:
                if pos_monster[0]-7 < x < pos_monster[0]+7:
                    del self.dict_pos_monsters[id_m]
                    return










###### _____ Master Objects _____ #####


class Objects:
    def __init__(self, dict_objects:dict, physic:Physic, world:int) -> None:
        """ generate objects """
        self.physic = physic
        self.world = world

        self.dict_objects = {}

        for id_w, world in dict_objects.items():
            self.dict_objects[id_w] = {}
            i = 0
            
            for type_object, list_pos in world.items():

                for pos in list_pos:

                    if type_object == "key":
                        self.dict_objects[id_w][i] = Key(i, pos[0], pos[1], self.physic, type_object)


                    i += 1



    
    def update(self):
        """ update all the objects """
        for objects in self.dict_objects[self.world].values():
            objects.update()



    def draw(self):
        """ draw all the objects """
        for objects in self.dict_objects[self.world].values():
            objects.draw()


    def on_object(self, x:int, y:int) -> tuple:
        """ detect if we are on an object and return his type or None """
        for obj in self.dict_objects[self.world].values():
            if obj.x-7 < x < obj.x+7 and obj.y-7 < y < obj.y+7:
                return obj.type_obj, obj.id_o
            

    def del_obj(self, id_obj:int) -> None:
        """ delete an object with his id """
        del self.dict_objects[self.world][id_obj]



    def add(self, type_obj:str, x:int, y:int, SPEED_X:int, SPEED_Y:int, slide_force:int=0) -> None:
        """ add an object """
        add = False
        k = 0
        for i in self.dict_objects.keys():
            if not i == k:

                # if the object is a key
                if type_obj == "key":
                    self.dict_objects[self.world][k] = Key(k, x, y, self.physic, type_obj, SPEED_X, SPEED_Y, slide_force)


                add = True
                break
            k += 1


        if not add:
            if type_obj == "key":
                    self.dict_objects[self.world][k] = Key(k, x, y, self.physic, type_obj, SPEED_X, SPEED_Y, slide_force)
        








##### _____ Object _____ #####
class Object:
    """ the master class for all objects """

    def __init__(self, id_o:int, x:int, y:int, physic:Physic, type_obj:str, speed_x:int=0, speed_y:int=0, slide_force:int=0) -> None:
        """ initialise base variables for the object """
        self.id_o = id_o
        self.x = x
        self.y = y
        self.physic = physic
        self.type_obj = type_obj

        self.SPEED_X = speed_x
        self.SPEED_Y = speed_y
        self.slide_force = slide_force
        
        self.bounce_floor_force = 0.3
        self.bounce_wall_force = 0.1
        self.gravity = 0.2



    def update(self) -> None:
        """ update the position of the object """
        tile_over = self.physic.get_tile(self.x, self.y-1)
        tile_over_right = self.physic.get_tile(self.x+8, self.y-1)
        tile_under = self.physic.get_tile(self.x, self.y+8)
        tile_under_right = self.physic.get_tile(self.x+8, self.y+8)
        tile_right = self.physic.get_tile(self.x+8, self.y)
        tile_left = self.physic.get_tile(self.x-1, self.y)
        tile_under_left = self.physic.get_tile(self.x-1, self.y+8)

        # if we go to the right
        if self.SPEED_X > 0:
            # if it's a wall
            if tile_right in TILE_SOLID + TILE_STAIR_LEFT or tile_under_right in TILE_SOLID + TILE_STAIR_LEFT:
                self.SPEED_X = 0

            # if we are on the floor
            elif tile_under in TILE_SOLID or tile_under_right in TILE_SOLID:
                self.SPEED_X *= self.slide_force
            
            else:
                self.SPEED_X -= 0.2

        # if we go to the left
        else:
            # if it's a wall
            if tile_left in TILE_SOLID + TILE_STAIR_RIGHT or tile_under_left in TILE_SOLID + TILE_STAIR_RIGHT:
                self.SPEED_X = 0

            # if we are on the floor
            elif tile_under in TILE_SOLID or tile_under_right in TILE_SOLID:
                self.SPEED_X *= self.slide_force
            
            else:
                self.SPEED_X += 0.2


        # if we fall
        if self.SPEED_Y > 0:
            # if we are on the floor
            if tile_under in TILE_GROUND or tile_under_right in TILE_GROUND:
                self.SPEED_Y = 0
                # if we are on stairs
                if tile_under_right in TILE_STAIR_RIGHT:
                    self.y = (self.y //8 *8) + 8 - (self.x % 8)
                
                elif tile_under in TILE_STAIR_LEFT:
                    self.y = (self.y //8 *8) + (self.x % 8)

                else:
                    self.y = self.y //8 *8
            
            else:
                self.SPEED_Y += self.gravity
                
        else:
            if tile_over in TILE_GROUND or tile_over_right in TILE_GROUND:
                self.SPEED_Y = 0


        # for x
        for _ in range(round(abs(self.SPEED_X))):
            tile_under = self.physic.get_tile(self.x, self.y+8)
            tile_under_right = self.physic.get_tile(self.x+8, self.y+8)
            tile_right = self.physic.get_tile(self.x+8, self.y)
            tile_left = self.physic.get_tile(self.x-1, self.y)
            tile_under_left = self.physic.get_tile(self.x-1, self.y+8)
            # if we go to the right
            if self.SPEED_X > 0:
                # if it's a wall
                if tile_right in TILE_SOLID + TILE_STAIR_LEFT or tile_right in TILE_SOLID + TILE_STAIR_LEFT:
                    self.SPEED_X = 0
                    break

                # if we are on stairs
                elif tile_under in TILE_STAIR_RIGHT or tile_under_right in TILE_STAIR_RIGHT:
                    self.SPEED_X -= 0.05
                    self.y = (self.y //8 *8) + 8 - (self.x % 8)
                
                self.x += 1

            else:
                # if it's a wall
                if tile_left in TILE_SOLID + TILE_STAIR_RIGHT or tile_under_left in TILE_SOLID + TILE_STAIR_RIGHT:
                    self.SPEED_X = 0
                    break

                elif tile_under in TILE_STAIR_LEFT or tile_under_right in TILE_STAIR_LEFT:
                    self.SPEED_X += 0.05
                    self.y = (self.y //8 *8) + (self.x % 8)
            
                self.x -= 1




                
            
            

        
            





##### _____ Key class _____ #####

class Key(Object):

    def draw(self) -> None:
        pyxel.blt(
            self.x,
            self.y,
            0,
            0,
            48,
            8,
            8,
            5
        )











##### _____ Player _____ #####

class Player:
    """ class used to control the player """

    def __init__(self, physic:Physic, pos_player:tuple, world:int, objects:Objects) -> None:
        """ initialise the player's class """
        self.objects = objects
        self.physic = physic
        self.x = pos_player[0]
        self.y = pos_player[1]
        self.direction = 1
        self.SPEED_X = 1
        self.SPEED_Y = 1
        self.jump_speed = 3
        self.gravity = 0.2
        self.have_key = False
        self.world = world
        self.coins = 0
        self.life = 5
        self.move = False
        self.time_life = 0
        self.object_select = "key"
        self.delay_life = 60



    def update(self) -> None:
        """ update the player """
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

                if new_x < WORLD_COORDINATES[0][1] - 8:
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

        # not on stairs
        if tile_under in TILE_SOLID or tile_under_right in TILE_SOLID:
            if not tile_left in TILE_STAIRS and not tile_right in TILE_STAIRS:
                self.y = self.y //8 *8


        # if we press jump
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

                # verify if we are over an ennemi to kill it
                self.physic.over_monster(self.x, self.y)

                self.y = new_y


        
        # grab an object
        tmp = self.objects.on_object(self.x, self.y)
        if tmp != None:
            type_obj, id_obj = tmp
            
            if type_obj == "key":
                self.have_key = True
                self.objects.del_obj(id_obj)

        
        # throw an object
        if pyxel.btnp(pyxel.KEY_A):
            if self.direction == 1:
                self.objects.add(
                    self.object_select,
                    self.x + 8,
                    self.y - 1,
                    3,
                    -2
                )

        

        
        # use an object
        if pyxel.btnp(pyxel.KEY_E):
            tm = pyxel.tilemaps[self.world]
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

        
        # update position in physic
        self.physic.pos_player = [self.x, self.y]

        # detect if we are on an monster
        if pyxel.frame_count - self.time_life > self.delay_life:
            if self.physic.on_monster(self.x, self.y):
                self.life -= 1
                self.time_life = pyxel.frame_count


    




    
    def draw(self) -> None:
        """ draw the player """
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

    
    def number(self, number:int) -> int:
        """ return a number between 0 and number depending on the frame """
        return pyxel.frame_count // 3 % number








##### _____ Camera _____ #####

class Camera:
    """ class used to control the camera """

    def __init__(self, world:int, physic:Physic) -> None:
        """ initialise the camera """
        self.physic = physic
        self.x = 0
        self.y = 0
        self.world = world


    def update(self, p_x:int, p_y:int) -> None:
        """ update the camera """
        # for x
        if WORLD_COORDINATES[0][0] + 54 < p_x < WORLD_COORDINATES[0][1] - 46:
            self.x = p_x - 54
        
        # for y
        if WORLD_COORDINATES[1][0] + 64 < p_y < WORLD_COORDINATES[1][1] - 56:
            self.y = p_y - 64


        pyxel.camera(self.x, self.y)


    def draw(self) -> None:
        """ draw the background and the objects """
        pyxel.cls(0)

        # the background
        pyxel.bltm(
            self.x,
            self.y,
            self.world,
            self.x,
            self.y,
            128,
            128
        )

        # the objects
        pass










##### _____ UI _____ #####
class UI:
    """ class used to diplay the UI """

    def __init__(self, app:App) -> None:
        """ initialise the UI """
        self.app = app
        self.list_objects = []
        self.life = 5
        self.coins = 0
        self.x = self.app.camera.x + 98
        self.y = self.app.camera.y
        self.pos_objects = [(3, 12)]


    def update(self) -> None:
        """ update all things to display on the UI """
        # for the key
        if self.app.player.have_key and "key" not in self.list_objects:
            self.list_objects.append("key")
        if not self.app.player.have_key and "key" in self.list_objects:
            self.list_objects.remove("key")
        
        self.life = self.app.player.life
        self.coins = self.app.player.coins
        self.x = self.app.camera.x + 98
        self.y = self.app.camera.y


    
    def draw(self) -> None:
        """ display the UI """
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
    """ the menu displayed at the start of the game """

    def __init__(self) -> None:
        """ initialise the menu and the buttons """
        self.play = False
        self.bouton_play = Button(35, 8, "jouer")
        self.bouton_quitter = Button(35, 50, "quitter")
        pyxel.mouse(True)

    
    def update(self) -> str:
        """ update the menu and return where we are """
        # if play
        if self.bouton_play.update():
            pyxel.mouse(False)
            return "game", 1
        
        # if we exit
        if self.bouton_quitter.update():
            pyxel.quit()
        

        return "start menu", 0
        

    def draw(self) -> None:
        """ display the menu """
        self.bouton_play.draw()
        self.bouton_quitter.draw()

    

        







##### _____ Fake player _____ #####

class FakePlayer:
    """ the fake player for the start menu """

    def __init__(self, world:int) -> None:
        """ initialise the fake player """
        self.world = world
        self.x = 0
        self.y = 104
        self.SPEED_X = 0
        self.SPEED_Y = 0
        self.direction = 1
        self.gravity = 0
        self.move = False
        self.visible = False
        self.start_time = pyxel.frame_count

        # delay between the actions
        self.delay = [40, 40, 112, 48, 3, 17, 23, 10, 20, 12, 10, 10, 70]

    
    def update(self) -> None:
        """ update the fake player """
        time = pyxel.frame_count - self.start_time
        if time % 830 == sum(self.delay[:0]):
            self.x = 0
            self.y = 104
            self.visible = False
            tilemap = pyxel.tilemaps[self.world]
            tilemap.set(13, 7, ["0605"])
            tilemap.set(1, 0, ["0006"])
        
        if time % 830 == sum(self.delay[:1]):
            self.visible = True

        elif time % 830 == sum(self.delay[:2]):
            self.SPEED_X = 1
            self.direction = 1
            self.move = True

        elif time % 830 == sum(self.delay[:3]):
            self.SPEED_X = 0
            self.SPEED_Y = -1
            self.direction = -1
        
        elif time % 830 == sum(self.delay[:4]):
            self.SPEED_X = -1
            self.SPEED_Y = 0
            pyxel.tilemaps[self.world].set(13, 7, ["0000"])

        elif time % 830 == sum(self.delay[:5]):
            self.SPEED_X = -1
            self.SPEED_Y = 0

        elif time % 830 == sum(self.delay[:6]):
            self.SPEED_X = -1
            self.SPEED_Y = -3
            self.gravity = 0.2

        elif time % 830 == sum(self.delay[:7]):
            self.SPEED_X = 0
            self.SPEED_Y = 0
            self.gravity = 0

        elif time % 830 == sum(self.delay[:8]):
            self.SPEED_X = 1
            self.SPEED_Y = -3
            self.gravity = 0.2
            self.direction = 1

        elif time % 830 == sum(self.delay[:9]):
            self.SPEED_X = 0
            self.SPEED_Y = 0
            self.gravity = 0
        
        elif time % 830 == sum(self.delay[:10]):
            self.SPEED_X = 0
            self.SPEED_Y = -3.3
            self.gravity = 0.2
            self.direction = -1

        elif time % 830 == sum(self.delay[:11]):
            self.SPEED_X = -1
            self.gravity = 0.2

        elif time % 830 == sum(self.delay[:12]):
            self.SPEED_X = -1
            self.SPEED_Y = 0
            self.gravity = 0

        elif time % 830 == sum(self.delay):
            self.SPEED_X = 0
            self.SPEED_Y = 0
            self.gravity = 0
            self.move = False
            pyxel.tilemaps[self.world].set(1, 0, ["0000"])
        
        elif time % 830 > sum(self.delay):
            return



        # apply speeds
        self.SPEED_Y += self.gravity
        self.x += self.SPEED_X
        self.y += self.SPEED_Y
        
            


    def draw(self) -> None:
        """ draw the fake player """
        if not self.visible:
            return
        
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

    def number(self, number:int) -> int:
        """ return a number between 0 and number depending on the frame """
        return pyxel.frame_count // 3 % number











### ___ subclass Button ___ ###

class Button:
    """ class used to create buttons """

    def __init__(self, x:int, y:int, text:str):
        """ initialise one button """
        self.x = x
        self.y = y
        self.text = text
        self.w = 50
        self.h = 16
        self.border = 2
        self.dec_x = (self.w - self.border*2 - len(text) * 4) // 2
        self.dec_y = 3
        self.color_1 = 2
        self.color_2 = 11
        self.color_3 = 0

    def update(self) -> bool:
        """ return if we have clicked on the button or not """
        if self.x <= pyxel.mouse_x <= self.x + self.w and self.y <= pyxel.mouse_y <= self.y + self.h:
            self.color_2 = 15
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                return True
        else:
            self.color_2 = 11
        return False


    def draw(self) -> None:
        """ draw the button """
        # the border of the button
        pyxel.rect(
            self.x,
            self.y,
            self.w,
            self.h,
            self.color_1
        )

        # the center of the button
        pyxel.rect(
            self.x + self.border,
            self.y + self.border,
            self.w - self.border*2,
            self.h - self.border*2,
            self.color_2
        )

        # the text of the button
        pyxel.text(
            self.x + self.border + self.dec_x,
            self.y + self.border + self.dec_y,
            self.text,
            self.color_3
        )











### ___ subclass Monster ___ ###

class Monster:
    """ class for one monster """

    def __init__(self, x:int, y:int, id_m:int, physic:Physic) -> None:
        """ create a new monster """
        self.physic = physic
        self.id_m = id_m
        self.x = x
        self.y = y
        self.SPEED_X = 1
        self.SPEED_Y = 0
        self.gravity = 0.2
        self.life = True
        self.time_dead = 20
        self.direction = 1
        self.action = 2                     # 0 for left 1 for right 2 for wait
        self.frames_actions = 60            # the number of frames to wait between 2 actions
        self.list_pos = [(40, 88), (48, 88), (56, 88), (64, 88)]
        self.len_list = len(self.list_pos)
        self.touch_ground = -1000           # when the monster touch the ground to apply skin
        self.on_floor = True



    def update(self) -> None:
        """ update the monster """
        # if the monster is dead he can't move
        if not self.life:
            self.time_dead -= 1
            return

        tile_under = self.physic.get_tile(self.x, self.y+8)
        tile_under_right = self.physic.get_tile(self.x+8, self.y+8)
        tile_over = self.physic.get_tile(self.x, self.y-1)
        tile_over_right = self.physic.get_tile(self.x+8, self.y-1)

        # if the monster is waiting an action
        if (tile_under in TILE_SOLID or tile_under_right in TILE_SOLID) and pyxel.frame_count % self.frames_actions == 0:
            number = random.randint(0, 10)

            # choose the action of the monster
            # random action
            if number < 4:
                self.action = random.randint(0, 1)
                self.SPEED_Y -= 1.5
                self.on_floor = False
            # go to the player
            elif number < 8:
                self.action = self.physic.side_player(self.x)
                self.SPEED_Y -= 1.5
                self.on_floor = False
            # wait
            else:
                self.action = 2

        
        # if the monster is on the floor but it's not the time for a new action
        elif tile_under in TILE_SOLID or tile_under_right in TILE_SOLID:
            self.SPEED_Y = 0
            self.on_floor = True
            if not (tile_under in TILE_STAIRS or tile_over_right in TILE_STAIRS):
                self.y = self.y //8 *8
            if pyxel.frame_count - self.touch_ground > 59 and self.action != 2:
                self.touch_ground = pyxel.frame_count
            self.action = 2

        # if the monster is in the air
        else:
            self.SPEED_Y += self.gravity


        # if the monster is in an action
        if self.action == 0:
            self.x = max(WORLD_COORDINATES[0][0], self.x - self.SPEED_X)
            self.direction = 1
        
        elif self.action == 1:
            self.x = min(WORLD_COORDINATES[0][1] -8, self.x + self.SPEED_X)
            self.direction = -1

        # apply the gravity to the monster
        if self.SPEED_Y > 0:
            for _ in range(round(self.SPEED_Y)):
                self.y += 1
                tile_under = self.physic.get_tile(self.x, self.y+8)
                tile_under_right = self.physic.get_tile(self.x+8, self.y+8)
                if tile_under in TILE_SOLID or tile_under_right in TILE_SOLID:
                    if tile_under in TILE_STAIRS or tile_under_right in TILE_STAIRS:
                        self.y = self.physic.stair_under(self.x, self.y)
                    break
        if self.SPEED_Y < 0:
            for _ in range(round(-self.SPEED_Y)):
                self.y -= 1
                tile_over = self.physic.get_tile(self.x, self.y-1)
                tile_over_right = self.physic.get_tile(self.x+8, self.y-1)
                if tile_over in TILE_SOLID or tile_over_right in TILE_SOLID:
                    break

        
        # set the position in the physic class
        self.physic.dict_pos_monsters[self.id_m] = (self.x, self.y)

    

    def draw(self) -> None:
        """ draw the monster """
        # the skin if the monster is dead
        if not self.life:
            pyxel.blt(
                self.x,
                self.y,
                0,
                self.list_pos[2][0],
                self.list_pos[2][1],
                8 * self.direction,
                8,
                5
            )
            return
        


        # calculate the monster skin
        if pyxel.frame_count - self.touch_ground <= 5:
            number_pos = self.list_pos[1]
        elif pyxel.frame_count - self.touch_ground <= 10:
            number_pos = self.list_pos[2]
        elif not self.on_floor:
            number_pos = self.list_pos[0]
        else:
            number_pos = self.list_pos[1]
        

        pyxel.blt(
            self.x,
            self.y,
            0,
            number_pos[0],
            number_pos[1],
            8 * self.direction,
            8,
            5
        )

    
    def is_alive(self) -> bool:
        if self.life:
            return True
        if self.time_dead != 0:
            return True
        return False

    
        


    





##### _____ Monsters _____ #####

class Monsters:
    """ class used to control all the monsters """

    def __init__(self, list_pos_monsters:dict, physic:Physic) -> None:
        """ initialise all the monsters """
        self.physic = physic
        self.dict_monsters = {}
        for id_m, pos in enumerate(list_pos_monsters):
            self.dict_monsters[id_m] = Monster(pos[0], pos[1], id_m, physic)
            self.physic.add_monster(id_m, pos)


    def update(self) -> None:
        """ update all the monsters and delete dead monsters """
        # detect if a monster is dead
        for id_m, monster in self.dict_monsters.items():
            if not id_m in self.physic.dict_pos_monsters.keys():
                monster.life = False


        # update monsters
        for monster in self.dict_monsters.values():
            monster.update()


        # if a monster is dead
        list_del = []
        for id_m, monster in self.dict_monsters.items():
            if not monster.is_alive():
                list_del.append(id_m)
        for id_m in list_del:
            del self.dict_monsters[id_m]
        

    
    def draw(self) -> None:
        """ draw all the monsters """
        for monster in self.dict_monsters.values():
            monster.draw()

    
    def add(self, pos:tuple) -> None:
        """ add a monster """
        add = False
        k = 0
        for id_m in self.dict_monsters.keys():
            if not id_m == k:
                self.dict_monsters[k] = Monster(pos[0], pos[1], k, self.physic)
                self.physic.add_monster(k, pos)
                add = True
                break
            k += 1

        if not add:
            self.dict_monsters[k] = Monster(pos[0], pos[1], k, self.physic)
            self.physic.add_monster(k, pos)
            





            


        



App()

