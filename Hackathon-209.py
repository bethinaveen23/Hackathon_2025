import sqlite3

conn = sqlite3.connect("mentor_connect.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    role TEXT CHECK(role IN ('Mentor', 'Mentee')),
    available_slots TEXT,
    preferred_slot INTEGER
)
""")

cursor.execute("""


CREATE TABLE IF NOT EXISTS chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message TEXT
)
""")
conn.commit()

def register_user():
    name = input("Enter name: ").strip()
    role = input("Enter role (Mentor/Mentee): ").strip()

    if role.lower() == "mentor":
        slot_count = int(input("Enter number of available slots: "))
        available_slots = input("Enter available slots (space-separated): ")
        preferred_slot = None
    elif role.lower() == "mentee":
        available_slots = None
        preferred_slot = int(input("Enter preferred slot: "))
    else:
        print("Invalid role! Try again.")
        return

    try:
        cursor.execute("INSERT INTO users (name, role, available_slots, preferred_slot) VALUES (?, ?, ?, ?)",
                       (name, role.capitalize(), available_slots, preferred_slot))
        conn.commit()
        print(f"User {name} registered successfully!")
    except sqlite3.IntegrityError:
        print("User with this name already exists! Try again.")

def show_available_slots():
    print("\nAvailable Mentor Slots:")
    cursor.execute("SELECT name, available_slots FROM users WHERE role='Mentor'")
    mentors = cursor.fetchall()
    if not mentors:
        print("No mentors available.")
    for mentor in mentors:
        print(f"Mentor: {mentor[0]} -> Slots: {mentor[1]}")

def book_mentor():
    show_available_slots()

    cursor.execute("SELECT id, name, preferred_slot FROM users WHERE role='Mentee'")
    mentees = cursor.fetchall()

    for mentee in mentees:
        mentee_id, mentee_name, preferred_slot = mentee
        assigned = False

        cursor.execute("SELECT id, name, available_slots FROM users WHERE role='Mentor'")
        mentors = cursor.fetchall()

        for mentor in mentors:
            mentor_id, mentor_name, available_slots = mentor
            if available_slots:
                slots = list(map(int, available_slots.split()))
                if preferred_slot in slots:
                    slots.remove(preferred_slot)
                    cursor.execute("UPDATE users SET available_slots=? WHERE id=?", (" ".join(map(str, slots)), mentor_id))
                    conn.commit()
                    print(f"{mentee_name} (Mentee) assigned to {mentor_name} (Mentor) at slot {preferred_slot}")
                    assigned = True
                    break

        if not assigned:
            for mentor in mentors:
                mentor_id, mentor_name, available_slots = mentor
                if available_slots:
                    slots = list(map(int, available_slots.split()))
                    next_slot = slots.pop(0)
                    cursor.execute("UPDATE users SET available_slots=? WHERE id=?", (" ".join(map(str, slots)), mentor_id))
                    conn.commit()
                    print(f"{mentee_name} (Mentee) assigned to {mentor_name} (Mentor) at next available slot {next_slot}")
                    assigned = True
                    break

        if not assigned:
            print(f"No mentor available for {mentee_name} at preferred slot {preferred_slot}")

def start_call():
    print("Starting video call... (Type 'exit' to end)")
    while True:
        message = input("Enter message: ").strip()
        if message.lower() == "exit":
            break
        cursor.execute("INSERT INTO chat_history (message) VALUES (?)", (message,))
        conn.commit()
        print("Message sent!")

def view_chat_history():
    print("\nChat History:")
    cursor.execute("SELECT message FROM chat_history")
    chats = cursor.fetchall()
    if not chats:
        print("No chat history found.")
    else:
        for i, chat in enumerate(chats, 1):
            print(f"{i}: {chat[0]}")

def upload_file():
    filename = input("Enter filename to upload: ")
    print(f"File '{filename}' uploaded successfully!")

def download_file():
    filename = input("Enter filename to download: ")
    print(f"File '{filename}' downloaded successfully!")

def main():
    while True:
        print("\n1. Register User\n2. Book Mentor\n3. Start Call\n4. View Chat History\n5. Upload File\n6. Download File\n7. Exit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            register_user()
        elif choice == "2":
            book_mentor()
        elif choice == "3":
            start_call()
        elif choice == "4":
            view_chat_history()
        elif choice == "5":
            upload_file()
        elif choice == "6":
            download_file()
        elif choice == "7":
            print("Exiting...")
            break
        else:
            print("Invalid choice! Try again.")


if __name__ == "__main__":
    main()
    conn.close()
