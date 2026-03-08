# Git の最低限運用

このリポジトリを安全に触るための、迷いにくい最小ルールです。

## まず覚えること

- `main` では作業しない
- 作業用ブランチを作って、その上で変更する
- ひと区切りごとに `commit` する
- バックアップや共有をしたいタイミングで `push` する

## 今回の作業ブランチ

この改善作業は `feature/theme` で進めます。

今いるブランチの確認:

```bash
git branch --show-current
```

## ブランチを切る前に見ること

まず `main` を最新にします。
古い `main` からブランチを切ると、あとで GitHub 上の `main` とズレて大きいコンフリクトになりやすいです。

```bash
git switch main
git fetch origin
git pull
```

`git branch` の一覧だけでは不十分です。
すでに別ブランチの変更が `main` にマージ済みだと、ブランチ名が消えていても履歴だけ残っていることがあります。

作業開始前は次の 3 つを見ると、後から大きいコンフリクトになりにくいです。

1. `main` の最近の履歴を確認する

```bash
git log --oneline --decorate origin/main -n 15
```

2. 触ろうとしているキーワードをコードと履歴の両方で探す

```bash
rg -n "body-grid|grid-full" .
git log --oneline --grep="body-grid"
```

3. これからやる変更が「新規」か「既存変更の追認・追従」かを先に決める

ポイント:

- 先に `main` を最新化してからブランチを切る
- 今ある branch 名だけで判断しない
- `main` にすでに近い変更が入っていないか先に見る
- 同じ領域の変更が見つかったら、別ブランチで新規に進めるか、既存変更に乗るかを決めてから着手する

## いつも使うコマンド

状態確認:

```bash
git status
```

変更内容の確認:

```bash
git diff
```

変更を保存する準備:

```bash
git add .
```

変更を 1 つの区切りとして保存:

```bash
git commit -m "テーマまわりの設計メモを追加"
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
git commit -m "README を更新"
```

この順番で、はじめて履歴に残ります。

## `add` し忘れを防ぐ方法

コミット前に `git status` を見ればほぼ防げます。

```bash
git status
git add .
git status
git commit -m "変更内容を短く書く"
```

見る場所は 2 つです。

- `Changes not staged for commit`: まだ `git add` していない変更
- `Changes to be committed`: 次の `git commit` に入る変更

コミットしたいファイルが `Changes to be committed` に入っていれば、そのまま `git commit` して大丈夫です。

## 最初の 1 回だけ必要なこと

新しいブランチを GitHub に作るときだけ、最初に次を実行します。

```bash
git push -u origin feature/theme
```

`-u` を付けると、次回からは `git push` だけで済みます。

## ブランチ名の目安

theme まわりの変更は、次の形に揃えると分かりやすいです。

```text
theme/<scope>-<change>
```

`scope` の例:

- `minimal`
- `gradient-blue`
- `classic`
- `shared`
- `parser`
- `config`
- `renderer`
- `docs`
- `qa`

例:

- `theme/minimal-section-spacing`
- `theme/gradient-blue-table-colors`
- `theme/shared-agenda-layout`
- `theme/parser-new-callout-block`
- `theme/docs-theme-authoring-fixes`

避けた方がよい名前:

- `theme/fixes`
- `theme/update`
- `theme/work`
- `theme/misc`

ポイント:

- 1 テーマだけ触るなら theme 名を入れる
- 複数 theme 横断なら `shared`
- 挙動変更なら `parser` / `config` / `renderer`
- 文書だけなら `docs`
- 検証基盤だけなら `qa`

## 1 回の作業の流れ

```bash
git status
git diff
git add .
git commit -m "変更内容を短く書く"
git push
```

## コミットメッセージの考え方

長文は不要です。何を変えたかが分かれば十分です。

例:

- `テーマ切り替えの設計メモを追加`
- `theme 用の設定項目を追加`
- `README のテーマ説明を更新`

## 困ったときの確認

今どこにいるか:

```bash
pwd
git branch --show-current
```

`pwd` がこのリポジトリを指していて、ブランチ名が `feature/theme` なら、そのまま作業して問題ありません。

## やらなくていいこと

- 毎回新しいターミナルを開き直すこと
- 毎回 `git push -u origin feature/theme` を打つこと
- 細かすぎる単位で無理にコミットすること

## 迷ったときの基準

- まだ途中でも、戻れた方が安心なら `commit`
- PC を閉じる前、区切りがついた後、相談前は `push`
- 不安なら `git status` を見る
