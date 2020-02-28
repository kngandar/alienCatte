"""
Functions: change_tex_set, walk, stop, update_animation, get_direction, inbound
Constants: STATIC, PLAYER, LATCH, CLICKDROP, AUTOPATH, BUTTON
"""

import arcade
import os
import glob

# CONSTANTS
STATIC = 1
PLAYER = 2
LATCH = 3
CLICKDROP = 4
AUTOPATH = 5
BUTTON = 6

# Default numbers
FRAME_RATE = 19
SPEED = 5
PRIORITY = 0
WALK_FRAME_RATE = 8


def change_tex_set(animo, key):
    """
    Switches current texture set with another
    """

    sprite = animo.sprite
    sprite.textures = animo.dictTexSet[key]
    sprite.texture = sprite.textures[0]

    animo.currTexIdx = 0
    animo.texLength = len(sprite.textures)


def walk(face, animo):
    """
    Handles starting/changing sprite speed + set walking direction
    """

    animo.isWalking = True
    sprite = animo.sprite
    speed = animo.speed
    if sprite.change_x is 0 and sprite.change_y is 0:
        if face is 'left' or face is 'right':
            if face is 'right':
                sprite.change_x = speed
            else:
                sprite.change_x = -speed
        else:
            if face is 'up':
                sprite.change_y = speed
            else:
                sprite.change_y = -speed
        animo.face = face
        key = 'walk_' + face
        change_tex_set(animo, key)

    else:
        if animo.face is not face:
            animo.face = face
            key = 'walk_' + face
            change_tex_set(animo, key)

        if face is 'left' or face is 'right':
            if face is 'right':
                sprite.change_x = speed
            else:
                sprite.change_x = -speed
            sprite.change_y = 0
        else:
            if face is 'up':
                sprite.change_y = speed
            else:
                sprite.change_y = -speed
            sprite.change_x = 0


def stop(animo):
    """
    Stops sprite from moving + set idle direction
    """

    animo.isWalking = False
    animo.sprite.change_x = 0
    animo.sprite.change_y = 0
    key = 'idle_' + animo.face
    change_tex_set(animo, key)


def update_animation(animo):
    """
    Handles the texture changing animation thingy
    """
    frame_rate = animo.frameRate

    if animo.group == PLAYER:
        # Special case: If player animo, it has walking frame rate (different from normal one)
        if animo.isWalking:
            frame_rate = animo.walkFrameRate

    curr_idx = animo.currTexIdx + 1
    tex_len = animo.texLength

    if curr_idx >= tex_len*frame_rate:
        curr_idx = 0

        if animo.group == STATIC:
            # Special case: Handles loop counter for static animos
            if animo.loops is not -1:
                animo.loops -= 1
                if animo.loops is 0:
                    return

    #print(frame_rate)
    #print(animo.filename + ': ' + str(curr_idx//frame_rate))
    animo.sprite.texture = animo.sprite.textures[curr_idx//frame_rate]
    animo.currTexIdx = curr_idx


def get_direction(x1, y1, x2, y2):
    """
    Special helper function for class PathManager - gets direction between 2 points
    """

    dx = x2 - x1
    dy = y2 - y1
    if dx > 0:
        return 'right'
    elif dx < 0:
        return 'left'
    elif dy > 0:
        return 'up'
    elif dy < 0:
        return 'down'
    else:
        return None


def inbound(animo, x, y):
    """
    For interactive animo category, checks if mouse pointer is within sprite bounds
    """

    sprite = animo.sprite
    left = sprite.left
    right = sprite.left + sprite.width
    bottom = sprite.bottom
    top = sprite.bottom + sprite.height

    if (x >= left) and (x <= right) and (y >= bottom) and (y <= top):
        return True
    else:
        return False


def traverse_sub_dir(folder, path, name, path_list, name_list):
    """
    Recursively loops through a folder to get list of name and paths of all the sub directories
    """

    # Gets the sub directories of a directory (folder names)
    sub_dir = [x for x in os.listdir(path) if os.path.isdir(os.path.join(path, x))]

    if not sub_dir:
        # We have reached deepest sub directory
        path_list.append(path)
        name_list.append(name)
        return path_list, name_list

    for sd in sub_dir:
        path2 = path + "/" + sd
        name2 = folder + "_" + sd
        path_list, name_list = traverse_sub_dir(sd, path2, name2, path_list, name_list)

    return path_list, name_list
