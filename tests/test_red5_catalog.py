import hashlib
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "generate-red5-catalog.py"


class Red5CatalogTest(unittest.TestCase):
    def test_generates_catalog_with_direct_download_links(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            archive = temp / "RED5.zip"
            output = temp / "content" / "RED5"

            with zipfile.ZipFile(archive, "w") as zip_file:
                zip_file.writestr("RED5/history.txt", "RED5 history\n")
                zip_file.writestr(
                    "RED5/RC5/RX/LR1121/R5 RC5 receiver.bin", b"receiver"
                )
                zip_file.writestr(
                    "RED5/RC6/TX/SX1280/R5+RC6 transmitter.bin", b"transmitter"
                )

            subprocess.run(
                [
                    "python3",
                    str(SCRIPT),
                    "--archive",
                    str(archive),
                    "--output",
                    str(output),
                    "--updated",
                    "2026-07-31",
                ],
                cwd=ROOT,
                check=True,
            )

            main_page = (output / "RED5.md").read_text(encoding="utf-8")
            root_index = (output / "Индекс.md").read_text(encoding="utf-8")
            receiver_index = (
                output / "RC5" / "RX" / "LR1121" / "Индекс.md"
            ).read_text(encoding="utf-8")
            manifest = (output / "Манифест файлов.md").read_text(encoding="utf-8")

            expected_sha = hashlib.sha256(archive.read_bytes()).hexdigest()
            self.assertIn(expected_sha, main_page)
            self.assertIn(
                "https://app.gorizontvverh.ru/downloads/RED5/RED5.zip", main_page
            )
            self.assertIn("[RC5](./RC5/Индекс.md)", main_page)
            self.assertIn("[[06_Прошивки_и_настройки/Прошивки ELRS/RED5/RC5/Индекс|RC5]]", root_index)
            self.assertIn(
                "https://app.gorizontvverh.ru/downloads/RED5/RC5/RX/LR1121/R5%20RC5%20receiver.bin",
                receiver_index,
            )
            self.assertIn(
                "https://app.gorizontvverh.ru/downloads/RED5/RC6/TX/SX1280/R5%2BRC6%20transmitter.bin",
                manifest,
            )
            self.assertIn("3 файла", main_page)
            self.assertFalse(list(output.rglob("*.bin")))


if __name__ == "__main__":
    unittest.main()
