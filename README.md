# NoteFinder

NoteFinder is a Python command-line app for searching local text and Markdown notes. It saves indexed file paths and contents in a local SQLite database.

## Features

- Scan folders and subfolders for `.txt` and `.md` files
- Index and refresh notes in SQLite
- Search for words or phrases without case sensitivity
- Rank results by match count
- Show an excerpt around the first match
- Filter results by file type or folder
- Show helpful messages for common errors

## Requirements

- Python 3

NoteFinder uses only Python's standard library. No extra packages are required.

## Run the app

Open a terminal in the project folder and run:

```bash
python notefinder.py
```

Choose a notes folder, index it, then search. You can try the included files in the `samples` folder.

## Run the tests

From the project folder, run:

```bash
python -m unittest discover -s tests -v
```

## Local database and privacy

NoteFinder creates `notefinder.db` beside `notefinder.py`. It contains copies of indexed note contents. The database is listed in `.gitignore` so it won't be included in your Git commits.

Re-index a folder after changing notes so searches use the updated content.

## Limitations

- Supports `.txt` and `.md` files only.
- Searches for the words or phrases you enter; it does not find related terms.
- Re-indexing updates found files but does not remove database entries for files that deleted or moved.
- This version runs in the terminal and has no graphical interface.

## Project structure

```text
notefinder/
├── notefinder.py
├── tests/
│   └── tests_notefinder.py
├── samples/
│   ├── python-notes.md
│   └── study-notes.txt
├── .gitignore
└── README.md
```

## Author

Tarun kumar Naval