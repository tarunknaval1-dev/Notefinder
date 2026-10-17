import sqlite3
from pathlib import Path

SUPPORTED_EXTENSIONS = {".txt", ".md"}
DATABASE_FILE = Path(__file__).with_name("notefinder.db")


def choose_folder():
    folder_input = input("Enter the folder path containing your notes: ").strip()

    if not folder_input:
        print("Folder path cannot be empty.")
        return None

    folder = Path(folder_input).expanduser()

    if not folder.exists():
        print("That folder does not exist. Check the path and try again.")
        return None

    if not folder.is_dir():
        print("Please enter a folder path, not a file path.")
        return None

    folder = folder.resolve()
    print(f"Folder selected: {folder}")
    return folder


def create_database():
    with sqlite3.connect(DATABASE_FILE) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                path TEXT PRIMARY KEY,
                content TEXT NOT NULL
            )
        """)


def find_note_files(folder):
    note_files = []

    try:
        for path in folder.rglob("*"):
            if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
                note_files.append(path)
    except OSError as error:
        print(f"Could not scan part of the folder: {error}")

    return sorted(note_files, key=lambda path: str(path).lower())


def index_folder(folder):
    note_files = find_note_files(folder)

    if not note_files:
        print("No .txt or .md files found.")
        return

    saved_count = 0
    skipped_count = 0

    with sqlite3.connect(DATABASE_FILE) as connection:
        for path in note_files:
            try:
                content = path.read_text(encoding="utf-8")
                connection.execute(
                    """
                    INSERT OR REPLACE INTO documents (path, content)
                    VALUES (?, ?)
                    """,
                    (str(path.resolve()), content)
                )
                saved_count += 1
            except (OSError, UnicodeError) as error:
                print(f"Skipped {path.name}: {error}")
                skipped_count += 1

    print(f"\nFound {len(note_files)} note file(s).")
    print(f"Added or refreshed {saved_count} file(s) in the database.")
    if skipped_count:
        print(f"Skipped {skipped_count} file(s).")


def search_documents():
    query = input("Enter a word or phrase to search for: ").strip()

    if not query:
        print("Search text cannot be empty.")
        return

    search_text = query.casefold()

    with sqlite3.connect(DATABASE_FILE) as connection:
        documents = connection.execute(
            "SELECT path, content FROM documents"
        ).fetchall()

    matches = [
        path for path, content in documents
        if search_text in content.casefold()
    ]

    if not matches:
        print(f'No indexed documents contain "{query}".')
        return

    print(f'\nFound "{query}" in {len(matches)} document(s):')
    for path in matches:
        print(f"- {path}")


def main():
    create_database()
    selected_folder = None

    while True:
        print("\n--- NoteFinder ---")
        print("1. Choose notes folder")
        print("2. Index or refresh selected folder")
        print("3. Search indexed notes")
        print("4. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            selected_folder = choose_folder()
        elif choice == "2":
            if selected_folder is None:
                print("Choose a folder first.")
            else:
                index_folder(selected_folder)
        elif choice == "3":
            search_documents()
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Please choose 1, 2, 3, or 4.")


if __name__ == "__main__":
    main()