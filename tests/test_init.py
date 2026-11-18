import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SCRIPT = """
from coursesmith import scaffold
from coursesmith.subject import load
scaffold.init("frfr-speakers", "How FRFR speakers work", ["Full-range speaker", "Loudspeaker"],
              ["Loudspeakers"], (4, 5), log=lambda *a: None)
s = load("frfr-speakers")
print(s.title, s.short, s.cfg["seeds"], s.cfg["categories"]["roots"], s.targets["per_unit"],
      s.cfg["scope"]["person_terms"], s.cfg["frame"])
try:
    scaffold.init("frfr-speakers", "x", log=lambda *a: None)
except scaffold.InitError:
    print("refused")
try:
    scaffold.init("Bad Slug", "x", log=lambda *a: None)
except scaffold.InitError:
    print("bad slug")
"""


class Init(unittest.TestCase):
    def test_init_writes_a_loadable_subject(self):
        with tempfile.TemporaryDirectory() as d:
            env = dict(os.environ, COURSESMITH_ROOT=d, PYTHONPATH=str(ROOT))
            out = subprocess.run([sys.executable, "-c", SCRIPT], env=env, capture_output=True, text=True,
                                 cwd=str(ROOT))
            self.assertEqual(out.returncode, 0, out.stderr)
            lines = out.stdout.splitlines()
            self.assertEqual(lines[0], "How FRFR speakers work frfr ['Full-range speaker', 'Loudspeaker'] "
                                       "['Category:Loudspeakers'] [4, 5] [] {}")
            self.assertEqual(lines[1:], ["refused", "bad slug"])
            self.assertTrue((Path(d) / "subjects" / "frfr-speakers" / "STATE.md").exists())


if __name__ == "__main__":
    unittest.main()
