#!/usr/bin/env python3
"""
知的財産管理技能検定2級 学習用クイズアプリ
Flask バックエンド
PythonAnywhere 等の WSGI 環境でも動作するよう、絶対パスとテーブル自動作成を行う。
"""
import os
import sqlite3
from flask import Flask, render_template, jsonify, request, session

app = Flask(__name__)
# セッション利用のため SECRET_KEY を設定（環境変数優先、未設定時はランダム）
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY") or os.urandom(24).hex()
# サーバー上のどこから実行されても同じ DB を指す絶対パス
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "quiz.db")

# 連続正解数に応じた称号（コンボ → 称号名）
COMBO_TITLES = [
    (50, "知財の神"),
    (30, "弁理士レベル"),
    (20, "歩く知的財産権法"),
    (10, "特許庁の注目株"),
    (5, "駆け出し知財担当"),
]


def get_title_for_combo(combo):
    """現在のコンボ数に応じた称号を返す。"""
    for threshold, title in COMBO_TITLES:
        if combo >= threshold:
            return title
    return None


def ensure_tables(conn):
    """questions と history（復習用・間違えた問題を保存するテーブル）が無ければ作成する。"""
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
            is_correct INTEGER NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (question_id) REFERENCES questions(id)
        )
        """
    )
    conn.commit()


def get_db():
    """DB接続（Rowでdictのように取得）。初回接続時にテーブルが無ければ作成する。"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        ensure_tables(conn)
    except sqlite3.Error:
        conn.close()
        raise
    return conn


@app.route("/")
def index():
    return render_template("index.html")


def _apply_exam_series(query, params, alias=""):
    """exam_series に応じた WHERE 句を追加する。alias は 'q.' のようにテーブル接頭辞（review用）。"""
    exam_series = request.args.get("exam_series")
    if not exam_series:
        return
    pre = alias
    if exam_series == "past":
        query.append(
            " AND (" + pre + "exam_type LIKE ? OR " + pre + "exam_type LIKE ? OR " + pre + "exam_type LIKE ?)"
        )
        params.extend(["第50回%", "第51回%", "第52回%"])
    elif exam_series == "ai":
        query.append(" AND " + pre + "exam_type = ?")
        params.append("AI模擬")
    elif exam_series in ("第50回", "第51回", "第52回"):
        query.append(" AND " + pre + "exam_type LIKE ?")
        params.append(exam_series + "%")


@app.route("/api/questions")
def api_questions():
    """問題一覧。mode=review のときは「最後に不正解だった問題」のみ返す。exam_series で試験種別・回を指定。"""
    mode = request.args.get("mode")
    category = request.args.get("category")
    conn = None
    try:
        conn = get_db()
        if mode == "review":
            query_parts = [
                "SELECT q.* FROM questions q ",
                "JOIN history h ON q.id = h.question_id ",
                "WHERE h.timestamp = (SELECT MAX(timestamp) FROM history WHERE question_id = q.id) ",
                "AND h.is_correct = 0",
            ]
            params = []
            _apply_exam_series(query_parts, params, "q.")
            if category:
                query_parts.append(" AND q.category = ?")
                params.append(category)
            query_parts.append(" ORDER BY q.id")
            cur = conn.execute("".join(query_parts), params)
        else:
            query_parts = [
                "SELECT id, exam_type, category, scenario, question_text, ",
                "option_a, option_b, option_c, option_d, correct_answer, explanation ",
                "FROM questions WHERE 1=1",
            ]
            params = []
            _apply_exam_series(query_parts, params, "")
            if category:
                query_parts.append(" AND category = ?")
                params.append(category)
            query_parts.append(" ORDER BY id")
            cur = conn.execute("".join(query_parts), params)
        rows = cur.fetchall()
        return jsonify([dict(r) for r in rows])
    except sqlite3.Error as e:
        app.logger.exception("api_questions: %s", e)
        return jsonify({"error": "database_error", "message": "問題の取得に失敗しました。"}), 500
    finally:
        if conn:
            conn.close()


@app.route("/api/record", methods=["POST"])
def api_record():
    """回答結果を history に記録する。一問でも不正解なら即座に保存され、復習一覧に反映される。"""
    data = request.get_json(force=True, silent=True) or {}
    question_id = data.get("question_id")
    is_correct = data.get("is_correct")
    if question_id is None or is_correct is None:
        return jsonify({"error": "question_id and is_correct required"}), 400
    conn = None
    try:
        conn = get_db()
        conn.execute(
            "INSERT INTO history (question_id, is_correct) VALUES (?, ?)",
            (int(question_id), 1 if is_correct else 0),
        )
        conn.commit()
        return jsonify({"ok": True})
    except (ValueError, sqlite3.IntegrityError) as e:
        app.logger.warning("api_record validation: %s", e)
        return jsonify({"error": "invalid_data"}), 400
    except sqlite3.Error as e:
        app.logger.exception("api_record: %s", e)
        return jsonify({"error": "database_error", "message": "記録に失敗しました。"}), 500
    finally:
        if conn:
            conn.close()


@app.route("/api/check/<int:question_id>")
def api_check(question_id):
    """正解判定。session で連続正解数（コンボ）を管理し、combo と title をレスポンスに含める。"""
    selected = request.args.get("answer")
    combo = session.get("combo", 0)
    is_correct = False
    conn = None
    try:
        conn = get_db()
        cur = conn.execute(
            "SELECT correct_answer, explanation FROM questions WHERE id = ?",
            (question_id,),
        )
        row = cur.fetchone()
        if not row:
            return jsonify({"error": "not_found"}), 404
        correct = row["correct_answer"]
        is_correct = selected == correct
        if is_correct:
            combo = combo + 1
            session["combo"] = combo
        else:
            session["combo"] = 0
            combo = 0
        title = get_title_for_combo(combo)
        return jsonify({
            "correct_answer": correct,
            "explanation": row["explanation"],
            "is_correct": is_correct,
            "combo": combo,
            "title": title,
        })
    except sqlite3.Error as e:
        app.logger.exception("api_check: %s", e)
        return jsonify({"error": "database_error", "message": "判定に失敗しました。"}), 500
    finally:
        if conn:
            conn.close()


@app.route("/api/quiz/start", methods=["POST"])
def api_quiz_start():
    """クイズ開始時にセッションのコンボを 0 にリセットする。"""
    session["combo"] = 0
    return jsonify({"ok": True})


@app.route("/dashboard")
def dashboard():
    """成績分析（ダッシュボード）ページ。"""
    return render_template("dashboard.html")


@app.route("/api/dashboard/stats")
def api_dashboard_stats():
    """history と questions を結合し、カテゴリごとの正解率を返す。レーダーチャート用。"""
    conn = None
    try:
        conn = get_db()
        cur = conn.execute(
            """
            SELECT q.category,
                   COUNT(*) AS total,
                   SUM(CASE WHEN h.is_correct = 1 THEN 1 ELSE 0 END) AS correct
            FROM history h
            JOIN questions q ON q.id = h.question_id
            GROUP BY q.category
            HAVING total > 0
            ORDER BY q.category
            """
        )
        rows = cur.fetchall()
        labels = []
        data = []
        for r in rows:
            labels.append(r["category"])
            rate = round(100 * r["correct"] / r["total"]) if r["total"] else 0
            data.append(rate)
        return jsonify({"labels": labels, "data": data})
    except sqlite3.Error as e:
        app.logger.exception("api_dashboard_stats: %s", e)
        return jsonify({"error": "database_error", "labels": [], "data": []}), 500
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
