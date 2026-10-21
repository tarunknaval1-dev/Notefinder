import re
import sqlite3
from contextlib import contextmanager
from pathlib import Path

SUPPORTED_EXTENSIONS = {".txt", ".md"}
DATABASE_FILE = Path(__file__).with_name("notefinder.db")


@contextmanager
def database_connection():
    """Open the database and always close the connection when finished."""
    connection = sqlite3.connect(DATABASE_FILE)

    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def choose_folder():
    folder_input = input("Enter the folder path containing your notes: ").strip()

    if not folder_input:
        print("Folder path cannot be empty.")
        return None

    folder = Path(folder_input).expanduser()

    try:
        if not folder.exists():
            print("That folder does not exist. Check the path and try again.")
            return None

        if not folder.is_dir():
            print("Please enter a folder path, not a file path.")
            return None

        folder = folder.resolve()
    except OSError as error:
        print(f"Could not access that folder: {error}")
        return None

    print(f"Folder selected: {folder}")
    return folder


def create_database():
    try:
        with database_connection() as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    path TEXT PRIMARY KEY,
                    content TEXT NOT NULL
                )
            """)
        return True
    except sqlite3.Error as error:
        print(f"Could not create or open the database: {error}")
        return False


def find_note_files(folder):
    try:
        if not folder.exists() or not folder.is_dir():
            print("The selected folder is no longer available. Please choose it again.")
            return None
    except OSError as error:
        print(f"Could not access the selected folder: {error}")
        return None

    note_files = []

    try:
        for path in folder.rglob("*"):
            try:
                if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
                    note_files.append(path)
            except OSError as error:
                print(f"Could not check {path}: {error}")
    except OSError as error:
        print(f"Could not scan the folder: {error}")
        return None

    return sorted(note_files, key=lambda path: str(path).lower())


def index_folder(folder):
    note_files = find_note_files(folder)

    if note_files is None:
        return

    if not note_files:
        print("No .txt or .md files found.")
        return

    saved_count = 0
    skipped_count = 0

    try:
        with database_connection() as connection:
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
    except sqlite3.Error as error:
        print(f"Could not save documents to the database: {error}")
        return

    print(f"\nFound {len(note_files)} note file(s).")
    print(f"Added or refreshed {saved_count} file(s) in the database.")

    if skipped_count:
        print(f"Skipped {skipped_count} file(s).")


def make_excerpt(content, match_start, match_end, context=55):
    start = max(0, match_start - context)
    end = min(len(content), match_end + context)

    excerpt = content[start:end].replace("\n", " ").strip()

    if start > 0:
        excerpt = "..." + excerpt

    if end < len(content):
        excerpt += "..."

    return excerpt


def choose_search_filter():
    print("\nFilter results by:")
    print("1. All indexed files")
    print("2. Text files (.txt)")
    print("3. Markdown files (.md)")
    print("4. Folder")

    choice = input("Choose a filter: ").strip()

    if choice == "1":
        return {"type": "all"}

    if choice == "2":
        return {"type": ".txt"}

    if choice == "3":
        return {"type": ".md"}

    if choice == "4":
        folder_input = input("Enter the folder path to search within: ").strip()

        if not folder_input:
            print("Folder path cannot be empty.")
            return None

        folder = Path(folder_input).expanduser()

        try:
            if not folder.exists() or not folder.is_dir():
                print("That folder does not exist or is not a folder.")
                return None

            return {"type": "folder", "path": folder.resolve()}
        except OSError as error:
            print(f"Could not access that folder: {error}")
            return None

    print("Invalid filter choice. Please choose 1, 2, 3, or 4.")
    return None


def document_matches_filter(path, search_filter):
    filter_type = search_filter["type"]
    document_path = Path(path)

    if filter_type in {".txt", ".md"}:
        return document_path.suffix.lower() == filter_type

    if filter_type == "folder":
        try:
            document_path.relative_to(search_filter["path"])
            return True
        except ValueError:
            return False

    return True


def search_documents():
    query = input("Enter a word or phrase to search for: ").strip()

    if not query:
        print("Search text cannot be empty.")
        return

    search_filter = choose_search_filter()

    if search_filter is None:
        return

    pattern = re.compile(re.escape(query), re.IGNORECASE)

    try:
        with database_connection() as connection:
            documents = connection.execute(
                "SELECT path, content FROM documents"
            ).fetchall()
    except sqlite3.Error as error:
        print(f"Could not search the database: {error}")
        return

    results = []

    for path, content in documents:
        if not document_matches_filter(path, search_filter):
            continue

        matches = list(pattern.finditer(content))

        if matches:
            first_match = matches[0]
            results.append({
                "path": path,
                "count": len(matches),
                "excerpt": make_excerpt(
                    content,
                    first_match.start(),
                    first_match.end()
                )
            })

    if not results:
        print(f'No indexed documents contain "{query}" for that filter.')
        return

    results.sort(key=lambda result: (-result["count"], result["path"].lower()))

    print(f'\nFound "{query}" in {len(results)} document(s):')

    for number, result in enumerate(results, start=1):
        print(f"\n{number}. {result['path']}")
        print(f"   Matches: {result['count']}")
        print(f"   Excerpt: {result['excerpt']}")


def main():
    if not create_database():
        return

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
                print("Choose a valid folder first.")
            else:
                index_folder(selected_folder)
        elif choice == "3":
            search_documents()
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid menu option. Please choose 1, 2, 3, or 4.")


if __name__ == "__main__":
    main()