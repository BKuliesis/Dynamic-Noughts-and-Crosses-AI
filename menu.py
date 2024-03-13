import sys
import database
import gui_utility
from constants import *


class Menu:
    def __init__(self, manager, title, options_array, options_pos_array):
        self.manager = manager
        self.title = MENU_TITLES[title]
        self.title_rect = self.title.get_rect(topleft=(0, 105))
        self.options_array = options_array
        self.number_of_options = len(self.options_array)
        self.options_buttons = []
        self.options_pos_array = options_pos_array

    def run(self):
        self.create_buttons()
        self.manager.screen.fill(COLOURS["background"])
        self.display_title()
        self.display_options_buttons()

    def create_buttons(self):
        self.options_buttons = []
        for option in range(self.number_of_options):
            self.options_buttons.append(
                gui_utility.Button(self.manager.screen, MENU_BUTTONS[self.options_array[option]],
                                   MENU_BUTTONS[self.options_array[option] + "_hovering"],
                                   self.options_pos_array[option]))

    def display_title(self):
        self.manager.screen.blit(self.title, self.title_rect)

    def display_options_buttons(self):
        for option in self.options_buttons:
            option.display_button()


class MainMenu(Menu):
    def __init__(self, manager):
        Menu.__init__(self, manager, "main_menu", ["play", "leaderboard", "settings", "exit"],
                      [(358, 293), (358, 414), (358, 535), (358, 656)])

    def run(self):
        while True:
            Menu.run(self)
            self.check_events()
            pygame.display.update()
            self.manager.clock.tick(FPS)

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.options_buttons[0].check_if_clicked():
                    self.manager.select_game_mode.run()
                elif self.options_buttons[1].check_if_clicked():
                    self.manager.leaderboard.run()
                elif self.options_buttons[2].check_if_clicked():
                    self.manager.settings_menu.run("main_menu")
                elif self.options_buttons[3].check_if_clicked():
                    pygame.quit()
                    sys.exit()


class SettingsMenu(Menu):
    def __init__(self, manager):
        Menu.__init__(self, manager, "settings", ["sound_on", "log_out", "back"],
                      [(358, 293), (358, 414), (358, 535)])

    def run(self, previous_page):
        while True:
            if self.manager.sound_enabled:
                self.options_array[0] = "sound_on"
            else:
                self.options_array[0] = "sound_off"
            Menu.run(self)
            self.check_events(previous_page)
            pygame.display.update()
            self.manager.clock.tick(FPS)

    def check_events(self, previous_page):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.options_buttons[0].check_if_clicked():
                    self.toggle_sound()
                elif self.options_buttons[1].check_if_clicked():
                    self.manager.login_screen.run()
                elif self.options_buttons[2].check_if_clicked():
                    if previous_page == "main_menu":
                        self.manager.main_menu.run()
                    elif previous_page == "options_menu":
                        self.manager.options_menu.run()

    def toggle_sound(self):
        database.connect_to_database()
        self.manager.sound_enabled = not self.manager.sound_enabled
        database.update_player_sound_enabled(self.manager.username, self.manager.sound_enabled)
        database.close_database()


class OptionsMenu(Menu):
    def __init__(self, manager):
        Menu.__init__(self, manager, "options", ["resume", "settings", "main_menu", "exit"],
                      [(358, 293), (358, 414), (358, 535), (358, 656)])

    def run(self):
        while True:
            Menu.run(self)
            self.check_events()
            pygame.display.update()
            self.manager.clock.tick(FPS)

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.options_buttons[0].check_if_clicked():
                    self.manager.noughts_and_crosses.run()
                elif self.options_buttons[1].check_if_clicked():
                    self.manager.settings_menu.run("options_menu")
                elif self.options_buttons[2].check_if_clicked():
                    self.manager.main_menu.run()
                elif self.options_buttons[3].check_if_clicked():
                    pygame.quit()
                    sys.exit()
