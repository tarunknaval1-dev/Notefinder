# NoteFinder

NoteFinder is a small Python command-line app for finding information in local notes.

## Current feature

- Choose a folder that contains notes
- Choose a folder containing notes
- Find `.txt` and `.md` files, including in subfolders 
- Store note file paths and contents in a local SQLite database
- Index and refresh `.txt` and `.md` documents in SQLite
- Search indexed notes by word or phrase
- Rank search results by match count
- Show a text excerpt around the first match
- Filter search results by file type or folder
- Validates folder paths and search/filter choices
- Shows helpful messages for unreadable files and database errors

## Run the app

Requires Python 3.

```bash
python notefinder.py