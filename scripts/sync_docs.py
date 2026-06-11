#!/usr/bin/env python3
"""Sync Hermes Agent Markdown docs, translate changed files, and build mdBook inputs."""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_ROOT = Path("/home/obj/.hermes/hermes-agent")
EN_ROOT = REPO_ROOT / "src" / "en"
ZH_ROOT = REPO_ROOT / "src" / "zh"
STATE_FILE = REPO_ROOT / "state" / "translation-hashes.tsv"
SUMMARY_FILE = REPO_ROOT / "src" / "SUMMARY.md"
INDEX_FILE = REPO_ROOT / "src" / "index.md"

EXCLUDED_DIRS = {
    ".git",
    ".next",
    ".turbo",
    ".venv",
    "venv",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "site-packages",
}

EXCLUDED_FILES = {
    "AGENTS.md",
    "CLAUDE.md",
    "README.zh-CN.md",
    "README.ur-pk.md",
}

TRANSLATION_INSTRUCTIONS = (
    "Translate prose to Simplified Chinese. Preserve Markdown structure, "
    "frontmatter, code fences, tables, links, file paths, commands, option names, "
    "environment variables, model names, API names, and identifiers. Do not add "
    "commentary."
)


@dataclass(frozen=True)
class DocFile:
    source: Path
    rel: Path
    sha256: str


def run(cmd: list[str], *, cwd: Path = REPO_ROOT, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, text=True, check=check)


def output(cmd: list[str], *, cwd: Path, check: bool = True) -> str:
    result = subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        check=check,
        capture_output=True,
    )
    return result.stdout


def maybe_update_source(source_root: Path) -> None:
    if not (source_root / ".git").exists():
        print(f"Source is not a git checkout; skipping source update: {source_root}")
        return
    status = output(["git", "status", "--porcelain"], cwd=source_root)
    if status.strip():
        print("Source checkout has local changes; skipping git pull --ff-only.")
        print(status.rstrip())
        return
    print("Updating source checkout with git pull --ff-only.")
    run(["git", "pull", "--ff-only"], cwd=source_root)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_doc(path: Path) -> bool:
    return path.suffix.lower() in {".md", ".mdx"}


def should_skip(rel: Path) -> bool:
    if any(part in EXCLUDED_DIRS for part in rel.parts):
        return True
    if rel.name in EXCLUDED_FILES:
        return True
    if len(rel.parts) >= 3 and rel.parts[0] == "website" and rel.parts[1] == "i18n":
        return True
    if rel.parts and rel.parts[0] == ".github":
        return True
    return False


def output_rel(rel: Path) -> Path:
    if rel.suffix.lower() == ".mdx":
        return rel.with_suffix(".md")
    return rel


def collect_docs(source_root: Path) -> list[DocFile]:
    docs: list[DocFile] = []
    for path in source_root.rglob("*"):
        if not path.is_file() or not is_doc(path):
            continue
        rel = path.relative_to(source_root)
        if should_skip(rel):
            continue
        out_rel = output_rel(rel)
        docs.append(DocFile(path, out_rel, sha256_file(path)))
    docs.sort(key=lambda item: item.rel.as_posix())
    return docs


def load_state() -> dict[str, str]:
    if not STATE_FILE.exists():
        return {}
    state: dict[str, str] = {}
    for line in STATE_FILE.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        rel, digest = line.split("\t", 1)
        state[rel] = digest
    return state


def save_state(state: dict[str, str]) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"{rel}\t{state[rel]}" for rel in sorted(state)]
    STATE_FILE.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def replace_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)


def copy_english_docs(docs: list[DocFile]) -> None:
    replace_tree(EN_ROOT)
    for doc in docs:
        dest = EN_ROOT / doc.rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(doc.source, dest)


def delete_removed_translations(state: dict[str, str], current_rels: set[str]) -> None:
    for rel in sorted(set(state) - current_rels):
        zh_path = ZH_ROOT / rel
        if zh_path.exists():
            zh_path.unlink()
        state.pop(rel, None)
    prune_empty_dirs(ZH_ROOT)


def prune_empty_dirs(root: Path) -> None:
    if not root.exists():
        return
    for path in sorted(root.rglob("*"), key=lambda item: len(item.parts), reverse=True):
        if path.is_dir():
            try:
                path.rmdir()
            except OSError:
                pass


def translate(doc: DocFile, *, lang: str) -> None:
    source = EN_ROOT / doc.rel
    output = ZH_ROOT / doc.rel
    output.parent.mkdir(parents=True, exist_ok=True)
    run(
        [
            "hymt",
            "translate-doc",
            str(source),
            "--output",
            str(output),
            "--lang",
            lang,
            "--yes",
            "--no-stream",
            "--template",
            "context-aware",
            "--context",
            "Hermes Agent technical documentation, CLI usage, agent skills, plugins, providers, and developer guides.",
            "--instructions",
            TRANSLATION_INSTRUCTIONS,
        ]
    )


def first_heading(path: Path) -> str:
    try:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            stripped = line.strip()
            if stripped.startswith("# "):
                return stripped[2:].strip() or path.stem
    except OSError:
        pass
    return path.stem.replace("-", " ").replace("_", " ").title()


def generate_index(source_root: Path, docs: list[DocFile], translated_count: int) -> None:
    total_bytes = sum(doc.source.stat().st_size for doc in docs)
    INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    INDEX_FILE.write_text(
        "\n".join(
            [
                "# Hermes Agent Docs i18n",
                "",
                "This mdBook mirrors Hermes Agent documentation in English and Simplified Chinese.",
                "",
                f"- Source tree: `{source_root}`",
                f"- Tracked source documents: {len(docs)}",
                f"- Source bytes: {total_bytes:,}",
                f"- Chinese pages currently present: {translated_count}",
                "- Translator: `hymt` with local `Hy-MT2-7B.i1-Q6_K.gguf`",
                "- Update policy: changed files are detected by SHA-256 and translated incrementally.",
                "",
                "Use the left navigation to browse English or Chinese pages. Individual pages also",
                "show a language switch link when a counterpart path exists.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def generate_summary(docs: list[DocFile]) -> None:
    lines = [
        "# Summary",
        "",
        "[Overview](index.md)",
        "",
        "# English",
        "",
    ]
    for doc in docs:
        path = EN_ROOT / doc.rel
        title = f"{doc.rel.as_posix()} - {first_heading(path)}"
        lines.append(f"- [{title}](en/{doc.rel.as_posix()})")

    zh_docs = [doc for doc in docs if (ZH_ROOT / doc.rel).exists()]
    if zh_docs:
        lines.extend(["", "# 中文", ""])
        for doc in zh_docs:
            path = ZH_ROOT / doc.rel
            title = f"{doc.rel.as_posix()} - {first_heading(path)}"
            lines.append(f"- [{title}](zh/{doc.rel.as_posix()})")

    SUMMARY_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def git_has_changes() -> bool:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=REPO_ROOT,
        text=True,
        check=True,
        capture_output=True,
    )
    return bool(result.stdout.strip())


def commit_and_push(*, push: bool) -> None:
    if not git_has_changes():
        print("No repository changes to commit.")
        return
    run(["git", "add", "."])
    run(["git", "commit", "-m", "docs: sync Hermes Agent documentation"])
    if push:
        run(["git", "push", "-u", "origin", "HEAD"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=DEFAULT_SOURCE_ROOT)
    parser.add_argument("--lang", default="zh")
    parser.add_argument("--update-source", action="store_true")
    parser.add_argument("--skip-translation", action="store_true")
    parser.add_argument("--max-files", type=int, default=None)
    parser.add_argument("--commit", action="store_true")
    parser.add_argument("--push", action="store_true")
    args = parser.parse_args()

    source_root = args.source_root.expanduser().resolve()
    if not source_root.exists():
        raise SystemExit(f"source root does not exist: {source_root}")
    if args.update_source:
        maybe_update_source(source_root)

    docs = collect_docs(source_root)
    if not docs:
        raise SystemExit(f"no Markdown documents found under {source_root}")

    state = load_state()
    current_rels = {doc.rel.as_posix() for doc in docs}

    copy_english_docs(docs)
    delete_removed_translations(state, current_rels)

    changed = [
        doc
        for doc in docs
        if state.get(doc.rel.as_posix()) != doc.sha256 or not (ZH_ROOT / doc.rel).exists()
    ]
    changed.sort(key=lambda item: (item.source.stat().st_size, item.rel.as_posix()))
    if args.max_files is not None:
        changed = changed[: args.max_files]

    print(f"Source documents: {len(docs)}")
    print(f"Files needing translation this run: {len(changed)}")

    if not args.skip_translation:
        for index, doc in enumerate(changed, start=1):
            print(f"[{index}/{len(changed)}] translating {doc.rel.as_posix()}", flush=True)
            translate(doc, lang=args.lang)
            state[doc.rel.as_posix()] = doc.sha256
            save_state(state)

    translated_count = sum(1 for doc in docs if (ZH_ROOT / doc.rel).exists())
    generate_index(source_root, docs, translated_count)
    generate_summary(docs)
    save_state(state)

    if args.commit or args.push:
        commit_and_push(push=args.push)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
