#!/usr/bin/env python3
import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "scripts" / "generate-maimun-archive-catalog.py"


def _load_human_size():
    spec = importlib.util.spec_from_file_location("maimun_archive_catalog", GENERATOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.human_size


class HumanSizeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.human_size = _load_human_size()

    def test_bytes_are_shown_as_integers(self) -> None:
        self.assertEqual(self.human_size(0), "0 Б")
        self.assertEqual(self.human_size(512), "512 Б")
        self.assertEqual(self.human_size(1023), "1023 Б")

    def test_kilobytes_use_one_decimal(self) -> None:
        self.assertEqual(self.human_size(1024), "1.0 КБ")
        self.assertEqual(self.human_size(1536), "1.5 КБ")

    def test_larger_units_scale_up(self) -> None:
        self.assertEqual(self.human_size(1024 ** 2), "1.0 МБ")
        self.assertEqual(self.human_size(1024 ** 3), "1.0 ГБ")
        self.assertEqual(self.human_size(1024 ** 4), "1.0 ТБ")

    def test_terabytes_do_not_overflow_to_a_missing_unit(self) -> None:
        # ТБ is the largest unit, so anything beyond it stays in ТБ.
        self.assertEqual(self.human_size(1024 ** 5), "1024.0 ТБ")


if __name__ == "__main__":
    unittest.main()
