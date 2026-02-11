#!/usr/bin/env python3
"""
questions.csv（過去問）と ai_questions.csv（AI模擬）を読み込み、
quiz.db の questions テーブルを更新する。
- 一旦 questions テーブルを空にする。
- questions.csv をインポートする。
- ai_questions.csv をインポートする。
"""
import csv
import os
import sqlite3

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, "quiz.db")
QUESTIONS_CSV = os.path.join(SCRIPT_DIR, "questions.csv")
AI_QUESTIONS_CSV = os.path.join(SCRIPT_DIR, "ai_questions.csv")


def ensure_schema(conn: sqlite3.Connection) -> None:
    """questions テーブルが存在することを保証する。"""
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exam_type TEXT NOT NULL,
            category TEXT NOT NULL,
            scenario TEXT,
            question_text TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            explanation TEXT
        )
        """
    )


def import_csv_into_db(conn: sqlite3.Connection, csv_path: str) -> int:
    """1つのCSVを questions テーブルに追記する。挿入件数を返す。"""
    if not os.path.exists(csv_path):
        return 0
    count = 0
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            exam_type = (row.get("exam_type") or "").strip()
            category = (row.get("category") or "").strip()
            scenario = (row.get("scenario") or "").strip() or None
            question_text = (row.get("question_text") or "").strip()
            option_a = (row.get("option_a") or "").strip() or "-"
            option_b = (row.get("option_b") or "").strip() or "-"
            option_c = (row.get("option_c") or "").strip() or "-"
            option_d = (row.get("option_d") or "").strip() or "-"
            correct_answer = (row.get("correct_answer") or "").strip()
            explanation = (row.get("explanation") or "").strip()
            if not question_text:
                continue
            conn.execute(
                """
                INSERT INTO questions (
                    exam_type, category, scenario, question_text,
                    option_a, option_b, option_c, option_d,
                    correct_answer, explanation
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    exam_type,
                    category,
                    scenario,
                    question_text,
                    option_a,
                    option_b,
                    option_c,
                    option_d,
                    correct_answer,
                    explanation,
                ),
            )
            count += 1
    return count


def main() -> None:
    if not os.path.exists(QUESTIONS_CSV):
        print(f"Error: {QUESTIONS_CSV} が見つかりません。")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        ensure_schema(conn)
        conn.execute("DELETE FROM questions")

        n1 = import_csv_into_db(conn, QUESTIONS_CSV)
        n2 = import_csv_into_db(conn, AI_QUESTIONS_CSV)

        conn.commit()
        print(f"Updated: {DB_PATH}")
        print(f"  過去問 (questions.csv): {n1} 件")
        print(f"  AI模擬 (ai_questions.csv): {n2} 件")
        print(f"  合計: {n1 + n2} 件")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
