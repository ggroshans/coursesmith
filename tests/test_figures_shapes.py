import unittest

from PIL import Image

from coursesmith.publish import figures as F


def flow(src, **kw):
    return {"type": "flow", "mermaid": src, "caption": "c", "sent_ids": ["s"], **kw}


class ParseTest(unittest.TestCase):
    def test_cylinder_is_a_database(self):
        horiz, nodes, edges = F.parse_mermaid("flowchart LR\n A[App] --> B[(Orders DB)]")
        self.assertTrue(horiz)
        self.assertEqual(nodes["B"]["kind"], "db")
        self.assertEqual(nodes["B"]["label"], "Orders DB")
        self.assertEqual(nodes["A"]["kind"], "box")
        self.assertEqual(len(edges), 1)

    def test_other_shapes_are_unchanged(self):
        _, nodes, _ = F.parse_mermaid("flowchart TD\n A([stadium]) --> B[[sub]] --> C((circle)) --> D{ok?} --> E(round) --> F[plain]")
        self.assertEqual({k: v["kind"] for k, v in nodes.items()},
                         {"A": "round", "B": "box", "C": "round", "D": "decision", "E": "round", "F": "box"})
        self.assertEqual(nodes["B"]["label"], "sub")

    def test_edge_text_form(self):
        _, nodes, edges = F.parse_mermaid("flowchart TD\n A -- reads from --> B\n B -->|writes| C\n C --- D")
        self.assertEqual([(e["a"], e["b"], e["label"]) for e in edges],
                         [("A", "B", "reads from"), ("B", "C", "writes"), ("C", "D", "")])
        self.assertFalse(edges[2]["arrow"])

    def test_plain_arrows_with_spaces_are_not_mistaken_for_edge_text(self):
        _, _, edges = F.parse_mermaid("flowchart TD\n A --> B --> C")
        self.assertEqual([(e["a"], e["b"], e["label"]) for e in edges], [("A", "B", ""), ("B", "C", "")])

    def test_subgraph_groups_one_level(self):
        src = ("flowchart TD\n Client --> LB\n subgraph Web tier\n  LB --> App1\n  LB --> App2\n end\n"
               " subgraph data[Data tier]\n  App1 --> DB[(Primary)]\n  subgraph inner\n   Cache[Cache]\n  end\n end\n App2 --> DB")
        _, nodes, edges = F.parse_mermaid(src)
        self.assertIsNone(nodes["Client"]["group"])
        self.assertEqual(nodes["LB"]["group"], None)  # first seen outside the block, so it stays out
        self.assertEqual(nodes["App1"]["group"], "Web tier")
        self.assertEqual(nodes["App2"]["group"], "Web tier")
        self.assertEqual(nodes["DB"]["group"], "Data tier")
        self.assertEqual(nodes["Cache"]["group"], "Data tier")  # a nested subgraph is flattened into the outer one
        self.assertEqual(len(edges), 5)

    def test_old_diagrams_have_no_groups(self):
        _, nodes, _ = F.parse_mermaid("flowchart TD\n A --> B")
        self.assertTrue(all(n["group"] is None for n in nodes.values()))

    def test_still_rejects_other_diagram_types(self):
        with self.assertRaises(ValueError):
            F.parse_mermaid("sequenceDiagram\n A->>B: hi")


class DrawTest(unittest.TestCase):
    def test_database_and_groups_draw(self):
        src = ("flowchart TD\n Client[Client] --> LB[Load balancer]\n subgraph Web tier\n  App1[App 1]\n  App2[App 2]\n end\n"
               " LB --> App1\n LB --> App2\n App1 --> DB[(Primary DB)]\n App2 --> DB\n DB -.-> R[(Replica)]")
        data = F.png(flow(src))
        self.assertTrue(data.startswith(b"\x89PNG"))
        self.assertEqual(F.validate(flow(src)), [])

    def test_group_boxes_change_the_picture(self):
        a = "flowchart TD\n A --> B\n B --> C"
        b = "flowchart TD\n A --> B\n subgraph G\n  B --> C\n end"
        import io
        ia, ib = (Image.open(io.BytesIO(F.png(flow(s)))) for s in (a, b))
        self.assertNotEqual(ia.tobytes(), ib.tobytes())

    def test_figure_numbers_in_labels_include_database_labels(self):
        nums = F.numbers(flow("flowchart LR\n A[App] --> B[(Shard 16)]"))
        self.assertIn(16.0, nums)

    def test_bad_flow_is_reported_by_validate(self):
        probs = F.validate(flow("sequenceDiagram\n A->>B: x"))
        self.assertTrue(any("does not draw" in p for p in probs))


class SinkTest(unittest.TestCase):
    class Book:
        def __init__(self):
            self.items = []

        def add(self, *a):
            self.items.append(a)

    def test_a_failing_figure_is_recorded_not_raised(self):
        F.ERRORS.clear()
        book = self.Book()
        sink = F.Sink(book)
        bad, good = flow("sequenceDiagram\n A->>B: x"), flow("flowchart TD\n A --> B")
        self.assertIsNone(sink(bad, "e1", 0))
        self.assertTrue(sink(good, "e1", 1).startswith("figures/e1-2"))
        self.assertEqual(len(book.items), 1)
        self.assertEqual(F.ERRORS[0][:2], ("e1", 1))
        html = F.figures_html([bad, good], sink, "e1")
        self.assertEqual(html.count("<figure"), 1)  # the bad one is simply left out
        F.ERRORS.clear()


if __name__ == "__main__":
    unittest.main()
