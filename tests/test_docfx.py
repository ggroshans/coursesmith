import unittest

from coursesmith.sources.github import GithubAdapter
from coursesmith.text import docfx as DX
from coursesmith.text.markdown import markdown_to_doc

from .fakes import FIXTURES, FakeHTTP

SHA = "a" * 40


def read(raw):
    doc = markdown_to_doc(DX.clean(raw))
    return DX.restore(doc.text), DX.restore(doc.name)


class DocfxTest(unittest.TestCase):
    def setUp(self):
        self.text, self.name = read((FIXTURES / "docfx" / "di.md").read_text(encoding="utf-8"))

    def test_extensions_do_not_leak_into_the_text(self):
        for junk in (":::", "[!", "xref", "snippets/Program.cs", "prereqs", "#tab", "{#lifetimes}", "Next steps",
                     "service-lifetimes"):
            self.assertNotIn(junk, self.text)

    def test_dots_that_start_a_word_keep_their_space(self):
        self.assertEqual(self.name, ".NET dependency injection")
        self.assertIn("Dependency injection in .NET is built into the framework.", self.text)
        self.assertIn("Edit the .config file, then build the .dll.", self.text)

    def test_callouts_become_a_label(self):
        self.assertIn("> Important: The examples use the Microsoft.NET.Sdk.Worker SDK.", self.text)

    def test_xrefs_become_the_member_or_type_name(self):
        self.assertIn("and IOptions.", self.text)
        self.assertIn("with GetService or List.Add.", self.text)
        self.assertIn("A typed link reads as text.", self.text)

    def test_structure_survives(self):
        self.assertIn("## Lifetimes", self.text)
        self.assertIn("## Last words", self.text)
        self.assertIn("### Windows", self.text.replace("#### Windows", "### Windows"))

    def test_the_other_sections_stay_when_a_links_only_section_is_dropped(self):
        self.assertIn("The end of the page.", self.text)

    def test_code_fences_are_left_alone(self):
        md = "# T\n\n```csharp\n[!NOTE] :::zone <xref:a.b>\n```\n\nText here is long enough.\n"
        self.assertIn("[!NOTE] :::zone <xref:a.b>", DX.clean(md))


class AdapterTest(unittest.TestCase):
    def test_markup_docfx_is_applied_when_fetching(self):
        raw = (FIXTURES / "docfx" / "di.md").read_text(encoding="utf-8")
        base = f"https://raw.githubusercontent.com/dotnet/docs/{SHA}"
        for markup, want in (("docfx", True), (None, False)):
            http = FakeHTTP({f"{base}/docs/core/di.md": raw})
            cfg = {"name": "dotnet-docs", "adapter": "github", "repo": "dotnet/docs", "ref": SHA,
                   "include": ["docs/**/*.md"], **({"markup": markup} if markup else {})}
            rec = GithubAdapter(cfg, http=http).fetch("gh>dotnet/docs/docs/core/di.md")
            text = rec["text"] if "text" in rec else ""
            self.assertEqual(":::code" not in text, want)
            self.assertEqual("in .NET is built" in text, want)


if __name__ == "__main__":
    unittest.main()
