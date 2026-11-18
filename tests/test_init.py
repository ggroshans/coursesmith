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


class InitSources(unittest.TestCase):
    def test_template_documents_sources_and_loads_with_defaults(self):
        from coursesmith import scaffold
        from coursesmith.subject import load
        from .helpers import temp_root
        with temp_root():
            scaffold.init("sd", "System design", ["rfc>9110"], [], (3, 4), log=lambda *a: None)
            s = load("sd")
            self.assertEqual((s.cfg["course_type"], s.cfg["distribution"], s.cfg["sources"]), ("survey", "personal", []))
            self.assertEqual(s.cfg["seeds"], ["rfc>9110"])
            self.assertEqual(s.targets["per_unit"], [3, 4])
            self.assertEqual(s.cfg["verification"]["units"], [])
            text = s.yaml_path.read_text()
            for phrase in ("sources check sd", "sources discover sd", "distribution: personal", "word_ranges", "fact_caps",
                           "paragraphs: true", "units: []", "rfc>9110"):
                self.assertIn(phrase, text)

    def test_questions_flag(self):
        from coursesmith import scaffold
        from coursesmith.subject import load
        from .helpers import temp_root
        with temp_root():
            scaffold.init("sd", "System design", course_type="questions", log=lambda *a: None)
            self.assertEqual(load("sd").cfg["course_type"], "questions")

    def test_cli_flag_reaches_the_subject(self):
        from coursesmith import cli
        from coursesmith.subject import load
        from .helpers import temp_root
        with temp_root():
            cli.main(["init", "qa", "--title", "Questions", "--questions", "--seed", "rfc>9110"])
            s = load("qa")
            self.assertEqual((s.cfg["course_type"], s.cfg["seeds"]), ("questions", ["rfc>9110"]))


class StatusSources(unittest.TestCase):
    def test_status_flags_unchecked_sources(self):
        from coursesmith import status
        from .helpers import make_subject, temp_root
        with temp_root():
            wiki = make_subject("w", "slug: w\ntitle: W\n")
            self.assertIsNone(status.subject_status(wiki)["sources"])
            s = make_subject("m", "slug: m\ntitle: M\nsources:\n  - {name: r, adapter: rfc, ids: [2119]}\n")
            self.assertEqual(status.subject_status(s)["sources"], (1, False))
            lines = []
            status.show("m", log=lines.append)
            self.assertTrue(any("NOT CHECKED: run `coursesmith sources check m`" in l for l in lines))
            from coursesmith.sources import check
            from coursesmith.util import write_json
            write_json(check.ok_path(s), {"hash": check.sources_hash(s)})
            self.assertEqual(status.subject_status(s)["sources"], (1, True))
