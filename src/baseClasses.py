"""
Base Classes: Animo, PathManager
"""

from functions import *


class Animo:
    """
    An animation object that contains sprite and other properties depending on its type
    """
    def __init__(self, group, filename, scale, left, bottom, **kwargs):
        self.group = group
        self.filename = filename
        self.scale = scale

        # Setting default values
        if 'frameRate' in kwargs:
            self.frameRate = kwargs['frameRate']
        else:
            self.frameRate = FRAME_RATE                 # Lucky catte numbah >:3

        if 'speed' in kwargs:
            self.speed = kwargs['speed']
        else:
            self.speed = SPEED                      # Stolen default speed from arcade website

        if 'priority' in kwargs:
            self.priority = kwargs['priority']
        else:
            self.priority = PRIORITY

        sprite = arcade.Sprite()
        self.dictTexSet = {}

        # Loads all texture sets under sprite filename
        cwd = os.getcwd()
        sprite_dir = cwd + "/images/" + filename
        path_list = []
        name_list = []

        # Get list of all deepest sub directories, (and name list for dictionary of texture sets)
        path_list, name_list = traverse_sub_dir(filename, sprite_dir, filename, path_list, name_list)

        for idx in range(0, len(path_list)):
            # Get all images/textures within a texture set
            textures = [f for f in glob.glob(path_list[idx] + "/*")]
            tex_set = []

            # Load each images into an array of textures
            for file in textures:
                tex_set.append(arcade.load_texture(file, scale=scale))

            # Map key to the texture array
            if name_list[idx][0:len(filename)] == filename:
                name = name_list[idx][len(filename)+1:]
            else:
                name = name_list[idx]
            self.dictTexSet[name] = tex_set

            # ^ ^ ^ Had to settle for dis uncool string manipulation
            # Cause I'm a noob who can't figure how to do it while traversing subdirs :/

        if len(path_list) == 1:
            # If filename has no sub directory, set its only texture set as default
            default = self.dictTexSet['']

        else:
            if 'idle_right' in self.dictTexSet:
                default = self.dictTexSet['idle_right']
            elif 'unlatch' in self.dictTexSet:
                default = self.dictTexSet['unlatch']
            elif 'idle' in self.dictTexSet:
                default = self.dictTexSet['idle']
            else:
                key = list(self.dictTexSet.keys())
                default = self.dictTexSet[key[0]]

        # Setting sprite values
        sprite.textures = default           # Stores texture set
        sprite.texture = default[0]         # Holds current texture to display
        sprite.scale = scale
        sprite.left = left
        sprite.bottom = bottom

        self.sprite = sprite
        self.currTexIdx = 0
        self.texLength = len(default)

        # Additional properties for different animo group types
        if group == STATIC:
            self.loops = kwargs['loops']

        elif group == PLAYER:
            self.face = 'right'
            self.isWalking = False
            if 'walkFrameRate' in kwargs:
                self.walkFrameRate = kwargs['walkFrameRate']
            else:
                self.walkFrameRate = WALK_FRAME_RATE

        else:
            # 'Interactive' animo category:

            # Add extra properties required for corresponding groups
            if group == LATCH:
                # Works like a toggle switch
                self.isLatched = False

            elif group == CLICKDROP:
                # Click and drops sprite to another point
                self.isClicked = False

            elif group == AUTOPATH:
                # Sprite will load path file and automatically go according to it
                self.pathManager = PathManager(self)
                if 'showAnimation' in kwargs:
                    self.showAnimation = kwargs['showAnimation']
                else:
                    self.showAnimation = True
                if 'default_face' in kwargs:
                    self.default_face = kwargs['default_face']
                else:
                    self.default_face = 'right'

            elif group == BUTTON:
                # Works with ButtonManager to allow customizable actions
                self.isClicked = False
                self.disable = False
                self.eventRunning = False

                if 'ME' in kwargs:
                    self.ME = kwargs['ME']
                else:
                    self.ME = False

                if 'syncBro' in kwargs:
                    self.syncBro = kwargs['syncBro']


class PathManager:
    """
    An object for autopath type animos; it handles the animation for moving along a predetermined path
    """
    def __init__(self, animo):
        self.curr_idx = -1
        self.prev_last_idx = -1
        self.pathArray = []
        self.pathArrLen = 0
        self.isMoving = False
        self.linkedAnimo = animo

        animo.pathManager = self            # Python is pretty nutty, I did this like back-to-back //smh

    def add(self, x, y):
        if not self.pathArray:
            self.curr_idx = 0
            c_x = self.linkedAnimo.sprite.left
            c_y = self.linkedAnimo.sprite.bottom
        else:
            c_x = self.pathArray[self.pathArrLen - 1][0]
            c_y = self.pathArray[self.pathArrLen - 1][1]

        x = int(x)
        y = int(y)

        dx = x - c_x
        dy = y - c_y

        if abs(dx) > 0 and abs(dy) > 0:
            # If need to move diagonally, then split point into two path points
            pt1 = [c_x, y]
            pt2 = [x, y]
            self.pathArray.append(pt1)
            self.pathArray.append(pt2)
            self.pathArrLen += 2

        else:
            self.pathArray.append([x, y])
            self.pathArrLen += 1

    def load(self, filename):
        cwd = os.getcwd()
        file_path = cwd + "/path/" + filename + ".txt"
        file = tuple(open(file_path, 'r'))

        for f in file:
            string = f.strip('\n').split(',')
            x = int(string[0])
            y = int(string[1])
            self.add(x, y)

    def run(self):
        if not self.pathArray:
            # If no path, then run() doesn't do anything
            return
        elif self.curr_idx == self.pathArrLen:
            # If already did path, then run() doesn't do anything
            return

        animo = self.linkedAnimo

        x = animo.sprite.left
        y = animo.sprite.bottom
        i = self.curr_idx

        x_pt = self.pathArray[i][0]
        y_pt = self.pathArray[i][1]

        direction = get_direction(x, y, x_pt, y_pt)

        if self.isMoving is False:
            self.prev_last_idx = self.curr_idx
            self.isMoving = True
        else:
            # Handles changing of path trajectory
            if animo.face is not direction:
                self.curr_idx += 1

                if self.curr_idx == self.pathArrLen:
                    # If reached end of array, then stop moving
                    self.isMoving = False
                    stop(animo)

                    animo.face = animo.default_face
                    change_tex_set(animo, 'idle_' + animo.default_face)         # Default face when stopped
                    return
                else:
                    x_pt = self.pathArray[self.curr_idx][0]
                    y_pt = self.pathArray[self.curr_idx][1]
                    direction = get_direction(x, y, x_pt, y_pt)

        if direction is None:
            # If the next point to go is where sprite is currently at, then run() does nothing
            return

        walk(direction, animo)

    def no_animation(self):
        # Just go to the end of path array
        self.isMoving = False
        self.curr_idx = self.pathArrLen

        x = self.pathArray[self.pathArrLen - 1][0]
        y = self.pathArray[self.pathArrLen - 1][1]
        animo = self.linkedAnimo
        animo.sprite.left = x
        animo.sprit.bottom = y

        animo.face = animo.default_face
        change_tex_set(animo, 'idle_' + animo.default_face)         # Default face when stopped
