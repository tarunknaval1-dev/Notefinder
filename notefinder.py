from pathlib import Path

SUPPORTED_EXTENSIONS = {".txt", ".md"}


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

    print(f"Folder selected: {folder.resolve()}")
    return folder


def find_note_files(folder):
    note_files = []

    try:
        for path in folder.rglob("*"):
            if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
                note_files.append(path)
    except OSError as error:
        print(f"Could not scan part of the folder: {error}")

    return sorted(note_files, key=lambda path: str(path).lower())


def scan_folder(folder):
    note_files = find_note_files(folder)

    if not note_files:
        print("No .txt or .md files found.")
        return

    print(f"\nFound {len(note_files)} note file(s):")

    for path in note_files:
        print(f"- {path.relative_to(folder)}")


def main():
    selected_folder = None

    while True:
        print("\n--- NoteFinder ---")
        print("1. Choose notes folder")
        print("2. Scan selected folder")
        print("3. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            selected_folder = choose_folder()

        elif choice == "2":
            if selected_folder is None:
                print("Choose a folder first.")
            else:
                scan_folder(selected_folder)

        elif choice == "3":
            print("Goodbye!")
            break

        else:
            print("Please choose 1, 2, or 3.")


if __name__ == "__main__":
    main()