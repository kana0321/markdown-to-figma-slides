# Markdown to Figma Slides Repo

このリポジトリは `markdown-to-figma-slides` スキル本体です。
生成されるスライドプロジェクトそのものではありません。

## 主な編集対象

- `skills/SKILL.md`: スキル本体の説明と起動条件
- `skills/references/`: workflow / markdown mapping / figma capture などの詳細
- `skills/scripts/`: スキルから使う補助スクリプト
- `skills/assets/project-template/`: 配布するプロジェクト雛形

## 重要な前提

- `skills/assets/project-template/` の変更は、新規に初期化されるプロジェクトの標準挙動に影響します。
- このリポジトリで Git 関連の作業をするときは `docs/git-workflow.md` を参照してください。
- 利用者向けの theme system 運用ルールは `skills/references/theme-system.md` を参照してください。
- maintainer 向けの theme system 設計判断は `docs/theme-design.md` を参照してください。
- theme まわりの実装状況、採用済みの判断、次の優先候補は `docs/theme-design.md` を参照してください。
- 現在の built-in theme は `classic`、`minimal`、`gradient-blue` です。

## 変更時の確認

- ファイルの追加・編集・削除を行う前に、変更内容を短く要約してユーザーの承認を取ってください。
- 承認があるまでは、`apply_patch` などによるファイル変更を実行しないでください。
- 読み取り、調査、設計提案、実装方針の整理までは承認なしで進めて構いません。
- 機能追加や仕様変更時は、必要に応じて `skills/SKILL.md` と `skills/references/` も更新してください。
- project template の運用ルールは `skills/assets/project-template/AGENTS.md` で管理します。
