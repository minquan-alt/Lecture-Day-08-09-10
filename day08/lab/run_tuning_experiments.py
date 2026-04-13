#!/usr/bin/env python3
"""
Simple experiment runner for Day08 lab.

Fixed parameters:
- CHUNK_SIZE = 500
- CHUNK_OVERLAP = 80
- CHUNK_STRATEGY = _split_by_paragraph_recursive

Runs only 3 retrieval variants:
- dense
- sparse
- hybrid (0.5 / 0.5)

Uses dataset: data/final_test_data.json
"""

import csv
import importlib
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


CHUNK_SIZE = 500
CHUNK_OVERLAP = 80
CHUNK_STRATEGY_FN = "_split_by_paragraph_recursive"
TOP_K_SEARCH = 10
TOP_K_SELECT = 3

TEST_DATA_PATH = Path(__file__).parent / "data" / "final_test_data.json"
RESULTS_ROOT = Path(__file__).parent / "results" / "experiments"

RETRIEVAL_VARIANTS = [
    {"retrieval_mode": "dense", "label": "dense"},
    {"retrieval_mode": "sparse", "label": "sparse"},
    {
        "retrieval_mode": "hybrid",
        "hybrid_dense_weight": 0.5,
        "hybrid_sparse_weight": 0.5,
        "label": "hybrid_50_50",
    },
]


eval_mod = None
index_mod = None
rag_mod = None
ORIGINAL_CHUNK_DOCUMENT = None
ORIGINAL_RETRIEVE_HYBRID = None


def load_modules() -> None:
    global eval_mod, index_mod, rag_mod
    global ORIGINAL_CHUNK_DOCUMENT, ORIGINAL_RETRIEVE_HYBRID

    eval_mod = importlib.import_module("eval")
    index_mod = importlib.import_module("index")
    rag_mod = importlib.import_module("rag_answer")

    ORIGINAL_CHUNK_DOCUMENT = index_mod.chunk_document
    ORIGINAL_RETRIEVE_HYBRID = rag_mod.retrieve_hybrid


def _build_chunk_document_with_fixed_strategy(splitter):
    def _chunk_document(doc: Dict[str, Any]) -> List[Dict[str, Any]]:
        text = doc["text"]
        base_metadata = doc["metadata"].copy()
        chunks: List[Dict[str, Any]] = []

        sections = re.split(r"(===.*?===)", text)
        current_section = "General"
        current_section_text = ""

        for part in sections:
            if re.match(r"===.*?===", part):
                if current_section_text.strip():
                    chunks.extend(
                        splitter(
                            current_section_text.strip(),
                            base_metadata=base_metadata,
                            section=current_section,
                        )
                    )
                current_section = part.strip("= ").strip()
                current_section_text = ""
            else:
                current_section_text += part

        if current_section_text.strip():
            chunks.extend(
                splitter(
                    current_section_text.strip(),
                    base_metadata=base_metadata,
                    section=current_section,
                )
            )

        return chunks

    return _chunk_document


def apply_fixed_chunking() -> None:
    splitter = getattr(index_mod, CHUNK_STRATEGY_FN)
    index_mod.CHUNK_SIZE = CHUNK_SIZE
    index_mod.CHUNK_OVERLAP = CHUNK_OVERLAP
    index_mod.chunk_document = _build_chunk_document_with_fixed_strategy(splitter)


def apply_hybrid_weights(dense_w: Optional[float], sparse_w: Optional[float]) -> None:
    if dense_w is None or sparse_w is None:
        rag_mod.retrieve_hybrid = ORIGINAL_RETRIEVE_HYBRID
        return

    def _wrapped_hybrid(query: str, top_k: int = rag_mod.TOP_K_SEARCH, **_: Any):
        return ORIGINAL_RETRIEVE_HYBRID(
            query,
            top_k=top_k,
            dense_weight=dense_w,
            sparse_weight=sparse_w,
        )

    rag_mod.retrieve_hybrid = _wrapped_hybrid


def compute_averages(rows: List[Dict[str, Any]]) -> Dict[str, Optional[float]]:
    metrics = ["faithfulness", "relevance", "context_recall", "completeness"]
    out: Dict[str, Optional[float]] = {}
    for metric in metrics:
        values = [r.get(metric) for r in rows if isinstance(r.get(metric), (int, float))]
        out[metric] = (sum(values) / len(values)) if values else None
    return out


def _fmt_score(v: Optional[float]) -> str:
    if v is None:
        return "N/A"
    return f"{v:.2f}/5"


def _fmt_delta(base: Optional[float], var: Optional[float]) -> str:
    if base is None or var is None:
        return "N/A"
    return f"{(var - base):+.2f}"


def _pick_variant(results: List[Dict[str, Any]], preferred_label: str) -> Optional[Dict[str, Any]]:
    for item in results:
        if item["label"] == preferred_label:
            return item
    return None


def _find_weak_questions(rows: List[Dict[str, Any]], top_n: int = 3) -> List[Dict[str, Any]]:
    ranked = []
    for r in rows:
        vals = [
            r.get("faithfulness"),
            r.get("relevance"),
            r.get("context_recall"),
            r.get("completeness"),
        ]
        numeric = [v for v in vals if isinstance(v, (int, float))]
        avg = (sum(numeric) / len(numeric)) if numeric else -1
        ranked.append((avg, r))
    ranked.sort(key=lambda x: x[0])
    return [r for _, r in ranked[:top_n]]


def build_tuning_log_markdown(results: List[Dict[str, Any]]) -> str:
    baseline = _pick_variant(results, "dense")
    if baseline is None:
        raise ValueError("Baseline (dense) result not found")

    variant1 = _pick_variant(results, "hybrid_50_50")
    if variant1 is None:
        variant1 = next((x for x in results if x["label"] != "dense"), None)

    variant2 = _pick_variant(results, "sparse")
    if variant2 is not None and variant1 is not None and variant2["label"] == variant1["label"]:
        variant2 = None

    bavg = baseline["averages"]
    v1avg = variant1["averages"] if variant1 else {}
    v2avg = variant2["averages"] if variant2 else {}

    weakest = _find_weak_questions(baseline["rows"], top_n=3)
    weakest_lines = []
    for r in weakest:
        weakest_lines.append(
            f"- {r.get('id')} ({r.get('category')}): "
            f"F={r.get('faithfulness')}, R={r.get('relevance')}, "
            f"Rc={r.get('context_recall')}, C={r.get('completeness')}"
        )

    today = datetime.now().strftime("%Y-%m-%d")

    md = [
        "# Tuning Log — RAG Pipeline (Auto-generated)",
        "",
        "> Auto-generated from `run_tuning_experiments.py` results.",
        "",
        "---",
        "",
        "## Baseline (Sprint 2)",
        "",
        f"**Ngày:** {today}",
        "**Config:**",
        "```",
        "retrieval_mode = \"dense\"",
        f"chunk_size = {CHUNK_SIZE} tokens",
        f"overlap = {CHUNK_OVERLAP} tokens",
        f"top_k_search = {TOP_K_SEARCH}",
        f"top_k_select = {TOP_K_SELECT}",
        "use_rerank = False",
        f"chunk_strategy = \"{CHUNK_STRATEGY_FN}\"",
        "```",
        "",
        "**Scorecard Baseline:**",
        "| Metric           | Average Score |",
        "| ---------------- | ------------- |",
        f"| Faithfulness     | {_fmt_score(bavg.get('faithfulness'))} |",
        f"| Answer Relevance | {_fmt_score(bavg.get('relevance'))} |",
        f"| Context Recall   | {_fmt_score(bavg.get('context_recall'))} |",
        f"| Completeness     | {_fmt_score(bavg.get('completeness'))} |",
        "",
        "**Câu hỏi yếu nhất (điểm thấp):**",
        *weakest_lines,
        "",
        "**Giả thuyết nguyên nhân (Error Tree):**",
        "- [ ] Indexing: Chunking cắt giữa điều khoản",
        "- [ ] Indexing: Metadata thiếu effective_date",
        "- [ ] Retrieval: Dense bỏ lỡ exact keyword / alias",
        "- [ ] Retrieval: Top-k quá ít -> thiếu evidence",
        "- [ ] Generation: Prompt không đủ grounding",
        "- [ ] Generation: Context quá dài -> lost in the middle",
        "",
        "---",
        "",
    ]

    if variant1 is not None:
        md.extend([
            "## Variant 1 (Sprint 3)",
            "",
            f"**Ngày:** {today}",
            f"**Biến thay đổi:** retrieval_mode = \"{variant1['config']['retrieval_mode']}\"",
            "**Lý do chọn biến này:**",
            "- Ưu tiên test retrieval variant theo đúng plan (dense/sparse/hybrid).",
            "",
            "**Config thay đổi:**",
            "```",
            f"retrieval_mode = \"{variant1['config']['retrieval_mode']}\"",
            f"chunk_size = {CHUNK_SIZE}",
            f"overlap = {CHUNK_OVERLAP}",
            f"top_k_search = {TOP_K_SEARCH}",
            f"top_k_select = {TOP_K_SELECT}",
            "use_rerank = False",
            "```",
            "",
            "**Scorecard Variant 1:**",
            "| Metric           | Baseline | Variant 1 | Delta |",
            "| ---------------- | -------- | --------- | ----- |",
            f"| Faithfulness     | {_fmt_score(bavg.get('faithfulness'))} | {_fmt_score(v1avg.get('faithfulness'))} | {_fmt_delta(bavg.get('faithfulness'), v1avg.get('faithfulness'))} |",
            f"| Answer Relevance | {_fmt_score(bavg.get('relevance'))} | {_fmt_score(v1avg.get('relevance'))} | {_fmt_delta(bavg.get('relevance'), v1avg.get('relevance'))} |",
            f"| Context Recall   | {_fmt_score(bavg.get('context_recall'))} | {_fmt_score(v1avg.get('context_recall'))} | {_fmt_delta(bavg.get('context_recall'), v1avg.get('context_recall'))} |",
            f"| Completeness     | {_fmt_score(bavg.get('completeness'))} | {_fmt_score(v1avg.get('completeness'))} | {_fmt_delta(bavg.get('completeness'), v1avg.get('completeness'))} |",
            "",
            "**Nhận xét:**",
            "- Xem chi tiết từng câu trong `scorecard.md` và `rows.json` của variant.",
            "",
            "**Kết luận:**",
            "- Dựa trên delta ở bảng trên để quyết định variant có tốt hơn baseline hay không.",
            "",
            "---",
            "",
        ])

    if variant2 is not None:
        md.extend([
            "## Variant 2 (nếu có thời gian)",
            "",
            f"**Biến thay đổi:** retrieval_mode = \"{variant2['config']['retrieval_mode']}\"",
            "**Config:**",
            "```",
            f"retrieval_mode = \"{variant2['config']['retrieval_mode']}\"",
            f"chunk_size = {CHUNK_SIZE}",
            f"overlap = {CHUNK_OVERLAP}",
            f"top_k_search = {TOP_K_SEARCH}",
            f"top_k_select = {TOP_K_SELECT}",
            "use_rerank = False",
            "```",
            "",
            "**Scorecard Variant 2:**",
            "| Metric           | Baseline | Variant 1 | Variant 2 | Best |",
            "| ---------------- | -------- | --------- | --------- | ---- |",
            f"| Faithfulness     | {_fmt_score(bavg.get('faithfulness'))} | {_fmt_score(v1avg.get('faithfulness'))} | {_fmt_score(v2avg.get('faithfulness'))} | ? |",
            f"| Answer Relevance | {_fmt_score(bavg.get('relevance'))} | {_fmt_score(v1avg.get('relevance'))} | {_fmt_score(v2avg.get('relevance'))} | ? |",
            f"| Context Recall   | {_fmt_score(bavg.get('context_recall'))} | {_fmt_score(v1avg.get('context_recall'))} | {_fmt_score(v2avg.get('context_recall'))} | ? |",
            f"| Completeness     | {_fmt_score(bavg.get('completeness'))} | {_fmt_score(v1avg.get('completeness'))} | {_fmt_score(v2avg.get('completeness'))} | ? |",
            "",
            "---",
            "",
        ])

    md.extend([
        "## Tóm tắt học được",
        "",
        "1. **Lỗi phổ biến nhất trong pipeline này là gì?**",
        "   > Điền theo kết quả thực tế sau khi review rows chi tiết.",
        "",
        "2. **Biến nào có tác động lớn nhất tới chất lượng?**",
        "   > So sánh delta các variant để kết luận.",
        "",
        "3. **Nếu có thêm 1 giờ, nhóm sẽ thử gì tiếp theo?**",
        "   > Bật rerank hoặc query transform rồi chạy lại cùng testset.",
    ])

    return "\n".join(md)


def run_variant(
    run_idx: int,
    variant: Dict[str, Any],
    test_questions: List[Dict[str, Any]],
    output_root: Path,
    rebuild_index: bool,
) -> Dict[str, Any]:
    label = variant["label"]
    retrieval_mode = variant["retrieval_mode"]

    run_dir = output_root / f"{run_idx:02d}_{label}"
    run_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n[run {run_idx:02d}] {label}", flush=True)

    apply_fixed_chunking()

    if rebuild_index:
        print("[index] Rebuilding index (REBUILD_INDEX=1)", flush=True)
        index_mod.build_index()

    if retrieval_mode == "hybrid":
        apply_hybrid_weights(variant.get("hybrid_dense_weight"), variant.get("hybrid_sparse_weight"))
    else:
        apply_hybrid_weights(None, None)

    config = {
        "retrieval_mode": retrieval_mode,
        "top_k_search": TOP_K_SEARCH,
        "top_k_select": TOP_K_SELECT,
        "use_rerank": False,
        "label": label,
    }

    rows = eval_mod.run_scorecard(config=config, test_questions=test_questions, verbose=False)
    averages = compute_averages(rows)

    (run_dir / "rows.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    (run_dir / "config.json").write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    (run_dir / "scorecard.md").write_text(
        eval_mod.generate_scorecard_summary(rows, label),
        encoding="utf-8",
    )

    print(
        f"[run {run_idx:02d}] avg -> "
        f"F={averages.get('faithfulness')} "
        f"R={averages.get('relevance')} "
        f"Rc={averages.get('context_recall')} "
        f"C={averages.get('completeness')}",
        flush=True,
    )

    return {
        "label": label,
        "config": config,
        "rows": rows,
        "averages": averages,
        "run_dir": str(run_dir),
    }


def write_summary(output_root: Path, results: List[Dict[str, Any]]) -> None:
    summary_rows = []
    for item in results:
        avg = item["averages"]
        summary_rows.append({
            "label": item["label"],
            "retrieval_mode": item["config"]["retrieval_mode"],
            "faithfulness": avg.get("faithfulness"),
            "relevance": avg.get("relevance"),
            "context_recall": avg.get("context_recall"),
            "completeness": avg.get("completeness"),
            "run_dir": item["run_dir"],
        })

    csv_path = output_root / "master_summary.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary_rows[0].keys()))
        writer.writeheader()
        writer.writerows(summary_rows)

    dense = next((x for x in results if x["label"] == "dense"), None)
    if dense is not None:
        for item in results:
            if item["label"] == "dense":
                continue
            name = f"ab_dense_vs_{item['label']}.csv"
            combined = dense["rows"] + item["rows"]
            with open(output_root / name, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=list(combined[0].keys()))
                writer.writeheader()
                writer.writerows(combined)

    note = [
        "# Simplified Experiment Summary",
        "",
        f"Dataset: {TEST_DATA_PATH}",
        f"Chunk strategy: {CHUNK_STRATEGY_FN}",
        f"Chunk size/overlap: {CHUNK_SIZE}/{CHUNK_OVERLAP}",
        "",
        "## Retrieval Variants",
        "- dense",
        "- sparse",
        "- hybrid_50_50",
        "",
        "## Future (commented for later)",
        "- Rerank experiments",
        "- Query transform experiments",
    ]
    (output_root / "README.md").write_text("\n".join(note), encoding="utf-8")

    tuning_log_md = build_tuning_log_markdown(results)
    (output_root / "tuning-log.md").write_text(tuning_log_md, encoding="utf-8")


def main() -> None:
    if not TEST_DATA_PATH.exists():
        raise FileNotFoundError(f"Missing dataset: {TEST_DATA_PATH}")

    load_modules()

    test_questions = json.loads(TEST_DATA_PATH.read_text(encoding="utf-8"))
    if not isinstance(test_questions, list) or not test_questions:
        raise ValueError("final_test_data.json must be a non-empty list")

    rebuild_index = os.getenv("REBUILD_INDEX", "0").strip().lower() in {"1", "true", "yes", "y"}

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_root = RESULTS_ROOT / f"simple_{timestamp}"
    output_root.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("Simple tuning run")
    print(f"Dataset: {TEST_DATA_PATH}")
    print(f"Output: {output_root}")
    print(f"REBUILD_INDEX: {rebuild_index}")
    print("=" * 80)

    results: List[Dict[str, Any]] = []

    try:
        for i, variant in enumerate(RETRIEVAL_VARIANTS, start=1):
            results.append(
                run_variant(
                    run_idx=i,
                    variant=variant,
                    test_questions=test_questions,
                    output_root=output_root,
                    rebuild_index=(rebuild_index and i == 1),
                )
            )

        write_summary(output_root, results)
        print("\nDone. See results in:", output_root)

        # FUTURE EXPERIMENTS (run later):
        # 1) Rerank:
        #    - set config["use_rerank"] = True and rerun each retrieval variant.
        # 2) Query transform:
        #    - wrap eval_mod.rag_answer with a transform_query-based wrapper,
        #      then compare against current 3 retrieval runs.

    finally:
        if index_mod is not None and ORIGINAL_CHUNK_DOCUMENT is not None:
            index_mod.chunk_document = ORIGINAL_CHUNK_DOCUMENT
        if rag_mod is not None and ORIGINAL_RETRIEVE_HYBRID is not None:
            rag_mod.retrieve_hybrid = ORIGINAL_RETRIEVE_HYBRID


if __name__ == "__main__":
    main()
