import pygame

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 900
GRID_HEIGHT_AND_WIDTH = 675
GRID_RESOLUTION = (GRID_HEIGHT_AND_WIDTH, GRID_HEIGHT_AND_WIDTH)
GRID_POSITION = ((SCREEN_WIDTH / 2) - (GRID_HEIGHT_AND_WIDTH / 2), (SCREEN_HEIGHT / 2) - (GRID_HEIGHT_AND_WIDTH / 2))
BACK_ARROW_HEIGHT_AND_WIDTH = 65
BACK_ARROW_POSITION = (10, SCREEN_HEIGHT - BACK_ARROW_HEIGHT_AND_WIDTH - 8)
FPS = 60

COLOURS = {"background": (42, 86, 105), "nought_colour": (161, 33, 33), "cross_colour": (23, 142, 76),
           "white": (255, 255, 255), "black": (0, 0, 0), "light_blue": (123, 182, 207), "red": (252, 58, 58)}

MENU_BUTTONS = {"login": pygame.image.load('Images/Buttons/login.png'),
                "login_hovering": pygame.image.load('Images/Buttons/login_hovering.png'),
                "create_account": pygame.image.load('Images/Buttons/create_account.png'),
                "create_account_hovering": pygame.image.load('Images/Buttons/create_account_hovering.png'),
                "play": pygame.image.load('Images/Buttons/play.png'),
                "play_hovering": pygame.image.load('Images/Buttons/play_hovering.png'),
                "leaderboard": pygame.image.load('Images/Buttons/leaderboard.png'),
                "leaderboard_hovering": pygame.image.load('Images/Buttons/leaderboard_hovering.png'),
                "settings": pygame.image.load('Images/Buttons/settings.png'),
                "settings_hovering": pygame.image.load('Images/Buttons/settings_hovering.png'),
                "exit": pygame.image.load('Images/Buttons/exit.png'),
                "exit_hovering": pygame.image.load('Images/Buttons/exit_hovering.png'),
                "standard": pygame.image.load('Images/Buttons/standard.png'),
                "standard_hovering": pygame.image.load('Images/Buttons/standard_hovering.png'),
                "impossible_3x3": pygame.image.load('Images/Buttons/impossible_3x3.png'),
                "impossible_3x3_hovering": pygame.image.load('Images/Buttons/impossible_3x3_hovering.png'),
                "player_vs_player": pygame.image.load('Images/Buttons/player_vs_player.png'),
                "player_vs_player_hovering": pygame.image.load('Images/Buttons/player_vs_player_hovering.png'),
                "sound_on": pygame.image.load('Images/Buttons/sound_on.png'),
                "sound_on_hovering": pygame.image.load('Images/Buttons/sound_on_hovering.png'),
                "sound_off": pygame.image.load('Images/Buttons/sound_off.png'),
                "sound_off_hovering": pygame.image.load('Images/Buttons/sound_off_hovering.png'),
                "log_out": pygame.image.load('Images/Buttons/log_out.png'),
                "log_out_hovering": pygame.image.load('Images/Buttons/log_out_hovering.png'),
                "back": pygame.image.load('Images/Buttons/back.png'),
                "back_hovering": pygame.image.load('Images/Buttons/back_hovering.png'),
                "resume": pygame.image.load('Images/Buttons/resume.png'),
                "resume_hovering": pygame.image.load('Images/Buttons/resume_hovering.png'),
                "main_menu": pygame.image.load('Images/Buttons/main_menu.png'),
                "main_menu_hovering": pygame.image.load('Images/Buttons/main_menu_hovering.png'),
                "play_again": pygame.image.load('Images/Buttons/play_again.png'),
                "play_again_hovering": pygame.image.load('Images/Buttons/play_again_hovering.png'),
                "confirm": pygame.image.load('Images/Buttons/confirm.png'),
                "confirm_hovering": pygame.image.load('Images/Buttons/confirm_hovering.png')}

MENU_TITLES = {"login": pygame.image.load('Images/Titles/login.png'),
               "create_account": pygame.image.load('Images/Titles/create_account.png'),
               "main_menu": pygame.image.load('Images/Titles/main_menu.png'),
               "leaderboard": pygame.image.load('Images/Titles/leaderboard.png'),
               "settings": pygame.image.load('Images/Titles/settings.png'),
               "game_mode": pygame.image.load('Images/Titles/game_mode.png'),
               "options": pygame.image.load('Images/Titles/options.png'),
               "grid_options": pygame.image.load('Images/Titles/grid_options.png')}

TEXT_BOX = {"selected": pygame.image.load('Images/Textbox/selected.png'),
            "not_selected": pygame.image.load('Images/Textbox/not_selected.png'),
            "error": pygame.image.load('Images/Textbox/error.png'),
            "number_selected": pygame.image.load('Images/Textbox/number_selected.png'),
            "number_not_selected": pygame.image.load('Images/Textbox/number_not_selected.png'),
            "number_error": pygame.image.load('Images/Textbox/number_error.png')}

IMAGES = {"X": pygame.image.load('Images/cross.png'),
          "O": pygame.image.load('Images/nought.png'),
          "blank_square": pygame.image.load('Images/blank_square.png'),
          "options_icon": pygame.image.load('Images/options_icon.png'),
          "options_icon_hovering": pygame.image.load('Images/options_icon_hovering.png'),
          "edit_icon": pygame.image.load('Images/edit_icon.png'),
          "edit_icon_hovering": pygame.image.load('Images/edit_icon_hovering.png'),
          "background_black": pygame.image.load('Images/background_black.jpg'),
          "icon": pygame.image.load("Images/icon.png"),
          "leaderboard": pygame.image.load("Images/leaderboard.png"),
          "help_icon": pygame.image.load("Images/help_icon.png"),
          "help_icon_hovering": pygame.image.load("Images/help_icon_hovering.png")}

ARROWS = {"left_arrow": pygame.image.load('Images/Arrows/left_arrow.png'),
          "left_arrow_hovering": pygame.image.load('Images/Arrows/left_arrow_hovering.png'),
          "right_arrow": pygame.image.load('Images/Arrows/right_arrow.png'),
          "right_arrow_hovering": pygame.image.load('Images/Arrows/right_arrow_hovering.png')}

pygame.display.set_icon(IMAGES["icon"])

pygame.font.init()
FONTS = {"login_heading": pygame.font.SysFont("consolas", 30),
         "create_account_text": pygame.font.Font("Fonts/Inter-Light.ttf", 40),
         "leaderboard": pygame.font.Font("Fonts/Inter-Medium.ttf", 45),
         "leaderboard_you": pygame.font.Font("Fonts/Inter-Bold.ttf", 45),
         "score": pygame.font.Font("Fonts/lemonmilk.otf", 50),
         "game": pygame.font.Font("Fonts/lemonmilk.otf", 65),
         "result": pygame.font.Font("Fonts/lemonmilk.otf", 110),
         "game_over": pygame.font.Font("Fonts/lemonmilk.otf", 130),
         "game_over_screen": pygame.font.Font("Fonts/lemonmilk.otf", 70),
         "text_box": pygame.font.SysFont("consolas", 25),
         "error_message": pygame.font.Font("Fonts/Inter-Regular.ttf", 20),
         "grid_options": pygame.font.Font("Fonts/lemonmilk.otf", 36)}

pygame.mixer.init()
SOUNDS = {"win": pygame.mixer.Sound('Sounds/win.wav'),
          "draw": pygame.mixer.Sound('Sounds/draw.wav'),
          "game_over": pygame.mixer.Sound('Sounds/game_over.wav'),
          "placement_made": pygame.mixer.Sound('Sounds/placement_made.wav')}
