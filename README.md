# 知的財産管理技能検定2級 一問一答

スマホで快適に使える、一問一答形式の学習用クイズアプリ。PWA対応でiPhoneのホーム画面に追加可能。

## Tech Stack

- **Backend**: Python (Flask)
- **Database**: SQLite
- **Frontend**: HTML5, CSS3 (Mobile First), JavaScript (Vanilla)
- **Chart Library**: Chart.js (CDN)

## セットアップ

### 1. 依存関係のインストール

```bash
cd ip_skill_quiz
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. データベースの初期化

```bash
# サンプルデータでDBを作成
python init_db.py

# または、CSVからインポート（過去問 + AI模擬）
python import_csv.py
```

### 3. 環境変数（本番環境推奨）

PythonAnywhere など本番環境では、セッション用の秘密鍵を設定してください：

```bash
export FLASK_SECRET_KEY="your-random-secret-key-here"
```

未設定の場合は起動のたびにランダム生成されます（サーバー再起動でセッションが無効化されます）。

## 起動

```bash
python app.py
```

ブラウザで http://127.0.0.1:5000/ を開いてください。スマホからは同一LAN内のPCのIP:5000 でアクセスできます。

## 主な機能

### クイズ機能

- **全問でスタート**: 登録されている全問題をランダムにシャッフルして出題
- **過去問を解く**: 第50-52回の過去問のみ出題
- **AI模擬を解く**: AI生成の模擬問題のみ出題
- **フィルタでスタート**: 試験種別（第52回/第51回/第50回/AI模擬）とジャンルで絞り込み
- **これまでの復習**: 間違えた問題のみを復習（データがある場合のみ表示）

### 学習履歴・分析

- **回答記録**: 各問題の正誤を自動記録（`history` テーブル）
- **復習モード**: 最後に不正解だった問題を自動抽出
- **成績分析（ダッシュボード）**: カテゴリ別の正解率をレーダーチャートで可視化
  - `/dashboard` にアクセス
  - 全回答履歴からカテゴリごとの正解率を計算

### ゲーミフィケーション

- **連続正解コンボ**: クイズ中に「🔥 COMBO: X」を表示（サーバー側で管理）
- **称号システム**: コンボ数に応じて称号を獲得
  - 5連勝: 駆け出し知財担当
  - 10連勝: 特許庁の注目株
  - 20連勝: 歩く知的財産権法
  - 30連勝: 弁理士レベル
  - 50連勝: 知財の神
- **結果画面の称号**: 正解率に応じて「知財の神」「知財エキスパート」「知財の卵」を表示
- **レーダーチャート**: 結果画面で今回のセッションのジャンル別正答率を表示

### PWA対応

- iPhoneのホーム画面に追加可能（スタンドアロンモード）
- アプリアイコン: `static/icon.png`（正方形・180×180px推奨）— ファビコン・ホーム画面アイコンとして表示
- ブラウザの戻るボタンが無い環境でも「🏠 ホームへ」ボタンでトップに戻れる

## データ管理

### CSVからのインポート

```bash
# questions.csv（過去問）と ai_questions.csv（AI模擬）をDBにインポート
python import_csv.py
```

### カテゴリの再分類

```bash
# questions.csv の category をキーワード判定で自動分類
python reclassify_categories.py
```

## DB スキーマ

### `questions` テーブル

id, exam_type, category, scenario, question_text, option_a～d, correct_answer, explanation

### `history` テーブル（復習用）

id, question_id (FK), is_correct (0/1), timestamp

アプリ起動時に自動生成されます（`ensure_tables`）。

## ファイル構成

```
ip_skill_quiz/
├── app.py                 # Flask バックエンド（API + ルーティング）
├── init_db.py            # DB初期化スクリプト
├── import_csv.py         # CSVインポート（過去問 + AI模擬）
├── reclassify_categories.py  # カテゴリ自動分類
├── requirements.txt      # Python依存関係
├── quiz.db              # SQLiteデータベース（gitignore対象）
├── questions.csv        # 過去問データ
├── ai_questions.csv     # AI模擬問題データ
├── templates/
│   ├── index.html       # メイン画面（SPA）
│   └── dashboard.html   # 成績分析ダッシュボード
└── static/
    ├── icon.png         # アプリアイコン（ファビコン・PWA用）
    ├── css/
    │   └── style.css    # スタイル（Mobile First）
    └── js/
        └── app.js       # フロントエンドロジック
```

## デプロイ（PythonAnywhere）

1. プロジェクトフォルダをアップロード
2. WSGI設定で `app.py` の `app` を指定
3. `FLASK_SECRET_KEY` を環境変数で設定（推奨）
4. `quiz.db` が書き込み可能なことを確認
5. Web タブで Reload

## ライセンス

このプロジェクトは学習目的で作成されています。
