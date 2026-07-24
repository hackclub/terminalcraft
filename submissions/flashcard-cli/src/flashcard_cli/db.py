""" 
Database Function Add Flashcard And Get All Flashcards
Func:
    add_flashcard(con, quiz, answer)
    get_all_flashcard(con)
    
"""
import sqlite3

def add_flashcard(con, question, answer):
    """A function add flashcard to database


    Args:
        con (sqlite3.connect): active database connection
        question (str): simple string question
        answer (str): simple string answer


    Returns:
        boolen: retun succes or not
    """
    if con:
        try:
            cur = con.cursor()
            # cheack database have named flashcard
            cur.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='flashcard'"
            )
            # if there no table named flashcard 
            if not cur.fetchone():
                # create table new name flashcard
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS flashcard (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        question TEXT NOT NULL,
                        answer TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
            cur.execute(
                "INSERT INTO flashcard(question, answer) VALUES(?, ?)", (question, answer)
            )
            con.commit()
            flashcard_id = cur.lastrowid

            # Retrieve the inserted row
            cur.execute("SELECT id, question, answer, created_at FROM flashcard WHERE id = ?", (flashcard_id,))
            row = cur.fetchone()

            return {
                "id": row[0],
                "question": row[1],
                "answer": row[2],
                "created_at": row[3]
            } if row else None
            
        except Exception as e:
            print(e)
            return []
    else:
        print("No active database connection.")
        return []
    
def get_all_flashcard(con):
    """Fetch all flashcard from database


    Args:
        con (sqlite3.connect): active connection dayabase

    Returns:
        tuple: tuple of data in database
    """
    if con:
        try:
            cur = con.cursor()
            # cheack database have named flashcard
            cur.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='flashcard'"
            )
            # if there no table named flashcard
            if not cur.fetchone():
                # create table new name flashcard
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS flashcard (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        question TEXT NOT NULL,
                        answer TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
            cur.execute("SELECT id, question, answer, created_at FROM flashcard")
            rows = cur.fetchall()
            return [
                {
                    "id": row[0],
                    "question": row[1],
                    "answer": row[2],
                    "created_at": row[3]
                }
                for row in rows
            ]
        except Exception as e:
            print(e)
            return []
    else:
        print("No active database connection.")
        return []
    
    
def edit_card(conn,id,question,answer):
    """Edit a flashcard in the database
    def edit_card(conn,id):

    Args:
        conn (sqlite3.connect): active database connection
        id (int): The id of the flashcard to edit
        question (str): The new question for the flashcard
        answer (str): The new answer for the flashcard

    Returns:
        bool: Whether the edit was successful or not
    """
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("UPDATE flashcard SET question = ?, answer = ? WHERE id = ?", (question,answer,id))
            conn.commit()
            cur.execute("SELECT id, question, answer, created_at FROM flashcard WHERE id = ?", (id,))
            row = cur.fetchone()
            return {
                "id": row[0],
                "question": row[1],
                "answer": row[2],
                "created_at": row[3]
            }
        except Exception as e:
            print(e)
            return []
    else:
        print("No active database connection.")
        return []
        

def delete_flashcard(conn, id):
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM flashcard WHERE id = ?", (id,))
            conn.commit()
            return True
        except Exception as e:
            print(e)
            return False
    else:
        print("No active database connection.")
        return False


# if __name__ == "__main__":
#     con = sqlite3.connect("flashcard.db")
#     while True:
#         quiz = input("Quiz: ")
#         answer = input("Answer: ")
#         if add_flashcard(con, quiz, answer):
#             print("flashcard added succesfull!")
#             flashcards = get_all_flashcard(con)
#             for flashcard in flashcards:
#                 print(flashcard)
#         else:
#             print("flashcard added failed!")
