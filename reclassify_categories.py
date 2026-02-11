#!/usr/bin/env python3
"""
questions.csv（過去問）の category を、question_text と explanation のキーワードに基づき
体系的なジャンルに自動で再分類するスクリプト。AI模擬用の ai_questions.csv は対象外。
"""
import csv
import os

CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "questions.csv")

# 優先順位順: (カテゴリ名, キーワードのリスト)
CLASSIFICATION_RULES = [
    ("3-1 調査", ["J-PlatPat", "調査", "検索"]),
    ("5-2 エンフォースメント", ["侵害", "警告", "差止", "損害賠償"]),
    ("5-1 契約", ["ライセンス", "許諾", "譲渡", "契約"]),
    ("4-1 ブランド保護", ["商標", "ブランド"]),
    ("4-2 技術保護", ["特許", "発明", "実用新案"]),
    ("4-3 コンテンツ保護", ["著作権", "コンテンツ"]),
    ("4-4 デザイン保護", ["意匠", "デザイン"]),
    ("6. 関係法規", ["条約", "パリ", "PCT"]),
]

DEFAULT_CATEGORY = "2-1 法務"


def classify_category(question_text: str, explanation: str) -> str:
    """question_text と explanation に含まれるキーワードから、優先順位に従い category を判定する。"""
    combined = (question_text or "") + " " + (explanation or "")
    for category, keywords in CLASSIFICATION_RULES:
        if any(kw in combined for kw in keywords):
            return category
    return DEFAULT_CATEGORY


def main():
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    counts = {}
    for row in rows:
        new_cat = classify_category(
            row.get("question_text", ""),
            row.get("explanation", ""),
        )
        row["category"] = new_cat
        counts[new_cat] = counts.get(new_cat, 0) + 1

    with open(CSV_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print("分類結果（件数）:")
    order = list(dict.fromkeys([r[0] for r in CLASSIFICATION_RULES]))
    if DEFAULT_CATEGORY not in order:
        order.append(DEFAULT_CATEGORY)
    for cat in order:
        if cat in counts:
            print(f"  {cat}: {counts[cat]} 件")
    print(f"  合計: {sum(counts.values())} 件")


if __name__ == "__main__":
    main()
