import database
import utility
import result as r
import gui_utility
import menu
import copy
import random
import time
import sys
from constants import *


class Manager:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Dynamic Noughts and Crosses AI")
        self.clock = pygame.time.Clock()
        self.username = None
        self.sound_enabled = True
        self.login_screen = Login(self)
        self.create_account_screen = CreateAccount(self)
        self.main_menu = menu.MainMenu(self)
        self.select_game_mode = SelectMode(self)
        self.noughts_and_crosses = None
        self.settings_menu = menu.SettingsMenu(self)
        self.leaderboard = LeaderBoard(self)
        self.options_menu = menu.OptionsMenu(self)
        self.grid_options_menu = GridOptionsMenu(self)
        self.login_screen.run()


class NoughtsAndCrosses:
    symbols = ["X", "O"]

    def __init__(self, manager, mode, grid_size, win_length):
        self.manager = manager
        self.game_mode = mode
        self.grid_size = grid_size
        self.win_length = win_length
        self.grid = GridLogic(self.grid_size, self.win_length)
        self.grid_graphics = GridGraphics(self.grid_size, self.manager.screen)
        self.turn = utility.random_one_or_zero()
        self.score = 0
        self.moves = utility.Stack()
        self.backwards_stack = None  # stack for going backwards in moves in review mode
        self.forward_stack = None  # stack for going forward in moves in review mode
        self.result = None
        self.win_or_draw_screen_active = False
        self.return_to_win_or_draw_screen = False
        self.return_to_game_over_screen = False
        self.ai = AI(self)
        self.win_or_draw = WinOrDraw(self)
        self.game_over = GameOver(self)
        self.impossible_3x3_result = Impossible3x3Result(self)
        self.player_vs_player_winner = PlayerVsPlayerWinner(self)
        self.options_button = None
        self.edit_button = None
        self.first_move = True
        self.review_mode = False
        self.review_active = False
        self.review_button = None
        self.arrow_buttons = [None, None]
        self.back_button = None

    def run(self):
        if not self.review_mode:
            while True:
                if not self.win_or_draw_screen_active:
                    self.display_current_game_state()
                    if self.game_mode == 0:
                        self.display_score()
                    self.grid_graphics.create_grid_buttons()
                    self.create_options_button()
                    self.options_button.display_button()
                    if self.game_mode == 2:
                        self.create_edit_button()
                        self.edit_button.display_button()
                    pygame.display.update()
                    if self.game_mode == 0 or self.game_mode == 1:
                        self.play_game()
                    elif self.game_mode == 2:
                        self.play_game_player_vs_player()
                    self.manager.clock.tick(FPS)
                else:
                    if self.game_mode == 0:
                        self.win_or_draw.run()
                    elif self.game_mode == 1:
                        self.impossible_3x3_result.run()
                    elif self.game_mode == 2:
                        self.player_vs_player_winner.run()
        else:
            self.run_review()

    def display_current_game_state(self):
        self.manager.screen.fill(COLOURS["background"])
        self.grid_graphics.display_grid_lines()
        self.grid_graphics.display_current_grid_state()
        self.display_turn()
        self.display_win_length()

    def check_events(self):
        position = [None, None]
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, row in enumerate(self.grid_graphics.get_grid()):
                    for j, grid_slot in enumerate(row):
                        if grid_slot.get_button().check_if_clicked():
                            position = [i, j]
                if self.options_button.check_if_clicked():
                    self.manager.options_menu.run()
                if self.game_mode == 2:
                    if self.edit_button.check_if_clicked():
                        self.manager.grid_options_menu.run("game")
        return position

    def play_game(self):
        if self.turn == 0:
            item_placed = self.place_item()
            if item_placed:
                self.operate_game()
        elif self.turn == 1:
            if self.first_move:
                available_positions = self.grid.get_array_of_positions_availability()[0]
                move_to_make = random.randint(0, len(available_positions) - 1)
                row_choice = available_positions[move_to_make][0]
                column_choice = available_positions[move_to_make][1]
                self.add_move_to_stack((row_choice, column_choice), self.symbols[1])
                self.grid.place_item_in_array(self.symbols[self.turn], row_choice, column_choice)
                self.grid_graphics.place_item(self.symbols[self.turn], row_choice, column_choice)
            else:
                start_time = time.time()
                move_to_make = self.ai.select_move()
                self.add_move_to_stack(move_to_make, self.symbols[1])
                end_time = time.time()
                elapsed_time = end_time - start_time
                if elapsed_time < 0.5:
                    remaining_time = 0.5 - elapsed_time
                    time.sleep(remaining_time)
                self.grid.place_item_in_array(self.symbols[self.turn], move_to_make[0], move_to_make[1])
                self.grid_graphics.place_item(self.symbols[self.turn], move_to_make[0], move_to_make[1])
            self.operate_game()

    def operate_game(self):
        if self.manager.sound_enabled:
            SOUNDS["placement_made"].play()
        result = r.check_result(self.grid_size, self.grid.get_items_in_grid_array(), self.win_length)
        if result[0]:  # if player has won
            self.first_move = True
            self.result = "win"
            if self.game_mode == 0:
                self.score += 10
            self.win_or_draw_screen_active = True
            if self.manager.sound_enabled:
                SOUNDS["win"].play()
        elif result[1]:  # if computer has won
            self.first_move = True
            if self.manager.sound_enabled:
                SOUNDS["game_over"].play()
            if self.game_mode == 0:
                self.game_over.run()
            elif self.game_mode == 1:
                self.result = "lose"
                self.win_or_draw_screen_active = True
        elif result[2]:  # if draw
            self.first_move = True
            self.result = "draw"
            self.win_or_draw_screen_active = True
            if self.manager.sound_enabled:
                SOUNDS["draw"].play()
        elif result[3]:  # if no result
            self.first_move = False
            self.turn = utility.flip_one_and_zero(self.turn)

    def play_game_player_vs_player(self):
        item_placed = self.place_item()
        if item_placed:
            if self.manager.sound_enabled:
                SOUNDS["placement_made"].play()
            result = r.check_result(self.grid_size, self.grid.get_items_in_grid_array(), self.win_length)
            if result[0]:  # if X has won
                self.result = "X"
                self.win_or_draw_screen_active = True
                if self.manager.sound_enabled:
                    SOUNDS["win"].play()
            elif result[1]:  # if O has won
                self.result = "O"
                self.win_or_draw_screen_active = True
                if self.manager.sound_enabled:
                    SOUNDS["win"].play()
            elif result[2]:  # if draw
                self.result = "draw"
                self.win_or_draw_screen_active = True
                if self.manager.sound_enabled:
                    SOUNDS["draw"].play()
            elif result[3]:  # if no result
                self.turn = utility.flip_one_and_zero(self.turn)

    def place_item(self):
        row_choice, column_choice = self.check_events()
        if row_choice is not None and column_choice is not None and \
                (row_choice, column_choice) in self.grid.get_array_of_positions_availability()[0]:
            self.add_move_to_stack((row_choice, column_choice), self.symbols[0])
            self.grid.place_item_in_array(self.symbols[self.turn], row_choice, column_choice)
            self.grid_graphics.place_item(self.symbols[self.turn], row_choice, column_choice)
            return True
        else:
            return False

    def run_review(self):
        if not self.review_active:
            self.backwards_stack = copy.deepcopy(self.moves)
            self.forward_stack = utility.Stack()
            self.review_active = True
        while True:
            if not self.win_or_draw_screen_active:
                self.manager.screen.fill(COLOURS["background"])
                self.display_reviewing_round()
                self.create_options_button()
                self.options_button.display_button()
                self.create_arrow_buttons()
                if self.backwards_stack.is_empty():
                    self.arrow_buttons[1].display_button()
                elif self.forward_stack.is_empty():
                    self.arrow_buttons[0].display_button()
                else:
                    self.arrow_buttons[0].display_button()
                    self.arrow_buttons[1].display_button()
                self.create_back_button()
                self.back_button.display_button()
                self.check_events_for_review()
                self.view_move()
                pygame.display.update()
                self.manager.clock.tick(FPS)
            else:
                self.win_or_draw.run()

    def check_events_for_review(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.options_button.check_if_clicked():
                    self.manager.options_menu.run()
                if self.arrow_buttons[0].check_if_clicked():
                    if not self.backwards_stack.is_empty():
                        self.forward_stack.push(self.backwards_stack.pop())
                if self.arrow_buttons[1].check_if_clicked():
                    if not self.forward_stack.is_empty():
                        self.backwards_stack.push(self.forward_stack.pop())
                if self.back_button.check_if_clicked():
                    self.review_active = False
                    if self.return_to_game_over_screen:
                        self.game_over.run()
                    if self.return_to_win_or_draw_screen:
                        self.win_or_draw_screen_active = True
                        self.review_mode = False
                        self.run()

    def view_move(self):
        temp_grid = GridLogic(self.grid_size, self.win_length)
        temp_grid_graphics = GridGraphics(self.grid_size, self.manager.screen)
        temp_backwards_stack = copy.deepcopy(self.backwards_stack)
        for move in range(temp_backwards_stack.size()):
            previous_move = temp_backwards_stack.pop()
            temp_grid.place_item_in_array(previous_move[1], previous_move[0][0], previous_move[0][1])
            temp_grid_graphics.place_item(previous_move[1], previous_move[0][0], previous_move[0][1])
        temp_grid_graphics.display_grid_lines()
        temp_grid_graphics.display_current_grid_state()

    def add_move_to_stack(self, position, symbol):
        self.moves.push((position, symbol))

    def create_options_button(self):
        pos = (SCREEN_WIDTH - 80, 8)
        self.options_button = gui_utility.ScaledImageButton(self.manager.screen, IMAGES["options_icon"],
                                                            IMAGES["options_icon_hovering"], 65, 65, pos)

    def create_edit_button(self):
        pos = (15, 8)
        self.edit_button = gui_utility.ScaledImageButton(self.manager.screen, IMAGES["edit_icon"],
                                                         IMAGES["edit_icon_hovering"], 60, 60, pos)

    def create_review_button(self, y_pos):
        text = FONTS["create_account_text"].render("REVIEW ROUND", True, COLOURS["white"])
        position = (int((SCREEN_WIDTH / 2) - (text.get_width() / 2)), y_pos)
        self.review_button = gui_utility.TextButton(self.manager.screen, "REVIEW ROUND", FONTS["create_account_text"],
                                                    COLOURS["white"], COLOURS["light_blue"], position)

    def create_arrow_buttons(self):
        for i, button in enumerate(["left", "right"]):
            self.arrow_buttons[i] = gui_utility.ScaledImageButton(self.manager.screen, ARROWS[f"{button}_arrow"],
                                                                  ARROWS[button + "_arrow_hovering"], 60, 60,
                                                                  (int((SCREEN_WIDTH / 2) - 120 + (180 * i)), 813))

    def create_back_button(self):
        pos = (15, 3)
        self.back_button = gui_utility.TextButton(self.manager.screen, "BACK", FONTS["score"], COLOURS["white"],
                                                  COLOURS["light_blue"], pos)

    def display_score(self):
        text = FONTS["score"].render(f"SCORE: {self.score}", True, COLOURS["white"])
        position = (13, 3)
        self.manager.screen.blit(text, position)

    def display_turn(self):
        if self.game_mode == 2:
            string = ["X'S TURN", "O'S TURN"]
        else:
            string = ["YOUR TURN", "COMPUTER'S TURN"]
        colour = [COLOURS["cross_colour"], COLOURS["nought_colour"]]
        text = FONTS["game"].render(string[self.turn], True, colour[self.turn])
        position = (int((SCREEN_WIDTH / 2) - (text.get_width() / 2)), 800)
        self.manager.screen.blit(text, position)

    def display_win_length(self):
        text = FONTS["game"].render(f"GET {self.win_length} IN A ROW", True, COLOURS["white"])
        position = (int((SCREEN_WIDTH / 2) - (text.get_width() / 2)), 10)
        self.manager.screen.blit(text, position)

    def display_reviewing_round(self):
        text = FONTS["game"].render("REVIEWING ROUND", True, COLOURS["white"])
        position = (int((SCREEN_WIDTH / 2) - (text.get_width() / 2)), 10)
        self.manager.screen.blit(text, position)


class GridLogic:
    def __init__(self, grid_size, win_length):
        self.grid_size = grid_size
        self.win_length = win_length
        self.grid = self.create_grid()

    def create_grid(self):
        grid = []
        for row in range(self.grid_size):
            grid.append([])
            for column in range(self.grid_size):
                grid[row].append(Square())
        return grid

    def place_item_in_array(self, item, row, column):
        self.grid[row][column].set_item(item)

    def get_items_in_grid_array(self):
        items = []
        for i, row in enumerate(self.grid):
            items.append([])
            for grid_slot in row:
                items[i].append(grid_slot.get_item())
        return items

    def get_array_of_positions_availability(self):
        positions = [[], []]  # available, taken
        for i, row in enumerate(self.get_items_in_grid_array()):
            for j, item in enumerate(row):
                if item is None:
                    positions[0].append((i, j))
                else:
                    positions[1].append((i, j))
        return positions


class GridGraphics:
    def __init__(self, size, surface):
        self.grid_size = size
        self.surface = surface
        self.grid = self.create_grid()

    def create_grid(self):
        grid = []
        for row in range(self.grid_size):
            grid.append([])
            for column in range(self.grid_size):
                grid[row].append(SquareGraphics(row, column, self.grid_size))
        return grid

    def create_grid_buttons(self):
        for row in self.grid:
            for grid_slot in row:
                button = gui_utility.ScaledImageButton(self.surface, IMAGES["blank_square"],
                                                       IMAGES["blank_square"], grid_slot.get_size()[0],
                                                       grid_slot.get_size()[1], grid_slot.get_position())
                grid_slot.set_button(button)

    def get_grid(self):
        return self.grid

    def display_grid_lines(self):
        grid_lines = []  # create grid lines
        number_of_lines = self.grid_size - 1
        thickness = 25 * (3 / self.grid_size)
        for vertical_line in range(number_of_lines):
            position = GRID_POSITION[0] + (1 + vertical_line) * (GRID_HEIGHT_AND_WIDTH / self.grid_size) - (
                    thickness / 2)
            grid_lines.append(pygame.Rect(position, GRID_POSITION[1], thickness, GRID_HEIGHT_AND_WIDTH))
        for horizontal_line in range(number_of_lines):
            position = GRID_POSITION[1] + (1 + horizontal_line) * (GRID_HEIGHT_AND_WIDTH / self.grid_size) - (
                    thickness / 2)
            grid_lines.append(pygame.Rect(GRID_POSITION[0], position, GRID_HEIGHT_AND_WIDTH, thickness))
        for line in grid_lines:  # draw grid lines
            pygame.draw.rect(self.surface, COLOURS["white"], line)

    def display_current_grid_state(self):
        for row in self.grid:
            for grid_slot in row:
                if grid_slot.get_item() is not None:
                    self.surface.blit(pygame.transform.scale(IMAGES[grid_slot.get_item()], grid_slot.get_size()),
                                      grid_slot.get_position())

    def place_item(self, item, row, column):
        self.grid[row][column].set_item(item)
        self.surface.blit(pygame.transform.scale(IMAGES[item], self.grid[row][column].get_size()),
                          self.grid[row][column].get_position())


class Square:
    def __init__(self):
        self.item = None

    def get_item(self):
        return self.item

    def set_item(self, item):
        self.item = item


class SquareGraphics(Square):
    def __init__(self, row, column, grid_size):
        Square.__init__(self)
        symbol_height = symbol_width = GRID_HEIGHT_AND_WIDTH / grid_size
        y_pos = int(GRID_POSITION[1] + (symbol_height * row))
        x_pos = int(GRID_POSITION[0] + (symbol_width * column))
        self.position = (x_pos, y_pos)
        self.size = (symbol_width, symbol_height)
        self.button = None

    def get_button(self):
        return self.button

    def set_button(self, button):
        self.button = button

    def get_position(self):
        return self.position

    def get_size(self):
        return self.size


class AI:
    def __init__(self, noughts_and_crosses):
        self.noughts_and_crosses = noughts_and_crosses

    def pygame_operations(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.noughts_and_crosses.options_button.check_if_clicked():
                    self.noughts_and_crosses.manager.options_menu.run()
        self.noughts_and_crosses.options_button.display_button()
        pygame.display.update()

    @staticmethod
    def get_array_of_available_positions_randomised(grid):
        available_positions = grid.get_array_of_positions_availability()[0]
        random.shuffle(available_positions)
        return available_positions

    def get_array_of_available_positions_sorted(self, grid):
        available_positions = self.get_array_of_available_positions_randomised(grid)
        if len(available_positions) <= 1:
            return available_positions
        else:
            taken_positions = grid.get_array_of_positions_availability()[1]

            def distance(position):
                distances = []
                for taken_position in taken_positions:
                    dx = abs(position[0] - taken_position[0])
                    dy = abs(position[1] - taken_position[1])
                    distances.append(max(dx, dy))
                return min(distances)

            return sorted(available_positions, key=distance)

    def minimax(self, grid, depth, alpha, beta, maximizing, t1):
        self.pygame_operations()
        t2 = time.time()
        if t2 - t1 > utility.fibonacci(self.noughts_and_crosses.grid_size):
            print(f"time: {t2 - t1}")
            raise
        state = r.check_result(self.noughts_and_crosses.grid_size, grid.get_items_in_grid_array(),
                               self.noughts_and_crosses.win_length)
        num_of_empty_squares_plus_one = len(grid.get_array_of_positions_availability()[0]) + 1

        if state[0]:
            return 1 * num_of_empty_squares_plus_one, None  # evaluation, move
        if state[1]:
            return -1 * num_of_empty_squares_plus_one, None  # evaluation, move
        if state[2] or depth == 0:
            return 0, None  # evaluation, move

        if maximizing:
            max_evaluation = -float("inf")
            best_move = None
            empty_squares = self.get_array_of_available_positions_sorted(grid)
            for row, col in empty_squares:
                temp_grid = copy.deepcopy(grid)
                temp_grid.place_item_in_array("X", row, col)
                evaluation = self.minimax(temp_grid, depth - 1, alpha, beta, False, t1)[0]
                if evaluation > max_evaluation:
                    max_evaluation = evaluation
                    alpha = evaluation
                    best_move = (row, col)
                if beta <= alpha:
                    return max_evaluation, best_move
            return max_evaluation, best_move

        elif not maximizing:
            min_evaluation = float("inf")
            best_move = None
            empty_squares = self.get_array_of_available_positions_sorted(grid)
            for row, col in empty_squares:
                temp_grid = copy.deepcopy(grid)
                temp_grid.place_item_in_array("O", row, col)
                evaluation = self.minimax(temp_grid, depth - 1, alpha, beta, True, t1)[0]
                if evaluation < min_evaluation:
                    min_evaluation = evaluation
                    beta = evaluation
                    best_move = (row, col)
                if beta <= alpha:
                    return min_evaluation, best_move
            return min_evaluation, best_move

    def iterative_deepening_minimax(self, grid, max_depth):
        best_move = None
        t1 = time.time()
        for depth in range(1, max_depth + 1):
            try:
                evaluation, best_move = self.minimax(grid, depth, -float("inf"), float("inf"), False, t1)
            except:
                print(f"depth: {depth}")
                return best_move
        print(f"depth: {max_depth}")
        return best_move

    def select_move(self):
        if self.noughts_and_crosses.game_mode == 0:
            if random.randint(1, 8) == 1:  # random move
                print("random")
                return random.choice(self.noughts_and_crosses.grid.get_array_of_positions_availability()[0])
            else:
                if self.noughts_and_crosses.grid_size == 3:
                    depth = random.randint(2, 6)
                    print(f"depth: {depth}")
                    return self.minimax(self.noughts_and_crosses.grid, depth, -float("inf"), float("inf"), False,
                                        float("inf"))[1]
                else:
                    return self.iterative_deepening_minimax(self.noughts_and_crosses.grid, 10)
        elif self.noughts_and_crosses.game_mode == 1:
            return self.minimax(self.noughts_and_crosses.grid, float("inf"), -float("inf"), float("inf"), False,
                                float("inf"))[1]


class EndResult:
    black_screen_opacity = 180

    def __init__(self, noughts_and_crosses):
        self.noughts_and_crosses = noughts_and_crosses

    def run(self):
        self.display_current_game_state()
        self.display_black_cover()

    def display_current_game_state(self):
        self.noughts_and_crosses.manager.screen.fill(COLOURS["background"])
        self.noughts_and_crosses.grid_graphics.display_grid_lines()
        self.noughts_and_crosses.grid_graphics.display_current_grid_state()
        self.noughts_and_crosses.display_turn()
        self.noughts_and_crosses.display_win_length()

    def display_black_cover(self):
        background = IMAGES["background_black"].convert_alpha()
        background.set_alpha(self.black_screen_opacity)
        self.noughts_and_crosses.manager.screen.blit(background, (0, 0))


class WinOrDraw(EndResult):
    def __init__(self, noughts_and_crosses):
        EndResult.__init__(self, noughts_and_crosses)
        continue_text = FONTS["game"].render("CONTINUE", True, COLOURS["white"])
        continue_text_x_pos = int((SCREEN_WIDTH / 2) - (continue_text.get_width() / 2))
        continue_text_y_pos = int((SCREEN_HEIGHT / 2) + continue_text.get_height())
        self.continue_text_pos = (continue_text_x_pos, continue_text_y_pos)
        self.continue_button = None

    def run(self):
        while True:
            EndResult.run(self)
            self.noughts_and_crosses.display_score()
            self.display_result()
            self.continue_button = gui_utility.TextButton(self.noughts_and_crosses.manager.screen, "CONTINUE",
                                                          FONTS["game"], COLOURS["white"], COLOURS["light_blue"],
                                                          self.continue_text_pos)
            self.noughts_and_crosses.create_options_button()
            self.noughts_and_crosses.create_review_button(self.continue_text_pos[1] + 90)
            self.continue_button.display_button()
            self.noughts_and_crosses.options_button.display_button()
            self.noughts_and_crosses.review_button.display_button()
            self.check_events()
            pygame.display.update()
            self.noughts_and_crosses.manager.clock.tick(FPS)

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.continue_button.check_if_clicked():
                    if self.noughts_and_crosses.result == "win":
                        self.noughts_and_crosses.grid_size += 1
                        self.noughts_and_crosses.win_length = utility.get_starting_win_length(
                            self.noughts_and_crosses.grid_size)
                    elif self.noughts_and_crosses.result == "draw":
                        if self.noughts_and_crosses.win_length > 3:
                            self.noughts_and_crosses.win_length -= 1
                    self.noughts_and_crosses.grid = GridLogic(self.noughts_and_crosses.grid_size,
                                                              self.noughts_and_crosses.win_length)
                    self.noughts_and_crosses.grid_graphics = GridGraphics(self.noughts_and_crosses.grid_size,
                                                                          self.noughts_and_crosses.manager.screen)
                    self.noughts_and_crosses.turn = utility.random_one_or_zero()
                    self.noughts_and_crosses.win_or_draw_screen_active = False
                    self.noughts_and_crosses.moves = utility.Stack()
                    self.noughts_and_crosses.run()
                elif self.noughts_and_crosses.options_button.check_if_clicked():
                    self.noughts_and_crosses.manager.options_menu.run()
                elif self.noughts_and_crosses.review_button.check_if_clicked():
                    self.noughts_and_crosses.review_mode = True
                    self.noughts_and_crosses.win_or_draw_screen_active = False
                    self.noughts_and_crosses.return_to_win_or_draw_screen = True
                    self.noughts_and_crosses.run()

    def display_result(self):
        string = {"win": "YOU WON", "draw": "DRAW"}
        text = FONTS["result"].render(string[self.noughts_and_crosses.result], True, COLOURS["white"])
        x_pos = int((SCREEN_WIDTH / 2) - (text.get_width() / 2))
        y_pos = int((SCREEN_HEIGHT / 2) - (text.get_height() / 2))
        self.noughts_and_crosses.manager.screen.blit(text, (x_pos, y_pos))


class GameOver(EndResult):
    game_over_y_pos = 135
    your_score_y_pos = 300
    best_score_y_pos = 400
    play_again_pos = (358, 520)
    main_menu_pos = (358, 641)

    def __init__(self, noughts_and_crosses):
        EndResult.__init__(self, noughts_and_crosses)
        self.play_again_button = None
        self.main_menu_button = None
        self.new_high_score = False

    def run(self):
        while True:
            EndResult.run(self)
            self.play_again_button = gui_utility.Button(self.noughts_and_crosses.manager.screen,
                                                        MENU_BUTTONS["play_again"], MENU_BUTTONS["play_again_hovering"],
                                                        self.play_again_pos)
            self.main_menu_button = gui_utility.Button(self.noughts_and_crosses.manager.screen,
                                                       MENU_BUTTONS["main_menu"], MENU_BUTTONS["main_menu_hovering"],
                                                       self.main_menu_pos)
            self.noughts_and_crosses.create_review_button(self.main_menu_pos[1] + 130)
            self.display_game_over()
            self.display_score_result()
            self.check_events()
            self.play_again_button.display_button()
            self.main_menu_button.display_button()
            self.noughts_and_crosses.review_button.display_button()
            pygame.display.update()
            self.noughts_and_crosses.manager.clock.tick(FPS)

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.play_again_button.check_if_clicked():
                    self.noughts_and_crosses.manager.noughts_and_crosses = NoughtsAndCrosses(
                        self.noughts_and_crosses.manager, 0, 3, 3)
                    self.noughts_and_crosses.manager.noughts_and_crosses.run()
                elif self.main_menu_button.check_if_clicked():
                    self.noughts_and_crosses.manager.main_menu.run()
                elif self.noughts_and_crosses.review_button.check_if_clicked():
                    self.noughts_and_crosses.review_mode = True
                    self.noughts_and_crosses.return_to_game_over_screen = True
                    self.noughts_and_crosses.run()

    def display_game_over(self):
        text = FONTS["game_over"].render("GAME OVER", True, COLOURS["red"])
        x_pos = int((SCREEN_WIDTH / 2) - (text.get_width() / 2))
        self.noughts_and_crosses.manager.screen.blit(text, (x_pos, self.game_over_y_pos))

    def display_score_result(self):
        self.display_your_score()
        database.connect_to_database()
        previous_high_score = database.get_player_high_score(self.noughts_and_crosses.manager.username)
        database.close_database()
        if not self.new_high_score:
            if self.noughts_and_crosses.score > previous_high_score:
                database.connect_to_database()
                database.update_player_high_score(self.noughts_and_crosses.manager.username,
                                                  self.noughts_and_crosses.score)
                database.close_database()
                self.new_high_score = True
                self.display_new_high_score()
            else:
                self.display_your_best_score()
        else:
            self.display_new_high_score()

    def display_your_score(self):
        text = FONTS["game_over_screen"].render(f"YOUR SCORE: {self.noughts_and_crosses.score}", True, COLOURS["white"])
        x_pos = int((SCREEN_WIDTH / 2) - (text.get_width() / 2))
        self.noughts_and_crosses.manager.screen.blit(text, (x_pos, self.your_score_y_pos))

    def display_your_best_score(self):
        database.connect_to_database()
        high_score = database.get_player_high_score(self.noughts_and_crosses.manager.username)
        database.close_database()
        text = FONTS["game_over_screen"].render(f"YOUR BEST: {high_score}", True, COLOURS["white"])
        x_pos = int((SCREEN_WIDTH / 2) - (text.get_width() / 2))
        self.noughts_and_crosses.manager.screen.blit(text, (x_pos, self.best_score_y_pos))

    def display_new_high_score(self):
        text = FONTS["game_over_screen"].render("NEW HIGH SCORE!", True, COLOURS["white"])
        x_pos = int((SCREEN_WIDTH / 2) - (text.get_width() / 2))
        self.noughts_and_crosses.manager.screen.blit(text, (x_pos, self.best_score_y_pos))


class Impossible3x3Result(EndResult):
    def __init__(self, noughts_and_crosses):
        EndResult.__init__(self, noughts_and_crosses)
        play_again_text = FONTS["game"].render("PLAY AGAIN", True, COLOURS["white"])
        play_again_text_x_pos = int((SCREEN_WIDTH / 2) - (play_again_text.get_width() / 2))
        play_again_text_y_pos = int((SCREEN_HEIGHT / 2) + play_again_text.get_height())
        self.play_again_text_pos = (play_again_text_x_pos, play_again_text_y_pos)
        self.play_again_button = None

    def run(self):
        while True:
            EndResult.run(self)
            self.display_result()
            self.play_again_button = gui_utility.TextButton(self.noughts_and_crosses.manager.screen, "PLAY AGAIN",
                                                            FONTS["game"], COLOURS["white"], COLOURS["light_blue"],
                                                            self.play_again_text_pos)
            self.noughts_and_crosses.create_options_button()
            self.noughts_and_crosses.create_edit_button()
            self.play_again_button.display_button()
            self.noughts_and_crosses.options_button.display_button()
            self.check_events()
            pygame.display.update()
            self.noughts_and_crosses.manager.clock.tick(FPS)

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.play_again_button.check_if_clicked():
                    self.noughts_and_crosses.grid = GridLogic(self.noughts_and_crosses.grid_size,
                                                              self.noughts_and_crosses.win_length)
                    self.noughts_and_crosses.grid_graphics = GridGraphics(self.noughts_and_crosses.grid_size,
                                                                          self.noughts_and_crosses.manager.screen)
                    self.noughts_and_crosses.turn = utility.random_one_or_zero()
                    self.noughts_and_crosses.win_or_draw_screen_active = False
                    self.noughts_and_crosses.manager.noughts_and_crosses.run()
                elif self.noughts_and_crosses.options_button.check_if_clicked():
                    self.noughts_and_crosses.manager.options_menu.run()

    def display_result(self):
        string = {"win": "YOU WON", "lose": "YOU LOST", "draw": "DRAW"}
        if self.noughts_and_crosses.result == "win":
            colour = COLOURS["cross_colour"]
        elif self.noughts_and_crosses.result == "lose":
            colour = COLOURS["nought_colour"]
        else:
            colour = COLOURS["white"]
        text = FONTS["game_over"].render(string[self.noughts_and_crosses.result], True, colour)
        x_pos = int((SCREEN_WIDTH / 2) - (text.get_width() / 2))
        y_pos = int((SCREEN_HEIGHT / 2) - (text.get_height() / 2))
        self.noughts_and_crosses.manager.screen.blit(text, (x_pos, y_pos))


class PlayerVsPlayerWinner(EndResult):
    def __init__(self, noughts_and_crosses):
        EndResult.__init__(self, noughts_and_crosses)
        play_again_text = FONTS["game"].render("PLAY AGAIN", True, COLOURS["white"])
        play_again_text_x_pos = int((SCREEN_WIDTH / 2) - (play_again_text.get_width() / 2))
        play_again_text_y_pos = int((SCREEN_HEIGHT / 2) + play_again_text.get_height())
        self.play_again_text_pos = (play_again_text_x_pos, play_again_text_y_pos)
        self.play_again_button = None

    def run(self):
        while True:
            EndResult.run(self)
            self.display_result()
            self.play_again_button = gui_utility.TextButton(self.noughts_and_crosses.manager.screen, "PLAY AGAIN",
                                                            FONTS["game"], COLOURS["white"], COLOURS["light_blue"],
                                                            self.play_again_text_pos)
            self.noughts_and_crosses.create_options_button()
            self.noughts_and_crosses.create_edit_button()
            self.play_again_button.display_button()
            self.noughts_and_crosses.options_button.display_button()
            self.noughts_and_crosses.edit_button.display_button()
            self.check_events()
            pygame.display.update()
            self.noughts_and_crosses.manager.clock.tick(FPS)

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.play_again_button.check_if_clicked():
                    self.noughts_and_crosses.grid = GridLogic(self.noughts_and_crosses.grid_size,
                                                              self.noughts_and_crosses.win_length)
                    self.noughts_and_crosses.grid_graphics = GridGraphics(self.noughts_and_crosses.grid_size,
                                                                          self.noughts_and_crosses.manager.screen)
                    self.noughts_and_crosses.turn = utility.random_one_or_zero()
                    self.noughts_and_crosses.win_or_draw_screen_active = False
                    self.noughts_and_crosses.manager.noughts_and_crosses.run()
                elif self.noughts_and_crosses.options_button.check_if_clicked():
                    self.noughts_and_crosses.manager.options_menu.run()
                elif self.noughts_and_crosses.edit_button.check_if_clicked():
                    self.noughts_and_crosses.manager.grid_options_menu.run("game")

    def display_result(self):
        string = {"X": "X WINS", "O": "O WINS", "draw": "DRAW"}
        if self.noughts_and_crosses.result == "X":
            colour = COLOURS["cross_colour"]
        elif self.noughts_and_crosses.result == "O":
            colour = COLOURS["nought_colour"]
        else:
            colour = COLOURS["white"]
        text = FONTS["game_over"].render(string[self.noughts_and_crosses.result], True, colour)
        x_pos = int((SCREEN_WIDTH / 2) - (text.get_width() / 2))
        y_pos = int((SCREEN_HEIGHT / 2) - (text.get_height() / 2))
        self.noughts_and_crosses.manager.screen.blit(text, (x_pos, y_pos))


class LoginScreen:
    def __init__(self, manager, title):
        self.manager = manager
        self.title = MENU_TITLES[title]
        self.title_rect = self.title.get_rect(topleft=(0, 105))
        self.box = [TEXT_BOX["not_selected"], TEXT_BOX["selected"], TEXT_BOX["error"]]
        self.username_text_box = gui_utility.Button(self.manager.screen, self.box[0], self.box[0], (360, 353))
        self.password_text_box = gui_utility.Button(self.manager.screen, self.box[0], self.box[0], (360, 477))
        self.username_text = ""
        self.password_text = ""
        self.hidden_password_text = ""
        self.text_surface = None
        self.username_box_index = 0
        self.password_box_index = 0

    def run(self):
        self.check_events()
        self.manager.screen.fill(COLOURS["background"])
        self.display_title()
        self.display_headings()

    def check_events(self):
        pass

    def display_title(self):
        self.manager.screen.blit(self.title, self.title_rect)

    def display_headings(self):
        headings = ["USERNAME:", "PASSWORD:"]
        x_pos = self.username_text_box.get_pos()[0] + 11
        y_pos = self.username_text_box.get_pos()[1] - 30
        for heading in headings:
            text = FONTS["login_heading"].render(heading, True, COLOURS["white"])
            self.manager.screen.blit(text, (x_pos, y_pos))
            y_pos = self.password_text_box.get_pos()[1] - 30

    def refresh_text(self):
        self.username_text = ""
        self.password_text = ""
        self.hidden_password_text = ""


class Login(LoginScreen):
    login_button_pos = (359, 584)

    def __init__(self, manager):
        LoginScreen.__init__(self, manager, "login")
        create_account_text = FONTS["create_account_text"].render("CREATE ACCOUNT", True, COLOURS["white"])
        self.create_account_pos = (int(SCREEN_WIDTH / 2) - (create_account_text.get_width() / 2), 726)
        self.login_button = None
        self.create_account_button = None
        self.display_error_message1 = False  # username does not exist
        self.display_error_message2 = False  # password is incorrect

    def run(self):
        while True:
            self.login_button = gui_utility.Button(self.manager.screen, MENU_BUTTONS["login"],
                                                   MENU_BUTTONS["login_hovering"], self.login_button_pos)
            self.create_account_button = gui_utility.TextButton(self.manager.screen, "CREATE ACCOUNT",
                                                                FONTS["create_account_text"], COLOURS["white"],
                                                                COLOURS["light_blue"], self.create_account_pos)
            LoginScreen.run(self)
            self.manager.screen.blit(self.box[self.username_box_index], self.username_text_box.get_pos())
            self.manager.screen.blit(self.box[self.password_box_index], self.password_text_box.get_pos())
            self.text_surface = FONTS["text_box"].render(self.username_text, True, COLOURS["black"])
            self.manager.screen.blit(self.text_surface,
                                     (
                                         self.username_text_box.get_pos()[0] + 11,
                                         self.username_text_box.get_pos()[1] + 8))
            self.text_surface = FONTS["text_box"].render(self.hidden_password_text, True, COLOURS["black"])
            self.manager.screen.blit(self.text_surface,
                                     (
                                         self.password_text_box.get_pos()[0] + 11,
                                         self.password_text_box.get_pos()[1] + 7))
            if self.display_error_message1:
                self.display_error_message(1)
            elif self.display_error_message2:
                self.display_error_message(2)
            self.login_button.display_button()
            self.create_account_button.display_button()
            pygame.display.update()
            self.manager.clock.tick(FPS)

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.username_text_box.check_if_clicked():
                    self.username_box_index = 1
                    if self.password_box_index != 2:
                        self.password_box_index = 0
                elif self.password_text_box.check_if_clicked():
                    if self.username_box_index != 2:
                        self.username_box_index = 0
                    self.password_box_index = 1
                else:
                    if self.username_box_index != 2:
                        self.username_box_index = 0
                    if self.password_box_index != 2:
                        self.password_box_index = 0
                if self.login_button.check_if_clicked():
                    self.login()
                elif self.create_account_button.check_if_clicked():
                    self.refresh_text()
                    self.display_error_message1 = False
                    self.display_error_message2 = False
                    self.username_box_index = self.password_box_index = 0
                    self.manager.create_account_screen.run()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.login()
                elif event.key == pygame.K_ESCAPE:
                    if self.username_box_index != 2:
                        self.username_box_index = 0
                    if self.password_box_index != 2:
                        self.password_box_index = 0
                else:
                    if self.username_box_index == 1:
                        if event.key == pygame.K_BACKSPACE:
                            self.username_text = self.username_text[: -1]
                        else:
                            if event.key == pygame.K_TAB:
                                self.username_box_index = 0
                                self.password_box_index = 1
                            else:
                                if len(self.username_text) < 33:
                                    self.username_text += event.unicode
                    elif self.password_box_index == 1:
                        if event.key == pygame.K_BACKSPACE:
                            self.password_text = self.password_text[: -1]
                            self.hidden_password_text = self.hidden_password_text[: -1]
                        else:
                            if event.key == pygame.K_TAB:
                                self.username_box_index = 1
                                self.password_box_index = 0
                            else:
                                if len(self.password_text) < 33:
                                    self.password_text += event.unicode
                                    self.hidden_password_text += len(event.unicode) * "•"

    def login(self):
        if self.check_login_details():
            self.manager.username = self.username_text
            database.connect_to_database()
            self.manager.sound_enabled = bool(database.get_player_sound_enabled(self.username_text))
            database.close_database()
            self.refresh_text()
            self.display_error_message1 = False
            self.display_error_message2 = False
            self.username_box_index = self.password_box_index = 0
            self.manager.main_menu.run()

    def check_login_details(self):
        database.connect_to_database()
        correct_login_details = False
        if len(self.username_text) == 0:
            self.username_box_index = 2
            self.display_error_message1 = False
            self.display_error_message2 = False
        if len(self.password_text) == 0:
            self.password_box_index = 2
            self.display_error_message1 = False
            self.display_error_message2 = False
        if len(self.username_text) > 0 and len(self.password_text) > 0:
            if database.check_if_username_exists(self.username_text):
                if database.check_if_password_correct(self.username_text, self.password_text):
                    self.display_error_message1 = False
                    self.display_error_message2 = False
                    correct_login_details = True
                else:
                    self.display_error_message1 = False
                    self.display_error_message2 = True
            else:
                self.display_error_message1 = True
                self.display_error_message2 = False
        database.close_database()
        return correct_login_details

    def display_error_message(self, error_message_number):
        messages = ["THAT USERNAME DOES NOT EXIST", "INCORRECT PASSWORD"]
        text = FONTS["error_message"].render(messages[error_message_number - 1], True, COLOURS["red"])
        x_pos = int((SCREEN_WIDTH / 2) - (text.get_width() / 2))
        self.manager.screen.blit(text, (x_pos, self.username_text_box.get_pos()[1] - 75))


class CreateAccount(LoginScreen):
    create_account_pos = (359, 584)
    back_pos = (359, 705)
    valid_username_characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_"

    def __init__(self, manager):
        LoginScreen.__init__(self, manager, "create_account")
        self.create_account_button = None
        self.back_button = None
        self.display_error_message1 = False  # username already taken
        self.display_error_message2 = False  # username not in character limit
        self.display_error_message3 = False  # password not in  character limit
        self.display_error_message4 = False  # username has invalid characters

    def run(self):
        while True:
            self.create_account_button = gui_utility.Button(self.manager.screen, MENU_BUTTONS["create_account"],
                                                            MENU_BUTTONS["create_account_hovering"],
                                                            self.create_account_pos)
            self.back_button = gui_utility.Button(self.manager.screen, MENU_BUTTONS["back"],
                                                  MENU_BUTTONS["back_hovering"],
                                                  self.back_pos)
            LoginScreen.run(self)
            self.manager.screen.blit(self.box[self.username_box_index], self.username_text_box.get_pos())
            self.manager.screen.blit(self.box[self.password_box_index], self.password_text_box.get_pos())
            self.text_surface = FONTS["text_box"].render(self.username_text, True, COLOURS["black"])
            self.manager.screen.blit(self.text_surface,
                                     (
                                         self.username_text_box.get_pos()[0] + 11,
                                         self.username_text_box.get_pos()[1] + 8))
            self.text_surface = FONTS["text_box"].render(self.hidden_password_text, True, COLOURS["black"])
            self.manager.screen.blit(self.text_surface,
                                     (
                                         self.password_text_box.get_pos()[0] + 11,
                                         self.password_text_box.get_pos()[1] + 7))
            if self.display_error_message1:
                self.display_error_message(1)
            elif self.display_error_message2:
                self.display_error_message(2)
            elif self.display_error_message3:
                self.display_error_message(3)
            elif self.display_error_message4:
                self.display_error_message(4)
            self.create_account_button.display_button()
            self.back_button.display_button()
            pygame.display.update()
            self.manager.clock.tick(FPS)

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.username_text_box.check_if_clicked():
                    self.username_box_index = 1
                    if self.password_box_index != 2:
                        self.password_box_index = 0
                elif self.password_text_box.check_if_clicked():
                    if self.username_box_index != 2:
                        self.username_box_index = 0
                    self.password_box_index = 1
                else:
                    if self.username_box_index != 2:
                        self.username_box_index = 0
                    if self.password_box_index != 2:
                        self.password_box_index = 0
                if self.create_account_button.check_if_clicked():
                    self.create_account()
                elif self.back_button.check_if_clicked():
                    self.refresh_text()
                    self.display_error_message1 = False
                    self.display_error_message2 = False
                    self.display_error_message3 = False
                    self.display_error_message4 = False
                    self.username_box_index = self.password_box_index = 0
                    self.manager.login_screen.run()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.create_account()
                elif event.key == pygame.K_ESCAPE:
                    if self.username_box_index != 2:
                        self.username_box_index = 0
                    if self.password_box_index != 2:
                        self.password_box_index = 0
                else:
                    if self.username_box_index == 1:
                        if event.key == pygame.K_BACKSPACE:
                            self.username_text = self.username_text[: -1]
                        else:
                            if event.key == pygame.K_TAB:
                                self.username_box_index = 0
                                self.password_box_index = 1
                            else:
                                if len(self.username_text) < 33:
                                    self.username_text += event.unicode
                    elif self.password_box_index == 1:
                        if event.key == pygame.K_BACKSPACE:
                            self.password_text = self.password_text[: -1]
                            self.hidden_password_text = self.hidden_password_text[: -1]
                        else:
                            if event.key == pygame.K_TAB:
                                self.username_box_index = 1
                                self.password_box_index = 0
                            else:
                                if len(self.password_text) < 33:
                                    self.password_text += event.unicode
                                    self.hidden_password_text += len(event.unicode) * "•"

    def create_account(self):
        if self.check_if_valid_login_details():
            database.connect_to_database()
            database.insert_new_player(self.username_text, self.password_text)
            database.close_database()
            self.manager.username = self.username_text
            self.refresh_text()
            self.manager.main_menu.run()

    def check_if_valid_login_details(self):
        database.connect_to_database()
        valid_account_details = False
        if len(self.username_text) == 0:
            self.username_box_index = 2
            self.display_error_message1 = False
            self.display_error_message2 = False
            self.display_error_message3 = False
            self.display_error_message4 = False
        if len(self.password_text) == 0:
            self.password_box_index = 2
            self.display_error_message1 = False
            self.display_error_message2 = False
            self.display_error_message3 = False
            self.display_error_message4 = False
        if len(self.username_text) > 0 and len(self.password_text) > 0:
            characters_valid = True
            for character in self.username_text:
                character_valid = False
                for valid_character in self.valid_username_characters:
                    if character == valid_character:
                        character_valid = True
                if not character_valid:
                    characters_valid = False
            if not characters_valid:
                self.display_error_message1 = False
                self.display_error_message2 = False
                self.display_error_message3 = False
                self.display_error_message4 = True
            elif len(self.username_text) < 3 or len(self.username_text) > 12:
                self.display_error_message1 = False
                self.display_error_message2 = True
                self.display_error_message3 = False
                self.display_error_message4 = False
            elif len(self.password_text) < 8 or len(self.password_text) > 12:
                self.display_error_message1 = False
                self.display_error_message2 = False
                self.display_error_message3 = True
                self.display_error_message4 = False
            elif database.check_if_username_exists(self.username_text):
                self.display_error_message1 = True
                self.display_error_message2 = False
                self.display_error_message3 = False
                self.display_error_message4 = False
            else:
                self.display_error_message1 = False
                self.display_error_message2 = False
                self.display_error_message3 = False
                self.display_error_message4 = False
                valid_account_details = True
        database.close_database()
        return valid_account_details

    def display_error_message(self, error_message_number):
        messages = ["USERNAME ALREADY TAKEN", "USERNAME MUST BE 3-12 CHARACTERS LONG",
                    "PASSWORD MUST BE 8-12 CHARACTERS LONG",
                    "USERNAME CONTAINS INVALID CHARACTERS"]
        text = FONTS["error_message"].render(messages[error_message_number - 1], True, COLOURS["red"])
        x_pos = int((SCREEN_WIDTH / 2) - (text.get_width() / 2))
        self.manager.screen.blit(text, (x_pos, self.username_text_box.get_pos()[1] - 80))


class SelectMode(menu.Menu):
    def __init__(self, manager):
        menu.Menu.__init__(self, manager, "game_mode", ["standard", "impossible_3x3", "player_vs_player", "back"],
                           [(358, 293), (358, 414), (358, 535), (358, 675)])
        y_pos = 10
        x_pos = SCREEN_WIDTH - 60
        self.help_icon_pos = (x_pos, y_pos)
        self.help_icon = None
        with open("game_instructions.txt", "r") as f:
            lines = f.readlines()
        self.instructions = [string.replace("\n", "") for string in lines]

    def run(self):
        while True:

            self.help_icon = gui_utility.ScaledImageButton(self.manager.screen, IMAGES["help_icon"],
                                                           IMAGES["help_icon_hovering"], 45, 45, self.help_icon_pos)
            if self.help_icon.check_if_clicked():   # if the user is hovering over the help icon
                self.manager.screen.fill(COLOURS["background"])
                self.display_title()
                self.display_instructions()
            else:
                menu.Menu.run(self)
            self.help_icon.display_button()
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
                    self.manager.noughts_and_crosses = NoughtsAndCrosses(self.manager, 0, 3, 3)
                    self.manager.noughts_and_crosses.run()
                elif self.options_buttons[1].check_if_clicked():
                    self.manager.noughts_and_crosses = NoughtsAndCrosses(self.manager, 1, 3, 3)
                    self.manager.noughts_and_crosses.run()
                elif self.options_buttons[2].check_if_clicked():
                    self.manager.noughts_and_crosses = NoughtsAndCrosses(self.manager, 2, 3, 3)
                    self.manager.grid_options_menu.run("select_game_mode")
                elif self.options_buttons[3].check_if_clicked():
                    self.manager.main_menu.run()

    def display_instructions(self):
        y_pos = 280
        for line in self.instructions:
            if len(line) > 0:
                if line[0] == "+":
                    line = line[1:]
                    font = FONTS["grid_options"]
                else:
                    font = FONTS["text_box"]
                text = font.render(line, True, COLOURS["white"])
                x_pos = int((SCREEN_WIDTH / 2) - (text.get_width() / 2))
                self.manager.screen.blit(text, (x_pos, y_pos))
                y_pos += text.get_height() + 5
            else:
                y_pos += 20


class GridOptionsMenu(menu.Menu):
    def __init__(self, manager):
        menu.Menu.__init__(self, manager, "grid_options", ["confirm", "back"], [(358, 522), (358, 643)])
        self.box = [TEXT_BOX["number_not_selected"], TEXT_BOX["number_selected"], TEXT_BOX["number_error"]]
        self.grid_size_text_box = gui_utility.Button(self.manager.screen, self.box[0], self.box[0], (701, 332))
        self.win_length_text_box = gui_utility.Button(self.manager.screen, self.box[0], self.box[0], (701, 421))
        self.grid_size_text = ""
        self.win_length_text = ""
        self.text_surface = None
        self.grid_size_box_index = 0
        self.win_length_box_index = 0
        self.confirm_button = None
        self.back_button = None
        self.display_error_message1 = False  # input is not integer
        self.display_error_message2 = False  # win length > grid size
        self.display_error_message3 = False  # grid size is too big
        self.display_error_message4 = False  # grid size is too small
        self.display_error_message5 = False  # win length is too small

    def run(self, previous_page):
        while True:
            menu.Menu.run(self)
            self.check_events(previous_page)
            self.manager.screen.blit(self.box[self.grid_size_box_index], self.grid_size_text_box.get_pos())
            self.manager.screen.blit(self.box[self.win_length_box_index], self.win_length_text_box.get_pos())
            self.text_surface = FONTS["text_box"].render(self.grid_size_text, True, COLOURS["black"])
            text_x_pos = self.grid_size_text_box.get_pos()[0] + 30 - int(self.text_surface.get_width() / 2)
            self.manager.screen.blit(self.text_surface, (text_x_pos, self.grid_size_text_box.get_pos()[1] + 9))
            self.text_surface = FONTS["text_box"].render(self.win_length_text, True, COLOURS["black"])
            text_x_pos = self.win_length_text_box.get_pos()[0] + 30 - int(self.text_surface.get_width() / 2)
            self.manager.screen.blit(self.text_surface, (text_x_pos, self.win_length_text_box.get_pos()[1] + 9))
            self.display_options_text()
            if self.display_error_message1:
                self.display_error_message(1)
            elif self.display_error_message2:
                self.display_error_message(2)
            elif self.display_error_message3:
                self.display_error_message(3)
            elif self.display_error_message4:
                self.display_error_message(4)
            elif self.display_error_message5:
                self.display_error_message(5)
            pygame.display.update()
            self.manager.clock.tick(FPS)

    def check_events(self, previous_page):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.grid_size_text_box.check_if_clicked():
                    self.grid_size_box_index = 1
                    if self.win_length_box_index != 2:
                        self.win_length_box_index = 0
                elif self.win_length_text_box.check_if_clicked():
                    if self.grid_size_box_index != 2:
                        self.grid_size_box_index = 0
                    self.win_length_box_index = 1
                else:
                    if self.grid_size_box_index != 2:
                        self.grid_size_box_index = 0
                    if self.win_length_box_index != 2:
                        self.win_length_box_index = 0
                if self.options_buttons[0].check_if_clicked():
                    valid, grid_size, win_length = self.check_if_valid_input()
                    if valid:
                        self.refresh_text()
                        self.display_error_message1 = False
                        self.display_error_message2 = False
                        self.display_error_message3 = False
                        self.display_error_message4 = False
                        self.display_error_message5 = False
                        self.grid_size_box_index = self.win_length_box_index = 0
                        self.manager.noughts_and_crosses = NoughtsAndCrosses(self.manager, 2, grid_size, win_length)
                        self.manager.noughts_and_crosses.run()
                elif self.options_buttons[1].check_if_clicked():
                    self.refresh_text()
                    self.display_error_message1 = False
                    self.display_error_message2 = False
                    self.display_error_message3 = False
                    self.display_error_message4 = False
                    self.display_error_message5 = False
                    self.grid_size_box_index = self.win_length_box_index = 0
                    if previous_page == "select_game_mode":
                        self.manager.select_game_mode.run()
                    elif previous_page == "game":
                        self.manager.noughts_and_crosses.run()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    valid, grid_size, win_length = self.check_if_valid_input()
                    if valid:
                        self.refresh_text()
                        self.display_error_message1 = False
                        self.display_error_message2 = False
                        self.display_error_message3 = False
                        self.display_error_message4 = False
                        self.display_error_message5 = False
                        self.grid_size_box_index = self.win_length_box_index = 0
                        self.manager.noughts_and_crosses = NoughtsAndCrosses(self.manager, 2, grid_size, win_length)
                        self.manager.noughts_and_crosses.run()
                elif event.key == pygame.K_ESCAPE:
                    if self.grid_size_box_index != 2:
                        self.grid_size_box_index = 0
                    if self.win_length_box_index != 2:
                        self.win_length_box_index = 0
                else:
                    if self.grid_size_box_index == 1:
                        if event.key == pygame.K_BACKSPACE:
                            self.grid_size_text = self.grid_size_text[: -1]
                        else:
                            if event.key == pygame.K_TAB:
                                self.grid_size_box_index = 0
                                self.win_length_box_index = 1
                            else:
                                if len(self.grid_size_text) < 2:
                                    self.grid_size_text += event.unicode
                    elif self.win_length_box_index == 1:
                        if event.key == pygame.K_BACKSPACE:
                            self.win_length_text = self.win_length_text[: -1]
                        else:
                            if event.key == pygame.K_TAB:
                                self.grid_size_box_index = 1
                                self.win_length_box_index = 0
                            else:
                                if len(self.win_length_text) < 2:
                                    self.win_length_text += event.unicode

    def check_if_valid_input(self):
        valid_characters = False
        grid_size = 0
        win_length = 0
        if len(self.grid_size_text) == 0:
            self.grid_size_box_index = 2
            self.display_error_message1 = False
            self.display_error_message2 = False
            self.display_error_message3 = False
            self.display_error_message4 = False
            self.display_error_message5 = False
        if len(self.win_length_text) == 0:
            self.win_length_box_index = 2
            self.display_error_message1 = False
            self.display_error_message2 = False
            self.display_error_message3 = False
            self.display_error_message4 = False
            self.display_error_message5 = False
        if len(self.grid_size_text) > 0 and len(self.win_length_text) > 0:
            try:
                grid_size = int(self.grid_size_text)
                win_length = int(self.win_length_text)
                if win_length > grid_size:
                    self.display_error_message1 = False
                    self.display_error_message2 = True
                    self.display_error_message3 = False
                    self.display_error_message4 = False
                    self.display_error_message5 = False
                elif grid_size > 75:
                    self.display_error_message1 = False
                    self.display_error_message2 = False
                    self.display_error_message3 = True
                    self.display_error_message4 = False
                    self.display_error_message5 = False
                elif grid_size < 3:
                    self.display_error_message1 = False
                    self.display_error_message2 = False
                    self.display_error_message3 = False
                    self.display_error_message4 = True
                    self.display_error_message5 = False
                elif win_length < 3:
                    self.display_error_message1 = False
                    self.display_error_message2 = False
                    self.display_error_message3 = False
                    self.display_error_message4 = False
                    self.display_error_message5 = True
                else:
                    valid_characters = True
            except ValueError:
                self.display_error_message1 = True
                self.display_error_message2 = False
                self.display_error_message3 = False
                self.display_error_message4 = False
                self.display_error_message5 = False
        return valid_characters, grid_size, win_length

    def display_options_text(self):
        text = FONTS["grid_options"].render("GRID SIZE:", True, COLOURS["white"])
        self.manager.screen.blit(text, (463, 329))
        text = FONTS["grid_options"].render("WIN LENGTH:", True, COLOURS["white"])
        self.manager.screen.blit(text, (424, 418))

    def display_error_message(self, error_message_number):
        messages = ["YOU MUST ENTER AN INTEGER", "WIN LENGTH CANNOT BE GREATER THAN GRID SIZE", "GRID SIZE TOO BIG",
                    "GRID SIZE TOO SMALL", "WIN LENGTH TOO SMALL"]
        text = FONTS["error_message"].render(messages[error_message_number - 1], True, COLOURS["red"])
        x_pos = int((SCREEN_WIDTH / 2) - (text.get_width() / 2))
        self.manager.screen.blit(text, (x_pos, self.grid_size_text_box.get_pos()[1] - 55))

    def refresh_text(self):
        self.grid_size_text = ""
        self.win_length_text = ""


class LeaderBoard:
    leaderboard_title_pos = (0, 105)
    back_button_x_pos = 358

    def __init__(self, manager):
        self.manager = manager
        self.back_button = None
        self.top_five_high_score_users = []

    def run(self):
        while True:
            self.manager.screen.fill(COLOURS["background"])
            self.check_events()
            self.create_top_five_ranking()
            back_button_y_pos = 300 + ((len(self.top_five_high_score_users) - 1) * 83) + 112
            self.back_button = gui_utility.Button(self.manager.screen, MENU_BUTTONS["back"],
                                                  MENU_BUTTONS["back_hovering"],
                                                  (self.back_button_x_pos, back_button_y_pos))
            self.display_leaderboard_title()
            self.display_leaderboard()
            self.back_button.display_button()
            pygame.display.update()
            self.manager.clock.tick(FPS)

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.back_button.check_if_clicked():
                    self.manager.main_menu.run()

    def create_top_five_ranking(self):
        database.connect_to_database()
        high_score_ranked_users = database.get_high_score_ranked_users()
        database.close_database()
        if len(high_score_ranked_users) >= 5:
            self.top_five_high_score_users = high_score_ranked_users[:5]
        else:
            self.top_five_high_score_users = high_score_ranked_users[:len(high_score_ranked_users)]

    def display_leaderboard_title(self):
        self.manager.screen.blit(MENU_TITLES["leaderboard"], self.leaderboard_title_pos)

    def display_leaderboard(self):
        leaderboard_y_pos = 300
        text_y_pos = 306
        for user in range(len(self.top_five_high_score_users)):
            rank = user + 1
            username = self.top_five_high_score_users[user]
            database.connect_to_database()
            high_score = database.get_player_high_score(username)
            database.close_database()
            text_font = FONTS["leaderboard"]
            if username == self.manager.username:
                username = "YOU"
                text_font = FONTS["leaderboard_you"]
            rank_text = text_font.render(str(rank), True, COLOURS["white"])
            username_text = text_font.render(username, True, COLOURS["white"])
            score_text = text_font.render(str(high_score), True, COLOURS["white"])
            rank_x_pos = int(316 - (rank_text.get_width() / 2))
            username_x_pos = int(580 - (username_text.get_width() / 2))
            score_x_pos = int(868 - (score_text.get_width() / 2))
            self.manager.screen.blit(IMAGES["leaderboard"], (0, leaderboard_y_pos))
            self.manager.screen.blit(rank_text, (rank_x_pos, text_y_pos))
            self.manager.screen.blit(username_text, (username_x_pos, text_y_pos))
            self.manager.screen.blit(score_text, (score_x_pos, text_y_pos))
            leaderboard_y_pos += 83
            text_y_pos += 83


if __name__ == "__main__":
    Manager()
