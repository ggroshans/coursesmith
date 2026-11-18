import json
import unittest
from datetime import datetime, timedelta, timezone

import yaml

from coursesmith import config
from coursesmith.sources import check as C
from coursesmith.sources import discover as D
from coursesmith.sources.registry import Registry

from .fakes import FIXTURES, FakeHTTP
from .helpers import make_subject, temp_root

GH = FIXTURES / "github"
SHA = "ae9bbd7b02d90b9866215de185217d33f39ab733"
RAW = f"https://raw.githubusercontent.com/donnemartin/system-design-primer/{SHA}"
API = "https://api.github.com"
NOW = datetime(2026, 11, 18, tzinfo=timezone.utc)


def http(extra=None):
    m = {
        f"{API}/repos/donnemartin/system-design-primer/commits/master": GH / "primer.commit.json",
        f"{API}/repos/donnemartin/system-design-primer/license?ref={SHA}": GH / "primer.license.json",
        f"{API}/repos/donnemartin/system-design-primer/git/trees/{SHA}?recursive=1": GH / "primer.tree.json",
    }
    m.update(extra or {})
    return FakeHTTP(m)


YAML_FLOW = """slug: sd
title: System Design
# sources are vetted before any crawl
sources:
  - {name: primer, adapter: github, repo: donnemartin/system-design-primer, ref: master, include: ["README.md"], tier: curated, license: {name: "CC BY 4.0"}}
seeds: ["gh>donnemartin/system-design-primer/README.md"]
"""
YAML_BLOCK = """slug: sd
title: System Design
sources:
  - name: primer   # the curated primer
    adapter: github
    repo: donnemartin/system-design-primer
    include: ["README.md"]
    tier: curated
    license: {name: "CC BY 4.0"}
seeds: []
"""


def registry_for(subj, h=None):
    return Registry.from_subject(subj, http=h or http())


class ScoreTest(unittest.TestCase):
    def test_parts(self):
        c = {"adapter": "github", "evidence": {"stars": 99999, "contributors": 240, "license_spdx": "CC-BY-4.0",
                                                "pushed_at": (NOW - timedelta(days=30)).isoformat(),
                                                "owner_type": "Organization"}}
        s, p = D.score(c, now=NOW)
        self.assertEqual(p["license"], 3)
        self.assertEqual(p["domain"], 1)
        self.assertEqual(p["stars"], 5.0)
        self.assertEqual(p["contributors"], 2)
        self.assertEqual((p["recent"], p["maintainer"], p["archived"]), (1, 1, 0))
        self.assertEqual(s, 13.0)

    def test_restricted_license_scores_lower_and_no_license_zero(self):
        lic = lambda ev: D.score({"adapter": "github", "evidence": ev})[1]["license"]
        self.assertEqual(lic({"license_spdx": "CC-BY-4.0"}), 3)
        self.assertEqual(lic({"license_spdx": "CC-BY-NC-ND-4.0"}), 1)
        # a license file GitHub cannot match (the System Design Primer's) is worth reading, so it earns a point
        self.assertEqual(lic({"license_spdx": "NOASSERTION"}), 1)
        self.assertEqual(lic({}), 0)

    def test_domain_classes(self):
        self.assertEqual(D.domain_class({"adapter": "rfc"}), "standards")
        self.assertEqual(D.domain_class({"adapter": "paper"}), "academic")
        self.assertEqual(D.domain_class({"adapter": "github"}), "community")
        self.assertEqual(D.domain_class({"adapter": "html", "domain_class": "official"}), "official")

    def test_archived_and_old(self):
        s, p = D.score({"adapter": "github", "evidence": {"archived": True, "pushed_at": "2019-01-01T00:00:00Z"}}, now=NOW)
        self.assertEqual((p["archived"], p["recent"]), (-3, 0))
        self.assertLess(s, 0)


class MergeTest(unittest.TestCase):
    def test_human_decisions_survive_new_evidence(self):
        old = [{"id": "gh:a/b", "status": "accept", "note": "yes", "evidence": {"stars": 1}}]
        new = [{"id": "gh:a/b", "evidence": {"stars": 9}}, {"id": "gh:c/d", "evidence": {}}]
        out = {c["id"]: c for c in D.merge_candidates(old, new)}
        self.assertEqual((out["gh:a/b"]["status"], out["gh:a/b"]["note"]), ("accept", "yes"))
        self.assertEqual(out["gh:a/b"]["evidence"]["stars"], 9)
        self.assertEqual(out["gh:c/d"]["status"], "candidate")


class DiscoverRunTest(unittest.TestCase):
    GLOBAL = """repos:
  - {repo: donnemartin/system-design-primer, tier: curated, class: community, topics: [system design],
     license: {spdx: CC-BY-4.0, class: cc-by, verified: 2026-11-18}}
  - {repo: other/unrelated, tier: curated, topics: [knitting]}
"""

    def test_registry_only_run(self):
        with temp_root() as root:
            (root / "sources").mkdir()
            config.REGISTRY_PATH.write_text(self.GLOBAL)
            subj = make_subject("sd", "slug: sd\ntitle: System Design\n")
            out = D.run(subj, network=False, log=lambda *a: None)
            self.assertEqual([c["id"] for c in out], ["gh:donnemartin/system-design-primer"])
            c = out[0]
            self.assertEqual((c["origin"], c["status"], c["suggested_tier"]), ("registry", "candidate", "curated"))
            self.assertEqual(c["license_seen"], "CC-BY-4.0")
            self.assertEqual(c["subject_yaml"]["adapter"], "github")
            self.assertEqual(c["subject_yaml"]["repo"], "donnemartin/system-design-primer")
            self.assertTrue(D.candidates_path(subj).exists())

    def test_rerun_keeps_status(self):
        with temp_root() as root:
            (root / "sources").mkdir()
            config.REGISTRY_PATH.write_text(self.GLOBAL)
            subj = make_subject("sd", "slug: sd\ntitle: System Design\n")
            D.run(subj, network=False, log=lambda *a: None)
            cands = yaml.safe_load(D.candidates_path(subj).read_text())
            cands[0]["status"], cands[0]["note"] = "accept", "the question list"
            D.write_candidates(subj, cands)
            again = D.run(subj, network=False, log=lambda *a: None)
            self.assertEqual((again[0]["status"], again[0]["note"]), ("accept", "the question list"))

    def test_network_run_scores_and_adds_contributors(self):
        with temp_root():
            subj = make_subject("sd", "slug: sd\ntitle: System Design\n")
            search = {"items": [{"full_name": "a/b", "name": "b", "html_url": "https://github.com/a/b", "description": "d",
                                 "stargazers_count": 900, "forks_count": 5, "pushed_at": (datetime.now(timezone.utc)).isoformat(),
                                 "license": {"spdx_id": "CC-BY-4.0"}, "topics": [], "owner": {"type": "Organization"},
                                 "default_branch": "main"}]}
            h = FakeHTTP({f"{API}/search/repositories?q=System%20Design%20stars:>200&sort=stars&order=desc&per_page=20": json.dumps(search),
                          "https://datatracker.ietf.org/api/v1/doc/document/": json.dumps({"objects": []}),
                          "https://api.openalex.org/works": json.dumps({"results": []})})
            h.get_orig = h.get

            def get(url, params=None, **kw):
                if url.endswith("/repos/a/b/contributors") or "/repos/a/b/contributors" in url:
                    return ("[{}]", {"link": '<x?page=61>; rel="last"'}) if kw.get("want_headers") else "[{}]"
                return h.get_orig(url, params, **kw)
            h.get = get
            reg = Registry.from_subject(subj, http=h)
            out = D.run(subj, registry=reg, log=lambda *a: None)
            c = next(c for c in out if c["id"] == "gh:a/b")
            self.assertEqual(c["origin"], "api")
            self.assertEqual(c["evidence"]["contributors"], 61)
            self.assertGreater(c["score"], 5)
            self.assertEqual(c["subject_yaml"]["repo"], "a/b")

    def test_a_failing_search_is_logged_not_fatal(self):
        with temp_root():
            subj = make_subject("sd", "slug: sd\ntitle: System Design\n")

            class Boom(FakeHTTP):
                def get(self, url, params=None, **kw):
                    from coursesmith.sources.base import SourceError
                    raise SourceError("rate limited")
            logs = []
            D.run(subj, registry=Registry.from_subject(subj, http=Boom()), log=logs.append)
            self.assertTrue(any("github search failed: rate limited" in l for l in logs))


class SessionTest(unittest.TestCase):
    def found(self, subj, items):
        p = D.found_path(subj)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(yaml.safe_dump(items))

    def test_merge_accepts_complete_entries_and_rejects_the_rest(self):
        with temp_root():
            subj = make_subject("sd", "slug: sd\ntitle: System Design\n")
            self.found(subj, [
                {"url": "https://github.com/x/y", "adapter": "github", "repo": "x/y", "title": "y", "why": "named maintainer, widely cited",
                 "license_seen": "CC BY 4.0", "license_url": "https://github.com/x/y/blob/main/LICENSE", "updated": "2026-10-01",
                 "domain_class": "official", "nc_nd": False},
                {"url": "https://blog.example/post", "adapter": "html", "title": "a blog post", "why": "popular"},
            ])
            logs = []
            out = D.merge(subj, log=logs.append)
            self.assertEqual([c["id"] for c in out], ["gh:x/y"])
            c = out[0]
            self.assertEqual((c["origin"], c["suggested_tier"], c["license_seen"]), ("session", "official", "CC BY 4.0"))
            self.assertEqual(c["evidence"]["license_url"], "https://github.com/x/y/blob/main/LICENSE")
            self.assertTrue(any("rejected" in l and "license_seen, license_url" in l for l in logs))

    def test_merge_without_a_found_file_explains(self):
        with temp_root():
            subj = make_subject("sd", "slug: sd\ntitle: System Design\n")
            with self.assertRaises(SystemExit) as cm:
                D.merge(subj)
            self.assertIn("run the search session first", str(cm.exception))

    def test_packet_lists_subject_chapters_sources_and_candidates(self):
        with temp_root():
            subj = make_subject("sd", YAML_BLOCK + "description: Interview prep.\n")
            subj.frame_path.write_text("parts:\n  - {key: q, title: Questions, question: true, chapters: [{key: c1, title: URL shortener}]}\n")
            D.write_candidates(subj, [{"id": "gh:a/b", "title": "b", "score": 7.5, "license_seen": "MIT"}])
            text = D.packet(subj, log=lambda *a: None).read_text()
            self.assertIn("Interview prep.", text)
            self.assertIn("**Questions** (each chapter is one question): URL shortener", text)
            self.assertIn("primer: github donnemartin/system-design-primer", text)
            self.assertIn("gh:a/b (score 7.5)", text)
            self.assertIn("subjects/sd/work/sources/found.yaml", text)


class CheckTest(unittest.TestCase):
    def test_passing_check_writes_a_stamp_that_gates_crawl(self):
        with temp_root():
            subj = make_subject("sd", YAML_FLOW)
            self.assertEqual(C.run(subj, registry=registry_for(subj), log=lambda *a: None), [])
            self.assertTrue(C.ok_path(subj).exists())
            C.require_ok(subj)  # passes
            self.assertIn("| primer | github | curated | CC BY 4.0 | cc-by |", (subj.reports_dir / "sources.md").read_text())

    def test_changing_sources_invalidates_the_stamp(self):
        with temp_root():
            subj = make_subject("sd", YAML_FLOW)
            C.run(subj, registry=registry_for(subj), log=lambda *a: None)
            changed = make_subject("sd", YAML_FLOW.replace('include: ["README.md"]', 'include: ["**/*.md"]'))
            with self.assertRaises(SystemExit) as cm:
                C.require_ok(changed)
            self.assertIn("have not passed", str(cm.exception))

    def test_wikipedia_only_subject_needs_no_check(self):
        with temp_root():
            C.require_ok(make_subject("w", "slug: w\ntitle: W\n"))

    def test_license_mismatch_fails_and_removes_the_stamp(self):
        with temp_root():
            subj = make_subject("sd", YAML_FLOW)
            C.run(subj, registry=registry_for(subj), log=lambda *a: None)
            bad = make_subject("sd", YAML_FLOW.replace('"CC BY 4.0"', "MIT"))
            logs = []
            probs = C.run(bad, registry=registry_for(bad), log=logs.append)
            self.assertTrue(any("declares MIT" in p for p in probs))
            self.assertFalse(C.ok_path(bad).exists())

    def test_missing_license_declaration(self):
        with temp_root():
            subj = make_subject("sd", YAML_FLOW.replace(', license: {name: "CC BY 4.0"}', ""))
            probs = C.run(subj, registry=registry_for(subj), log=lambda *a: None)
            self.assertTrue(any("declare its license" in p for p in probs))

    def test_public_distribution_rejects_restricted_license(self):
        with temp_root():
            subj = make_subject("sd", (YAML_FLOW + "distribution: public\n").replace('"CC BY 4.0"', '"CC BY-NC-ND 4.0"'))
            probs = C.run(subj, registry=registry_for(subj), log=lambda *a: None)
            self.assertTrue(any("does not allow public distribution" in p for p in probs))

    def test_bad_distribution_value_and_unknown_tier(self):
        with temp_root():
            subj = make_subject("sd", (YAML_FLOW + "distribution: world\n").replace("tier: curated", "tier: gold"))
            probs = C.run(subj, registry=registry_for(subj), log=lambda *a: None)
            self.assertTrue(any("distribution must be" in p for p in probs))
            self.assertTrue(any("tier 'gold'" in p for p in probs))

    def test_seed_outside_the_allowlist(self):
        with temp_root():
            subj = make_subject("sd", YAML_FLOW.replace("README.md\"]\nseeds", "README.md\"]\nseeds").replace(
                'seeds: ["gh>donnemartin/system-design-primer/README.md"]',
                'seeds: ["gh>donnemartin/system-design-primer/README.md", "gh>other/repo/x.md"]'))
            probs = C.run(subj, registry=registry_for(subj), log=lambda *a: None)
            self.assertTrue(any("seed gh>other/repo/x.md" in p for p in probs))

    def test_unknown_adapter_is_a_problem_not_a_crash(self):
        with temp_root():
            subj = make_subject("sd", "slug: sd\nsources:\n  - {name: x, adapter: nope}\n")
            probs = C.run(subj, log=lambda *a: None)
            self.assertTrue(any("unknown source adapter 'nope'" in p for p in probs))

    def test_branch_ref_note_and_fix(self):
        with temp_root():
            subj = make_subject("sd", YAML_FLOW)
            logs = []
            C.run(subj, registry=registry_for(subj), log=logs.append)
            self.assertTrue(any("ref: master" in l or f"ref: {SHA}" in l for l in logs))
            C.run(subj, fix_refs=True, registry=registry_for(subj), log=lambda *a: None)
            text = subj.yaml_path.read_text()
            self.assertIn(f"ref: {SHA}", text)
            self.assertNotIn("ref: master", text)
            self.assertIn("# sources are vetted before any crawl", text)  # comments survive
            from coursesmith.subject import load
            C.require_ok(load("sd"))  # the stamp covers the pinned sources block


class SetRefTest(unittest.TestCase):
    def test_flow_replace_and_insert(self):
        t = "sources:\n  - {name: a, repo: o/r, ref: master, tier: curated}\n  - {name: b, repo: p/q}\n"
        out = C.set_ref(t, "o/r", "abc")
        self.assertIn("{name: a, repo: o/r, ref: abc, tier: curated}", out)
        out = C.set_ref(t, "p/q", "def")
        self.assertIn("{name: b, repo: p/q, ref: def}", out)
        self.assertIn("ref: master", out)

    def test_block_replace_and_insert(self):
        t = ("# top\nsources:\n  - name: a\n    repo: o/r   # the repo\n    ref: master\n    tier: curated\n"
             "  - name: b\n    repo: p/q\n    include: [README.md]\nseeds: []\n")
        out = C.set_ref(t, "o/r", "abc")
        self.assertIn("    ref: abc\n    tier: curated", out)
        self.assertIn("# the repo", out)
        out2 = C.set_ref(t, "p/q", "def")
        self.assertIn("    repo: p/q\n    ref: def\n    include: [README.md]", out2)
        self.assertEqual(yaml.safe_load(out2)["sources"][1]["ref"], "def")
        self.assertEqual(yaml.safe_load(out2)["sources"][0]["ref"], "master")  # the other entry is untouched

    def test_dash_on_the_repo_line(self):
        t = "sources:\n  - repo: o/r\n    name: a\n"
        out = C.set_ref(t, "o/r", "abc")
        self.assertEqual(yaml.safe_load(out)["sources"][0], {"repo": "o/r", "name": "a", "ref": "abc"})

    def test_ref_listed_before_repo_is_replaced_not_duplicated(self):
        t = "sources:\n  - name: a\n    ref: master\n    repo: o/r\n    tier: curated\nseeds: []\n"
        out = C.set_ref(t, "o/r", "abc")
        self.assertEqual(yaml.safe_load(out)["sources"][0]["ref"], "abc")
        self.assertEqual(out.count("ref:"), 1)

    def test_nested_lists_do_not_end_the_entry_early(self):
        t = "sources:\n  - name: a\n    repo: o/r\n    include:\n      - README.md\n      - docs/*.md\n    ref: master\nseeds: []\n"
        out = C.set_ref(t, "o/r", "abc")
        self.assertEqual(yaml.safe_load(out)["sources"][0]["ref"], "abc")
        self.assertEqual(out.count("ref:"), 1)

    def test_unknown_repo(self):
        self.assertIsNone(C.set_ref("sources: []\n", "o/r", "abc"))


if __name__ == "__main__":
    unittest.main()


class RelevanceTest(unittest.TestCase):
    PRIMER = {"title": "system-design-primer", "repo": "donnemartin/system-design-primer",
              "snippet": "Learn how to design large-scale systems. Prep for the system design interview.",
              "evidence": {"stars": 378396, "topics": ["interview"]}}
    CSS = {"title": "css", "repo": "primer/css", "snippet": "The CSS implementation of GitHub's Primer Design System",
           "evidence": {"stars": 13060, "owner_type": "Organization", "license_spdx": "MIT"}}

    def test_relevant_beats_famous(self):
        qs = ["system design interview", "system design primer"]
        self.assertGreater(D.relevance(self.PRIMER, qs), D.relevance(self.CSS, qs) + 1)
        sp, parts = D.score(self.PRIMER, queries=qs)
        sc, _ = D.score(self.CSS, queries=qs)
        self.assertGreater(sp, sc)
        self.assertIn("relevance", parts)

    def test_no_queries_means_no_relevance_part(self):
        self.assertNotIn("relevance", D.score(self.PRIMER)[1])

    def test_phrase_counts_and_stopwords_do_not(self):
        c = {"title": "x", "snippet": "a design for the system"}
        self.assertEqual(D.relevance(c, ["the for and"]), 0)
        self.assertLess(D.relevance(c, ["system design"]), D.relevance({"title": "system design"}, ["system design"]))

    def test_papers_are_opt_in(self):
        self.assertNotIn("paper", D.SEARCHERS)
