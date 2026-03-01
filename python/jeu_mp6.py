import pyxel
import random
import os
from datetime import datetime
import json




# tiles coordinates
TILE_FLOOR = [
    (0, 1), (1, 1), (2, 1), (0, 2), (1, 2), (2, 2), (0, 3), (1, 3), (2, 3),
    (5, 2), (6, 2), (5, 3), (6, 3),
    (3, 1), (3, 2), (3, 3),
    (7, 3), (8, 3)
]
TILE_SNOW = [(2, 7), (0, 8)]
TILE_ICE = [(1, 8), (7, 7), (7, 8)]
TILE_FLOOR_AIR = [(0, 4), (1, 4), (2, 4)]
TILE_STAIR_RIGHT = [(6, 1)]
TILE_STAIR_LEFT = [(5, 1)]
TILE_DOOR_CLOSE = [(2, 5), (2, 6)]
TILE_DOOR_OPEN = [(1, 5), (1, 6)]
TILE_LADDER = [(9, 1), (9, 2), (9, 3)]

TILE_DOOR = TILE_DOOR_CLOSE + TILE_DOOR_OPEN
TILE_STAIRS = TILE_STAIR_LEFT + TILE_STAIR_RIGHT
TILE_SOLID = TILE_FLOOR + TILE_FLOOR_AIR + TILE_SNOW
TILE_GROUND = TILE_SOLID + TILE_STAIR_LEFT + TILE_STAIR_RIGHT + TILE_SNOW


WORLD_COORDINATES = {
    0: [(0, 128), (0, 128)],
    1: [(0, 448), (0, 168)],
    2: [(0, 664), (0, 128)]
}






##### _____ App _____ ######

class App:
    def __init__(self):
        pyxel.init(
            128,
            128,
            title="rentre chez toi",
            fps=60,
        )
        pyxel.screen_mode(0)
        pyxel.fullscreen(True)

        pyxel.load('4.pyxres')

        # variables
        # positions of monsters
        self.pos_monsters = {
            0: [],
            1: [(104, 80), (288, 144)],
            2: [(184, 104), (488, 88)]
        }
        # position of objects
        self.pos_objects = {
            0: {},
            1: {
                "key" : [(248, 32)],
                "coin" : [(144, 56), (40, 80)]
            },
            2: {
                "key" : [(232, 32)],
                "coin" : [(160, 40), (523, 88)]
            }
        }
        # position of doors
        self.pos_doors = {
            0: [],
            1: [((88, 16), False, 2, (40, 96))],
            2: [
                ((40, 96), True, 1, (88, 16)),
                ((640, 48), False, 3, (0, 0))
            ]
        }
        # position of chests
        self.pos_chests = {
            0: [],
            1: [
                ((408, 88), 10),
                ((408, 152), 15)
            ],
            2: [
                ((560, 0), 20),
                ((248, 48), 15)
            ]
        }
        # positions of coin cubes
        self.pos_coin_cubes = {
            0: [],
            1: [
                ((320, 128), 10)
            ],
            2: [

            ]
        }

        pos_player = (15, 15)
        self.whereami = "start menu"
        self.world = 0      # the tilemap
        self.end_world = 3  # the world to teleport in the end menu
        self.pause = False
        self.language = "fr"
        self.cheats = False

        # instances objects
        self.physic = Physic(pos_player, self.world)
        self.chests = Chests(self.pos_chests, self.world)
        self.doors = Doors(self.pos_doors, self.world)
        self.coin_cubes = CoinCubes(self.pos_coin_cubes, self.world, self)
        self.objects = Objects(self.pos_objects, self.physic, self.world)
        self.player = Player(self.physic, pos_player, self.world, self.objects, self.doors, self.chests, self.coin_cubes)
        self.camera = Camera(self.world, self.physic)
        self.ui = UI(self, self.language)
        self.fake_player = FakePlayer(self.world)
        self.start_menu = StartMenu(self.language)
        self.monsters = Monsters(self.pos_monsters, self.physic, self.world)
        self.death_menu = DeathScreen(self.language)
        self.end_menu = EndScreen(self.language)
        self.cheat = Cheats(self)
        
        # run the app
        pyxel.run(self.update, self.draw)




    def update(self) -> None:
        """ update all the things """
        # if we put pause
        if pyxel.btnp(pyxel.KEY_P) and not self.cheats:
            self.pause = not self.pause


        # if we are in the game
        if self.whereami == "game" and not self.pause:

            self.objects.update()
            
            # update the line command or the player
            if self.cheats:
                self.cheat.update()
            else:
                self.player.update()

            # detect if the player is dead
            if self.player.life == 0:
                self.whereami = "death menu"

            # change the world if the world has changed
            elif self.world != self.player.world:
                self.update_world(self.player.world)
            
            
            self.coin_cubes.update()
            self.camera.update(self.player.x, self.player.y)
            self.monsters.update()
            self.ui.update()

        

        # if we are in the start menu
        elif self.whereami == "start menu":
            self.whereami, self.world = self.start_menu.update()
            self.fake_player.update()

            # update the world variable
            self.update_world(self.world)


        elif self.whereami == "death menu":
            self.death_menu.update()

        elif self.whereami == "end menu":
            self.end_menu.update()

        # if we enable or disable cheats
        if pyxel.btnp(pyxel.KEY_T) and not self.cheats:
            self.cheats = not self.cheats


    

    def update_world(self, world:int) -> None:
        """ change all the instances world """
        # if we have win
        if world == self.end_world:
            self.whereami = "end menu"
            return

        self.doors.world = world
        self.world = world
        self.coin_cubes.change_world(world)
        self.chests.world = world
        self.player.world = world
        self.physic.world = world
        self.camera.change_world(world, self.player.x, self.player.y)
        self.objects.world = world
        self.monsters.world = world






    def draw(self) -> None:
        """ draw all the things """
        # if we are in the game
        if self.whereami == "game":
            self.camera.draw()
            self.objects.draw()
            self.doors.draw()
            self.chests.draw()
            self.player.draw()
            self.coin_cubes.draw()
            self.monsters.draw()
            self.ui.draw()

            if self.cheats:
                self.cheat.draw()


        # if we are in the menu
        elif self.whereami == "start menu":
            self.camera.draw()
            self.start_menu.draw()
            if not self.start_menu.option:
                self.fake_player.draw()


        # if we are in the death menu
        elif self.whereami == "death menu":
            pyxel.cls(0)
            self.death_menu.draw()

        elif self.whereami == "end menu":
            pyxel.cls(0)
            self.end_menu.draw()


        return None










##### _____ Language _____ #####
def lang(text:int, language:str) -> str:
    """ return the text ascociated with the number and the language """
    lang = {
        "fr" : {
            0: "vie",
            1: "jouer",
            2: "quitter",
            3: "redemarrer",
            4: "VOUS ETES MORT",
            5: "langue",
            6: "style",
            7: "normal",
            8: "lisse",
            9: "retro",
            10: "retour",
            11: "options",
            12: "Bravo, tu est rentre"
        },
        "en" : {
            0: "life",
            1: "play",
            2: "quit",
            3: "restart",
            4: "YOU ARE DEAD",
            5: "language",
            6: "style",
            7: "normal",
            8: "smooth",
            9: "retro",
            10: "back",
            11: "options",
            12: "Well done, you are in"
        }
    }
    return lang[language][text]









##### _____ Physics _____ #####

class Physic:
    """ this class is used to have things relative to many things """

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
        """ 
            return 0 if the player is at the left of the position
            or 1 if the player is at right 
            used for monsters
        """
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
    

    def gen_world_for_monster(self, n:int) -> None:
        """ generate n world for monster """
        for world in range(n):
            self.dict_pos_monsters[world] = {}
    

    def add_monster(self, id_m:int, pos:tuple, world:int) -> None:
        """ add the monster in the physic class """
        self.dict_pos_monsters[world][id_m] = pos

    def del_monster(self, id_m:int, world:int) -> None:
        """ delete a monster """
        del self.dict_pos_monsters[world][id_m]


    def on_monster(self, x:int, y:int) -> bool:
        """ return if we are on a monster """
        for pos_monster in self.dict_pos_monsters[self.world].values():
            if pos_monster[1]-7 < y < pos_monster[1]+7:
                if pos_monster[0]-7 < x < pos_monster[0]+7:
                    return True
        return False
    

    def over_monster(self, x:int, y:int) -> None:
        """ search if we are over a monster and kill it """
        for id_m, pos_monster in self.dict_pos_monsters[self.world].items():
            if pos_monster[1]-8 < y < pos_monster[1]-4:
                if pos_monster[0]-7 < x < pos_monster[0]+7:
                    self.del_monster(id_m, self.world)
                    pyxel.play(0, 3)
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
                    # if the object is a key
                    if type_object == "key":
                        self.dict_objects[id_w][i] = Key(i, pos[0], pos[1], self.physic, type_object, self.world)
                    # if it's a coin
                    if type_object == "coin":
                        self.dict_objects[id_w][i] = Coin(i, pos[0], pos[1], self.physic, type_object, self.world)


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



    def add(self, type_obj:str, x:int, y:int, SPEED_X:int, SPEED_Y:int) -> None:
        """ add an object """
        add = False
        k = 0
        for i in sorted(self.dict_objects[self.world].keys()):
            if not i == k:

                # if the object is a key
                if type_obj == "key":
                    self.dict_objects[self.world][k] = Key(k, x, y, self.physic, type_obj, self.world, SPEED_X, SPEED_Y, 0.9)
                
                # if the object is a coin
                if type_obj == "coin":
                    self.dict_objects[self.world][k] = Coin(k, x, y, self.physic, type_obj, self.world, SPEED_X, SPEED_Y, 0.9)


                add = True
                break
            k += 1


        if not add:
            # if the object is a key
            if type_obj == "key":
                    self.dict_objects[self.world][k] = Key(k, x, y, self.physic, type_obj, self.world, SPEED_X, SPEED_Y, 0.9)
            
            # if it's a coin
            if type_obj == "coin":
                    self.dict_objects[self.world][k] = Coin(k, x, y, self.physic, type_obj, self.world, SPEED_X, SPEED_Y, 0.9)
        








##### _____ Object _____ #####
class Object:
    """ the master class for all objects """

    def __init__(self, id_o:int, x:int, y:int, physic:Physic, type_obj:str, world:int, speed_x:int=0, speed_y:int=0, slide_force:int=0) -> None:
        """ initialise base variables for the object """
        self.id_o = id_o
        self.world = world
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
            if tile_right in TILE_SOLID + TILE_STAIR_LEFT or tile_under_right in TILE_SOLID + TILE_STAIR_LEFT or self.x > (WORLD_COORDINATES[self.world][0][1] - 10):
                self.SPEED_X = 0

            # if we are on the floor but not on ice
            elif tile_under in TILE_SOLID or tile_under_right in TILE_SOLID:
                self.SPEED_X = 0

            # if we are on ice
            elif tile_under in TILE_ICE or tile_under_right in TILE_ICE:
                self.SPEED_X *= self.slide_force

            # if we are in the air
            else:
                self.SPEED_X -= 0.1

        # if we go to the left
        else:
            # if it's a wall
            if tile_left in TILE_SOLID + TILE_STAIR_RIGHT or tile_under_left in TILE_SOLID + TILE_STAIR_RIGHT or self.x < WORLD_COORDINATES[self.world][0][0]:
                self.SPEED_X = 0

            # if we are on the floor
            elif tile_under in TILE_SOLID or tile_under_right in TILE_SOLID:
                self.SPEED_X = 0

            # if we are on ice
            elif tile_under in TILE_ICE or tile_under_right in TILE_ICE:
                self.SPEED_X *= self.slide_force
            
            else:
                self.SPEED_X += 0.1


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
                self.SPEED_Y = self.gravity
            else:
                self.SPEED_Y += self.gravity


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
                if tile_right in TILE_SOLID + TILE_STAIR_LEFT + TILE_ICE or tile_right in TILE_SOLID + TILE_STAIR_LEFT + TILE_ICE:
                    self.SPEED_X = 0
                    break

                # if we are on stairs
                elif tile_under in TILE_STAIR_RIGHT or tile_under_right in TILE_STAIR_RIGHT:
                    self.SPEED_X -= 0.05
                    self.y = (self.y //8 *8) + 8 - (self.x % 8)
                
                self.x += 1

            # if we go on the left
            else:
                # if it's a wall
                if tile_left in TILE_SOLID + TILE_STAIR_RIGHT + TILE_ICE or tile_under_left in TILE_SOLID + TILE_STAIR_RIGHT + TILE_ICE:
                    self.SPEED_X = 0
                    break

                elif tile_under in TILE_STAIR_LEFT or tile_under_right in TILE_STAIR_LEFT:
                    self.SPEED_X += 0.05
                    self.y = (self.y //8 *8) + (self.x % 8)
            
                self.x -= 1

        
        # for y
        for _ in range(round(abs(self.SPEED_Y))):
            tile_over = self.physic.get_tile(self.x, self.y-1)
            tile_over_right = self.physic.get_tile(self.x+8, self.y-1)
            tile_under = self.physic.get_tile(self.x, self.y+8)
            tile_under_right = self.physic.get_tile(self.x+8, self.y+8)

            if self.SPEED_Y > 0:
                # if we are on the floor
                if tile_under in TILE_GROUND + TILE_ICE or tile_under_right in TILE_GROUND + TILE_ICE:
                    self.SPEED_Y = 0

                    # if we are on stairs
                    if tile_under_right in TILE_STAIR_RIGHT:
                        self.y = (self.y //8 *8) + 8 - (self.x % 8)
                
                    elif tile_under in TILE_STAIR_LEFT:
                        self.y = (self.y //8 *8) + (self.x % 8)

                    else:
                        self.y = self.y //8 *8
                
                    break

                self.y += 1

            else:
                if tile_over in TILE_GROUND + TILE_ICE or tile_over_right in TILE_GROUND + TILE_ICE:
                    self.SPEED_Y = 0
                
                else:
                    self.y -= 1











##### _____ Key class _____ #####

class Key(Object):

    def draw(self) -> None:
        """ draw the key """
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



##### _____ Coin class _____ #####

class Coin(Object):

    def draw(self) -> None:
        """ draw the coin """
        pyxel.blt(
            self.x,
            self.y,
            0,
            48,
            40,
            8,
            8,
            5
        )










##### _____ Chests _____ #####

class Chests:
    """ class used to control chests """

    def __init__(self, dict_chests:dict, world:int) -> None:
        """ initialise the chests """
        self.world = world

        # create all chests
        self.chests = {}
        for id_w, world in dict_chests.items():
            self.chests[id_w] = {}
            for chest in world:
                pos = chest[0]
                self.chests[id_w][chest[0]] = Chest(pos[0], pos[1], chest[1])

    
    def is_chest(self, x:int, y:int) -> int:
        """ return the number of coins of the chest if we are on a chest else return None """
        for pos, chest in self.chests[self.world].items():
            if pos[0] -7 < x < pos[0] +7 and pos[1] -7 < y < pos[1] +7 and chest.state:
                chest.state = False
                return chest.coins
            
    

    def draw(self) -> None:
        """ draw every chest """
        for chest in self.chests[self.world].values():
            chest.draw()


        







### ___ Chest ___ ###

class Chest:
    """ a chest object """

    def __init__(self, x:int, y:int, coins:int) -> None:
        """ initialise the chest """
        self.x = x
        self.y = y
        self.coins = coins
        self.state = True

    
    def draw(self) -> None:
        """ draw the chest """
        if self.state:
            pyxel.blt(
                self.x,
                self.y,
                0,
                56,
                40,
                8,
                8,
                5
            )
        else:
            pyxel.blt(
                self.x,
                self.y,
                0,
                64,
                40,
                8,
                8,
                5
            )











##### _____ Doors _____ #####
class Doors:
    """ the role of this class is to manage doors """

    def __init__(self, dict_pos_doors:dict, world:int) -> None:
        """ initialise all the doors """
        self.world = world

        self.dict_doors = {}

        for id_w, world in dict_pos_doors.items():
            # for each world create a dictionary to stock position and instances
            self.dict_doors[id_w] = {}
            for pos_door, state, dir_w, pos_w in world:
                self.dict_doors[id_w][pos_door] = Door(state, dir_w, pos_w, pos_door)



    def is_door(self, x:int, y:int) -> int:
        """ return 
         0 if there is no door
         1 if the door is close
         2 if the door is open
        """
        # search for each door
        for pos, door in self.dict_doors[self.world].items():
            # if the object is next to the door
            if pos[0] -8 < x < pos[0] +8 and y == pos[1] +8:
                # if the door is open
                if door.state:
                    return 2
                # if the door is close
                elif not door.state:
                    return 1
        # if there is no door
        return 0


                
    def enter_door(self, x:int, y:int) -> tuple:
        """ return the world to teleport and coordinates """
        for pos, door in self.dict_doors[self.world].items():
            # if the object is next to the door
            if pos[0] -8 < x < pos[0] +8 and y == pos[1] +8:
                # if the door is open
                if door.state:
                    return door.enter()
                
        # if there is no door or the door is close
        return None
    


    def open_door(self, x:int, y:int) -> None:
        """ open the door """
        for pos, door in self.dict_doors[self.world].items():
            # if the object is next to the door
            if pos[0] -8 < pos[0] +8 and y == pos[1] +8:
                # if the door is close
                if not door.state:
                    door.open()
            
        # if there is no door or the door is already open
        return 0


    def draw(self) -> None:
        """ draw all the doors """
        for door in self.dict_doors[self.world].values():
            door.draw()








### ___ subclass Door ___ ###
class Door:
    """ this object is one door """
    
    def __init__(self, state:bool, dir_w:int, pos_w:tuple, my_pos:tuple) -> None:
        """ initialise one door """
        self.state = state
        self.dir_w = dir_w
        self.pos_w = pos_w
        self.my_pos = my_pos

    
    def open(self) -> None:
        """ open the door """
        self.state = True

    def close(self) -> None:
        """ close the door """
        self.state = False

    def enter(self) -> tuple:
        """ return the world to teleport and coordinates """
        return self.dir_w, self.pos_w

    def draw(self) -> None:
        """ draw the door """
        pyxel.blt(
            self.my_pos[0],
            self.my_pos[1],
            0,
            (8 if self.state else 16),
            40,
            8,
            16,
            5
        )











##### _____ Coin Cube _____ #####

class CoinCubes:
    """ class used to control all coins cubes """

    def __init__(self, dict_pos_cubes:dict, world:int, master:App) -> None:
        """ initialise all the coins cubes """
        self.world = world
        self.master = master

        self.cubes = {}
        self.list_coins = []
        
        for id_w, world in dict_pos_cubes.items():
            self.cubes[id_w] = {}

            for pos, coins in world:
                self.cubes[id_w][pos] = CoinCube(pos[0], pos[1], coins)

    
    def under_cube(self, x:int, y:int) -> None:
        """ detect if the player is under a cube """
        for pos, cube in self.cubes[self.world].items():
            if pos[0] -2 < x < pos[0] +2 and pos[1] -2 < y < pos[1] +2:
                cube.steady = False

    

    def draw(self) -> None:
        """ draw all the cubes """
        for cube in self.cubes[self.world].values():
            cube.draw()
        
        for coin, _ in self.list_coins:
            coin.draw()

    
    def update(self) -> None:
        """ update cubes and coins """
        # coins
        list_supp = []
        for i in range(len(self.list_coins)):
            self.list_coins[i][0].update()
            self.list_coins[i][1] -= 1
            # if we have to delete the coin due to end of the time
            if self.list_coins[i][1] == 0:
                list_supp = [i] + list_supp
        
        for a in list_supp:
            self.list_coins.pop(a)

        # cubes
        tmp = self.is_on_player()
        if tmp != None:
            cube = self.cubes[self.world][tmp]
            # update the cube
            if cube.update(self.master.player.x, self.master.player.y -2):
                # add a coin to the player inventory
                if "coin" in self.master.player.dict_objects:
                    self.master.player.dict_objects["coin"] += 1
                else:
                    self.master.player.dict_objects["coin"] = 1

                # create a fake coin
                x = self.cubes[self.world][tmp].x
                y = self.cubes[self.world][tmp].y
                self.list_coins.append([FakeCoin(x, y, 0, -2.5, self.world), 25])

                # play the sound
                pyxel.play(0, 0)


            # if we delete the cube
            if not cube.state:
                del self.cubes[self.world][tmp]



    def is_on_player(self) -> tuple:
        """ return if a cube is on the player """
        for pos, cube in self.cubes[self.world].items():
            if not cube.state:
                del self.cubes[self.world][pos]
                return None
            elif not cube.steady:
                return pos
        return None
    

    def change_world(self, world:int) -> None:
        """ change the world and set varables """
        self.list_coins = []

        # if we have a cube
        tmp = self.is_on_player()
        if tmp != None:
            self.cubes[world][tmp] = self.cubes[self.world][tmp]
            self.cubes[world][tmp].world = world
            self.cubes[world][tmp].x = self.master.player.x
            self.cubes[world][tmp].y = self.master.player.y -2

        self.world = world










### ___ subclass Cube ____ ###
class CoinCube:
    """ class for instance coin cubes """
    def __init__(self, x:int, y:int, coins:int):
        """ initialise a coin cube """
        self.x = x
        self.y = y
        self.state = True
        self.steady = True
        self.delay = 0
        self.coin_delay = 60
        self.coin_remaining = coins


    def draw(self):
        """ draw the cube """
        pyxel.blt(
            self.x,
            self.y,
            0,
            40,
            40,
            8,
            8,
            5,
            scale=(1 if self.steady else 0.8)
        )

    def update(self, x:int, y:int) -> bool:
        """
            update the cube (only when on the head of the player)
            return if we have to increment player's coins
        """
        self.x = x
        self.y = y
        self.delay += 1

        if self.delay == self.coin_delay:
            self.delay = 0
            self.coin_remaining -= 1
            
            if self.coin_remaining == 0:
                self.state = False

            return True
        return False
    







### ___ subclass Fake Coin ___ ###

class FakeCoin:
    """ class used to have fake coins """
    def __init__(self, x:int, y:int, v_x:float, v_y:float, world:int):
        self.x = x
        self.y = y
        self.v_x = v_x
        self.v_y = v_y
        self.world = world
        self.gravity = 0.2

    
    def update(self):
        # x
        self.x += self.v_x
        self.v_x *= 0.8

        # y
        self.y += self.v_y
        self.v_y += self.gravity

    
    def draw(self):
        pyxel.blt(
            self.x,
            self.y,
            0,
            48,
            40,
            8,
            8,
            5
        )











##### _____ Player _____ #####

class Player:
    """ class used to control the player """

    def __init__(self, physic:Physic, pos_player:tuple, world:int, objects:Objects, doors:Doors, chests:Chests, coin_cubes:CoinCubes) -> None:
        """ initialise the player's class """
        # instances
        self.objects = objects
        self.doors = doors
        self.chests = chests
        self.physic = physic
        self.coin_cubes = coin_cubes

        # variables
        self.x = pos_player[0]
        self.y = pos_player[1]
        self.direction = 1
        self.SPEED_X = 1
        self.v_x = 0
        self.slide_force_x = 0.95
        self.counter_slide_force = 0.25
        self.SPEED_Y = 1
        self.jump_speed = 3
        self.gravity = 0.2
        self.dict_objects = {}
        self.world = world
        self.life = 5
        self.move = False
        self.time_life = 0
        self.object_select = None
        self.delay_life = 60
        self.selected_id = 0
        self.has_open_chest = 0



    def update(self) -> None:
        """ update the player """
        self.move = False

        tile_player = self.physic.get_tile(self.x, self.y)
        tile_left = self.physic.get_tile(self.x-1, self.y)
        tile_right = self.physic.get_tile(self.x+8, self.y)
        tile_over = self.physic.get_tile(self.x, self.y-1)
        tile_over_right = self.physic.get_tile(self.x+8, self.y-1)
        tile_under = self.physic.get_tile(self.x, self.y+8)
        tile_under_right = self.physic.get_tile(self.x+7, self.y+8)

        
        # gravity
        lad_1 = self.physic.get_tile(self.x+1, self.y)
        lad_2 = self.physic.get_tile(self.x+8, self.y+8)
        # if we are on a ladder
        if lad_1 in TILE_LADDER or lad_2 in TILE_LADDER:
            pass
        # if we are on the ground
        elif tile_under in TILE_SOLID or tile_under_right in TILE_SOLID:
            self.y = self.y //8 *8
        # if we are in the air
        else:
            self.SPEED_Y += self.gravity


        # player's mouvemnt
        if (pyxel.btn(pyxel.KEY_D) and not pyxel.btn(pyxel.KEY_Q)) or (pyxel.btn(pyxel.KEY_RIGHT) and not pyxel.btn(pyxel.KEY_LEFT)):
            # if we are on ice
            if tile_under in TILE_ICE or tile_under_right in TILE_ICE:
                self.v_x = self.v_x * self.slide_force_x + self.SPEED_X * self.counter_slide_force
                    
            # if we are not on ice
            else:
                self.v_x = self.SPEED_X
            self.direction = 1

        elif (pyxel.btn(pyxel.KEY_Q) and not pyxel.btn(pyxel.KEY_D)) or (pyxel.btn(pyxel.KEY_LEFT) and not pyxel.btn(pyxel.KEY_RIGHT)):
            # if we are on ice
            if tile_under in TILE_ICE or tile_under_right in TILE_ICE:
                self.v_x = self.v_x * self.slide_force_x - self.SPEED_X * self.counter_slide_force
                    
            # if we are not on ice
            else:
                self.v_x = -self.SPEED_X
            self.direction = -1

        # if we don't want to move but we are on ice
        elif tile_under in TILE_ICE or tile_under_right in TILE_ICE:
            self.v_x = self.v_x * self.slide_force_x

        # if we don't move but we are in the air
        elif tile_under not in TILE_GROUND + TILE_LADDER and tile_under_right not in TILE_GROUND + TILE_LADDER:
            self.v_x *= 0.9

        # if we don't move
        else:
            self.v_x = 0



        # for x
        for _ in range(round(abs(self.v_x * 10))):  # we muliply by 10 to be more precise
            new_x = self.x + (0.1 if self.v_x > 0 else -0.1)

            tile_right = self.physic.get_tile(new_x+8, self.y)
            tile_under = self.physic.get_tile(new_x, self.y+8)
            tile_under_right = self.physic.get_tile(new_x+8, self.y+8)

            # if we are in the world
            if WORLD_COORDINATES[self.world][0][0] < new_x < WORLD_COORDINATES[self.world][0][1] - 8:

                # if we go to the right
                if self.v_x > 0:
                    # if we are on stairs
                    if tile_right in TILE_STAIR_RIGHT or tile_under_right in TILE_STAIR_RIGHT:
                        self.y -= 0.1
                        self.x = new_x
                        self.move = True

                    elif tile_under in TILE_STAIR_LEFT:
                        self.y += 0.1
                        self.x = new_x
                        self.move = True
                
                    # if we are next to a wall
                    elif tile_right in TILE_SOLID + TILE_ICE:
                        self.v_x = 0
                        break

                    else:
                        self.x = new_x
                        self.move = True
                

                # if we go to the left
                else:
                    # if we are on stairs
                    if tile_left in TILE_STAIR_LEFT or tile_under in TILE_STAIR_LEFT:
                        self.y -= 0.1
                        self.x = new_x
                        self.move = True

                    elif tile_under_right in TILE_STAIR_RIGHT:
                        self.y += 0.1
                        self.x = new_x
                        self.move = True
                    
                    
                    # if we are next to a wall
                    elif tile_left in TILE_SOLID + TILE_ICE:
                        self.v_x = 0
                        break

                    else:
                        self.x = new_x
                        self.move = True

            # if we are out of the world
            else:
                break




        # if we press jump
        if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_UP):
            if tile_under in TILE_GROUND + TILE_ICE + TILE_LADDER or tile_under_right in TILE_GROUND + TILE_ICE + TILE_LADDER:
                self.SPEED_Y -= self.jump_speed



        # for y
        for _ in range(round(abs(self.SPEED_Y))):
            # if we fall
            if self.SPEED_Y > 0:
                new_y = self.y +1
                tile_under = self.physic.get_tile(self.x, new_y+8)
                tile_under_right = self.physic.get_tile(self.x+8,new_y+8)

                 # if we are in a ladder
                if tile_player in TILE_LADDER or tile_under in TILE_LADDER:
                    self.SPEED_Y = 0
                    break

                # if we are on the ground
                elif tile_under in TILE_GROUND + TILE_ICE or tile_under_right in TILE_GROUND + TILE_ICE:
                    self.SPEED_Y = 0

                    # if we are on stairs
                    if tile_under_right in TILE_STAIR_RIGHT:
                        self.y = (new_y //8 *8) + 8 - (self.x % 8)

                    elif tile_under in TILE_STAIR_LEFT:
                        self.y = (new_y //8 *8) + (self.x % 8)

                    # not on stairs
                    else:
                        self.y = new_y //8 *8

                    break
                

                # if we are not on the ground
                self.y = new_y

            # if we jump
            else:
                new_y = self.y -1
                tile_over = self.physic.get_tile(self.x, new_y-1)
                tile_over_right = self.physic.get_tile(self.x+8, new_y-1)

                # if we are under a solid
                if tile_over in TILE_GROUND + TILE_ICE or tile_over_right in TILE_GROUND + TILE_ICE:
                    self.SPEED_Y = 0
                    break
                
                self.y = new_y
        
        # verify if we kill a monster
        self.physic.over_monster(self.x, self.y)
        self.coin_cubes.under_cube(self.x, self.y)


        # if the player is climbing a ladder
        tile_player = self.physic.get_tile(self.x+1, self.y)
        tile_right = self.physic.get_tile(self.x+6, self.y)
        tile_under = self.physic.get_tile(self.x+1, self.y+8)
        tile_under_1 = self.physic.get_tile(self.x, self.y+8)
        tile_under_2 = self.physic.get_tile(self.x, self.y+7)
        tile_under_right = self.physic.get_tile(self.x+6, self.y+8)
        tile_under_right_2 = self.physic.get_tile(self.x+6, self.y+7)

        # up
        if pyxel.btn(pyxel.KEY_Z) or pyxel.btn(pyxel.KEY_UP):
            if tile_player in TILE_LADDER or tile_right in TILE_LADDER or tile_under_2 in TILE_LADDER and tile_under_right_2 in TILE_LADDER:
                self.y -= 1

        # down
        elif pyxel.btn(pyxel.KEY_S) or pyxel.btn(pyxel.KEY_DOWN):
            if tile_under in TILE_LADDER and tile_under_right in TILE_LADDER:
                if tile_under_1 in TILE_LADDER:
                    self.x = self.x //8 *8
                else:
                    self.x = (self.x //8 +1) *8
                self.y += 1



        
        # grab an object
        tmp = self.objects.on_object(self.x, self.y)
        if tmp != None:
            type_obj, id_obj = tmp

            # if it's the first of our inventory
            if self.dict_objects == {}:
                self.object_select = type_obj

            # add the object in our inventory
            if type_obj in self.dict_objects:
                self.dict_objects[type_obj] += 1
            else:
                self.dict_objects[type_obj] = 1
            
            # delete the object of the world
            self.objects.del_obj(id_obj)

            # play the sound
            if type_obj in ["key", "coin"]:
                pyxel.play(0, 0)


        
        # throw an object
        if pyxel.btnp(pyxel.KEY_A) and self.dict_objects != {}:
            # add the object in the world
            self.objects.add(
                self.object_select,
                self.x + (8 if self.direction == 1 else -8),
                self.y - 1,
                (3 if self.direction == 1 else -3),
                -2
            )

            # delete the object of our inventory
            if self.dict_objects[self.object_select] == 1:
                del self.dict_objects[self.object_select]
                # change the selected object
                if self.dict_objects == {}:
                    self.object_select = None
                else:
                    for key in self.dict_objects.keys():
                        break
                    self.object_select = key

            else:
                self.dict_objects[self.object_select] -= 1

            # if we have no much objetcs
            if self.dict_objects == {}:
                self.object_select = None
            

        

        
        # use an object or enter somewere
        if pyxel.btnp(pyxel.KEY_E):

            # if the player try to open a door
            door = self.doors.is_door(self.x, self.y)
            if door == 1:
                # verify if we have the key
                if "key" in self.dict_objects:
                    if self.dict_objects["key"] > 0:
                        # open the door
                        self.doors.open_door(self.x, self.y)
                        
                        # delete one key
                        if self.dict_objects["key"] > 1:
                            self.dict_objects["key"] -= 1
                        else:
                            del self.dict_objects["key"]
                            # change the selected object
                            if self.dict_objects == {}:
                                self.object_select = None
                            else:
                                for key in self.dict_objects.keys():
                                    break
                                self.object_select = key

                        # play the sound
                        pyxel.play(0, 1)


            # if the player try to open a chest
            tmp = self.chests.is_chest(self.x, self.y)
            if tmp:
                # add the coin
                if "coin" in self.dict_objects:
                    self.dict_objects["coin"] += tmp
                else:
                    self.dict_objects["coin"] = tmp

                # play the sound
                pyxel.play(0, 1)
                self.has_open_chest = 1
            
            # if the player try to enter in a new world
            elif door == 2:
                tmp = self.doors.enter_door(self.x, self.y)
                if tmp != None:
                    self.world, (self.x, self.y) = tmp

        

        # update position in physic
        self.physic.pos_player = [self.x, self.y]


        # detect if we are on an monster
        if pyxel.frame_count - self.time_life > self.delay_life:
            if self.physic.on_monster(self.x, self.y):
                self.life -= 1
                pyxel.play(0, 2)
                self.time_life = pyxel.frame_count

        

        # change the selected object
        if pyxel.btnp(pyxel.KEY_R):
            # if we are at the start of the list
            if self.selected_id == 0:
                pass
            else:
                for i, objects in enumerate(self.dict_objects.keys()):
                    if i +1 == self.selected_id:
                        self.selected_id = i
                        self.object_select = objects

        
        if pyxel.btnp(pyxel.KEY_F):
            # if we are at the end of the list
            if self.selected_id == len(self.dict_objects) -1:
                pass
            for i, objects in enumerate(self.dict_objects.keys()):
                if i -1 == self.selected_id:
                    self.selected_id = i
                    self.object_select = objects

        

        # play the coin sound after the chest sound
        if self.has_open_chest > 0:
            self.has_open_chest += 1
            if self.has_open_chest == 20:
                self.has_open_chest = 0
                pyxel.play(0, 0)

    




    
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


    def update(self, p_x:int, p_y:int, world:int=None) -> None:
        """ update the camera """
        

        # for x
        if WORLD_COORDINATES[self.world][0][0] + 45 < p_x < WORLD_COORDINATES[self.world][0][1] - 53:
            self.x = p_x - 45
        
        elif p_x <= WORLD_COORDINATES[self.world][0][0] + 45:
            self.x = 0
        
        elif p_x > WORLD_COORDINATES[self.world][0][1] - 53:
            self.x = WORLD_COORDINATES[self.world][0][1] - 98

        # for y
        if WORLD_COORDINATES[self.world][1][0] + 60 < p_y < WORLD_COORDINATES[self.world][1][1] - 68:
            self.y = p_y - 60

        elif p_y < WORLD_COORDINATES[self.world][1][0] + 60:
            self.y = 0
        
        elif p_y > WORLD_COORDINATES[self.world][1][1] - 68:
            self.y = WORLD_COORDINATES[self.world][1][1] - 128

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

    
    def change_world(self, world:int, x:int, y:int) -> None:
        """ change the world and the position of the camera """
        self.world = world
        # for x
        if WORLD_COORDINATES[self.world][0][0] + 45 < x < WORLD_COORDINATES[self.world][0][1] - 53:
            self.x = x - 45

        elif x < WORLD_COORDINATES[self.world][0][0] + 45:
            self.x = 0
        
        elif x > WORLD_COORDINATES[self.world][0][1] - 53:
            self.x = WORLD_COORDINATES[self.world][0][1] - 98
        
        # for y
        if WORLD_COORDINATES[self.world][1][0] + 60 < y < WORLD_COORDINATES[self.world][1][1] - 68:
            self.y = y - 60

        elif WORLD_COORDINATES[self.world][1][0] + 60 > y:
            self.y = 0
        
        elif y > WORLD_COORDINATES[self.world][1][1] - 68:
            self.y = WORLD_COORDINATES[self.world][1][1] - 128


        pyxel.camera(self.x, self.y)









##### _____ UI _____ #####
class UI:
    """ class used to diplay the UI """

    def __init__(self, app:App, language:str) -> None:
        """ initialise the UI """
        self.app = app
        self.dict_objects = {}
        self.life = 5
        self.coins = 0
        self.x = self.app.camera.x + 98
        self.y = self.app.camera.y
        self.pos_objects = [(3, 12), (3, 22), (3, 32)]
        self.selected = None
        self.language = language


    def update(self) -> None:
        """ update all things to display on the UI """
        # for all things to draw
        self.dict_objects = self.app.player.dict_objects
        self.selected = self.app.player.object_select
        self.life = self.app.player.life

        # for the camera
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

        # life
        pyxel.text(
            self.x + 3,
            self.y + 3,
            f"{lang(0, self.language)}: {self.life}",
            4
        )

        # objects
        for i, (objects, number) in enumerate(self.dict_objects.items()):
            # draw the square if the object is selected
            if objects == self.selected:
                pyxel.rect(
                self.x + self.pos_objects[i][0] -1,
                self.y + self.pos_objects[i][1] -1,
                10,
                10,
                12
            )
            pyxel.rect(
                self.x + self.pos_objects[i][0],
                self.y + self.pos_objects[i][1],
                8,
                8,
                0
            )

            # draw the object
            if objects == "key":
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
            if objects == "coin":
                pyxel.blt(
                    self.x + self.pos_objects[i][0],
                    self.y + self.pos_objects[i][1],
                    0,
                    48,
                    40,
                    8,
                    8,
                    5
                )


            
            # draw the text
            pyxel.text(
                self.x + self.pos_objects[i][0] +10,
                self.y + self.pos_objects[i][1] +2,
                f"x:{number}",
                4
            )







##### _____ Start Menu _____ #####

class StartMenu:
    """ the menu displayed at the start of the game """

    def __init__(self, language:str) -> None:
        """ initialise the menu and the buttons """
        # variables
        self.play = False
        self.option = False
        self.language = language
        self.bouton_play = Button(35, 8, 1, self)
        self.bouton_quitter = Button(35, 50, 2, self)
        pyxel.mouse(True)

        # instances
        self.option_menu = Options(self.language)

    
    def update(self) -> str:
        """ update the menu and return where we are """
        # if we are not in the option menu
        if not self.option:
            # if play
            if self.bouton_play.update():
                pyxel.mouse(False)
                return "game", 1
            
            # if we exit
            if self.bouton_quitter.update():
                pyxel.quit()

            # if we enter in parameter
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                if 115 < pyxel.mouse_x < 125 and 3 < pyxel.mouse_y < 13:
                    self.option = True
        
        # if we are in the option menu
        else:
            tmp = self.option_menu.update()
            if tmp != None:
                self.language = tmp
                self.option = False
        

        return "start menu", 0
        

    def draw(self) -> None:
        """ display the menu """
        # if we are not in the option menu
        if not self.option:
            self.bouton_play.draw()
            self.bouton_quitter.draw()

            # the button for the option menu
            pyxel.rect(
                115,
                3,
                10,
                10,
                0
            )
            pyxel.text(
                118,
                5,
                "!",
                8
            )


        # if we are in the option menu
        else:
            pyxel.cls(0)
            self.option_menu.draw()
    

        







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

    def __init__(self, x:int, y:int, text, master):
        """ initialise one button """
        self.master = master
        self.x = x
        self.y = y
        self.text = text
        self.w = 50
        self.h = 16
        self.border = 2
        self.dec_y = 3
        self.color_1 = 2
        self.color_2 = 11
        self.color_3 = 0

    def update(self) -> bool:
        """ return if we have clicked on the button or not """
        # detect if the mouse is on the button to change to color and to return if we click on it
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

        # calcul the decalage to appy to the text to center it
        if type(self.text) == str:
            text = self.text
            dec_x = (self.w - self.border*2 - len(text) * 4) // 2
        else:
            text = lang(self.text, self.master.language)
            dec_x = (self.w - self.border*2 - len(text) * 4) // 2

        # the text of the button
        pyxel.text(
            self.x + self.border + dec_x,
            self.y + self.border + self.dec_y,
            text,
            self.color_3
        )










##### _____ End Screen _____ #####

class EndScreen:
    """ this class is used to display the end screen """
    def __init__(self, language:str):
        self.language = language
        self.button_restart = Button(40, 30, 3, self)
        self.button_quit = Button(40, 50, 2, self)



    def update(self):
        """ update the menu """
        pyxel.camera(0, 0)
        pyxel.mouse(True)
        # update all the buttons
        if self.button_quit.update():
            pyxel.quit()

        elif self.button_restart.update():
            pyxel.reset()

    

    def draw(self):
        """ draw the menu """
        # the text
        pyxel.text(
            40,
            15,
            lang(12, self.language),
            8
        )

        # the buttons
        self.button_restart.draw()
        self.button_quit.draw()









##### _____ Death Screen _____ #####

class DeathScreen:
    """ this class is used to display the death screen """
    def __init__(self, language:str):
        self.language = language
        self.button_restart = Button(40, 30, 3, self)
        self.button_quit = Button(40, 50, 2, self)



    def update(self):
        """ update the menu """
        pyxel.camera(0, 0)
        pyxel.mouse(True)
        # update all the buttons
        if self.button_quit.update():
            pyxel.quit()

        elif self.button_restart.update():
            pyxel.reset()

    

    def draw(self):
        """ draw the menu """
        # the text
        pyxel.text(
            40,
            15,
            lang(4, self.language),
            8
        )

        # the buttons
        self.button_restart.draw()
        self.button_quit.draw()










### ___ subclass Monster ___ ###

class Monster:
    """ class for one monster """

    def __init__(self, x:int, y:int, id_m:int, physic:Physic, world:int) -> None:
        """ create a new monster """
        self.physic = physic
        self.world = world
        self.id_m = id_m
        self.x = x
        self.y = y
        self.SPEED_X = 1
        self.SPEED_Y = 0
        self.gravity = 0.2
        self.life = True
        self.time_dead = 20                 # the time to apply a fake skin of death
        self.direction = 1
        self.action = 2                     # 0 for left 1 for right 2 for wait
        self.frames_actions = 60            # the number of frames to wait between 2 actions
        self.list_pos = [(40, 88), (48, 88), (56, 88), (64, 88)]
        self.len_list = len(self.list_pos)
        self.touch_ground = -1000           # when the monster touch the ground to apply skin
        self.on_floor = True

        self.physic.add_monster(self.id_m, (self.x, self.y), self.world)



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
        if (tile_under in TILE_SOLID + TILE_ICE or tile_under_right in TILE_SOLID + TILE_ICE) and pyxel.frame_count % self.frames_actions == 0:
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
        elif tile_under in TILE_SOLID + TILE_ICE or tile_under_right in TILE_SOLID + TILE_ICE:
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
            self.x = max(WORLD_COORDINATES[self.world][0][0], self.x - self.SPEED_X)
            self.direction = 1
        
        elif self.action == 1:
            self.x = min(WORLD_COORDINATES[self.world][0][1] -8, self.x + self.SPEED_X)
            self.direction = -1

        # apply the gravity to the monster
        if self.SPEED_Y > 0:
            for _ in range(round(self.SPEED_Y)):
                self.y += 1
                tile_under = self.physic.get_tile(self.x, self.y+8)
                tile_under_right = self.physic.get_tile(self.x+8, self.y+8)
                if tile_under in TILE_SOLID + TILE_ICE or tile_under_right in TILE_SOLID + TILE_ICE:
                    if tile_under in TILE_STAIRS or tile_under_right in TILE_STAIRS:
                        self.y = self.physic.stair_under(self.x, self.y)
                    break
        if self.SPEED_Y < 0:
            for _ in range(round(-self.SPEED_Y)):
                self.y -= 1
                tile_over = self.physic.get_tile(self.x, self.y-1)
                tile_over_right = self.physic.get_tile(self.x+8, self.y-1)
                if tile_over in TILE_SOLID + TILE_ICE or tile_over_right in TILE_SOLID + TILE_ICE:
                    break

        
        # set the position in the physic class
        self.physic.dict_pos_monsters[self.world][self.id_m] = (self.x, self.y)

    

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
        """ return if the monster is alive or not """
        if self.life or self.time_dead != 0:
            return True
        return False

    
        


    





##### _____ Monsters _____ #####

class Monsters:
    """ class used to control all the monsters """

    def __init__(self, dict_pos_monsters:dict, physic:Physic, world:int) -> None:
        """ initialise all the monsters """
        self.physic = physic
        self.world = world
        self.dict_monsters = {}

        # generate the worlds in physic for the monsters
        self.physic.gen_world_for_monster(len(dict_pos_monsters))

        # for every world
        for id_w, world in dict_pos_monsters.items():
            self.dict_monsters[id_w] = {}
            # for every monster of every world
            for id_m, pos in enumerate(world):
                self.dict_monsters[id_w][id_m] = Monster(pos[0], pos[1], id_m, self.physic, id_w)



    def update(self) -> None:
        """ update all the monsters and delete dead monsters """
        # detect if a monster is dead
        for id_m, monster in self.dict_monsters[self.world].items():
            if not id_m in self.physic.dict_pos_monsters[self.world].keys():
                monster.life = False


        # update monsters
        for monster in self.dict_monsters[self.world].values():
            monster.update()


        # if a monster is dead
        list_del = []
        for id_m, monster in self.dict_monsters[self.world].items():
            if not monster.is_alive():
                list_del.append(id_m)
        for id_m in list_del:
            del self.dict_monsters[self.world][id_m]
        

    
    def draw(self) -> None:
        """ draw all the monsters """
        for monster in self.dict_monsters[self.world].values():
            monster.draw()

    
    def add(self, pos:tuple) -> None:
        """ add a monster """
        add = False
        k = 0
        for id_m in self.dict_monsters[self.world].keys():
            if not id_m == k:
                self.dict_monsters[self.world][k] = Monster(pos[0], pos[1], k, self.physic)
                add = True
                break
            k += 1

        if not add:
            self.dict_monsters[self.world][k] = Monster(pos[0], pos[1], k, self.physic)
            







##### _____ Options Menu _____ #####

class Options:
    """ the class of the options menu """
    def __init__(self, language) -> None:
        """ initialise the menu """
        # variables
        self.language = language
        self.place = "main"
        self.language = language
        self.button_lang = Button(40, 30, 5, self)
        self.button_style = Button(40, 50, 6, self)
        self.button_back = Button(40, 70, 10, self)

        # instances
        self.menu_language = OptionLanguage(self)
        self.menu_style = OptionStyle(self)



    def update(self) -> str:
        """ update the menu """
        # if we are in the main menu
        if self.place == "main":
            if self.button_lang.update():
                self.place = "lang"

            elif self.button_style.update():
                self.place = "style"

            elif self.button_back.update():
                return self.language

        
        # if we are in the language menu
        elif self.place == "lang":
            lang = self.menu_language.update()
            if lang != None:
                self.language = lang

        # if we are in the style menu
        elif self.place == "style":
            self.menu_style.update()



    def draw(self) -> None:
        """ display the menu """
        # if we are in the main menu
        if self.place == "main":
            self.button_lang.draw()
            self.button_style.draw()
            self.button_back.draw()
            pyxel.text(
                30,
                15,
                lang(11, self.language),
                8
            )


        # if we are in the language menu
        elif self.place == "lang":
            self.menu_language.draw()

        # if we are in the style menu
        elif self.place == "style":
            self.menu_style.draw()





### ___ subclass language ___ ###
class OptionLanguage:
    """ the language option menu """
    def __init__(self, master:Options) -> None:
        """ initialise the menu """
        self.master = master
        self.button_fr = Button(40, 30, "Francais", None)
        self.button_en = Button(40, 50, "English", None)
        self.button_back = Button(40, 70, 10, self.master)
        

    
    def update(self) -> str:
        """ update the menu """
        if self.button_fr.update():
            return "fr"
        
        elif self.button_en.update():
            return "en"

        elif self.button_back.update():
            self.master.place = "main"
            return None
        
    
    def draw(self) -> None:
        self.button_en.draw()
        self.button_fr.draw()
        self.button_back.draw()
        pyxel.text(
            30,
            15,
            lang(5, self.master.language),
            8
        )




### ___ subclass style ___ ###
class OptionStyle:
    """ the style option menu """
    def __init__(self, master:Options) -> None:
        """ initialise the menu """
        self.master = master
        self.button_norm = Button(40, 30, 7, self.master)
        self.button_smooth = Button(40, 50, 8, self.master)
        self.button_retro = Button(40, 70, 9, self.master)
        self.button_back = Button(40, 90, 10, self.master)

    
    def update(self) -> None:
        """ update the menu """
        if self.button_norm.update():
            pyxel.screen_mode(0)
        
        elif self.button_smooth.update():
            pyxel.screen_mode(1)

        elif self.button_retro.update():
            pyxel.screen_mode(2)

        elif self.button_back.update():
            self.master.place = "main"


    def draw(self) -> None:
        """ display the menu """
        self.button_norm.draw()
        self.button_smooth.draw()
        self.button_retro.draw()
        self.button_back.draw()
        pyxel.text(
            30,
            15,
            lang(6, self.master.language),
            8
        )









##### _____ Cheat _____ #####

class Cheats:
    """ this class is used to cheat because of the difficulty of the game ;) """
    def __init__(self, master:App) -> None:
        """ initialise the cheats """
        self.keys = {
            "a": pyxel.KEY_A,
            "b": pyxel.KEY_B,
            "c": pyxel.KEY_C,
            "d": pyxel.KEY_D,
            "e": pyxel.KEY_E,
            "f": pyxel.KEY_F,
            "g": pyxel.KEY_G,
            "h": pyxel.KEY_H,
            "i": pyxel.KEY_I,
            "j": pyxel.KEY_J,
            "k": pyxel.KEY_K,
            "l": pyxel.KEY_L,
            "m": pyxel.KEY_M,
            "n": pyxel.KEY_N,
            "o": pyxel.KEY_O,
            "p": pyxel.KEY_P,
            "q": pyxel.KEY_Q,
            "r": pyxel.KEY_R,
            "s": pyxel.KEY_S,
            "t": pyxel.KEY_T,
            "u": pyxel.KEY_U,
            "v": pyxel.KEY_V,
            "w": pyxel.KEY_W,
            "x": pyxel.KEY_X,
            "y": pyxel.KEY_Y,
            "z": pyxel.KEY_Z,
            " ": pyxel.KEY_SPACE,
            "0": pyxel.KEY_0,
            "1": pyxel.KEY_1,
            "2": pyxel.KEY_2,
            "3": pyxel.KEY_3,
            "4": pyxel.KEY_4,
            "5": pyxel.KEY_5,
            "6": pyxel.KEY_6,
            "7": pyxel.KEY_7,
            "8": pyxel.KEY_8,
            "9": pyxel.KEY_9
        }
    
        self.line = ""
        self.a_line = ""
        self.master = master
        
        # set x and y
        self.x = self.master.camera.x
        self.y = self.master.camera.y


    def update(self) -> None:
        """ update the command line """
        # update x and y
        self.x = self.master.camera.x
        self.y = self.master.camera.y


        # if a button is pressed
        for letter, k_id in self.keys.items():
            if pyxel.btnp(k_id):
                self.line += letter

        # if we enter the command
        if pyxel.btnp(pyxel.KEY_RETURN):
            line_decomp = self.line.split(" ")
            self.a_line = self.line
            self.line = ""
            self.command(line_decomp)

        # if we delete a char
        elif pyxel.btnp(pyxel.KEY_BACKSPACE):
            self.line = self.line[:-1]

        # if we want the ancient line
        elif pyxel.btnp(pyxel.KEY_UP):
            self.line = self.a_line
        
        # if we want a new line
        elif pyxel.btnp(pyxel.KEY_DOWN):
            self.line = ""

        # if we close the command line
        elif pyxel.btnp(pyxel.KEY_CTRL):
            self.master.cheats = False


    
    def command(self, line_decomp:list) -> None:
        """ try to execute the command """
        cmd = line_decomp[0]

        if cmd == "give":
            if len(line_decomp) == 2:
                self.give(line_decomp[1])
            elif len(line_decomp) == 3:
                self.give(line_decomp[1], line_decomp[2])


        elif cmd == "tp":
            # without change world
            if len(line_decomp) == 3:
                self.tp(line_decomp[1], line_decomp[2])
            
            # change world
            if len(line_decomp) == 4:
                self.tp(line_decomp[1], line_decomp[2])
                self.change_world(line_decomp[3])
        
        elif cmd == "gamerule":
            if len(line_decomp) == 3:
                self.gamerule(line_decomp[1], line_decomp[2])


        elif cmd == "exit":
            pyxel.quit()

        elif cmd == "restart":
            pyxel.reset()

        elif cmd == "end":
            self.master.update_world(self.master.end_world)
    
        elif cmd == "death":
            self.master.player.life = 0

        elif cmd == "player":
            if len(line_decomp) == 3:
                self.player(line_decomp[1], line_decomp[2])



    
    def draw(self):
        # draw the rect
        pyxel.rect(
            self.x,
            self.y,
            98,
            7,
            0
        )

        # draw the text
        pyxel.text(
            self.x +1,
            self.y +1,
            self.line,
            4
        )
    


    ### --- The list of commands --- ###

    def give(self, obj:str, number:str="1") -> None:
        """ add the object in the player list of object """
        # verify if the object is good
        if not obj in ["key", "coin"]:
            return
        
        # add the object
        if obj in self.master.player.dict_objects:
            self.master.player.dict_objects[obj] += int(number)
        else:
            self.master.player.dict_objects[obj] = int(number)


    def tp(self, x:str, y:str) -> None:
        """ teleport the player """
        self.master.player.x = int(x)
        self.master.player.y = int(y)


    def change_world(self, world:str):
        """ change the world of the player """
        self.master.update_world(int(world))

    
    def gamerule(self, rule:str, param:str) -> None:
        """ change a parameter of the game """
        if not rule in ["fullscreen"]:
            return
        
        if rule == "fullscreen" and param in ["true", "false"]:
            pyxel.fullscreen((True if param == "true" else False))


    
    def player(self, option:str, param:str) -> None:
        """ change a thing of the player """
        if not option in ["life"]:
            return
        
        if option == "life":
            self.master.player.life = int(param)









##### _____ Map Screen _____ #####

class MapScreen:
    """ class used to display and interact with the choosing map menu """

    def __init__(self) -> None:
        """ initialise the menu """
        self.list_saves = os.listdir()
        self.nbr_menu = 0
        self.dict_buttons = {}

        if self.list_saves > 4:
            self.button_left = Button(5, 60, "<", None)
            self.button_right = Button(120, 60, ">", None)

        # set the right number of dict in the base dict
        for k in range(len(self.list_saves) // 4 + (0 if len(self.self.list_saves) %4 == 0 else 1)):
            self.dict_buttons[k] = {}

        # add all the buttons in the right place in dict
        for i, save in enumerate(self.list_saves):
            y = k %4 *20 +30
            self.dict_buttons[i //4][save] = Button(40, y, save, None)








# if we are not in the right folder
if "python" in os.listdir():
    os.chdir("python")

# my libs integrated

class Json:
    def Read(file):
        try:
            data = json.load(open(file, "r"))
        except Exception as e:
            print(f"a error has occured : {e}")
        return data

    def Save(data, file):
        try:
            json.dump(data, open(file, "w"))
        except Exception as e:
            print(f"an error has occured : {e}")

App()

