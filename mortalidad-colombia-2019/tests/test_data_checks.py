import unittest
from src.data.loader import load_all_data
from src.processing.transformations import prepare, AGE_MAP, top_causes

class MortalityDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_all_data()
        cls.df = prepare(cls.data["mortality"])

    def test_records_and_year(self):
        self.assertEqual(len(self.df), 244355)
        self.assertEqual(set(self.df["AÑO"].unique()), {2019})

    def test_divipola_merge_has_department_names(self):
        self.assertEqual(self.df["DEPARTAMENTO"].isna().sum(), 0)
        self.assertEqual(self.df["MUNICIPIO"].isna().sum(), 0)

    def test_age_unknown_is_retained(self):
        self.assertIn("Edad desconocida", set(self.df["GRUPO_EDAD_LABEL"]))

    def test_top_causes_are_descending(self):
        result = top_causes(self.df)
        self.assertEqual(len(result), 10)
        self.assertTrue(result["Total"].is_monotonic_decreasing)

if __name__ == "__main__":
    unittest.main()
