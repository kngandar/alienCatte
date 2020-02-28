from random import *
from animation import *
import datetime

FONT_PATH = r'ARCADEPI'

# Functions


def roll_chance(p_thresh):
    """
    True if within probability, False if outside
    A potentially biased flip-the-coin
    """

    p = round(random(),2)
    if p <= p_thresh:
        return True
    else:
        return False


def hourly_rand_actions():
    """
    Gets random number of actions to every hour,
    Also returns the minutes of when actions happen
    """

    loop = randint(0, 5)
    minutes = []
    temp = 0

    for i in range(0, loop):
        temp += randint(0, 15)
        if temp > 60:
            temp = temp % 60
        minutes.append(temp)

    minutes = sorted(minutes)
    return minutes


def custom_texture_loading(animo, key, order):
    # Rewrites the order of animation for a texture set
    tex_src = animo.dictTexSet[key]
    tex_tar = []
    for x in order:
        tex_tar.append(tex_src[x-1])
    animo.dictTexSet[key] = tex_tar

    if key is '':
        animo.texLength = len(tex_tar)


class ButtonManager:
    """
    Checks every cycle if any button was clicked
    Returns functions if clicked
    """
    def __init__(self, stats):
        # Calls events for corresponding buttons
        self.button_list_now = {}
        self.button_list_ME = {}
        self.event_list = {}
        self.pressed_button = None
        self.stats = stats
        self.out_of_mp = False

    def register(self, name, button, cb):
        # Add button - event into manager
        key = button.filename
        if button.ME is True:
            self.button_list_ME[key] = button
        else:
            self.button_list_now[key] = button
        self.event_list[key] = cb

    def handle(self):
        rem_mp = self.stats.mp - 5

        # Handling of button disabling + re-enabling due to MP
        if not self.pressed_button and self.stats.mp > 0 and rem_mp == 0:
            # SPECIAL CASE: Re-enabling of buttons upon regeneration
            for x in self.button_list_ME.keys():
                self.out_of_mp = False
                self.button_list_ME[x].disable = False
                change_tex_set(self.button_list_ME[x], 'idle')

        elif self.stats.mp >= 0 and rem_mp < 0:
            # Disable if we outta MP,
            for x in self.button_list_ME.keys():
                self.out_of_mp = True
                self.button_list_ME[x].disable = True
                change_tex_set(self.button_list_ME[x], 'disable')

        # If there is sufficient MP, then only do action
        if rem_mp >= 0:
            # Handling non-mutually exclusive buttons; just run event
            # Not actually used rn
            if self.button_list_now:
                for x in self.button_list_now.keys():
                    if self.button_list_now[x].isClicked is True:
                        self.event_list[x]()

            # Handling mutually exclusive buttons
            if self.button_list_ME:
                for x in self.button_list_ME.keys():
                    # Only one button in button list can be pressed
                    if self.pressed_button is None:

                        if self.button_list_ME[x].isClicked is True:
                            # If clicked, return callback function
                            self.button_list_ME[x].isClicked = False
                            self.button_list_ME[x].eventRunning = True
                            self.pressed_button = x

                    # Disable all other buttons if pressed button is found
                    else:
                        self.button_list_ME[x].disable = True
                        change_tex_set(self.button_list_ME[x], 'disable')

                # Returns None is no button was pressed, otherwise return callback function
                if self.pressed_button is None:
                    return
                else:
                    return self.event_list[self.pressed_button]

    def event_done(self):
        # Update that event for pressed button is done running
        key = self.pressed_button
        self.button_list_ME[key].eventRunning = False
        self.pressed_button = None

        # Re-enable all buttons in list
        for x in self.button_list_ME.keys():
            self.button_list_ME[x].disable = False

            change_tex_set(self.button_list_ME[x], 'idle')

        print('Re-enabled buttons')


class SyncBro:
    """
    In charge of syncing up when multiple sprites should run
    Usually triggered by a button click

    For static animos only
    """
    def __init__(self, ani_list, key_list, loop_list, cue_list, ani_layer, frame_rate):
        self.animo_list = ani_list
        self.key_list = key_list
        self.cue_idx_list = cue_list
        self.loop_list = loop_list

        self.ani_layer = ani_layer
        self.frame_rate = frame_rate

        self.cycles = 0
        self.tex_idx = 0
        self.tex_idx_update = True

        self.max_tex_idx = 0
        self.initialize = True

    def edit_key(self, key, filename):
        # Changes the texture set to load for a specified animo in syncbro
        for x in range(0, len(self.animo_list)):
            if self.animo_list[x].filename == filename:
                self.key_list[x] = key
                return

    def execute(self):
        if self.initialize:
            self.initialize = False
            # Update the texture in animo with the proper key
            max_len = []
            for idx in range(0, len(self.animo_list)):
                animo = self.animo_list[idx]
                key = self.key_list[idx]
                if key is not None:
                    change_tex_set(animo, key)

                animo.frameRate = self.frame_rate
                animo.loops = self.loop_list[idx]

                max_len.append(animo.texLength)

            self.max_tex_idx = max(max_len)

        animation = self.ani_layer

        if self.tex_idx_update is True:
            self.tex_idx_update = False

            for idx in range(0, len(self.animo_list)):
                # If there is tex_idx count changed,

                    # Check if it's cue for animo to be loaded up
                    if self.cue_idx_list[idx] == self.tex_idx:
                        animation.load(self.animo_list[idx])

        self.cycles += 1
        x = self.cycles // self.frame_rate

        if x >= self.max_tex_idx:
            # If done, reset values and return True for ButtonManager
            self.cycles = 0
            self.tex_idx = 0
            self.tex_idx_update = True
            self.initialize = True
            return True

        if x is not self.tex_idx:
            self.tex_idx_update = True
            self.tex_idx = x

        return False


class NaviBuddy:
    """
    Handles toggling the different buttons
    """
    def __init__(self, butt_list, left, right, ani_layer):
        self.butt_list = butt_list
        self.left = left
        self.right = right
        self.animation = ani_layer
        self.curr_idx = 0
        self.butt_len = len(self.butt_list)
        self.direction = None

    def handle(self):
        if self.left.isClicked or self.right.isClicked:
            # Remove previous button
            prev_key = self.butt_list[self.curr_idx].filename
            self.animation.interactiveList.remove(prev_key)

            if self.right.isClicked:
                self.right.isClicked = False
                idx = (self.curr_idx + 1) % self.butt_len
            else:
                self.left.isClicked = False
                idx = (self.curr_idx - 1)
                if idx < 0:
                    idx += self.butt_len

            # Change button icon displayed
            butt = self.butt_list[idx]
            if butt.disable:
                change_tex_set(butt, 'disable')
            self.animation.load(butt)
            self.curr_idx = idx


class StatsPal:
    """
    Handles stats info of user: Level, XP, MP
    """
    def __init__(self):
        self.level = 0
        self.xp = 0
        self.mp = 0
        self.last_opened = None

        self.xp_thresh = 0
        self.mp_thresh = 0
        self.minute_update = None
        self.delta_min = 1

        self.load()
        self.get_thresh()

        # If new day, fully restored MP
        now = datetime.datetime.now()
        curr_day = int(str(now.year) + str(now.month) + str(now.day))
        if self.last_opened != curr_day:
            self.mp = self.mp_thresh

        if self.mp < self.mp_thresh and (self.mp % 5) == 0:
            now = datetime.datetime.now()
            self.minute_update = (now.minute + self.delta_min) % 60
        elif self.mp == self.mp_thresh:
            print("Full MP, do nothing")
        else:
            print("Oi, that's illegal")
            self.mp = 0

    def get_thresh(self):
        if self.level > 10:
            self.xp_thresh = 5000
        else:
            self.xp_thresh = self.level*500

        if self.level > 16:
            self.mp_thresh = 125
        else:
            self.mp_thresh = 25 + (self.level-1)*5

    def action(self):
        # An action is done, so reward xp, and reduce MP
        self.mp -= 5
        self.xp += 100

        if self.xp >= self.xp_thresh:
            self.level += 1
            self.xp = 0
            self.mp += 5
            self.get_thresh()

        now = datetime.datetime.now()
        self.minute_update = now.minute + self.delta_min

        # Does auto-save,
        self.last_opened = str(now.year) + str(now.month) + str(now.day)
        self.save()

    def update(self):
        # For regenerating MP,
        # Regenerates 5 energy after 5 minutes,
        if self.minute_update:
            now = datetime.datetime.now()
            if now.minute == self.minute_update:
                self.mp += 5
                self.minute_update = (self.minute_update + self.delta_min) % 60
                if self.mp >= self.mp_thresh:
                    self.mp = self.mp_thresh
                    self.minute_update = None

                # Does auto-save,
                self.last_opened = str(now.year) + str(now.month) + str(now.day)
                self.save()

    def draw(self):
        arcade.draw_text("Level: " + str(self.level), 130, 435, arcade.color.BLACK, 13, font_name=FONT_PATH)
        arcade.draw_text("XP: " + str(self.xp) + "/ " + str(self.xp_thresh), 130, 415, arcade.color.BLACK, 13, font_name=FONT_PATH)
        arcade.draw_text("MP: " + str(self.mp) + "/ " + str(self.mp_thresh), 130, 395, arcade.color.BLACK, 13, font_name=FONT_PATH)

    def delete(self):
        try:
            f = open("alien.catte", "r+")
            f.seek(0)
            f.truncate()
            f.close()
        except IOError:
            print("File not accessible")

    def load(self):
        try:
            f = open("alien.catte", "r")
            lines = f.readlines()

            self.level = int(lines[0])
            self.xp = int(lines[1])
            self.mp = int(lines[2])
            self.last_opened = int(lines[3])

        except IOError:
            print("File not accessible")

    def save(self):
        self.delete()
        f = open("alien.catte", "w+")
        f.write(str(self.level) + '\n')
        f.write(str(self.xp) + '\n')
        f.write(str(self.mp) + '\n')
        f.write(str(self.last_opened) + '\n')
        f.close()


class BubbleFren:
    """
    Handles text bubble drawing
    """
    def __init__(self, tex_bub, animation):
        self.text = ''
        self.countdown = 0
        self.items = {'idle': []}

        self.text_duration = 19
        self.bubble = tex_bub
        self.bubble.loops = self.text_duration
        self.animation = animation

        self.sz = 11
        self.U = 0
        self.L = 0

        # Default text lines
        self.items['instructions'] = ['TODO: Take care of catte\n while it accompanies you \n\n'
                                      + 'Food/Drink: Costs 5 MP\n\n'
                                      + 'MP: Stamina, regenerates \nevery 5 minutes\n\n'
                                      + 'XP: To level up and get \nmore MP and more \nqualitea catte time']

        self.items['warning'] = ['No MP left to take \n\ncare of catte!\n'
                                 + 'Take a break!']

    def load(self, file, key):
        lines = []

        try:
            f = open(file, 'r')
            lines = f.readlines()
            f.close()
        except:
            print('Could not read ' + file)

        if key in self.items.keys():
            self.items[key] += lines
        else:
            self.items[key] = lines

    def execute(self, key):
        lines = self.items[key]

        if key == 'instructions':
            self.sz = 10
            self.L = 230
            self.U = 350
            self.text_duration = 50
            self.bubble.loops = 25

        elif key == 'warning':
            self.sz = 15
            self.L = 230
            self.U = 330
            self.text_duration = 13
            self.bubble.loops = 13

        elif key == 'greet':
            self.sz = 12
            self.L = 220
            self.U = 300
            self.text_duration = 10
            self.bubble.loops = 10

        else:
            self.sz = 12
            self.L = 215
            self.U = 300
            self.text_duration = 13
            self.bubble.loops = 13

        if lines is not None and len(lines) > 0:
            self.text = lines[randint(0, len(lines)-1)]
            self.countdown = self.bubble.frameRate*self.text_duration

    def update(self):
        if self.countdown > 0:
            self.countdown -= 1

    def draw(self):
        if self.countdown > 0:
            self.bubble.sprite.draw()
            arcade.draw_text(self.text, self.L, self.U, arcade.color.BLACK, self.sz,
                             anchor_x="left", anchor_y="top", font_name=FONT_PATH)


class AlienCatteLogic:
    """
    Handles actions for alien catte
    """
    def __init__(self, animo, button_man, stats_pal, text_bub, ani_layer):
        self.animo = animo
        self.off_duty = True
        self.change_shift = True
        self.animation = ani_layer
        self.func = None

        # Holds ButtonManager that acts a communication medium between click events and callbacks
        self.button_man = button_man

        self.stats = stats_pal

        self.text_bub = text_bub

        change_tex_set(self.animo, 'idle_right')
        self.animo.loops = -1
        self.animo.frameRate = FRAME_RATE
        self.change_shift = False
        self.animation.load(self.animo)

        now = datetime.datetime.now()
        self.chat_interval = 15
        self.chat_time = (now.minute + self.chat_interval) % 60

        if self.stats.xp == 0 and self.stats.level == 1:
            # If new game, show instructions
            self.text_bub.execute('instructions')
        else:
            # Greet when first open game
            self.text_bub.execute('greet')

    def handle(self):
        """
        Handles things every cycle
        """

        # Say smth random every 15 minutes
        now = datetime.datetime.now()
        if self.chat_time == now.minute:
            self.text_bub.execute("random")
            self.chat_time = (now.minute + self.chat_interval) % 60

        # Checks if any button triggered
        cb = self.button_man.handle()

        # Check if any event needs to be executed
        if cb is not None and self.func is None:
            print('Event start')

            self.stats.action()

            self.off_duty = False
            self.change_shift = True
            self.func = cb

            # "Hush, I know this code isn't elegante, but I was pressed for time" - Catte dev
            if self.button_man.out_of_mp:
                self.text_bub.execute('warning')
            elif self.button_man.pressed_button[0:4] == 'food':
                self.text_bub.execute('food')
            elif self.button_man.pressed_button[0:5] == 'drink':
                self.text_bub.execute('drink')

        # If off duty, then pentacat just run idle animation
        if self.off_duty and self.change_shift:
            print('Off duty')

            # Remove previous animation before loading new animation
            ani_layer = self.animation
            for i in range(0, len(ani_layer.staticList.animoList)):
                if ani_layer.staticList.animoList[i].filename == 'pentacat':
                    ani_layer.staticList.remove(i)
                    break

            change_tex_set(self.animo, 'idle_right')
            self.animo.loops = -1
            self.animo.frameRate = FRAME_RATE
            self.change_shift = False
            self.animation.load(self.animo)

        # If on duty, execute
        elif not self.off_duty:
            if self.change_shift:
                self.change_shift = False

                print('Removed idle')

                # Remove previous animation before loading new animation
                ani_layer = self.animation
                for i in range(0, len(ani_layer.staticList.animoList)):
                    if ani_layer.staticList.animoList[i].filename == 'pentacat':
                        ani_layer.staticList.remove(i)
                        break

            #print('Event running')
            if self.func():
                print('Event done')
                self.button_man.event_done()
                self.func = None
                self.off_duty = True
                self.change_shift = True


class StaticAnimoSupervisor:
    """
    In charge of tracking when to switch up sequence of static animo textures
    This is specifically to allow running of multiple finite static animos

    THIS MIGHT NOT BE NECESSARY ???
    """
    def __init__(self, animo):
        self.frame_end = 0
        self.animo = animo
        self.idx = 0
        self.key_arr = None
        self.loops_arr = None
        self.frame_arr = None
        self.on_duty = False     # For when it's looping a sequence of animation (???)
        self.change_shift = True

    def add(self, key, loops, frame_rate):
        self.key_arr = key
        self.loops_arr = loops
        self.frame_arr = frame_rate
        self.on_duty = True

    def handle(self, frame, **kwargs):
        # If there is a set of static animation to run, then it is on duty
        if self.on_duty:

            # If it was previously off duty, need to remove the infinitely bouncing catte
            if self.change_shift:
                ani_layer = kwargs['aniLayer']
                for i in range(0, len(ani_layer.staticList.animoList)):
                    if ani_layer.staticList.animoList[i].filename == 'pentacat':
                        ani_layer.staticList.remove(i)
                        continue

            # Time to load next texture set
            if self.frame_end == frame:
                if self.idx >= len(self.key_arr):
                    self.on_duty = False
                    self.change_shift = True
                    return "DONE"

                self.calculate(frame)

                # Load details of next texture set
                i = self.idx
                change_tex_set(self.animo, self.key_arr[i])
                self.animo.loops = self.loops_arr[i]
                self.animo.frameRate = self.frame_arr[i]

                self.idx += 1
                return self.animo

            # Just letting static list play out the current texture set
            else:
                return

        # Otherwise, run the idle bouncing animation
        elif not self.on_duty and self.change_shift:
            change_tex_set(self.animo, 'idle_right')
            self.animo.loops = -1
            self.animo.frameRate = FRAME_RATE
            self.change_shift = False
            return self.animo

    def calculate(self, frame):
        # Calculate when to switch up the texture set
        i = self.idx
        key = self.key_arr[i]
        loop = self.loops_arr[i]
        fr_rate = self.frame_arr[i]

        tex_set_len = len(self.animo.dictTexSet[key])
        duration = fr_rate * tex_set_len * loop

        self.frame_end = frame + duration


'''
# CODEYARD
# --------
class TexSetSupervisor:
    """
    In charge of tracking when to switch up sequence of static animo textures
    This is specifically to allow running of multiple finite static animos
    """
    def __init__(self, animo, sequence):
        self.frame_st = 0
        self.frame_end = -1
        self.animo = animo
        self.key_seq = sequence     # An array of [dict key, loop]
        self.key_idx = 0
        self.idx_changed = True

    def handle(self, frame):
        if self.frame_end == frame+1:
            self.frame_st = self.frame_end
            self.key_idx += 1
            self.idx_changed = True

        if self.idx_changed:
            # If key_idx last index of key_seq, it is done
            if self.key_idx == len(self.key_seq):
                return 'Done'

            self.idx_changed = False
            self.calculate(frame)

            # Load the next texture set, and how number of times to loop
            i = self.key_idx
            change_tex_set(self.animo, self.key_seq[i][0])
            self.animo.loops = self.key_seq[i][1]
            return self.animo

        else:
            return

    def calculate(self, frame):
        # Calculate when to switch up the texture set
        i = self.key_idx
        key = self.key_seq[i][0]
        loop = self.key_seq[i][1]

        fr_rate = self.animo.frameRate
        tex_set_len = len(self.animo.dictTexSet[key])
        duration = fr_rate * tex_set_len * loop

        self.frame_st = frame
        self.frame_end = self.frame_st + duration

'''






