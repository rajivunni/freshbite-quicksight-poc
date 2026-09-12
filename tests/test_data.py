"""Offline fixture/source checks. No AWS or database access is performed."""

import ast
import csv
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


def rows(name):
    with (ROOT / "data" / name).open(newline="") as stream:
        return list(csv.DictReader(stream))


class DataChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.franchises = rows("dim_franchises.csv")
        cls.locations = rows("dim_locations.csv")
        cls.products = rows("dim_products.csv")
        cls.sales = rows("fact_daily_sales.csv")
        cls.feedback = rows("fact_customer_feedback.csv")
        cls.permissions = rows("rls_user_permissions.csv")

    def test_fixture_counts(self):
        self.assertEqual(
            list(map(len, (self.franchises, self.locations, self.products,
                           self.sales, self.feedback, self.permissions))),
            [10, 50, 20, 103947, 27278, 11],
        )

    def test_unique_dimension_keys(self):
        for data, key in ((self.franchises, "franchise_id"),
                          (self.locations, "location_id"),
                          (self.products, "product_id")):
            self.assertEqual(len(data), len({row[key] for row in data}))

    def test_foreign_keys(self):
        franchises = {row["franchise_id"] for row in self.franchises}
        locations = {row["location_id"] for row in self.locations}
        products = {row["product_id"] for row in self.products}
        self.assertTrue(all(row["franchise_id"] in franchises for row in self.locations))
        self.assertTrue(all(row["location_id"] in locations and
                            row["product_id"] in products for row in self.sales))
        self.assertTrue(all(row["location_id"] in locations for row in self.feedback))
        self.assertEqual(
            {row["franchise_id"] for row in self.permissions}, franchises | {"ALL"}
        )

    def test_sales_grain_and_date_range(self):
        keys = {(row["sale_date"], row["location_id"], row["product_id"])
                for row in self.sales}
        self.assertEqual(len(keys), len(self.sales))
        dates = {row["sale_date"] for row in self.sales}
        self.assertEqual((min(dates), max(dates)), ("2026-01-01", "2026-06-30"))

    def test_generator_parses(self):
        ast.parse((ROOT / "scripts" / "generate_mock_data.py").read_text())

    def test_documented_parameter_and_permission_columns(self):
        readme = (ROOT / "README.md").read_text()
        schema = (ROOT / "sql" / "01_create_tables.sql").read_text()
        views = (ROOT / "sql" / "03_create_views.sql").read_text()
        self.assertIn("AdminUserPassword", readme)
        self.assertIn("user_email", schema)
        self.assertIn("SELECT user_email AS UserName, franchise_id", views)
        self.assertNotIn("SELECT owner_email AS UserName", views)


if __name__ == "__main__":
    unittest.main()
