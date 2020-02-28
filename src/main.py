from pentacatLogic import *

# Constants
WIDTH = 500
HEIGHT = 500
SPRITE_SCALING = 1
BUTTON_SCALING = 0.5
ICON_SCALING = 0.70
BG_SCALING = 0.75
TEXT_SCALING = 1


# ttg: INTRO VIEW
class IntroView(arcade.View):
    def on_show(self):
        arcade.set_background_color(arcade.color.BABY_BLUE)

    def on_draw(self):
        arcade.start_render()
        arcade.draw_text("a \nbeep \nbeep \n\nmeow \nproduction", WIDTH/2, HEIGHT/2,
                         arcade.color.BLACK, font_size=25, anchor_x="center", font_name=FONT_PATH)
        arcade.draw_text(">>>", WIDTH-50, 30,
                         arcade.color.BLACK, font_size=15, anchor_x="center", font_name=FONT_PATH)

    def on_mouse_press(self, x, y, button, modifiers):
        prologue_view = Prologue()
        self.window.show_view(prologue_view)


# ttg: PROLOGUE VIEW
class Prologue(arcade.View):
    def __init__(self):
        super().__init__()
        self.background_list = ['images/story/bg_1.png',
                                'images/story/bg_2.png',
                                'images/story/bg_3.png']
        self.idx = 0

    def on_show(self):
        arcade.set_background_color(arcade.color.BLUE_SAPPHIRE)

    def on_draw(self):
        arcade.start_render()

        # Draws background
        arcade.draw_texture_rectangle(WIDTH // 2, HEIGHT // 2,
                                      WIDTH, HEIGHT, arcade.load_texture(self.background_list[self.idx]))
        arcade.draw_text(">>>", WIDTH-50, 30,
                         arcade.color.WHITE, font_size=15, anchor_x="center", font_name=FONT_PATH)

    def on_mouse_press(self, x, y, button, modifiers):
        if self.idx < len(self.background_list)-1:
            self.idx += 1

        else:
            message = Message()
            self.window.show_view(message)


# ttg: MESSAGE
class Message(arcade.View):
    p_text = list()
    p_text.append("CONGRATULATIONS!\n\n\n\n")
    p_text.append("You're one of the few lucky people \n\n to receive PENTACLAW's gift!")
    p_text.append("\n\n\nAn ALIEN CATTE!")
    p_text.append("\n\n\nA friend to keep you company through")
    p_text.append("\n\n\nThicc and Thin,")
    p_text.append("\n\n\nHotte and Colde,")
    p_text.append("\n\n\nDry and Dank.")

    j = 0
    list_length = len(p_text)

    message = p_text[j]

    def on_show(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        arcade.start_render()

        i = 0
        while i < self.j:
            self.message = self.p_text[i]
            arcade.draw_text(self.message, WIDTH / 2, HEIGHT * 3.75 / 5 - i * 28,
                             arcade.color.WHITE, font_size=15, anchor_x="center", anchor_y="top", font_name=FONT_PATH)
            i += 1

        arcade.draw_text(">>>", WIDTH - 50, 30,
                         arcade.color.WHITE, font_size=10, anchor_x="center", font_name=FONT_PATH)

    def on_mouse_press(self, x, y, button, modifiers):
        if self.j < self.list_length:
            self.on_draw()
            self.j += 1
        else:
            message2 = Message2()
            self.window.show_view(message2)


# ttg: MESSAGE 2
class Message2(arcade.View):
    p_text = list()
    p_text.append("...Btw,")
    p_text.append("The beam shot with a bit more..")
    p_text.append("power than we had expected.")
    p_text.append("We apologize if the impact might cause")
    p_text.append("a side effect on alien catte's memory")
    p_text.append("Shouldn't be anything major, though.")
    p_text.append("Its data on your profile...")
    p_text.append("might've been a liiittle corrupted.")

    j = 0
    list_length = len(p_text)

    message = p_text[j]

    def on_show(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        arcade.start_render()

        i = 0
        while i < self.j:
            self.message = self.p_text[i]
            arcade.draw_text(self.message, WIDTH / 2, HEIGHT * 3.55 / 5 - i * 28,
                             arcade.color.WHITE, font_size=15, anchor_x="center", font_name=FONT_PATH)
            i += 1

        arcade.draw_text(">>>", WIDTH - 50, 30,
                         arcade.color.WHITE, font_size=10, anchor_x="center", font_name=FONT_PATH)

    def on_mouse_press(self, x, y, button, modifiers):
        if self.j < self.list_length:
            self.on_draw()
            self.j += 1
        else:
            game_view = GameView()
            game_view.setup()
            self.window.show_view(game_view)


# ttg: GAME VIEW
class GameView(arcade.View):
    def __init__(self):
        super().__init__()

        self.background = None
        self.animation = None
        self.alien_catte = None
        self.stats = None
        self.food_navi = None
        self.drink_navi = None

        self.talk_msg = ""
        self.text_bub = None
        self.talk_trigger = True

    def setup(self):
        # Background texture
        self.background = arcade.load_texture('images/background.png')

        # Animation manager
        self.animation = AnimationLayer()

        # Stats pal
        self.stats = StatsPal()

        # Button manager + event list
        butt_man = ButtonManager(self.stats)

        # [ ALIEN CATTE ]
        # Make sprite and set animation sequence
        catte = Animo(STATIC, 'pentacat', SPRITE_SCALING, 180, 60, loops=-1, priority=1)
        # Modify the texture set to fit desired animation sequence
        key_order = {
            'smile': [1, 2, 3, 4, 5, 6, 7, 6, 7, 6, 7, 6, 5, 4, 3, 2, 1],
            'eat': [1, 2, 3, 4, 5, 6, 5, 6, 5, 6, 5, 4, 3, 2, 1],
            'drink': [1, 2, 3, 4, 3, 4, 3, 4, 3, 2, 1]
        }
        for key in key_order.keys():
            custom_texture_loading(catte, key, key_order[key])

        # [ PROFILE PICTURE ]
        icon = Animo(STATIC, 'icons', ICON_SCALING, 20, 390, loops=-1)
        self.animation.load(icon)

        # [ TEXT BUBBLE ]
        text_bub = Animo(STATIC, 'text_bubble', 1, 200, 200, loops=1)
        self.text_bub = BubbleFren(text_bub, self.animation)
        self.text_bub.load('text/greet.txt', 'greet')
        self.text_bub.load('text/food.txt', 'food')
        self.text_bub.load('text/drink.txt', 'drink')
        self.text_bub.load('text/random.txt', 'random')

        # [ EAT ]
        # Animo and texture set initialization
        blubabes = Animo(STATIC, 'food/blubabes', SPRITE_SCALING, 200, 60, loops=1, priority=2)
        frice = Animo(STATIC, 'food/frice', SPRITE_SCALING, 200, 60, loops=1, priority=2)
        salmon = Animo(STATIC, 'food/salmon', SPRITE_SCALING, 200, 60, loops=1, priority=2)
        spinach = Animo(STATIC, 'food/spinach', SPRITE_SCALING, 200, 60, loops=1, priority=2)
        food_dict = {'blubabes': blubabes,
                     'frice': frice,
                     'salmon': salmon,
                     'spinach': spinach}

        for x in food_dict.keys():
            custom_texture_loading(food_dict[x], '', [1, 1, 1, 1, 1, 1, 1, 2, 2, 3, 3])

        eat_BB = [catte, blubabes]
        eat_FR = [catte, frice]
        eat_SL = [catte, salmon]
        eat_SP = [catte, spinach]

        # Sync animation object
        cue_list = [0, 0]
        loop_list = [-1, 1]
        key_list = ['eat', '']
        BB_sync = SyncBro(eat_BB, key_list, loop_list, cue_list, self.animation, 20)
        FR_sync = SyncBro(eat_FR, key_list, loop_list, cue_list, self.animation, 20)
        SL_sync = SyncBro(eat_SL, key_list, loop_list, cue_list, self.animation, 20)
        SP_sync = SyncBro(eat_SP, key_list, loop_list, cue_list, self.animation, 20)

        # Food button
        f_butt_x = 60
        f_butt_y = 140
        blubabes = Animo(BUTTON, 'food_butt/blubabes', BUTTON_SCALING, f_butt_x, f_butt_y, syncBro=BB_sync, ME=True)
        frice = Animo(BUTTON, 'food_butt/frice', BUTTON_SCALING, f_butt_x, f_butt_y, syncBro=FR_sync, ME=True)
        salmon = Animo(BUTTON, 'food_butt/salmon', BUTTON_SCALING, f_butt_x, f_butt_y, syncBro=SL_sync, ME=True)
        spinach = Animo(BUTTON, 'food_butt/spinach', BUTTON_SCALING, f_butt_x, f_butt_y, syncBro=SP_sync, ME=True)
        food_butt = [blubabes, frice, salmon, spinach]

        butt_man.register('blubabes', blubabes, BB_sync.execute)
        butt_man.register('frice', frice, FR_sync.execute)
        butt_man.register('salmon', salmon, SL_sync.execute)
        butt_man.register('spinach', spinach, SP_sync.execute)

        # Navigation button
        eat_navi_L = Animo(BUTTON, 'nav_butt/left', BUTTON_SCALING, f_butt_x-20, f_butt_y)
        eat_navi_R = Animo(BUTTON, 'nav_butt/right', BUTTON_SCALING, f_butt_x+64, f_butt_y)
        self.food_navi = NaviBuddy(food_butt, eat_navi_L, eat_navi_R, self.animation)

        # [ DRINK ]
        # Animo and texture set initialization
        boba = Animo(STATIC, 'drink/boba', SPRITE_SCALING, 190, 60, loops=1, priority=2)
        milk = Animo(STATIC, 'drink/milk', SPRITE_SCALING, 190, 60, loops=1, priority=2)
        mint_tea = Animo(STATIC, 'drink/mint_tea', SPRITE_SCALING, 190, 60, loops=1, priority=2)
        woter = Animo(STATIC, 'drink/woter', SPRITE_SCALING, 190, 60, loops=1, priority=2)
        drink_dict = {'boba': boba,
                      'milk': milk,
                      'mint_tea': mint_tea,
                      'woter': woter}

        for x in drink_dict.keys():
            custom_texture_loading(drink_dict[x], '', [1, 1, 1, 1, 2, 2, 3, 3])

        boba_s = Animo(STATIC, 'straw/boba', SPRITE_SCALING, 190, 60, loops=1, priority=2)
        milk_s = Animo(STATIC, 'straw/milk', SPRITE_SCALING, 190, 60, loops=1, priority=2)
        mint_tea_s = Animo(STATIC, 'straw/mint_tea', SPRITE_SCALING, 190, 60, loops=1, priority=2)
        woter_s = Animo(STATIC, 'straw/woter', SPRITE_SCALING, 190, 60, loops=1, priority=2)
        straw_dict = {'boba_s': boba_s,
                      'milk_s': milk_s,
                      'mint_tea_s': mint_tea_s,
                      'woter_s': woter_s}

        for x in straw_dict.keys():
            custom_texture_loading(straw_dict[x], '', [2, 2, 2, 1, 2, 1, 2, 1])

        drink_BB = [catte, boba, boba_s]
        drink_ML = [catte, milk, milk_s]
        drink_MT = [catte, mint_tea, mint_tea_s]
        drink_WT = [catte, woter, woter_s]

        # Sync animation object
        cue_list = [0, 0, 0]
        loop_list = [-1, 1, 1]
        key_list = ['drink', '', '']
        BB_sync = SyncBro(drink_BB, key_list, loop_list, cue_list, self.animation, 20)
        ML_sync = SyncBro(drink_ML, key_list, loop_list, cue_list, self.animation, 20)
        MT_sync = SyncBro(drink_MT, key_list, loop_list, cue_list, self.animation, 20)
        WT_sync = SyncBro(drink_WT, key_list, loop_list, cue_list, self.animation, 20)

        # Drink button
        d_butt_x = 60
        d_butt_y = 260
        boba = Animo(BUTTON, 'drink_butt/boba', BUTTON_SCALING, d_butt_x, d_butt_y, syncBro=BB_sync, ME=True)
        milk = Animo(BUTTON, 'drink_butt/milk', BUTTON_SCALING, d_butt_x, d_butt_y, syncBro=ML_sync, ME=True)
        mint_tea = Animo(BUTTON, 'drink_butt/mint_tea', BUTTON_SCALING, d_butt_x, d_butt_y, syncBro=MT_sync, ME=True)
        woter = Animo(BUTTON, 'drink_butt/woter', BUTTON_SCALING, d_butt_x, d_butt_y, syncBro=WT_sync, ME=True)
        drink_butt = [boba, milk, mint_tea, woter]

        butt_man.register('boba', boba, BB_sync.execute)
        butt_man.register('milk', milk, ML_sync.execute)
        butt_man.register('mint_tea', mint_tea, MT_sync.execute)
        butt_man.register('woter', woter, WT_sync.execute)

        # Navigation button
        drink_navi_L = Animo(BUTTON, 'nav_butt/left', BUTTON_SCALING, d_butt_x-20, d_butt_y)
        drink_navi_R = Animo(BUTTON, 'nav_butt/right', BUTTON_SCALING, d_butt_x+64, d_butt_y)
        self.drink_navi = NaviBuddy(drink_butt, drink_navi_L, drink_navi_R, self.animation)

        self.animation.load(eat_navi_L)
        self.animation.load(eat_navi_R)
        self.animation.load(blubabes)

        self.animation.load(drink_navi_L)
        self.animation.load(drink_navi_R)
        self.animation.load(boba)

        self.alien_catte = AlienCatteLogic(catte, butt_man, self.stats, self.text_bub, self.animation)

    def on_draw(self):
        arcade.start_render()

        # Draws background
        arcade.draw_texture_rectangle(WIDTH // 2, HEIGHT // 2, WIDTH, HEIGHT, self.background)

        # Draws UI text
        arcade.draw_text("Gyerek", 130, 455, arcade.color.BLACK, 19, font_name=FONT_PATH)
        now = datetime.datetime.now().strftime("%I:%M%p")
        now_x = 300
        if now[0] == '0':
            now = now[1:]
            now_x = 330
        arcade.draw_text(now, now_x, 15, arcade.color.BLACK, 30, font_name=FONT_PATH)
        arcade.draw_text("DRINKS", 60, 330, arcade.color.BLACK, 13, font_name=FONT_PATH)
        arcade.draw_text("FOODS", 60, 210, arcade.color.BLACK, 13, font_name=FONT_PATH)

        self.stats.draw()

        self.text_bub.draw()

        self.animation.draw()

    def update(self, delta_time):
        self.animation.update()
        self.stats.update()
        self.text_bub.update()

        self.food_navi.handle()
        self.drink_navi.handle()
        self.alien_catte.handle()

    def on_mouse_motion(self, x, y, dx, dy):
        self.animation.interactiveList.hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        self.animation.interactiveList.click(x, y)


def main():
    window = arcade.Window(WIDTH, HEIGHT, "an absolute banger of a game")
    do_intro = True

    file = open("do_intro.txt", "r")
    first_time = file.readline()
    if first_time == '0':
        do_intro = False
    file.close()

    if do_intro:
        intro_view = IntroView()
        window.show_view(intro_view)
        file = open("do_intro.txt", "w")
        file.write('0')
        file.close()
    else:
        game_view = GameView()
        game_view.setup()
        window.show_view(game_view)
    arcade.run()


if __name__ == "__main__":
    main()
