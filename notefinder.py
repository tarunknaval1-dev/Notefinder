from pathlib import Path


def choose_folder():
    folder_input = input("Enter the folder path containing your notes: ").strip()
    folder = Path(folder_input).expanduser()

    if not folder.exists():
        print("That folder does not exist. Check the path and try again.")
        return None

    if not folder.is_dir():
        print("Please enter a folder path, not a file path.")
        return None

    print(f"Folder selected: {folder.resolve()}")
    return folder


def main():
    selected_folder = None

    while True:
        print("\n--- NoteFinder ---")
        print("1. Choose notes folder")
        print("2. Show selected folder")
        print("3. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            selected_folder = choose_folder()
        elif choice == "2":
            if selected_folder is None:
                print("Choose a folder first.")
            else:
                print(f"Selected folder: {selected_folder.resolve()}")
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Please choose 1, 2, or 3.")


if __name__ == "__main__":
    main()