#!/usr/bin/env python3
"""
知的財産管理技能検定2級 学習用クイズアプリ
データベース初期化スクリプト（SQLite）
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "quiz.db")

SAMPLE_DATA = [
    {
        "exam_type": "第52回 学科",
        "category": "特許法（職務発明）",
        "scenario": None,
        "question_text": "ア～エを比較して、職務発明に関して、最も適切と考えられるものはどれか。",
        "option_a": "従業者が職務発明を完成した場合であっても、当該従業者がその職務発明について特許を受ける権利を、その発生したときから有しないことがある。",
        "option_b": "企業の取締役は、特許法に規定される「従業者等」に含まれない。",
        "option_c": "従業者が特許を受ける権利を会社に譲渡した場合、予め契約により定めのある場合に限り会社から相当の利益を受ける権利を得る。",
        "option_d": "従業者が職務発明について特許権を取得した場合において会社がその発明を実施しようとする場合には、会社は特許権を取得した従業者から実施の許諾を受ける必要がある。",
        "correct_answer": "ウ",
        "explanation": "特許法第35条参照。相当の利益を受ける権利は、契約等により定められる。",
    },
    {
        "exam_type": "第52回 学科",
        "category": "著作権法（公衆送信権）",
        "scenario": None,
        "question_text": "ア～エを比較して、公衆送信権等に関して、最も不適切と考えられるものはどれか。",
        "option_a": "プログラムの著作物を同一構内における電気通信設備により送信することは、公衆送信に該当する。",
        "option_b": "公衆送信は、公衆によって直接受信されることを目的とした無線通信又は有線電気通信の送信のことであるため、放送・有線放送の他、自動公衆送信も含まれる。",
        "option_c": "レコード製作者の送信可能化権の対象となるのは、商業用レコードのみである。",
        "option_d": "複製権又は公衆送信権を有する者は、出版権を設定することができる。",
        "correct_answer": "イ",
        "explanation": "同一構内送信は公衆送信から除かれるが、プログラムの著作物は例外として公衆送信に含まれる。",
    },
    {
        "exam_type": "第52回 実技",
        "category": "特許法（侵害・訴訟）",
        "scenario": "材料メーカーX社は、プラスチックAに関する特許権Pを有している。X社の知的財産部の部員は、他社が販売しているプラスチックを調査したところ、Y社が販売しているプラスチックBで特許権Pに係る特許発明が実施されていることが判明したため、差止請求訴訟,損害賠償請求訴訟を提起することを検討している。",
        "question_text": "ア～エを比較して、部員の発言として、最も適切と考えられるものを1つ選びなさい。",
        "option_a": "「わが社はW社に対して特許権Pの全範囲について専用実施権を設定していますが、わが社はY社に対して特許権Pに基づいて差止請求訴訟を提起することができます。」",
        "option_b": "「わが社は、差止請求をするに際し、Y社が販売しているプラスチックBの廃棄を請求することはできません。」",
        "option_c": "「特許権PについてY社の侵害行為に対する損害賠償が認められた場合、Y社に対して刑事罰の適用はありません。」",
        "option_d": "「Y社による特許権Pの侵害における過失の立証責任はわが社にありますので、早急に証拠を収集しましょう。」",
        "correct_answer": "ア",
        "explanation": "専用実施権を設定した後でも、特許権者は差止請求権を有する（判例・通説）。",
    },
]


def init_schema(conn: sqlite3.Connection) -> None:
    """questions と history テーブルを作成する。"""
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
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id INTEGER NOT NULL,
            is_correct BOOLEAN NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (question_id) REFERENCES questions(id)
        )
        """
    )
    conn.commit()


def insert_sample_data(conn: sqlite3.Connection) -> None:
    """サンプル問題をINSERTする。"""
    for row in SAMPLE_DATA:
        conn.execute(
            """
            INSERT INTO questions (
                exam_type, category, scenario, question_text,
                option_a, option_b, option_c, option_d,
                correct_answer, explanation
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row["exam_type"],
                row["category"],
                row["scenario"],
                row["question_text"],
                row["option_a"],
                row["option_b"],
                row["option_c"],
                row["option_d"],
                row["correct_answer"],
                row["explanation"],
            ),
        )
    conn.commit()


def main() -> None:
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        init_schema(conn)
        insert_sample_data(conn)
        print(f"DB initialized: {DB_PATH}")
        cur = conn.execute("SELECT COUNT(*) FROM questions")
        print(f"Inserted {cur.fetchone()[0]} questions.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
