import unittest

from coursesmith.publish.units import UnitError, choose_n, size_bounds, split


class ChooseN(unittest.TestCase):
    def test_full_year(self):
        self.assertEqual(choose_n(1672, want=365), 365)

    def test_default_is_about_four_and_a_half(self):
        self.assertEqual(choose_n(60), 13)

    def test_clamped_to_what_sizes_allow(self):
        self.assertEqual(choose_n(60, want=20), 15)
        self.assertEqual(choose_n(60, want=5), 12)

    def test_no_cap_on_length(self):
        self.assertEqual(choose_n(4000), 889)
        self.assertEqual(choose_n(5 * 365 + 1), 406)

    def test_small_and_awkward_counts(self):
        self.assertEqual(size_bounds(11), (3, 5))
        self.assertEqual(choose_n(11), 3)
        self.assertEqual(choose_n(3), 1)
        self.assertEqual(choose_n(1), 1)
        self.assertEqual(size_bounds(60), (4, 5))
        with self.assertRaises(UnitError):
            choose_n(0)

    def test_every_count_splits(self):
        for n in range(1, 40):
            order = [f"e{i:02d}" for i in range(n)]
            lo, hi = size_bounds(n)
            k = choose_n(n)
            spans = split(order, {e: "a" for e in order}, {}, k, (lo, hi))
            self.assertEqual((spans[0][0], spans[-1][1], len(spans)), (0, n, k), n)
            self.assertTrue(all(lo <= b - a <= hi for a, b in spans), (n, spans))


class Split(unittest.TestCase):
    def test_sizes_and_coverage(self):
        order = [f"e{i:03d}" for i in range(23)]
        leaf = {e: "a" for e in order}
        spans = split(order, leaf, {}, 5)
        self.assertEqual(len(spans), 5)
        self.assertEqual(spans[0][0], 0)
        self.assertEqual(spans[-1][1], 23)
        for (a, b), (c, d) in zip(spans, spans[1:]):
            self.assertEqual(b, c)
        self.assertTrue(all(4 <= b - a <= 5 for a, b in spans))

    def test_never_opens_with_chapter_last_entry(self):
        # chapters of 5, 4 and 9 entries: a naive 4/5 split would strand chapter one's fifth entry
        order = [f"e{i:02d}" for i in range(18)]
        leaf = {e: ("c1" if i < 5 else "c2" if i < 9 else "c3") for i, e in enumerate(order)}
        spans = split(order, leaf, {}, 4)
        for a, b in spans:
            if a == 0:
                continue
            last_of_chapter = a + 1 == len(order) or leaf[order[a + 1]] != leaf[order[a]]
            started_before = leaf[order[a - 1]] == leaf[order[a]]
            self.assertFalse(last_of_chapter and started_before, spans)

    def test_prefers_ending_at_chapter_boundaries(self):
        order = [f"e{i:02d}" for i in range(18)]
        leaf = {e: ("c1" if i < 9 else "c2") for i, e in enumerate(order)}
        spans = split(order, leaf, {}, 4)
        self.assertIn(9, [b for _, b in spans])


if __name__ == "__main__":
    unittest.main()
