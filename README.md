# Markdown to Figma Slides

![Markdown to Figma Slides Preview](docs/readme-preview.png)

日本語: このページ / English: [README.en.md](README.en.md)

Markdown を HTML スライドに変換し、Figma に取り込める形で運用するためのスキルです。

このリポジトリはスライド成果物そのものではなく、スキル本体と配布用 project template を管理します。生成されるプロジェクトはバージョン付きスナップショット (`v1`, `v2`, ...) を持ち、theme を切り替えながら再現可能に運用できます。

## このリポジトリの役割

- スキル本体: `skills/SKILL.md`
- 詳しい実行手順: `skills/references/workflow.md`
- 詳しい Markdown 記法: `skills/references/markdown-mapping.md`
- 詳しい Figma 取り込み手順: `skills/references/figma-capture.md`
- 配布する雛形: `skills/assets/project-template/`

利用者向けの theme system 運用ルールは `skills/references/theme-system.md`、repo maintainer 向けの設計判断は `docs/theme-design.md` を基準にしています。

## 最短で試す

### 前提条件

- Python 3.9 以上が使えること
- Figma に取り込みたい場合は Figma MCP が使えること
- AI エージェントがこのリポジトリを参照できること

Figma capture まで自動で進められるのは Claude Code を想定しています。Codex では現時点で Figma capture ステップは実行できません。

### まず体験してみる

まずは `skills/assets/sample-catalog.md` を使って、どんなスライドが生成されるかを確認するのがおすすめです。

Claude Code や Codex に、たとえば次のように依頼してください。

```text
このリポジトリの sample-catalog.md を使って、テスト用のスライドプロジェクトを作成し、スライドを生成してください。まずはどんなスライドができるか確認したいです。
```

少し具体的に頼むなら、次の形でも大丈夫です。

```text
skills/assets/sample-catalog.md を元に、テストプロジェクトを初期化してスライドを生成してください。生成後は、確認すべき出力先も教えてください。
```

この手順で、まず次をまとめて確認できます。

- どういう見た目のスライドが生成されるか
- built-in theme や template の雰囲気
- 自分の Markdown を流し込む前に、全体のワークフローがどう動くか

## AI に依頼する例

ここからは、実際の Markdown や調整したい内容があるときの依頼例です。

### 自分の Markdown から生成したい

```text
Markdownファイルをスライドにしたいです。
```

### 入力ファイルを指定して生成したい

```text
input/raw/source.md をもとにスライドを生成してください。
```

### 生成後に見た目も調整したい

```text
まず生成して、そのあとで配色や余白を調整したいです。
```

### Figma への取り込みまで進めたい

```text
生成したスライドを Figma に取り込むところまで進めてください。
```

この依頼は Claude Code 向けです。Codex を使う場合は、スライド生成までは進められますが、Figma capture 自体は別途行う前提です。

## theme と設定の考え方

- built-in theme は `classic`、`minimal`、`gradient-blue`
- active theme は `design.config.yaml.theme.name` で決まる
- baseline の見た目は theme defaults で決まる
- `design.config.yaml` には project 固有 override だけを追加する

theme を切り替えたいときは、たとえば次のように依頼できます。

```text
このスライドの theme を minimal に切り替えて、見た目を確認できるようにしてください。
```

使える built-in theme は `classic`、`minimal`、`gradient-blue` です。利用者向けの theme 運用ルールは `skills/references/theme-system.md`、具体的な実行手順は `skills/references/workflow.md` を参照してください。repo maintainer 向けの設計判断は `docs/theme-design.md` にあります。

## project scaffold の見取り図

```text
my-slides/
  design.config.yaml
  shared/
    styles/
      slide.css
  themes/
    <name>/
      theme.yaml
      styles/
      templates/
  scripts/
  input/
    raw/
    normalized/
    current.md
  output/
    vN/
      slides/
      source/
      SLIDES.md
      manifest.json
    slides.html
```

新規 project の運用ルールは `skills/assets/project-template/CLAUDE.md` に含まれます。

## 詳細ドキュメント

| 知りたいこと | 参照先 |
| --- | --- |
| 初期化、生成、再実行判断、手動コマンド | `skills/references/workflow.md` |
| Markdown 記法、template、special comments | `skills/references/markdown-mapping.md` |
| Figma 取り込みと polling | `skills/references/figma-capture.md` |
| theme system の運用ルール | `skills/references/theme-system.md` |
| built-in theme の追加・調整 | `skills/references/theme-authoring.md` |
| multi-theme の見た目確認 | `skills/references/visual-qa.md` |
| maintainer 向け変更判断 | `docs/maintainer-change-guide.md` |

## トラブルシューティング

依存が足りない場合:

```bash
pip3 install jinja2 pyyaml pygments
```

`scripts/` がない場合は project 初期化前です。

```bash
./skills/scripts/init_project.sh /path/to/my-slides
```

preview できない場合:

```bash
cd /path/to/my-slides/output
python3 -m http.server 8080
```
