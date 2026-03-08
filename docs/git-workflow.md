# Git の最低限運用

このリポジトリを安全に触るための、迷いにくい最小ルールです。

## まず覚えること

- `main` では作業しない
- 先に `main` を最新にしてから作業ブランチを切る
- ひと区切りごとに `commit` する
- バックアップや共有をしたいタイミングで `push` する

## 作業開始前の確認

まず、今どこにいて、作業開始してよい状態かを確認します。

```bash
git branch --show-current
git status --short
git switch main
git fetch origin
git pull --ff-only
```

古い `main` からブランチを切ると、あとで GitHub 上の `main` とズレて大きいコンフリクトになりやすいです。

新しい作業を始めるときは、次の 3 つを見ると後から詰まりにくくなります。

1. `main` の最近の履歴を確認する

```bash
git log --oneline --decorate origin/main -n 15
```

2. 触ろうとしているキーワードをコードと履歴の両方で探す

```bash
rg -n "<keyword>" docs skills
git log --oneline --grep="<keyword>"
```

3. これからやる変更が「新規」か「既存変更の追認・追従」かを先に決める

ポイント:

- 先に `main` を最新化してからブランチを切る
- 今ある branch 名だけで判断しない
- `main` にすでに近い変更が入っていないか先に見る
- 同じ領域の変更が見つかったら、別ブランチで新規に進めるか、既存変更に乗るかを決めてから着手する

## ブランチを作る

`main` を最新化したら、作業用ブランチを切ります。

```bash
git switch -c docs/git-minimum-workflow-refresh
```

## いつも使うコマンド

今いるブランチの確認:

```bash
git branch --show-current
```

状態確認:

```bash
git status
```

変更内容の確認:

```bash
git diff
git diff --staged
```

変更を保存対象に入れる:

```bash
git add docs/git-workflow.md
```

変更を 1 つの区切りとして保存:

```bash
git commit -m "Refresh Git minimum workflow guide"
```

GitHub に送る:

```bash
git push
```

## `git add` と `git commit` の違い

- `git add`: この変更を次の保存対象に入れる
- `git commit`: 保存対象に入れた変更を、1 つの履歴として確定する

たとえば `README.md` を編集しただけでは、まだコミット対象にはなっていません。

```bash
git add README.md
git commit -m "Update README"
```

この順番で、はじめて履歴に残ります。

## `add` し忘れを防ぐ方法

コミット前に `git status` を見ればほぼ防げます。

```bash
git status
git add docs/git-workflow.md
git status
git commit -m "Refresh Git minimum workflow guide"
```

見る場所は 2 つです。

- `Changes not staged for commit`: まだ `git add` していない変更
- `Changes to be committed`: 次の `git commit` に入る変更

コミットしたいファイルが `Changes to be committed` に入っていれば、そのまま `git commit` して大丈夫です。

`git add .` は便利ですが、意図しない差分まで拾いやすいです。
迷う間は `git add <file>` を基本にした方が安全です。

## 最初の 1 回だけ必要なこと

新しいブランチを GitHub に作るときだけ、最初に次を実行します。

```bash
git push -u origin docs/git-minimum-workflow-refresh
```

`-u` を付けると、次回からは `git push` だけで済みます。

## ブランチ名の目安

このリポジトリでは、次の形に寄せると判断しやすくなります。

```text
<type>/<scope>-<change>
```

`type` の目安:

- `docs`: 文書、運用メモ、手順書
- `fix`: バグ修正、仕様ずれの修正、同期漏れの解消
- `feature`: 新機能や大きめの機能追加
- `theme`: theme 実装そのものに閉じた変更

実際の履歴にある例:

- `docs/git-workflow-pre-branch-checks`
- `docs/git-minimum-workflow-refresh`
- `fix/body-grid-spec-sync`

避けた方がよい名前:

- `feature/theme`
- `fix/misc`
- `docs/update`
- `work/tmp`

ポイント:

- ブランチ名だけで大まかな作業種別が分かるようにする
- `scope` は触る領域を短く書く
- `change` は何をするかを短く書く
- theme 専用変更でないのに `theme/...` にしない
- 長すぎる名前より、検索しやすい名前を優先する

## 1 回の作業の流れ

```bash
git branch --show-current
git status
git diff
git add docs/git-workflow.md
git commit -m "Refresh Git minimum workflow guide"
git push
```

## コミットメッセージの考え方

長文は不要です。何を変えたかが分かれば十分です。

例:

- `Refresh Git minimum workflow guide`
- `Fix body-grid spec sync`
- `Add gradient-blue built-in theme`

## PR を作るときのポイント

PR タイトルは英語で、何を変える PR なのかが一目で分かる形にします。

例:

- `Refresh Git minimum workflow guide`
- `Fix body-grid spec sync`
- `Add regression checks for theme config`

PR 本文は日本語で、背景と変更内容を短く整理します。
文書変更だけでも、何を削除して何を整理したかを書くとレビューしやすくなります。

最低限あるとよい項目:

- 概要
- 変更内容
- 確認ポイント

テンプレート:

```md
## 概要

この PR で何を整理したか、何を直したかを 1 から 2 行で書く。

## 変更内容

- 変更した内容を箇条書きで書く
- 削除した古い記述や置き換えた手順も書く

## 確認ポイント

- レビュー時に見てほしい点を書く
- 未確認のことがあれば正直に書く
```

## 困ったときの確認

今どこにいるか:

```bash
pwd
git branch --show-current
git status
```

`pwd` がこのリポジトリを指していて、今いるブランチが `main` 以外で、`git status` の内容を理解できていれば、そのまま作業してよい状態です。

## やらなくていいこと

- 毎回新しいターミナルを開き直すこと
- 毎回 `git push -u origin <branch-name>` を打つこと
- 細かすぎる単位で無理にコミットすること
- `main` で少しだけだからと直接編集を始めること

## 迷ったときの基準

- まだ途中でも、戻れた方が安心なら `commit`
- PC を閉じる前、区切りがついた後、相談前は `push`
- 不安なら `git status` と `git branch --show-current` を見る
