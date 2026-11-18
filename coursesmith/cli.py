"""coursesmith <command> [subject] [args]

Run `coursesmith -h` for the command list, `coursesmith <command> -h` for one command.
"""
import argparse
import sys

from .subject import SubjectError, load

COMMANDS = []


def command(name, help_, *args_spec, subject=True):
    """Register a command. args_spec: (flags, kwargs) pairs for argparse."""
    def deco(fn):
        COMMANDS.append((name, help_, args_spec, subject, fn))
        return fn
    return deco


def arg(*flags, **kw):
    return flags, kw


# --------------------------------------------------------------------- status
@command("status", "where each subject stands (run this first when resuming)",
         arg("slug", nargs="?", default=None, help="one subject (default: all)"), subject=False)
def cmd_status(a):
    from . import status
    status.show(a.slug)


@command("init", "start a new subject: write subjects/<slug>/subject.yaml",
         arg("slug", help="lowercase-hyphenated name, e.g. frfr-speakers"),
         arg("--title", required=True, help="the course title or question"),
         arg("--seed", action="append", default=[], help="a page the course must cover: a Wikipedia title or a source key such as rfc>9110 (repeatable)"),
         arg("--category", action="append", default=[], help="a Wikipedia category root (repeatable)"),
         arg("--per-unit", type=int, nargs=2, default=[4, 5], metavar=("MIN", "MAX"), help="entries per unit"),
         arg("--questions", action="store_true", help="a course of questions, each with a worked answer"),
         arg("--force", action="store_true", help="overwrite an existing subject.yaml"), subject=False)
def cmd_init(a):
    from . import scaffold
    try:
        scaffold.init(a.slug, a.title, a.seed, a.category, a.per_unit, a.force,
                      course_type="questions" if a.questions else "survey")
    except scaffold.InitError as e:
        raise SystemExit(f"init: {e}")


# --------------------------------------------------------------------- sources
@command("sources discover", "find candidate sources for the subject (writes scope/sources.candidates.yaml)",
         arg("--query", action="append", default=[], help="a search phrase (repeatable; default: the title and seeds)"),
         arg("--limit", type=int, default=20), arg("--offline", action="store_true", help="registry only, no network"),
         arg("--papers", action="store_true", help="also search papers (noisy: name the papers you want instead)"))
def cmd_sources_discover(a):
    from .sources import discover
    discover.run(a.subject, a.query, a.limit, network=not a.offline, papers=a.papers)


@command("sources packet", "write the brief for a web-search session (guides/SOURCES_GUIDE.md)")
def cmd_sources_packet(a):
    from .sources import discover
    discover.packet(a.subject)


@command("sources merge", "fold a search session's work/sources/found.yaml into the candidates")
def cmd_sources_merge(a):
    from .sources import discover
    discover.merge(a.subject)


@command("sources parts", "list the page keys of a split one-file source, to paste into frame.yaml",
         arg("source", nargs="?", default=None, help="a source's name (default: every split source)"))
def cmd_sources_parts(a):
    from .sources import parts
    parts.run(a.subject, a.source)


@command("sources check", "verify subject.yaml's sources (licenses, allowlists, pins) before crawling",
         arg("--fix-refs", action="store_true", help="pin a branch or tag ref to the commit it points at now"))
def cmd_sources_check(a):
    from .sources import check
    if check.run(a.subject, fix_refs=a.fix_refs):
        raise SystemExit(1)


# --------------------------------------------------------------------- crawl + extract
@command("fetch", "fetch one page into the shared cache (a Wikipedia title, or a source key with --subject)",
         arg("title"), arg("--force", action="store_true"),
         arg("--subject", default=None, help="the subject whose sources own a qualified key such as rfc>9110"),
         subject=False)
def cmd_fetch(a):
    from .crawl.api import WikiClient
    from .crawl.fetch import fetch_page
    from .crawl.store import Store
    from .sources.registry import Registry
    store, client = Store(), WikiClient()
    registry = Registry.from_subject(load(a.subject), wiki_client=client) if a.subject else None
    rec, text, status = fetch_page(client, store, a.title, force=a.force, adapters=registry)
    store.flush_caches()
    print(f"{rec['title']} {rec.get('revid') or rec.get('version')} ({status}); {len(text):,} chars, "
          f"{len(rec.get('lead_links') or [])} lead links")


@command("frame plan-packet", "packet for the syllabus planner pass (guides/PLANNER_GUIDE.md)")
def cmd_frame_plan_packet(a):
    from .frame import syllabus
    syllabus.plan_packet(a.subject)


@command("frame resolve", "map the planned syllabus to entries, pages or phrases; reports/syllabus.md")
def cmd_frame_resolve(a):
    from .frame import syllabus
    syllabus.resolve(a.subject)


@command("frame build", "scout the subject's hubs and draft frame.yaml for review",
         arg("--scout", type=int, default=100, help="pages to fetch in the scout crawl"),
         arg("--refresh", action="store_true", help="re-read the navboxes instead of using the hub cache"))
def cmd_frame_build(a):
    from .frame import build
    build.build(a.subject, scout=a.scout, refresh=a.refresh)


@command("scope tune", "fit the scope threshold to the labeled calibration set")
def cmd_scope_tune(a):
    from .crawl import scope
    scope.tune(a.subject)


@command("scope judge-packets", "packets of borderline pages for the scope judge passes (guides/JUDGE_GUIDE.md)",
         arg("--size", type=int, default=600))
def cmd_scope_judge_packets(a):
    from .crawl import judge
    judge.packets(a.subject, a.size)


@command("scope judge-merge", "merge the judge passes' verdicts into scope/judge.json; score them on the calibration set")
def cmd_scope_judge_merge(a):
    from .crawl import judge
    judge.merge(a.subject)


@command("scope rescore", "re-score the calibration set with the current scope settings")
def cmd_scope_rescore(a):
    from .crawl import scope
    scope.rescore(a.subject)


@command("scope test", "score titles against the subject's scope", arg("titles", nargs="+"))
def cmd_scope_test(a):
    from .crawl.api import WikiClient
    from .crawl.fetch import prescreen
    from .crawl.scope import Scope
    from .crawl.store import Store
    store, sc = Store(), Scope(a.subject)
    resolved = prescreen(WikiClient(), store, a.titles)
    store.flush_caches()
    for t in a.titles:
        c = resolved.get(t, t)
        s, why = sc.score(c, store.meta.get(c))
        print(f"{s:>4} {'IN ' if s >= sc.threshold else 'out'} {c}: {'; '.join(why)}")


@command("crawl", "crawl the subject from its seeds and frame articles",
         arg("--chapter", default=None, help="only this frame chapter's seeds (key or title)"),
         arg("--max-pages", type=int, default=300), arg("--depth", type=int, default=2),
         arg("--resume", action="store_true"),
         arg("--hubs", action="store_true", help="also crawl every hub-list page that passes the threshold"),
         arg("--judged", action="store_true", help="also crawl every page the scope judge marked in or support"),
         arg("--context", action="store_true", help="tier A: fetch every page linked from the selected entries' leads"))
def cmd_crawl(a):
    from . import config
    from .crawl import crawl
    if not config.CONTACT:
        raise SystemExit("set COURSESMITH_CONTACT (email or URL) or write cache/contact.txt before crawling")
    from .sources import check as sources_check
    sources_check.require_ok(a.subject)
    if a.context:
        crawl.context(a.subject, a.max_pages)
    else:
        crawl.crawl(a.subject, a.chapter, a.max_pages, a.depth, a.resume, hubs=a.hubs, judged=a.judged)


@command("extract", "index the subject's crawled pages into the shared sentence index",
         arg("--force", action="store_true", help="re-index pages already indexed"))
def cmd_extract(a):
    from .extract import sentences
    sentences.build(a.subject, force=a.force)


@command("sent", "look sentences up by id", arg("ids", nargs="+"))
def cmd_sent(a):
    from .extract import sentences
    db = sentences.connect()
    found = sentences.lookup(db, a.ids)
    for i in a.ids:
        r = found.get(i)
        print(f"S:{i} | {r['title']} § {r['section']} | {r['sentence']}" if r else f"S:{i} | not found")


@command("ctx", "sentences around the first one containing PHRASE on a page", arg("title"), arg("phrase"),
         arg("-n", type=int, default=6))
def cmd_ctx(a):
    from .extract import sentences
    rows = sentences.context(sentences.connect(), a.title, a.phrase, a.n)
    if not rows:
        print("no match")
    for idx, sid, section, s in rows:
        print(f"S:{sid} | {section} | {s}")


@command("sections", "a page's sections with their sentence counts", arg("title"))
def cmd_sections(a):
    from .extract import sentences
    for sec, n in sentences.sections(sentences.connect(), a.title):
        print(f"{n:>4}  {sec}")


@command("page", "a page's sentences with ids, optionally one section", arg("title"),
         arg("--section", default=None), arg("-n", type=int, default=120))
def cmd_page(a):
    from .extract import sentences
    rows = sentences.page_sentences(sentences.connect(), a.title)
    rows = [r for r in rows if a.section is None or r[1] == a.section or r[1].startswith(a.section + " > ")]
    for sid, section, idx, text, *_ in rows[:a.n]:
        print(f"S:{sid} | § {section} | {text}")
    if len(rows) > a.n:
        print(f"... {len(rows) - a.n} more (raise -n)")


@command("search", "sentences containing PHRASE across the subject's pages", arg("phrase"),
         arg("-n", type=int, default=40))
def cmd_search(a):
    from .extract import sentences
    for sid, title, section, s in sentences.search(sentences.connect(), a.subject.slug, a.phrase, a.n):
        print(f"S:{sid} | {title} § {section} | {s}")


# --------------------------------------------------------------------- graph, coverage, dossiers
@command("reclean", "re-clean cached pages after a cleaner fix, carrying citations over to the new sentence ids",
         arg("--dry-run", action="store_true"))
def cmd_reclean(a):
    from .port import reclean
    reclean.run(a.subject, dry_run=a.dry_run)


@command("frame add", "put pages into a chapter's seeds (a gap-fill); see guides/GAPFILL_GUIDE.md",
         arg("chapter", help="chapter key or title"),
         arg("pages", nargs="+", help="Wikipedia titles or source keys such as rfc>9110"),
         arg("--also", action="store_true", help="context pages (also:) instead of seeds"))
def cmd_frame_add(a):
    from .frame import add
    add.run(a.subject, a.chapter, a.pages, also=a.also)


@command("report gaps", "unresolved names, thin entries and gaps files: what to gap-fill",
         arg("--probe", action="store_true", help="ask Wikipedia whether each unresolved name is a page"))
def cmd_report_gaps(a):
    from .frame import gaps
    gaps.run(a.subject, probe=a.probe)


@command("graph build", "concept graph: edges, importance, difficulty, chapter, RefD",
         arg("--pageviews", action="store_true", help="add a year of pageviews to importance (one request per page)"))
def cmd_graph_build(a):
    from .graph import build
    build.build(a.subject, pageviews=a.pageviews)


@command("report coverage", "hub lists vs crawl and entries; thin chapters",
         arg("--chapter", default=None))
def cmd_report_coverage(a):
    from .frame import coverage
    coverage.run(a.subject, a.chapter)


@command("dossier", "chapter dossiers for the consolidation passes", arg("chapter", nargs="?", default="all"),
         arg("--phrases", action="store_true", help="dossiers for syllabus concepts with no page, from sentence search"),
         arg("--new", action="store_true", help="a gap-fill: only pages no earlier chunk covers, as new chunks"))
def cmd_dossier(a):
    if a.phrases:
        from .frame import syllabus
        syllabus.phrase_dossiers(a.subject)
        return
    from .consolidate import dossier
    dossier.build(a.subject, a.chapter, new=a.new)


# --------------------------------------------------------------------- consolidate, select, order, verify
@command("finalize", "validate draft entries and write the final entry files",
         arg("chapter", nargs="?", default="all"), arg("--check", default=None, help="only validate this draft file"),
         arg("--merge", action="store_true", help="join a split chapter's part files into one draft file"))
def cmd_finalize(a):
    from .consolidate import finalize
    if not a.merge and not a.check:
        from .sources import check as sources_check
        sources_check.require_ok(a.subject)
    if a.merge:
        if a.chapter == "all":
            raise SystemExit("--merge needs a chapter")
        finalize.merge_parts(a.subject, a.chapter)
        return
    problems = finalize.finalize(a.subject, a.chapter, a.check)
    if problems:
        raise SystemExit(1)


@command("select", "curriculum test, score, trim to target",
         arg("--chapter", default=None, help="select within one chapter (the pilot)"),
         arg("--trim", action="store_true", help="cut each chapter to its frame target (default: keep all)"))
def cmd_select(a):
    from .order import select
    select.run(a.subject, a.chapter, a.trim)


@command("order build", "order the selected entries and write output/curriculum.md",
         arg("--force", action="store_true", help="rebuild even if the order is locked"))
def cmd_order(a):
    from .order import order
    order.build(a.subject, force=a.force)


@command("order packet", "write the ordering pass's packet (work/order/packet.md)")
def cmd_order_packet(a):
    from .order import order
    order.packet(a.subject)


@command("order lock", "freeze the order (takes hand edits from output/curriculum.md)")
def cmd_order_lock(a):
    from .order import order
    order.lock(a.subject)


@command("verify", "tiers B-D: cited works, authorities, added context",
         arg("--no-network", action="store_true", help="use cached lookups only"))
def cmd_verify(a):
    from .verify import verify
    verify.run(a.subject, network=not a.no_network)


# --------------------------------------------------------------------- write
@command("write skeleton", "writer packets per part (work/write/packet-*.md)")
def cmd_write_skeleton(a):
    from .write import skeleton
    skeleton.build(a.subject)


@command("write questions", "question packet per unit (after units build)")
def cmd_write_questions(a):
    from .write import skeleton
    skeleton.questions(a.subject)


@command("write check", "voice and number rules for the written prose",
         arg("--part", default=None, help="report only this part (frame key), for parallel writers"))
def cmd_write_check(a):
    from .write import check
    problems, _ = check.run(a.subject, a.part)
    if problems:
        raise SystemExit(1)


@command("write render", "merge writing batches into output/prose.json and render output/course.md")
def cmd_write_render(a):
    from .write import render
    render.render(a.subject)


# --------------------------------------------------------------------- units + publish
@command("units build", "split the locked order into units (per_unit entries each, as many as needed)",
         arg("--units", type=int, default=None, help="number of units (default: subject.yaml or ~4.5/unit)"))
def cmd_units_build(a):
    from .publish import units
    try:
        units.build(a.subject, a.units)
    except units.UnitError as e:
        raise SystemExit(f"units build: {e}")


@command("publish build", "build every unit EPUB and the complete-course EPUB",
         arg("--unit", type=int, action="append", help="only these units (repeatable)"),
         arg("--no-complete", action="store_true", help="skip the complete-course EPUB"))
def cmd_publish_build(a):
    from .publish import build
    build.build(a.subject, units=a.unit, complete=not a.no_complete)


@command("images", "fetch licensed, dithered images for entries that want one",
         arg("--all-landmarks", action="store_true"), arg("--force", action="store_true"))
def cmd_images(a):
    from .publish import images
    images.fetch(a.subject, a.all_landmarks, a.force)


@command("figures", "draw an entry's figures (figures.json) to PNG files to look at before publishing",
         arg("ids", nargs="*", help="entry ids (default: all)"), arg("--out", default=None))
def cmd_figures(a):
    from pathlib import Path

    from .publish import figures
    figures.preview(a.subject, Path(a.out) if a.out else a.subject.dir / "work" / "figures", a.ids)


@command("publish check", "fail if any unit edition breaks the course's rules")
def cmd_publish_check(a):
    from .publish import check
    problems, _ = check.run(a.subject)
    if problems:
        raise SystemExit(1)


@command("export", "write output/course.json: the whole course, prose and cited sentences in one file",
         arg("--out", default=None, help="path to write (default: subjects/<slug>/output/course.json)"),
         arg("--images", action="store_true", help="also copy entry images next to the file"),
         arg("--strict", action="store_true", help="fail if any cited sentence is missing from the index"))
def cmd_export(a):
    from pathlib import Path

    from .publish import export
    try:
        export.export(a.subject, Path(a.out) if a.out else None, a.images, a.strict)
    except export.ExportError as e:
        raise SystemExit(f"export: {e}")


# --------------------------------------------------------------------- main
def build_parser():
    p = argparse.ArgumentParser(prog="coursesmith", description="Sourced courses from Wikipedia and vetted sources.")
    sub = p.add_subparsers(dest="command", metavar="<command>")
    groups = {}
    for name, help_, args_spec, needs_subject, fn in COMMANDS:
        parts = name.split()
        if len(parts) == 1:
            sp = sub.add_parser(name, help=help_)
        else:
            top, leaf = parts
            if top not in groups:
                g = sub.add_parser(top, help=f"{top} commands")
                groups[top] = g.add_subparsers(dest="action", metavar="<action>")
            sp = groups[top].add_parser(leaf, help=help_)
        if needs_subject:
            sp.add_argument("subject", help="subject slug, e.g. soil-science")
        for flags, kw in args_spec:
            sp.add_argument(*flags, **kw)
        sp.set_defaults(fn=fn, needs_subject=needs_subject)
    return p


def main(argv=None):
    p = build_parser()
    a = p.parse_args(argv)
    if not getattr(a, "fn", None):
        p.print_help()
        sys.exit(1)
    if a.needs_subject:
        try:
            a.subject = load(a.subject)
        except SubjectError as e:
            sys.exit(str(e))
    a.fn(a)
