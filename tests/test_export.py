import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SCRIPT = r"""
import json
from coursesmith import config
from coursesmith.extract import sentences as SN
from coursesmith.publish import export
from coursesmith.subject import load
from coursesmith.util import write_json, write_jsonl

d = config.SUBJECTS / "tiny"
d.mkdir(parents=True)
(d / "subject.yaml").write_text("title: Tiny\nshort: tiny\n")
s1, s2 = SN.sent_id("Speaker", "A speaker turns signals into sound."), "frozen000001"
e = lambda i, t, sid: {"id": i, "title": t, "kind": "Concept", "weight": "Major", "level": "Foundational",
                       "part": "Basics", "chapter": "Sound", "selected": True, "score": 3,
                       "definition": {"text": t, "sent_ids": [sid]}, "facts": [{"text": "x", "sent_ids": [sid]}],
                       "sources": [{"title": "Speaker", "url": "https://en.wikipedia.org/wiki/Speaker",
                                    "revid": 7, "sent_ids": [sid]}]}
write_jsonl(d / "entries" / "sound.jsonl", [e("tiny-a", "Speaker", s1), e("tiny-b", "Driver", s2)])
write_json(d / "order.json", {"order": ["tiny-a", "tiny-b"], "locked": True})
write_json(d / "output" / "prose.json", {"entries": {"tiny-b": {"title": "Driver", "text": "Builds on {{ref:tiny-a}}."}},
                                         "openers": {}, "reviews": {}, "glossary": {}, "questions": {}})
write_jsonl(d / "sentences.jsonl", [{"sent_id": s2, "title": "Driver", "url": "u", "revid": 8, "section": "",
                                      "sentence": "A driver moves air."}])
db = SN.connect()
db.execute("INSERT INTO pages (title, url, revid) VALUES ('Speaker', 'https://en.wikipedia.org/wiki/Speaker', 7)")
db.execute("INSERT INTO sentences (sent_id, title, revid, section, idx, sentence) VALUES (?, 'Speaker', 7, '', 0, "
           "'A speaker turns signals into sound.')", (s1,))
db.commit()
doc = export.export(load("tiny"), strict=True, log=lambda *a: None)
print(json.dumps({"ids": [x["id"] for x in doc["entries"]], "plain": doc["entries"][1]["text_plain"],
                  "raw": doc["entries"][1]["text"], "sent": sorted(doc["sentences"]),
                  "permalink": doc["license"]["pages"]["Speaker"]["permalink"],
                  "internal": [k for k in ("selected", "score") if k in doc["entries"][0]],
                  "outline": [n["id"] for n in doc["outline"]]}))
"""


class Export(unittest.TestCase):
    def test_export_bundles_prose_and_sentences(self):
        with tempfile.TemporaryDirectory() as d:
            env = dict(os.environ, COURSESMITH_ROOT=d, PYTHONPATH=str(ROOT))
            out = subprocess.run([sys.executable, "-c", SCRIPT], env=env, capture_output=True, text=True,
                                 cwd=str(ROOT))
            self.assertEqual(out.returncode, 0, out.stderr)
            r = json.loads(out.stdout.strip().splitlines()[-1])
            self.assertEqual(r["ids"], ["tiny-a", "tiny-b"])
            self.assertEqual(r["plain"], "Builds on Speaker.")
            self.assertEqual(r["raw"], "Builds on {{ref:tiny-a}}.")
            self.assertEqual(len(r["sent"]), 2)
            self.assertIn("oldid=7", r["permalink"])
            self.assertEqual(r["internal"], [])
            self.assertEqual(len(r["outline"]), 2)


if __name__ == "__main__":
    unittest.main()
