# GitHub Merge Analytics

過去1ヶ月間のGitHubリポジトリの日次マージ数を分析・可視化するPythonアプリケーションです。

## 機能

- 任意のパブリックGitHubリポジトリから日次マージ数を取得
- matplotlibを使用したインタラクティブなグラフの生成
- 簡単に統合できるコマンドラインインターフェース
- 様々なGitHub URL形式のサポート
- 分析期間のカスタマイズ
- レート制限とエラーハンドリング

## 📊 出力例

以下は、このツールで生成される日次マージ数可視化の例です：
<img width="1230" alt="daily_merge_count" src="https://github.com/user-attachments/assets/54be662d-c561-4a66-94f7-b8be1077f7dd" />
*例：nakanoh/github-merge-analyticsの過去30日間の日次マージ数分析*

グラフには以下が表示されます：
- **合計**：1マージ
- **平均**：1日あたり0.0マージ  
- **ピーク**：1マージ（1日あたりの最大値）

## 要件

- Python 3.8+
- GitHub API アクセス用のインターネット接続

## インストール

1. このリポジトリをクローンします：
```bash
git clone https://github.com/nakanoh/github-merge-analytics.git
cd github-merge-analytics
```

2. 依存関係をインストールします：
```bash
pip install -r requirements.txt
```

## GitHub認証（オプション）

APIレート制限を1時間あたり60リクエストから5000リクエストに増加させるには、GitHub Personal Access Tokenを設定してください：

1. Personal Access Tokenを作成します：
   - GitHub Settings → Developer settings → Personal access tokens → Tokens (classic) に移動
   - "Generate new token (classic)" をクリック
   - スコープを選択：パブリックリポジトリには `public_repo` のみが必要
   - 生成されたトークンをコピー

2. 環境変数を設定します：
```bash
export GITHUB_TOKEN=ghp_your_token_here
```

3. 通常通りアプリケーションを実行します：
```bash
python main.py --repo https://github.com/owner/repo
```

アプリケーションは自動的にトークンを検出し、認証に使用します。

## 使用方法

### 基本的な使用方法

過去30日間のリポジトリを分析します：
```bash
python main.py --repo https://github.com/owner/repo
```

### 代替URL形式

このツールは様々なGitHub URL形式をサポートしています：
```bash
# HTTPS URL
python main.py --repo https://github.com/microsoft/vscode

# SSH URL形式
python main.py --repo git@github.com:microsoft/vscode.git

# 短縮形式
python main.py --repo microsoft/vscode
```

### カスタム期間

異なる日数で分析します：
```bash
python main.py --repo https://github.com/owner/repo --days 60
```

### コマンドラインオプション

- `--repo`（必須）：GitHub リポジトリ URL または owner/repo 形式
- `--days`（オプション）：分析する日数（デフォルト：30）

## 出力

アプリケーションは以下を実行します：

1. ターミナルに分析進捗を表示
2. リポジトリのマージ活動に関する統計を表示
3. 以下を含むグラフを生成・表示：
   - 指定期間の日次マージ数
   - 総マージ数、1日あたりの平均、ピーク活動
   - 読みやすい日付フォーマット

## 例

### 例1：Reactリポジトリの分析
```bash
python main.py --repo https://github.com/facebook/react
```

### 例2：カスタム期間での分析
```bash
python main.py --repo microsoft/typescript --days 14
```

## グラフ機能

生成されるグラフには以下が含まれます：
- 日次マージ活動を示すマーカー付きライングラフ
- 読みやすさを向上するグリッド線
- 重複を防ぐ回転した日付ラベル
- 下部の統計サマリー
- 適切なタイトルとラベルを持つプロフェッショナルなスタイリング

## APIレート制限

アプリケーションはGitHub APIレート制限を処理します：
- 適切なUser-Agentヘッダーを使用
- レート制限に達した場合の明確なエラーメッセージ
- **1時間あたり5000リクエストのGitHub Personal Access Token認証をサポート**（認証なしの場合は60）
- `GITHUB_TOKEN`環境変数を自動検出・使用
- トークンが提供されない場合は認証なしリクエストに適切にフォールバック

## エラーハンドリング

アプリケーションには以下の包括的なエラーハンドリングが含まれています：
- 無効なリポジトリURL
- ネットワーク接続の問題
- GitHub APIエラー
- 無効なコマンドライン引数

## 技術詳細

### 依存関係
- `requests`：GitHub API呼び出し用HTTPライブラリ
- `matplotlib`：グラフ生成用プロットライブラリ

### GitHub API
- GitHub REST API v3を使用
- マージ情報付きのクローズされたプルリクエストを取得
- 日次集計のためのマージタイムスタンプを処理

### データ処理
- マージ日によるプルリクエストのフィルタリング
- データの日次カウントへの集計
- タイムゾーン変換の適切な処理

## 制限事項

- パブリックリポジトリでのみ動作
- GitHub APIレート制限の対象（トークンなしで1時間あたり60リクエスト、トークンありで5000）
- matplotlib出力にはグラフィカルディスプレイが必要

## 貢献

1. リポジトリをフォーク
2. フィーチャーブランチを作成
3. 変更を加える
4. 該当する場合はテストを追加
5. プルリクエストを送信

## ライセンス

このプロジェクトはオープンソースです。ライセンス詳細についてはリポジトリを確認してください。

## トラブルシューティング

### よくある問題

**"Rate limit exceeded"**：
- GitHub Personal Access Tokenを設定してください（上記のGitHub認証セクションを参照）
- またはレート制限がリセットされるまで待ってください（通常、認証なしリクエストの場合は60分）

**"Invalid GitHub repository URL"**：
- URLが正しい形式であることを確認してください
- 短縮形式を試してください：`owner/repo`

**グラフが表示されない**：
- グラフィカル環境があることを確認してください
- matplotlibが適切にインストールされていることを確認してください

**データが見つからない**：
- 指定された期間内にマージされたプルリクエストがリポジトリにあることを確認してください
- リポジトリが存在し、パブリックであることを確認してください

## サポート

問題が発生した場合：
1. 上記のトラブルシューティングセクションを確認してください
2. PythonとDependencyのバージョンを確認してください
3. 詳細なエラー情報を含めてGitHubリポジトリにissueを開いてください