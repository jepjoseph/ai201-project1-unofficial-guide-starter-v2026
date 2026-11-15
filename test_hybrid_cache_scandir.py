import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import config
from hybrid_cache import _signature, clear_cache, get_retriever


class ScandirCacheTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.corpus_patch = patch.object(
            config, "corpus_path", return_value=self.folder
        )
        self.corpus_patch.start()
        self.addCleanup(self.corpus_patch.stop)
        clear_cache()
        self.addCleanup(clear_cache)

        (self.folder / "original.txt").write_text(
            "Initial content", encoding="utf-8"
        )

        self.build_count = 0

    def factory(self):
        self.build_count += 1
        return object()

    def lookup(self):
        return get_retriever("test_corpus", self.factory)

    def test_new_document_invalidates_cache(self):
        self.lookup()
        self.assertTrue(self.lookup()[1])

        (self.folder / "new.md").write_text(
            "New content", encoding="utf-8"
        )

        self.assertFalse(self.lookup()[1])
        self.assertEqual(self.build_count, 2)

    def test_deleted_document_invalidates_cache(self):
        self.lookup()
        self.assertTrue(self.lookup()[1])

        (self.folder / "original.txt").unlink()

        self.assertFalse(self.lookup()[1])
        self.assertEqual(self.build_count, 2)

    def test_ignored_extension_preserves_cache(self):
        self.lookup()

        (self.folder / "ignored.json").write_text(
            '{"test": true}', encoding="utf-8"
        )

        self.assertTrue(self.lookup()[1])
        self.assertEqual(self.build_count, 1)

    def test_signature_matches_original_algorithm(self):
        (self.folder / "second.md").write_text(
            "Second document", encoding="utf-8"
        )

        files = sorted(
            (
                path for path in self.folder.iterdir()
                if path.is_file()
                and path.suffix.lower() in {".txt", ".md"}
            ),
            key=lambda path: path.name,
        )

        expected = (
            str(self.folder.resolve()),
            config.CHUNK_SIZE,
            config.CHUNK_OVERLAP,
            tuple(
                (
                    path.name,
                    path.stat().st_size,
                    path.stat().st_mtime_ns,
                )
                for path in files
            ),
        )

        self.assertEqual(_signature("test_corpus"), expected)


if __name__ == "__main__":
    unittest.main()
