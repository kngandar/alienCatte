from subClasses import *


class AnimationLayer:
    """
    All animation management is handled here,
    In general , the layer is divided into 3 different sub-classes:
        1. Static
        2. Player
        3. Interactive

        (Refer to subClasses.py for more info on them)

    Order of file dependence:
    (Highest)   AnimationLayer: Just a wrapper, really
                    |
                    SubClasses: Actual management algorithm
                        |
                        BaseClasses: Building component for sub-classes ish
                            |
    (Lowest)                Functions: All the helper functions in one place
    """

    def __init__(self):
        self.staticList = None
        self.playerList = None
        self.interactiveList = None
        self.priorityList = []
        self.frame = 0

    def load(self, animo):
        if animo.group == STATIC:
            if self.staticList is None:
                self.staticList = StaticList()
            self.staticList.add(animo)

        elif animo.group == PLAYER:
            # Note: There can only be one player, so if you try to add another player type animo into a non-empty
            #       playerList then it will replace the old player animo
            if self.playerList is None:
                self.playerList = PlayerList()
            self.playerList.add(animo)

        else:
            if self.interactiveList is None:
                self.interactiveList = InteractiveList()
            self.interactiveList.add(animo)

        # Add unique priority values, and sort
        if animo.priority not in self.priorityList:
            self.priorityList.append(animo.priority)
            self.priorityList = sorted(self.priorityList)

    def draw(self):
        for i in self.priorityList:
            if self.staticList is not None:
                self.staticList.draw(i)

            if self.playerList is not None:
                self.playerList.draw(i)

            if self.interactiveList is not None:
                self.interactiveList.draw(i)

    def update(self):
        self.frame += 1

        for i in self.priorityList:
            if self.staticList is not None:
                self.staticList.update(i)

            if self.playerList is not None:
                self.playerList.update(i)

            if self.interactiveList is not None:
                self.interactiveList.update(i)

        if self.staticList is not None and self.staticList.removedAnimo is True:
            # If animo is popped off in static list,
            # Recheck what unique priority numbers are still being used
            temp = []

            if self.staticList is not None:
                for x in self.staticList.animoList:
                    if x.priority not in temp:
                        temp.append(x.priority)

            if self.playerList is not None:
                if self.playerList.player.priority not in temp:
                    temp.append(self.playerList.player.priority)

            if self.interactiveList is not None:
                for x in self.interactiveList.animoList:
                    if x.priority not in temp:
                        temp.append(x.priority)

            self.priorityList = temp
            self.priorityList = sorted(self.priorityList)
            self.staticList.removedAnimo = False
