import contextlib
import io
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import notefinder


class NoteFinderTests(unittest.TestCase):
    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.test_folder = Path(self.temp_directory.name)
        self.database_path = self.test_folder / "test_notefinder.db"

        self.database_patch = patch.object(
            notefinder, "DATABASE_FILE", self.database_path
        )
        self.database_patch.start()

    def tearDown(self):
        self.database_patch.stop()
        self.temp_directory.cleanup()

    def test_finds_text_and_markdown_files_recursively(self):
        (self.test_folder / "note.txt").write_text("Python notes", encoding="utf-8")

        subfolder = self.test_folder / "subfolder"
        subfolder.mkdir()
        (subfolder / "readme.md").write_text("# Notes", encoding="utf-8")
        (self.test_folder / "ignore.py").write_text("print('hi')", encoding="utf-8")

        found_files = notefinder.find_note_files(self.test_folder)
        found_names = {path.name for path in found_files}

        self.assertEqual(found_names, {"note.txt", "readme.md"})

    def test_make_excerpt_includes_matching_text(self):
        content = "A note about Python programming and practice."
        start = content.index("Python")
        end = start + len("Python")

        excerpt = notefinder.make_excerpt(content, start, end, context=10)

        self.assertIn("Python", excerpt)

    def test_index_folder_saves_file_contents(self):
        note_path = self.test_folder / "python.txt"
        note_path.write_text("Python is fun to learn.", encoding="utf-8")

        notefinder.create_database()

        with contextlib.redirect_stdout(io.StringIO()):
            notefinder.index_folder(self.test_folder)

        with notefinder.database_connection() as connection:
            saved_document = connection.execute(
                "SELECT path, content FROM documents"
            ).fetchone()

        self.assertIsNotNone(saved_document)
        self.assertEqual(saved_document[0], str(note_path.resolve()))
        self.assertEqual(saved_document[1], "Python is fun to learn.")

    def test_file_type_filter(self):
        self.assertTrue(
            notefinder.document_matches_filter(
                "/notes/readme.md", {"type": ".md"}
            )
        )
        self.assertFalse(
            notefinder.document_matches_filter(
                "/notes/readme.md", {"type": ".txt"}
            )
        )

    def test_folder_filter_includes_subfolders(self):
        folder = self.test_folder / "notes"
        nested_file = folder / "class" / "lesson.txt"
        nested_file.parent.mkdir(parents=True)
        nested_file.write_text("Lesson notes", encoding="utf-8")

        search_filter = {"type": "folder", "path": folder.resolve()}

        self.assertTrue(
            notefinder.document_matches_filter(
                str(nested_file.resolve()), search_filter
            )
        )

    def test_search_ranks_documents_by_match_count(self):
        notefinder.create_database()

        with notefinder.database_connection() as connection:
            connection.executemany(
                "INSERT INTO documents (path, content) VALUES (?, ?)",
                [
                    ("/notes/one.txt", "Python is useful."),
                    ("/notes/two.txt", "Python Python Python.")
                ]
            )

        captured_output = io.StringIO()
        with (
            patch("builtins.input", side_effect=["Python", "1"]),
            contextlib.redirect_stdout(captured_output)
        ):
            notefinder.search_documents()

        output = captured_output.getvalue()
        self.assertLess(output.index("/notes/two.txt"), output.index("/notes/one.txt"))


if __name__ == "__main__":
    unittest.main()