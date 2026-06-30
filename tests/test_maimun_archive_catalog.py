#!/usr/bin/env python3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "scripts" / "generate-maimun-archive-catalog.py"
SOURCE_ARCHIVE = Path("/Users/sergejsavcuk/Desktop/I.P.D/!FPV")


class MaimunArchiveCatalogTests(unittest.TestCase):
    def test_generator_indexes_fpv_archive_without_copying_raw_files(self) -> None:
        self.assertTrue(SOURCE_ARCHIVE.exists(), "source !FPV archive must exist")
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "content"
            result = subprocess.run(
                [
                    sys.executable,
                    str(GENERATOR),
                    "--source",
                    str(SOURCE_ARCHIVE),
                    "--content-dir",
                    str(out_dir),
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            index = out_dir / "База данных Маймуна.md"
            self.assertTrue(index.exists())

            text = index.read_text(encoding="utf-8")
            self.assertIn("# База данных Маймуна", text)
            self.assertIn("Файлов в исходной папке: **195**", text)
            self.assertIn("Общий размер исходной папки:", text)
            self.assertIn("3D", text)
            self.assertIn("НСУ", text)
            self.assertIn("сырого архива", text)
            self.assertIn("obsidian://open?vault=I.P.D&file=%21FPV%2F", text)
            self.assertIn("[EXCERA-8100\\_ТФ.stl](<obsidian://open?vault=I.P.D&file=%21FPV%2F3D%2F", text)
            self.assertNotIn("](<file://", text)

            generated_files = {path.suffix.lower() for path in out_dir.rglob("*") if path.is_file()}
            self.assertEqual({".md"}, generated_files)


if __name__ == "__main__":
    unittest.main()
