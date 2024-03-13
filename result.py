def horizontal_win(grid_size, items_in_grid_array, win_length):
    x_winner = False
    o_winner = False
    draw = False
    empty_squares = False

    for row in range(grid_size):
        previous_item = items_in_grid_array[row][0]
        count = 1
        if previous_item is None:
            empty_squares = True
        for column in range(1, grid_size):
            current_item = items_in_grid_array[row][column]
            if current_item is None:
                count = 1
                empty_squares = True
            else:
                if current_item == previous_item:
                    count += 1
                    if count >= win_length:
                        if current_item == "X":
                            x_winner = True
                        elif current_item == "O":
                            o_winner = True
                else:
                    count = 1
            previous_item = current_item

    if not x_winner and not o_winner and not empty_squares:
        draw = True

    return x_winner, o_winner, draw


def vertical_win(grid_size, items_in_grid_array, win_length):
    x_winner = False
    o_winner = False
    draw = False
    empty_squares = False

    for column in range(grid_size):
        previous_item = items_in_grid_array[0][column]
        count = 1
        if previous_item is None:
            empty_squares = True
        for row in range(1, grid_size):
            current_item = items_in_grid_array[row][column]
            if current_item is None:
                count = 1
                empty_squares = True
            else:
                if current_item == previous_item:
                    count += 1
                    if count >= win_length:
                        if current_item == "X":
                            x_winner = True
                        elif current_item == "O":
                            o_winner = True
                else:
                    count = 1
            previous_item = current_item

    if not x_winner and not o_winner and not empty_squares:
        draw = True

    return x_winner, o_winner, draw


def diagonal_win_desc(grid_size, items_in_grid_array, win_length):
    x_winner = False
    o_winner = False
    draw = False
    empty_squares = False
    difference_plus_one = grid_size - win_length + 1
    for row in range(difference_plus_one):
        for column in range(difference_plus_one):
            diagonal_of_n_items = [items_in_grid_array[row][column]]
            if diagonal_of_n_items[0] is None:
                empty_squares = True
            else:
                for i in range(1, win_length):
                    diagonal_of_n_items.append(items_in_grid_array[row + i][column + i])
                previous_item = diagonal_of_n_items[0]
                if previous_item is None:
                    empty_squares = True
                else:
                    count = 1
                    for item in range(1, win_length):
                        current_item = diagonal_of_n_items[item]
                        if current_item is None:
                            empty_squares = True
                            count = 1
                        else:
                            if current_item == previous_item:
                                count += 1
                        previous_item = current_item
                    if count == win_length:
                        if current_item == "X":
                            x_winner = True
                        elif current_item == "O":
                            o_winner = True

    if not x_winner and not o_winner and not empty_squares:
        for row in range(grid_size):
            for column in range(grid_size):
                if items_in_grid_array[row][column] is None:
                    empty_squares = True
        if not empty_squares:
            draw = True

    return x_winner, o_winner, draw


def diagonal_win_asc(grid_size, items_in_grid_array, win_length):
    x_winner = False
    o_winner = False
    draw = False
    empty_squares = False
    difference_plus_one = grid_size - win_length + 1
    for row in range(difference_plus_one):
        for column in range(difference_plus_one):
            column_index = grid_size - column - 1
            diagonal_of_n_items = [items_in_grid_array[row][column_index]]
            if diagonal_of_n_items[0] is None:
                empty_squares = True
            else:
                for i in range(1, win_length):
                    diagonal_of_n_items.append(items_in_grid_array[row + i][column_index - i])
                previous_item = diagonal_of_n_items[0]
                if previous_item is None:
                    empty_squares = True
                else:
                    count = 1
                    for item in range(1, win_length):
                        current_item = diagonal_of_n_items[item]
                        if current_item is None:
                            empty_squares = True
                            count = 1
                        else:
                            if current_item == previous_item:
                                count += 1
                        previous_item = current_item
                    if count == win_length:
                        if current_item == "X":
                            x_winner = True
                        elif current_item == "O":
                            o_winner = True

    if not x_winner and not o_winner and not empty_squares:
        for row in range(grid_size):
            for column in range(grid_size):
                if items_in_grid_array[row][column] is None:
                    empty_squares = True
        if not empty_squares:
            draw = True

    return x_winner, o_winner, draw


def check_result(grid_size, items_in_grid_array, win_length):
    x_winner = False
    o_winner = False
    draw = False
    no_result = False

    directions = [horizontal_win(grid_size, items_in_grid_array, win_length),
                  vertical_win(grid_size, items_in_grid_array, win_length),
                  diagonal_win_desc(grid_size, items_in_grid_array, win_length),
                  diagonal_win_asc(grid_size, items_in_grid_array, win_length)]

    possible_draw = False
    for direction in directions:
        if direction[0]:
            x_winner = True
        if direction[1]:
            o_winner = True
        if direction[2]:
            possible_draw = True

    if not x_winner and not o_winner:
        if possible_draw:
            draw = True
        else:
            no_result = True

    return x_winner, o_winner, draw, no_result
