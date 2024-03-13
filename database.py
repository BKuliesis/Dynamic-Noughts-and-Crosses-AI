import sqlite3
import utility

connection = None
cursor = None


def connect_to_database():
    global connection, cursor
    global cursor
    connection = sqlite3.connect("players.db")
    cursor = connection.cursor()


def create_table():
    cursor.execute("""CREATE TABLE Player (
                   Username TEXT PRIMARY KEY,
                   Password TEXT,
                   HighScore INTEGER,
                   SoundEnabled INTEGER
                   )""")


def insert_new_player(username, password):
    cursor.execute("INSERT INTO Player VALUES (:Username, :Password, 0, 1)",
                   {'Username': username, 'Password': password})


def check_if_username_exists(username):
    cursor.execute("SELECT Username FROM Player WHERE Username=:Username", {'Username': username})
    if len(cursor.fetchall()) == 0:
        return False
    else:
        return True


def check_if_password_correct(username, password):
    cursor.execute("SELECT Password FROM Player WHERE Username=:Username", {'Username': username})
    if password == cursor.fetchone()[0]:
        return True
    else:
        return False


def get_player_high_score(username):
    cursor.execute("SELECT HighScore FROM Player WHERE Username=:Username", {'Username': username})
    return cursor.fetchone()[0]


def update_player_high_score(username, high_score):
    cursor.execute("UPDATE Player SET HighScore=:HighScore WHERE Username=:Username",
                   {'Username': username, 'HighScore': high_score})


def get_player_sound_enabled(username):
    cursor.execute("SELECT SoundEnabled FROM Player WHERE Username=:Username", {'Username': username})
    return cursor.fetchone()[0]


def update_player_sound_enabled(username, sound_enabled):
    cursor.execute("UPDATE Player SET SoundEnabled=:SoundEnabled WHERE Username=:Username",
                   {'Username': username, 'SoundEnabled': sound_enabled})


def delete_player(username):
    cursor.execute("DELETE FROM Player WHERE Username=:Username", {'Username': username})


def get_high_score_ranked_users():
    high_score_ranked_users_and_scores = []
    for user, high_score in cursor.execute("SELECT Username, HighScore FROM PLAYER"):
        high_score_ranked_users_and_scores.append((user, high_score))
    utility.reverse_merge_sort_tuple(high_score_ranked_users_and_scores, 1)
    high_score_ranked_users = []
    for user in high_score_ranked_users_and_scores:
        high_score_ranked_users.append(user[0])
    return high_score_ranked_users


def print_table():
    print("Username/Password/HighScore/SoundEnabled")
    for row in cursor.execute("SELECT * FROM Player"):
        for attribute in row:
            print(attribute, end="/")
        print()


def close_database():
    connection.commit()
    connection.close()


if __name__ == "__main__":
    connect_to_database()
    close_database()
