#!/usr/bin/env python3
"""Sync Hermes Agent Markdown docs, translate changed files, and build mdBook inputs."""

from __future__ import annotations

import argparse
import collections
import concurrent.futures
import hashlib
import os
import shutil
import subprocess
import sys
import time
import tomllib
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_ROOT = Path("/home/obj/.hermes/hermes-agent")
EN_ROOT = REPO_ROOT / "src" / "en"
ZH_ROOT = REPO_ROOT / "src" / "zh"
STATE_FILE = REPO_ROOT / "state" / "translation-hashes.tsv"
SUMMARY_FILE = REPO_ROOT / "src" / "SUMMARY.md"
INDEX_FILE = REPO_ROOT / "src" / "index.md"
DEFAULT_CONFIG_FILE = REPO_ROOT / "config" / "sync.toml"
DEFAULT_TRANSLATION_WORKERS = 1
DEFAULT_WORKER_CEILING = 10
DEFAULT_CONFIG_RELOAD_SECONDS = 10.0

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


@dataclass(frozen=True)
class SyncConfig:
    translation_workers: int
    worker_ceiling: int
    hot_reload_interval_seconds: float


@dataclass
class SummaryNode:
    dirs: dict[str, "SummaryNode"]
    files: list[DocFile]


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


def positive_int(value: object, *, name: str, default: int) -> int:
    if value is None:
        return default
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{name} must be a positive integer")
    return value


def positive_float(value: object, *, name: str, default: float) -> float:
    if value is None:
        return default
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
        raise ValueError(f"{name} must be a positive number")
    return float(value)


def parse_sync_config(path: Path) -> SyncConfig:
    data: dict[str, object] = {}
    if path.exists():
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    translation = data.get("translation", {})
    if not isinstance(translation, dict):
        raise ValueError("translation must be a TOML table")

    workers = positive_int(
        translation.get("workers"),
        name="translation.workers",
        default=DEFAULT_TRANSLATION_WORKERS,
    )
    worker_ceiling = positive_int(
        translation.get("worker_ceiling"),
        name="translation.worker_ceiling",
        default=DEFAULT_WORKER_CEILING,
    )
    reload_seconds = positive_float(
        translation.get("hot_reload_interval_seconds"),
        name="translation.hot_reload_interval_seconds",
        default=DEFAULT_CONFIG_RELOAD_SECONDS,
    )
    if workers > worker_ceiling:
        raise ValueError("translation.workers cannot exceed translation.worker_ceiling")
    return SyncConfig(
        translation_workers=workers,
        worker_ceiling=worker_ceiling,
        hot_reload_interval_seconds=reload_seconds,
    )


def load_sync_config(path: Path, *, fallback: SyncConfig | None = None) -> SyncConfig:
    try:
        return parse_sync_config(path)
    except (OSError, tomllib.TOMLDecodeError, ValueError) as error:
        if fallback is None:
            raise SystemExit(f"invalid sync config {path}: {error}") from error
        print(f"WARNING: keeping previous sync config; failed to load {path}: {error}", file=sys.stderr)
        return fallback


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


def translate(doc: DocFile, *, lang: str) -> subprocess.CompletedProcess[str]:
    source = EN_ROOT / doc.rel
    output = ZH_ROOT / doc.rel
    output.parent.mkdir(parents=True, exist_ok=True)
    return subprocess.run(
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
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
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


def display_title(value: str) -> str:
    return value.replace("-", " ").replace("_", " ").title()


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


def build_summary_tree(docs: list[DocFile]) -> SummaryNode:
    root = SummaryNode(dirs={}, files=[])
    for doc in docs:
        node = root
        for part in doc.rel.parts[:-1]:
            node = node.dirs.setdefault(part, SummaryNode(dirs={}, files=[]))
        node.files.append(doc)
    return root


def preferred_index_doc(node: SummaryNode) -> DocFile | None:
    by_name = {doc.rel.name.lower(): doc for doc in node.files}
    return by_name.get("readme.md") or by_name.get("index.md")


def doc_summary_title(doc: DocFile, content_root: Path) -> str:
    return first_heading(content_root / doc.rel)


def render_summary_tree(
    node: SummaryNode,
    *,
    content_root: Path,
    book_prefix: str,
    level: int = 0,
    skip_doc: DocFile | None = None,
) -> list[str]:
    lines: list[str] = []
    indent = "  " * level
    skip_rel = skip_doc.rel if skip_doc else None

    files = sorted(node.files, key=lambda doc: doc.rel.name.lower())
    index_doc = preferred_index_doc(node)
    if level > 0 and index_doc is not None:
        files = [index_doc] + [doc for doc in files if doc.rel != index_doc.rel]
    for doc in files:
        if doc.rel == skip_rel:
            continue
        title = doc_summary_title(doc, content_root)
        lines.append(f"{indent}- [{title}]({book_prefix}/{doc.rel.as_posix()})")

    for dirname, child in sorted(node.dirs.items()):
        index_doc = preferred_index_doc(child)
        title = display_title(dirname)
        if index_doc is not None:
            lines.append(f"{indent}- [{title}]({book_prefix}/{index_doc.rel.as_posix()})")
        else:
            lines.append(f"{indent}- [{title}]()")
        lines.extend(
            render_summary_tree(
                child,
                content_root=content_root,
                book_prefix=book_prefix,
                level=level + 1,
                skip_doc=index_doc,
            )
        )

    return lines


def generate_summary(docs: list[DocFile], translated_rels: set[str] | None = None) -> None:
    lines = [
        "# Summary",
        "",
        "[Overview](index.md)",
        "",
        "# English",
        "",
    ]
    lines.extend(render_summary_tree(build_summary_tree(docs), content_root=EN_ROOT, book_prefix="en"))

    if translated_rels is None:
        translated_rels = {doc.rel.as_posix() for doc in docs if (ZH_ROOT / doc.rel).exists()}
    zh_docs = [doc for doc in docs if doc.rel.as_posix() in translated_rels]
    if zh_docs:
        lines.extend(["", "# 中文", ""])
        lines.extend(render_summary_tree(build_summary_tree(zh_docs), content_root=ZH_ROOT, book_prefix="zh"))

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


def git_stage_existing(paths: list[Path]) -> None:
    existing = [str(path) for path in paths if path.exists()]
    if existing:
        run(["git", "add", "--", *existing])


def commit_subject_for_doc(doc: DocFile) -> str:
    rel = doc.rel.as_posix()
    subject = f"docs: translate {rel}"
    if len(subject) <= 72:
        return subject
    return f"docs: translate {doc.rel.name}"


def commit_translated_doc(
    doc: DocFile,
    *,
    source_root: Path,
    docs: list[DocFile],
    state: dict[str, str],
    push: bool,
) -> None:
    translated_rels = set(state)
    generate_index(source_root, docs, len(translated_rels))
    generate_summary(docs, translated_rels)
    save_state(state)
    git_stage_existing(
        [
            EN_ROOT / doc.rel,
            ZH_ROOT / doc.rel,
            SUMMARY_FILE,
            INDEX_FILE,
            STATE_FILE,
        ]
    )
    status = output(["git", "diff", "--cached", "--name-only"], cwd=REPO_ROOT)
    if not status.strip():
        print(f"No staged changes for {doc.rel.as_posix()}; skipping commit.")
        return
    subject = commit_subject_for_doc(doc)
    body = f"Translated Hermes Agent source document:\n\n{doc.rel.as_posix()}"
    run(["git", "commit", "-m", subject, "-m", body])
    if push:
        run(["git", "push", "-u", "origin", "HEAD"])


def translate_changed(
    docs: list[DocFile],
    *,
    lang: str,
    source_root: Path,
    all_docs: list[DocFile],
    state: dict[str, str],
    config_path: Path,
    initial_config: SyncConfig,
    commit_each: bool,
    push: bool,
) -> None:
    if not docs:
        return
    worker_ceiling = initial_config.worker_ceiling
    config = initial_config
    next_reload = 0.0
    last_reported_workers: int | None = None
    pending = collections.deque(docs)
    completed = 0
    failures: list[tuple[DocFile, subprocess.CompletedProcess[str]]] = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=worker_ceiling) as executor:
        future_to_doc: dict[concurrent.futures.Future[subprocess.CompletedProcess[str]], DocFile] = {}
        while pending or future_to_doc:
            now = time.monotonic()
            if now >= next_reload:
                config = load_sync_config(config_path, fallback=config)
                next_reload = now + config.hot_reload_interval_seconds
                if config.translation_workers != last_reported_workers:
                    last_reported_workers = config.translation_workers
                    print(
                        f"Active translation worker limit: {config.translation_workers} "
                        f"(ceiling {worker_ceiling})",
                        flush=True,
                    )

            while pending and len(future_to_doc) < config.translation_workers:
                doc = pending.popleft()
                future = executor.submit(translate, doc, lang=lang)
                future_to_doc[future] = doc
                print(f"queued {doc.rel.as_posix()}", flush=True)

            if not future_to_doc:
                continue

            done, _pending = concurrent.futures.wait(
                future_to_doc,
                timeout=config.hot_reload_interval_seconds,
                return_when=concurrent.futures.FIRST_COMPLETED,
            )
            if not done:
                continue

            for future in done:
                doc = future_to_doc.pop(future)
                completed += 1
                print(f"[{completed}/{len(docs)}] completed {doc.rel.as_posix()}", flush=True)
                try:
                    result = future.result()
                except Exception as error:  # subprocess setup failure, not translation quality.
                    print(f"ERROR: translation task crashed for {doc.rel.as_posix()}: {error}", file=sys.stderr)
                    raise
                if result.stdout:
                    print(result.stdout.rstrip())
                if result.stderr:
                    print(result.stderr.rstrip(), file=sys.stderr)
                if result.returncode == 0:
                    state[doc.rel.as_posix()] = doc.sha256
                    save_state(state)
                    if commit_each:
                        commit_translated_doc(
                            doc,
                            source_root=source_root,
                            docs=all_docs,
                            state=state,
                            push=push,
                        )
                else:
                    failures.append((doc, result))
    if failures:
        lines = [
            f"{doc.rel.as_posix()} exited {result.returncode}"
            for doc, result in failures
        ]
        raise SystemExit("translation failures:\n" + "\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=DEFAULT_SOURCE_ROOT)
    parser.add_argument("--lang", default="zh")
    parser.add_argument("--update-source", action="store_true")
    parser.add_argument("--skip-translation", action="store_true")
    parser.add_argument("--max-files", type=int, default=None)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_FILE)
    parser.add_argument(
        "--workers",
        type=int,
        default=None,
        help="Initial translation worker limit before config hot reload. Prefer config/sync.toml.",
    )
    parser.add_argument("--commit", action="store_true")
    parser.add_argument("--push", action="store_true")
    args = parser.parse_args()

    source_root = args.source_root.expanduser().resolve()
    if not source_root.exists():
        raise SystemExit(f"source root does not exist: {source_root}")
    if args.update_source:
        maybe_update_source(source_root)
    config_path = args.config.expanduser().resolve()
    config = load_sync_config(config_path)
    if args.workers is not None:
        config = SyncConfig(
            translation_workers=positive_int(args.workers, name="--workers", default=config.translation_workers),
            worker_ceiling=max(config.worker_ceiling, args.workers),
            hot_reload_interval_seconds=config.hot_reload_interval_seconds,
        )

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
        print(f"Config file: {config_path}")
        translate_changed(
            changed,
            lang=args.lang,
            source_root=source_root,
            all_docs=docs,
            state=state,
            config_path=config_path,
            initial_config=config,
            commit_each=args.commit or args.push,
            push=args.push,
        )

    translated_count = sum(1 for doc in docs if doc.rel.as_posix() in state)
    generate_index(source_root, docs, translated_count)
    generate_summary(docs, set(state))
    save_state(state)

    if (args.commit or args.push) and args.skip_translation:
        commit_and_push(push=args.push)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
