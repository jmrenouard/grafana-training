"""Executable validation tests for Diátaxis EN/FR docs, Mermaid diagrams, YAML, JSON, and scripts."""

from __future__ import annotations

import json
import os
import py_compile
import re
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = REPO_ROOT / "docs"
DOCS_FR_DIR = DOCS_DIR / "fr"

LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)\n]+)\)")
FENCE_RE = re.compile(r"^(?P<indent>[ \t]*)(?P<ticks>`{3,}|~{3,})(?P<info>.*)$")
BOX_CHAR_RE = re.compile(r"[\u2500-\u257f▼▲◄►]")
SCRIPT_REF_RE = re.compile(r"(scripts/(?:grafana/)?[a-zA-Z0-9_.-]+\.(?:sh|py))")
PLAYBOOK_REF_RE = re.compile(r"(ansible/playbooks/[a-zA-Z0-9_.-]+\.yml)")

FRENCH_MARKERS = re.compile(
    r"\b(?:procédure|tutoriel|démarrage|prérequis|vérification|"
    r"retour\s+arrière|utilisation|tableau\s+de\s+bord|pare-feu)\b",
    re.IGNORECASE,
)
ENGLISH_ONLY_HEADINGS = re.compile(
    r"(?m)^#{1,4}\s+(?:Getting Started|Prerequisites|Troubleshooting|Overview|Rollback|Verification)\b"
)
ENGLISH_HOWTO_BANNED = re.compile(
    r"(?:;|should\b|would\b|may\b|might\b|shall\b|"
    r"\b(?:don't|doesn't|isn't|aren't|won't|can't|let's)\b)",
    re.IGNORECASE,
)
FRENCH_HOWTO_BANNED = re.compile(r"(?:;|\b(?:devrait|devraient|pourrait|pourraient)\b)", re.IGNORECASE)


def _iter_markdown() -> list[Path]:
    """Return all tracked/workspace Markdown files excluding .git."""
    return sorted(p for p in REPO_ROOT.rglob("*.md") if ".git/" not in p.as_posix())


def _strip_fenced_blocks(text: str) -> list[tuple[int, str]]:
    """Return (lineno, line) tuples outside fenced code blocks."""
    out: list[tuple[int, str]] = []
    fence_char: str | None = None
    fence_len = 0
    for lineno, raw_line in enumerate(text.splitlines(), start=1):
        if fence_char is not None:
            if re.match(rf"^\s*{re.escape(fence_char)}{{{fence_len},}}\s*$", raw_line):
                fence_char = None
                fence_len = 0
            continue
        match = FENCE_RE.match(raw_line)
        if match:
            ticks = match.group("ticks")
            fence_char = ticks[0]
            fence_len = len(ticks)
            continue
        out.append((lineno, raw_line))
    return out


def _extract_fenced_blocks(text: str) -> list[dict[str, object]]:
    """Extract all fenced code blocks with line number, indent, info string, and body."""
    blocks: list[dict[str, object]] = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        match = FENCE_RE.match(lines[i])
        if not match:
            i += 1
            continue
        indent = match.group("indent")
        ticks = match.group("ticks")
        info = match.group("info").strip()
        fence_char = ticks[0]
        fence_len = len(ticks)
        start_line = i + 1
        body: list[str] = []
        i += 1
        while i < len(lines):
            if re.match(rf"^\s*{re.escape(fence_char)}{{{fence_len},}}\s*$", lines[i]):
                break
            body.append(lines[i])
            i += 1
        blocks.append({"line": start_line, "indent": indent, "info": info, "code": "\n".join(body)})
        i += 1
    return blocks


class TestDocsTutorialsAndHowTos(unittest.TestCase):
    """Validate Diátaxis EN/FR suites, Mermaid diagrams, YAML/JSON assets, and scripts."""

    def test_diataxis_en_and_fr_structure_and_links(self) -> None:
        required_files = [
            DOCS_DIR / "index.md",
            DOCS_DIR / "01-tutorials" / "index.md",
            DOCS_DIR / "01-tutorials" / "01-monitoring-lab-setup.md",
            DOCS_DIR / "01-tutorials" / "02-dashboards-alerts-and-metrics.md",
            DOCS_DIR / "02-how-to-guides" / "index.md",
            DOCS_DIR / "02-how-to-guides" / "deploy-and-verify-stack.md",
            DOCS_DIR / "02-how-to-guides" / "provision-dashboards-and-backup.md",
            DOCS_DIR / "03-reference" / "index.md",
            DOCS_DIR / "03-reference" / "ports-configs-and-scripts.md",
            DOCS_DIR / "04-explanation" / "index.md",
            DOCS_DIR / "04-explanation" / "scraping-provisioning-and-architecture.md",
            DOCS_FR_DIR / "index.md",
            DOCS_FR_DIR / "01-tutoriels" / "index.md",
            DOCS_FR_DIR / "01-tutoriels" / "01-atelier-docker-monitoring.md",
            DOCS_FR_DIR / "02-guides-pratiques" / "index.md",
            DOCS_FR_DIR / "02-guides-pratiques" / "deployer-et-verifier-stack.md",
            DOCS_FR_DIR / "02-guides-pratiques" / "provisionner-dashboards-et-sauvegarde.md",
            DOCS_FR_DIR / "03-reference" / "index.md",
            DOCS_FR_DIR / "03-reference" / "ports-configs-et-scripts.md",
            DOCS_FR_DIR / "04-explications" / "index.md",
            DOCS_FR_DIR / "04-explications" / "architecture-collecte-et-provisionnement.md",
            REPO_ROOT / "configuration" / "README.md",
        ]
        for path in required_files:
            self.assertTrue(path.is_file(), f"Missing required document: {path}")
            self.assertGreater(len(path.read_text(encoding="utf-8").strip()), 0, f"Empty doc: {path}")

        repo_resolved = REPO_ROOT.resolve()
        for md_file in _iter_markdown():
            text = md_file.read_text(encoding="utf-8")
            self.assertNotIn("https://www.google.com/search?q=", text, f"Google search hijack in {md_file}")
            for lineno, line in _strip_fenced_blocks(text):
                for match in LINK_RE.finditer(line):
                    raw = match.group(1).strip()
                    target = raw.split()[0] if not raw.startswith("<") else raw[1 : raw.find(">")]
                    target = target.split("#", 1)[0].split("?", 1)[0].strip()
                    if not target or target.startswith(("http://", "https://", "mailto:", "data:")):
                        continue
                    self.assertFalse(target.startswith("file://"), f"Disallowed file:// URI in {md_file}:{lineno}")
                    resolved = (md_file.parent / target).resolve()
                    self.assertTrue(
                        resolved.exists() and str(resolved).startswith(str(repo_resolved)),
                        f"Broken relative link in {md_file}:{lineno} -> {target}",
                    )

        for guide in sorted((DOCS_DIR / "02-how-to-guides").glob("*.md")):
            if guide.name == "index.md":
                continue
            text = guide.read_text(encoding="utf-8")
            self.assertRegex(text, r"(?m)^##\s+Prerequisites\b")
            self.assertRegex(text, r"(?m)^##\s+Verification\b")
            self.assertRegex(text, r"(?m)^##\s+Rollback\b")
            prose = "\n".join(line for _, line in _strip_fenced_blocks(text))
            self.assertIsNone(ENGLISH_HOWTO_BANNED.search(prose), f"STE violation in {guide}")

        for guide in sorted((DOCS_FR_DIR / "02-guides-pratiques").glob("*.md")):
            if guide.name == "index.md":
                continue
            text = guide.read_text(encoding="utf-8")
            self.assertRegex(text, r"(?m)^##\s+Prérequis\b")
            self.assertRegex(text, r"(?m)^##\s+Vérification\b")
            self.assertRegex(text, r"(?m)^##\s+Retour\s+arrière\b")
            prose = "\n".join(line for _, line in _strip_fenced_blocks(text))
            self.assertIsNone(FRENCH_HOWTO_BANNED.search(prose), f"STF violation in {guide}")

        skills_root = Path.home() / ".gemini" / "config" / "skills" / "diataxis-docs" / "scripts"
        en_check = skills_root / "diataxis_check.py"
        if en_check.is_file():
            res = subprocess.run(
                [sys.executable, str(en_check), str(DOCS_DIR), "--strict", "--check-ste", "--lang", "en"],
                capture_output=True,
                text=True,
                timeout=60,
            )
            self.assertEqual(res.returncode, 0, f"diataxis_check.py failed:\n{res.stdout}\n{res.stderr}")

        fr_check = skills_root / "diataxis_check_fr.py"
        if fr_check.is_file():
            res = subprocess.run(
                [sys.executable, str(fr_check), str(DOCS_FR_DIR), "--strict", "--check-stf"],
                capture_output=True,
                text=True,
                timeout=60,
            )
            self.assertEqual(res.returncode, 0, f"diataxis_check_fr.py failed:\n{res.stdout}\n{res.stderr}")

    def test_fr_en_separation(self) -> None:
        readme_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        readme_fr = (REPO_ROOT / "README.fr.md").read_text(encoding="utf-8")
        self.assertIn("[Français](README.fr.md)", readme_en)
        self.assertIn("[English](README.md)", readme_fr)
        self.assertIsNone(FRENCH_MARKERS.search(readme_en), "French markers leaked into README.md")
        self.assertIsNone(ENGLISH_ONLY_HEADINGS.search(readme_fr), "English headings leaked into README.fr.md")

        for md_file in sorted(DOCS_DIR.rglob("*.md")):
            text = md_file.read_text(encoding="utf-8")
            if DOCS_FR_DIR in md_file.parents:
                self.assertIsNone(ENGLISH_ONLY_HEADINGS.search(text), f"English heading in FR doc {md_file}")
            else:
                self.assertIsNone(FRENCH_MARKERS.search(text), f"French markers leaked into EN doc {md_file}")

        for en_ansible in sorted((REPO_ROOT / "ansible" / "doc").glob("doc_*.md")):
            if en_ansible.name.endswith("_fr.md"):
                continue
            self.assertIsNone(FRENCH_MARKERS.search(en_ansible.read_text(encoding="utf-8")))

    def test_mermaid_diagrams_and_zero_ascii_art(self) -> None:
        mermaid_count = 0
        for md_file in _iter_markdown():
            text = md_file.read_text(encoding="utf-8")
            for lineno, line in _strip_fenced_blocks(text):
                self.assertIsNone(BOX_CHAR_RE.search(line), f"Box/arrow ASCII art in prose {md_file}:{lineno}")
            for block in _extract_fenced_blocks(text):
                code = str(block["code"])
                info = str(block["info"]).lower()
                indent = str(block["indent"])
                lineno = int(block["line"])
                self.assertIsNone(BOX_CHAR_RE.search(code), f"ASCII box/arrow diagram in {md_file}:{lineno}")
                if info.startswith("mermaid"):
                    self.assertEqual(indent, "", f"Indented mermaid fence in {md_file}:{lineno}")
                    self.assertRegex(
                        code.lstrip(),
                        r"^(?:graph|flowchart|sequenceDiagram|stateDiagram|classDiagram|erDiagram)\b",
                    )
                    mermaid_count += 1
                elif re.match(r"^(?:graph|flowchart)\s+(?:TD|LR|TB|RL)\b|^sequenceDiagram\b", code.lstrip()):
                    self.fail(f"Untagged Mermaid block at {md_file}:{lineno}")

        self.assertGreaterEqual(mermaid_count, 8)

    def test_yaml_json_compose_ansible_python_and_shell_scripts(self) -> None:
        self.assertFalse((REPO_ROOT / "scripts" / "ttoto.sh").exists(), "Broken scratch scripts/ttoto.sh must not exist")

        for md_file in [REPO_ROOT / "README.md", REPO_ROOT / "README.fr.md", *sorted(DOCS_DIR.rglob("*.md"))]:
            text = md_file.read_text(encoding="utf-8")
            for match in SCRIPT_REF_RE.finditer(text):
                rel = match.group(1)
                self.assertTrue((REPO_ROOT / rel).is_file(), f"Missing script {rel} referenced in {md_file}")
            for match in PLAYBOOK_REF_RE.finditer(text):
                rel = match.group(1)
                self.assertTrue((REPO_ROOT / rel).is_file(), f"Missing playbook {rel} referenced in {md_file}")

        for json_file in sorted(REPO_ROOT.rglob("*.json")):
            data = json.loads(json_file.read_text(encoding="utf-8"))
            self.assertIsNotNone(data)
        overview = json.loads((REPO_ROOT / "examples" / "dashboards" / "system-overview.json").read_text(encoding="utf-8"))
        self.assertIn("dashboard", overview)
        self.assertGreater(len(overview["dashboard"]["panels"]), 0)

        try:
            import yaml  # type: ignore
        except ImportError:
            yaml = None
        if yaml is not None:
            yml_files = sorted(REPO_ROOT.rglob("*.y*ml"))
            self.assertGreaterEqual(len(yml_files), 28)
            for yml_file in yml_files:
                yaml.safe_load(yml_file.read_text(encoding="utf-8"))

        docker_compose_sub = (REPO_ROOT / "docker" / "docker-compose.yml").read_text(encoding="utf-8")
        self.assertNotIn("/var/lin/grafana", docker_compose_sub)

        py_compile.compile(str(REPO_ROOT / "scripts" / "generate-metrics.py"), doraise=True)
        help_res = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "generate-metrics.py"), "--help"],
            capture_output=True,
            text=True,
            timeout=20,
        )
        self.assertEqual(help_res.returncode, 0)
        self.assertIn("--port", help_res.stdout)
        self.assertIn("--verbose", help_res.stdout)

        if os.name != "nt" and shutil.which("docker"):
            for cf in (REPO_ROOT / "docker-compose.yml", REPO_ROOT / "docker" / "docker-compose.yml"):
                res = subprocess.run(
                    ["docker", "compose", "-f", str(cf), "config", "-q"],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                self.assertEqual(res.returncode, 0, f"docker compose config failed for {cf}: {res.stderr}")

        if os.name != "nt" and shutil.which("bash"):
            sh_files = sorted(REPO_ROOT.rglob("*.sh"))
            self.assertGreaterEqual(len(sh_files), 15)
            for sh_file in sh_files:
                res = subprocess.run(["bash", "-n", str(sh_file)], capture_output=True, text=True, timeout=15)
                self.assertEqual(res.returncode, 0, f"bash -n failed on {sh_file}: {res.stderr}")


if __name__ == "__main__":
    unittest.main()
