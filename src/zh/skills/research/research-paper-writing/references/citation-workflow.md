# 引用管理与幻觉防范

本文档提供了完整的流程指南，帮助您通过编程方式管理引用、防止人工智能生成的虚假引用，并维护整洁的参考文献列表。

---

## 目录

- [为何需要引用验证](#why-citation-verification-matters)
- [引用 API 概览](#citation-apis-overview)
- [经过验证的引用处理流程](#verified-citation-workflow)
- [Python 实现方案](#python-implementation)
- [BibTeX 管理](#bibtex-management)
- [常见引用格式](#common-citation-formats)
- [故障排除](#troubleshooting)

---

## 为何需要引用验证

### 幻觉问题

研究表明，人工智能生成的引用存在严重问题：
- 根据 Enago Academy 的研究，人工智能生成的引用错误率高达 **约 40%**
- NeurIPS 2025 的会议中发现有 **100 多条虚假引用** 漏过了审核
- 常见错误包括：
  - 使用真实作者姓名编造论文标题
  - 出版机构或发表年份错误
  - 具有看似真实的元数据但实际并不存在的论文
  - 错误的 DOI 或 arXiv 编号

### 后果

- 部分学术期刊会直接拒收相关论文
- 降低在审稿人眼中的可信度
- 若论文已发表，还可能面临撤稿风险
- 浪费时间寻找根本不存在的参考资料

### 解决方案

**切勿凭记忆生成引用——务必通过编程方式进行验证。**

---

## 引用 API 概览

### 主要 API

| API | 覆盖范围 | 请求频率限制 | 适用场景 |
|-----|----------|-------------|----------|
| **Semantic Scholar** | 2.14 亿篇论文 | 免费密钥：1 次/秒 | 机器学习/AI 相关论文、引用图谱分析 |
| **CrossRef** | 1.4 亿+ DOI | 带邮件回调的限流机制 | DOI 查询、BibTeX 数据检索 |
| **arXiv** | 预印本 | 3 秒延迟 | 机器学习预印本、PDF 文件获取 |
| **OpenAlex** | 2.4 亿+学术成果 | 每日 10 万次请求，10 次/秒 | MAG 的开源替代方案 |

### API 选择指南

```
Need ML paper search? → Semantic Scholar
Have DOI, need BibTeX? → CrossRef content negotiation
Looking for preprint? → arXiv API
Need open data, bulk access? → OpenAlex
```

### 无官方的 Google Scholar API

Google Scholar 并未提供官方 API。通过抓取数据的行为违反了其服务条款。仅当 Semantic Scholar 的收录范围无法满足需求时，才可使用 SerpApi（费用为每月 75 至 275 美元）。

---

## 经过验证的引用处理流程

### 五步操作流程

```
1. SEARCH → Query Semantic Scholar with specific keywords
     ↓
2. VERIFY → Confirm paper exists in 2+ sources
     ↓
3. RETRIEVE → Get BibTeX via DOI content negotiation
     ↓
4. VALIDATE → Confirm the claim appears in source
     ↓
5. ADD → Add verified entry to .bib file
```

### 第一步：搜索

使用 Semantic Scholar 搜索机器学习/人工智能领域的论文：

```python
from semanticscholar import SemanticScholar

sch = SemanticScholar()
results = sch.search_paper("transformer attention mechanism", limit=10)

for paper in results:
    print(f"Title: {paper.title}")
    print(f"Year: {paper.year}")
    print(f"DOI: {paper.externalIds.get('DOI', 'N/A')}")
    print(f"arXiv: {paper.externalIds.get('ArXiv', 'N/A')}")
    print(f"Citation count: {paper.citationCount}")
    print("---")
```

### 第2步：验证存在性

确认该文档在至少两个来源中确实存在：

```python
import requests

def verify_paper(doi=None, arxiv_id=None, title=None):
    """Verify paper exists in multiple sources."""
    sources_found = []

    # Check Semantic Scholar
    sch = SemanticScholar()
    if doi:
        paper = sch.get_paper(f"DOI:{doi}")
        if paper:
            sources_found.append("Semantic Scholar")

    # Check CrossRef (via DOI)
    if doi:
        resp = requests.get(f"https://api.crossref.org/works/{doi}")
        if resp.status_code == 200:
            sources_found.append("CrossRef")

    # Check arXiv
    if arxiv_id:
        resp = requests.get(
            f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
        )
        if "<entry>" in resp.text:
            sources_found.append("arXiv")

    return len(sources_found) >= 2, sources_found
```

### 第3步：获取BibTeX格式数据

通过DOI内容协商机制确保数据的准确性：

```python
import requests

def doi_to_bibtex(doi: str) -> str:
    """Get verified BibTeX from DOI via CrossRef content negotiation."""
    response = requests.get(
        f"https://doi.org/{doi}",
        headers={"Accept": "application/x-bibtex"},
        allow_redirects=True
    )
    response.raise_for_status()
    return response.text

# Example: "Attention Is All You Need"
bibtex = doi_to_bibtex("10.48550/arXiv.1706.03762")
print(bibtex)
```

### 第4步：验证论断的真实性

在引用某篇论文中的特定论断之前，需先确认该论断确实存在：

```python
def get_paper_abstract(doi):
    """Get abstract to verify claims."""
    sch = SemanticScholar()
    paper = sch.get_paper(f"DOI:{doi}")
    return paper.abstract if paper else None

# Verify claim appears in abstract
abstract = get_paper_abstract("10.48550/arXiv.1706.03762")
claim = "attention mechanism"
if claim.lower() in abstract.lower():
    print("Claim appears in paper")
```

### 第5步：添加到参考文献列表

使用统一的关键字格式，将经过验证的条目添加到您的.bib文件中：

```python
def generate_citation_key(bibtex: str) -> str:
    """Generate consistent citation key: author_year_firstword."""
    import re

    # Extract author
    author_match = re.search(r'author\s*=\s*\{([^}]+)\}', bibtex, re.I)
    if author_match:
        first_author = author_match.group(1).split(',')[0].split()[-1]
    else:
        first_author = "unknown"

    # Extract year
    year_match = re.search(r'year\s*=\s*\{?(\d{4})\}?', bibtex, re.I)
    year = year_match.group(1) if year_match else "0000"

    # Extract title first word
    title_match = re.search(r'title\s*=\s*\{([^}]+)\}', bibtex, re.I)
    if title_match:
        first_word = title_match.group(1).split()[0].lower()
        first_word = re.sub(r'[^a-z]', '', first_word)
    else:
        first_word = "paper"

    return f"{first_author.lower()}_{year}_{first_word}"
```

## Python 实现方案

### 完整的引用管理器类

{% raw %}
```python
"""
Citation Manager - Verified citation workflow for ML papers.
"""

import requests
import time
from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass

try:
    from semanticscholar import SemanticScholar
except ImportError:
    print("Install: pip install semanticscholar")
    SemanticScholar = None

@dataclass
class Paper:
    title: str
    authors: List[str]
    year: int
    doi: Optional[str]
    arxiv_id: Optional[str]
    venue: Optional[str]
    citation_count: int
    abstract: Optional[str]

class CitationManager:
    """Manage citations with verification."""

    def __init__(self, api_key: Optional[str] = None):
        self.sch = SemanticScholar(api_key=api_key) if SemanticScholar else None
        self.verified_papers: Dict[str, Paper] = {}

    def search(self, query: str, limit: int = 10) -> List[Paper]:
        """Search for papers using Semantic Scholar."""
        if not self.sch:
            raise RuntimeError("Semantic Scholar not available")

        results = self.sch.search_paper(query, limit=limit)
        papers = []

        for r in results:
            paper = Paper(
                title=r.title,
                authors=[a.name for a in (r.authors or [])],
                year=r.year or 0,
                doi=r.externalIds.get('DOI') if r.externalIds else None,
                arxiv_id=r.externalIds.get('ArXiv') if r.externalIds else None,
                venue=r.venue,
                citation_count=r.citationCount or 0,
                abstract=r.abstract
            )
            papers.append(paper)

        return papers

    def verify(self, paper: Paper) -> Tuple[bool, List[str]]:
        """Verify paper exists in multiple sources."""
        sources = []

        # Already found in Semantic Scholar via search
        sources.append("Semantic Scholar")

        # Check CrossRef if DOI available
        if paper.doi:
            try:
                resp = requests.get(
                    f"https://api.crossref.org/works/{paper.doi}",
                    timeout=10
                )
                if resp.status_code == 200:
                    sources.append("CrossRef")
            except Exception:
                pass

        # Check arXiv if ID available
        if paper.arxiv_id:
            try:
                resp = requests.get(
                    f"http://export.arxiv.org/api/query?id_list={paper.arxiv_id}",
                    timeout=10
                )
                if "<entry>" in resp.text and "<title>" in resp.text:
                    sources.append("arXiv")
            except Exception:
                pass

        return len(sources) >= 2, sources

    def get_bibtex(self, paper: Paper) -> Optional[str]:
        """Get BibTeX for verified paper."""
        if paper.doi:
            try:
                resp = requests.get(
                    f"https://doi.org/{paper.doi}",
                    headers={"Accept": "application/x-bibtex"},
                    timeout=10,
                    allow_redirects=True
                )
                if resp.status_code == 200:
                    return resp.text
            except Exception:
                pass

        # Fallback: generate from paper data
        return self._generate_bibtex(paper)

    def _generate_bibtex(self, paper: Paper) -> str:
        """Generate BibTeX from paper metadata."""
        # Generate citation key
        first_author = paper.authors[0].split()[-1] if paper.authors else "unknown"
        first_word = paper.title.split()[0].lower().replace(',', '').replace(':', '')
        key = f"{first_author.lower()}_{paper.year}_{first_word}"

        # Format authors
        authors = " and ".join(paper.authors) if paper.authors else "Unknown"

        bibtex = f"""@article{{{key},
  title = {{{paper.title}}},
  author = {{{authors}}},
  year = {{{paper.year}}},
  {'doi = {' + paper.doi + '},' if paper.doi else ''}
  {'eprint = {' + paper.arxiv_id + '},' if paper.arxiv_id else ''}
  {'journal = {' + paper.venue + '},' if paper.venue else ''}
}}"""
        return bibtex

    def cite(self, query: str) -> Optional[str]:
        """Full workflow: search, verify, return BibTeX."""
        # Search
        papers = self.search(query, limit=5)
        if not papers:
            return None

        # Take top result
        paper = papers[0]

        # Verify
        verified, sources = self.verify(paper)
        if not verified:
            print(f"Warning: Could only verify in {sources}")

        # Get BibTeX
        bibtex = self.get_bibtex(paper)

        # Cache
        if bibtex:
            self.verified_papers[paper.title] = paper

        return bibtex


# Usage example
if __name__ == "__main__":
    cm = CitationManager()

    # Search and cite
    bibtex = cm.cite("attention is all you need transformer")
    if bibtex:
        print(bibtex)
```
### 快速功能

```python
def quick_cite(query: str) -> str:
    """One-liner citation."""
    cm = CitationManager()
    return cm.cite(query)

def batch_cite(queries: List[str], output_file: str = "references.bib"):
    """Cite multiple papers and save to file."""
    cm = CitationManager()
    bibtex_entries = []

    for query in queries:
        print(f"Processing: {query}")
        bibtex = cm.cite(query)
        if bibtex:
            bibtex_entries.append(bibtex)
        time.sleep(1)  # Rate limiting

    with open(output_file, 'w') as f:
        f.write("\n\n".join(bibtex_entries))

    print(f"Saved {len(bibtex_entries)} citations to {output_file}")
```

## BibTeX 管理

### BibTeX 与 BibLaTeX 的对比

| 功能特性 | BibTeX | BibLaTeX |
|---------|--------|----------|
| Unicode 支持 | 有限 | 完全支持 |
| 条目类型 | 标准型 | 扩展型（@online、@dataset） |
| 自定义程度 | 有限 | 非常灵活 |
| 后端引擎 | bibtex | Biber（推荐） |

**建议**：在提交会议论文时，建议结合 BibTeX 使用 natbib——所有主流会议的模板（NeurIPS、ICML、ICLR、ACL、AAAI、COLM）均预置了 natbib 及对应的 `.bst` 文件。对于可以自行控制模板的期刊文章或个人项目，可选择搭配 Biber 的 BibLaTeX。

### LaTeX 配置

```latex
% In preamble
\usepackage[
    backend=biber,
    style=numeric,
    sorting=none
]{biblatex}
\addbibresource{references.bib}

% In document
\cite{vaswani_2017_attention}

% At end
\printbibliography
```

### 引用命令

```latex
\cite{key}      % Numeric: [1]
\citep{key}     % Parenthetical: (Author, 2020)
\citet{key}     % Textual: Author (2020)
\citeauthor{key} % Just author name
\citeyear{key}  % Just year
```

### 一致的引用键格式

请遵循以下格式：`作者_年份_首词`

```
vaswani_2017_attention
devlin_2019_bert
brown_2020_language
```

## 常见引用格式

### 会议论文

```bibtex
@inproceedings{vaswani_2017_attention,
  title = {Attention Is All You Need},
  author = {Vaswani, Ashish and Shazeer, Noam and Parmar, Niki and
            Uszkoreit, Jakob and Jones, Llion and Gomez, Aidan N and
            Kaiser, Lukasz and Polosukhin, Illia},
  booktitle = {Advances in Neural Information Processing Systems},
  volume = {30},
  year = {2017},
  publisher = {Curran Associates, Inc.}
}
```

### 期刊文章

```bibtex
@article{hochreiter_1997_long,
  title = {Long Short-Term Memory},
  author = {Hochreiter, Sepp and Schmidhuber, J{\"u}rgen},
  journal = {Neural Computation},
  volume = {9},
  number = {8},
  pages = {1735--1780},
  year = {1997},
  publisher = {MIT Press}
}
```

### arXiv 预印本

```bibtex
@misc{brown_2020_language,
  title = {Language Models are Few-Shot Learners},
  author = {Brown, Tom and Mann, Benjamin and Ryder, Nick and others},
  year = {2020},
  eprint = {2005.14165},
  archiveprefix = {arXiv},
  primaryclass = {cs.CL}
}
```

---

## 故障排除

### 常见问题

**问题：Semantic Scholar 未返回任何结果**
- 尝试使用更具体的关键词
- 检查作者姓名的拼写
- 对完整短语加上引号

**问题：DOI 无法转换为 BibTeX 格式**
- 该 DOI 可能已注册，但未与 CrossRef 关联
- 如有 arXiv ID，可尝试使用该编号
- 手动根据元数据生成 BibTeX 文件

**问题：遇到速率限制错误**
- 在多次请求之间添加延迟（1-3 秒）
- 如有 API 密钥，请使用它
- 缓存结果以避免重复查询

**问题：BibTeX 文件存在编码问题**
- 使用正确的 LaTeX 转义格式：用 `{\"u}` 表示 “ü”
- 确保文件为 UTF-8 编码
- 使用 BibLaTeX 结合 Biber 工具以更好地处理 Unicode 字符

### 验证清单

在添加引用之前，请确认以下事项：
- [ ] 该论文在至少 2 个来源中均有记载
- [ ] DOI 或 arXiv ID 已经过验证
- [ ] BibTeX 文件是从外部获取的（而非凭记忆生成）
- [ ] 引用类型正确（如 @inproceedings 或 @article）
- [ ] 作者姓名完整且格式正确
- [ ] 年份和会议/出版地信息已核实
- [ ] 引用键的格式统一

---

## 其他资源

**API 接口：**
- Semantic Scholar：https://api.semanticscholar.org/api-docs/
- CrossRef：https://www.crossref.org/documentation/retrieve-metadata/rest-api/
- arXiv：https://info.arxiv.org/help/api/basics.html
- OpenAlex：https://docs.openalex.org/

**Python 库：**
- `semanticscholar`：https://pypi.org/project/semanticscholar/
- `arxiv`：https://pypi.org/project/arxiv/
- `habanero`（用于处理 CrossRef 数据）：https://github.com/sckott/habanero

**验证工具：**
- Citely：https://citely.ai/citation-checker
- ReciteWorks：https://reciteworks.com/
