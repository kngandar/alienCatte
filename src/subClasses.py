"""
Sub Classes: StaticList, PlayerList, InteractiveList
"""

from baseClasses import *


class StaticList:
    """
    Holds animos that cannot be interacted and either runs on a finite or infinite loop.
    It essentially works like a GIF.

    Suggested usage: Background objects, temporary message pop-ups, non-moving GIF
    Used helper functions: update_animation
    """

    def __init__(self):
        self.animoList = []
        self.listLength = 0
        self.removedAnimo = False

    def add(self, animo):
        print('Animo added ' + animo.filename)
        self.animoList.append(animo)
        self.listLength += 1

    def draw(self, priority):
        for animo in self.animoList:
            if animo.priority is priority:
                animo.sprite.draw()

    def update(self, priority):
        to_remove = []
        for idx in range(0, self.listLength):
            animo = self.animoList[idx]
            if animo.priority is priority:
                animo.sprite.update()

                update_animation(self.animoList[idx])
                if self.animoList[idx].loops == 0:
                    to_remove.append(idx)

        # Need to remove this backwards otherwise cannot pop the correct sprites after
        for idx in range(len(to_remove)-1, -1, -1):
            self.remove(to_remove[idx])

    def remove(self, idx):
        self.animoList.pop(idx)
        self.listLength -= 1
        self.removedAnimo = True


class PlayerList:
    """
    Holds an animo that are controlled by the keyboard.

    Suggested usage: Player 1
    Used functions: update_animation, walk, stop, change_tex_set
    """

    def __init__(self):
        self.player = None

        # These properties are required for better movement, taken from arcade website:
        # http://arcade.academy/examples/sprite_move_keyboard_better.html?highlight=on_key_release
        self.right_pressed = False
        self.left_pressed = False
        self.up_pressed = False
        self.down_pressed = False

    def add(self, animo):
        self.player = animo

    def draw(self, priority):
        if self.player.priority is priority:
            self.player.sprite.draw()

    def keyboard(self, key, on_press):
        # Sticky key problem prevention
        if on_press is True:
            if key == arcade.key.RIGHT:
                self.right_pressed = True
            elif key == arcade.key.LEFT:
                self.left_pressed = True
            elif key == arcade.key.UP:
                self.up_pressed = True
            elif key == arcade.key.DOWN:
                self.down_pressed = True

        else:
            if key == arcade.key.RIGHT:
                self.right_pressed = False
            elif key == arcade.key.LEFT:
                self.left_pressed = False
            elif key == arcade.key.UP:
                self.up_pressed = False
            elif key == arcade.key.DOWN:
                self.down_pressed = False

        # Send actual commands,
        if self.right_pressed and not self.left_pressed:
            face = 'right'
            walk(face, self.player)
        elif self.left_pressed and not self.right_pressed:
            face = 'left'
            walk(face, self.player)
        elif self.up_pressed and not self.down_pressed:
            face = 'up'
            walk(face, self.player)
        elif self.down_pressed and not self.up_pressed:
            face = 'down'
            walk(face, self.player)
        elif not self.right_pressed and\
                not self.left_pressed and\
                not self.up_pressed and\
                not self.down_pressed:
                    stop(self.player)

    def update(self, priority):
        if self.player.priority is priority:
            self.player.sprite.update()
            update_animation(self.player)


class InteractiveList:
    """
    Holds animos that can be interacted with a mouse.
    Four different sub-groups of interactive animos:
    1. Latch
        It functions like a toggle switch
        Suggested use: To show an item is equipped, a switch (lmao)

    2. Clickdrop
        It is basically drag and drop, but you click to pick up or drop instead
        Suggested use: Moving items/characters in game

    3. Autopath
        Makes sprite moves in the path determined from a text file
        It has a showAnimation property if it is turned off then sprite will just "teleport" to the end point of the path
        Suggested use: Moving NPCs probably

    4 Button
        It calls its corresponding callback function.
        This is basically the customizable animo type
        Suggested use: Whatever you want pal, it's free real estate

    Used functions: update_animation, walk, stop, change_tex_set, inbound, get_direction*
    """

    def __init__(self):
        self.animoList = []
        self.hoverIdx = -1
        self.clickDropIdx = -1
        self.listLength = 0

    def add(self, animo):
        self.animoList.append(animo)
        self.listLength += 1

    def remove(self, filename):
        for idx in range(0, len(self.animoList)):
            if self.animoList[idx].filename == filename:
                self.animoList.pop(idx)
                break
        self.listLength -= 1

    def draw(self, priority):
        for animo in self.animoList:
            if animo.priority is priority:
                animo.sprite.draw()

        # Note: The documentation for drawing by individual sprite vs. drawing by using SpriteList is somewhat sketchy
        # If something goes wrong with drawing, this section might be a potential cause of problem

    def update(self, priority):
        for animo in self.animoList:
            if animo.priority is priority:
                animo.sprite.update()

                # Load up the next texture to display
                if animo.group == AUTOPATH:
                    if animo.pathManager.isMoving is True:
                        animo.pathManager.run()

                update_animation(animo)

    def hover(self, x, y):
        if self.clickDropIdx >= 0:
            # Special Case: If sprite is click n drop type, and is clicked, then sprite just follows mouse pointer
            sprite = self.animoList[self.clickDropIdx].sprite
            sprite.center_x = x
            sprite.center_y = y

        else:
            if self.hoverIdx >= 0:
                # If previously highlighted sprite is no longer highlighted, reset the texture
                prev_animo = self.animoList[self.hoverIdx]
                if inbound(prev_animo, x, y) is False:
                    self.hoverIdx = -1
                    if prev_animo.group is LATCH:
                        if prev_animo.isLatched:
                            key = 'latch'
                        else:
                            key = 'unlatch'
                    elif prev_animo.group is AUTOPATH:
                        key = 'idle_' + prev_animo.default_face
                    elif prev_animo.group is BUTTON and prev_animo.disable is True:
                        key = 'disable'
                    else:
                        key = 'idle'
                    change_tex_set(prev_animo, key)

                else:
                    # Very special case: For handling if mouse cursor still within button even after event executed
                    if prev_animo.group is BUTTON and prev_animo.disable is False:
                        key = 'hover'
                        change_tex_set(prev_animo, key)

            else:
                # If nothing was highlighted, check through all sprites if pointer is within any of its bounds
                # Exit loop if there is a match (pointer can hover only on one sprite)
                for idx in range(0, self.listLength):
                    animo = self.animoList[idx]
                    if inbound(animo, x, y) is True:
                        if animo.group is LATCH:
                            if animo.isLatched:
                                key = 'hover_latch'
                            else:
                                key = 'hover_unlatch'
                        elif animo.group is BUTTON and animo.disable is True:
                            key = 'disable'
                        else:
                            key = 'hover'

                        # ( Note: It is assumed AUTOPATH animo will only have 'hover' folder,
                        #         and not 'hover_right', etc.)

                        change_tex_set(animo, key)
                        self.hoverIdx = idx
                        print('>>> Hover idx: ' + str(idx))
                        continue

    def click(self, x, y):
        if self.hoverIdx >= 0:
            animo = self.animoList[self.hoverIdx]

            if animo.group == LATCH:
                animo.isLatched = 1 - animo.isLatched
                if animo.isLatched:
                    change_tex_set(animo, 'hover_latch')
                else:
                    key = 'hover_unlatch'
                    change_tex_set(animo, key)

            elif animo.group == CLICKDROP:
                if animo.isClicked is False:
                    animo.isClicked = True
                    self.clickDropIdx = self.hoverIdx
                else:
                    animo.isClicked = False
                    animo.sprite.center_x = x
                    animo.sprite.center_y = y
                    self.clickDropIdx = -1

            elif animo.group == AUTOPATH:
                if animo.showAnimation is True:
                    animo.pathManager.run()
                else:
                    animo.pathManager.no_animation()

            elif animo.group == BUTTON:
                # If animo is not disabled, then click will trigger event to button manager
                if animo.disable is False:
                    animo.isClicked = True
                    if animo.ME:
                        change_tex_set(animo, 'disable')
