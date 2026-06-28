#!/usr/bin/env python3
import csv
import json
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "scripts" / "generate-vtx-frequency-catalog.py"
DATA_FILE = ROOT / "data" / "vtx-frequency-tables.json"


class VtxFrequencyCatalogTests(unittest.TestCase):
    def test_data_file_has_required_manufacturers_and_unique_ids(self) -> None:
        self.assertTrue(DATA_FILE.exists(), "data/vtx-frequency-tables.json must exist")
        payload = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        tables = payload.get("tables", [])
        self.assertGreaterEqual(len(tables), 40)

        ids = [table["id"] for table in tables]
        self.assertEqual(len(ids), len(set(ids)), "table ids must be unique")

        manufacturers = {table["manufacturer"] for table in tables}
        for manufacturer in {"AKK", "Flywoo", "Foxeer", "Matek", "RUSHFPV", "SpeedyBee", "TBS"}:
            self.assertIn(manufacturer, manufacturers)

        manufacturer_counts = Counter(table["manufacturer"] for table in tables)
        self.assertGreaterEqual(manufacturer_counts["Foxeer"], 5)

        table_ids = {table["id"] for table in tables}
        for table_id in {
            "flywoo-goku-hm600-global",
            "flywoo-goku-vtx625-v2-global",
            "foxeer-reaper-extreme-3w-betaflight-64ch",
            "foxeer-reaper-infinity-v2-5w-80ch",
            "matek-vtx-hv-global",
            "speedybee-tx800-usa",
        }:
            self.assertIn(table_id, table_ids)

        self.assertTrue(
            any(table.get("source_image_url") for table in tables),
            "at least one table should preserve a source image/manual link",
        )

    def test_generator_validates_and_writes_expected_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)
            result = subprocess.run(
                [
                    sys.executable,
                    str(GENERATOR),
                    "--content-dir",
                    str(out_dir / "content"),
                    "--static-dir",
                    str(out_dir / "static"),
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            index = out_dir / "content" / "Частотные сетки VTX.md"
            manifest = out_dir / "static" / "manifest.json"
            csv_file = out_dir / "static" / "csv" / "akk-fx2-dominator-global.csv"

            self.assertTrue(index.exists())
            self.assertTrue(manifest.exists())
            self.assertTrue(csv_file.exists())

            index_text = index.read_text(encoding="utf-8")
            self.assertIn("## Производители", index_text)
            self.assertIn("[[Производители/AKK|AKK]]", index_text)
            self.assertIn("Foxeer", index_text)
            self.assertIn("SpeedyBee", index_text)
            self.assertIn("Изображение/мануал сетки", index_text)

            manifest_payload = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertGreaterEqual(manifest_payload["table_count"], 40)
            self.assertIn("manufacturers", manifest_payload)

            with csv_file.open(encoding="utf-8", newline="") as f:
                rows = list(csv.DictReader(f))
            self.assertTrue(rows)
            self.assertEqual({"band", "letter", "channel", "frequency_mhz"}, set(rows[0]))
            self.assertTrue(any(row["frequency_mhz"] == "5865" for row in rows))

            format_result = subprocess.run(
                [
                    "npx",
                    "prettier",
                    "--check",
                    str(out_dir / "content" / "**" / "*.md"),
                    str(out_dir / "static" / "**" / "*.json"),
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(format_result.returncode, 0, format_result.stderr + format_result.stdout)


if __name__ == "__main__":
    unittest.main()
