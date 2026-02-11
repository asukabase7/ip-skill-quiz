# 知的財産管理技能検定2級 一問一答

スマホで快適に使える、一問一答形式の学習用クイズアプリ（MVP）です。

## Tech Stack

- **Backend**: Python (Flask)
- **Database**: SQLite
- **Frontend**: HTML5, CSS3 (Mobile First), JavaScript (Vanilla)

## セットアップ

```bash
cd ip_skill_quiz
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python init_db.py
```

## 起動

```bash
python app.py
```

ブラウザで http://127.0.0.1:5000/ を開いてください。スマホからは同一LAN内のPCのIP:5000 でアクセスできます。

## 機能

- **全問でスタート**: 登録されている全問題を順に解く
- **フィルタでスタート**: 試験種別・カテゴリで絞って出題
- 学科・実技どちらにも対応（実技は `scenario` に事例文を表示）
- 解答後に正誤と解説を表示し、次へ進む
- 一巡後に結果サマリを表示し、「もう一度」でスタート画面へ戻る

## DB スキーマ

`questions` テーブル:  
id, exam_type, category, scenario, question_text, option_a～d, correct_answer, explanation

問題の追加は `init_db.py` の `SAMPLE_DATA` に追記するか、SQLite で直接 INSERT してください。
