# Theme Doc Update Checklist

## この文書の目的

theme 関連の変更を入れたときに、どのドキュメントを更新確認すべきかを素早く判断するための短い checklist。

迷ったら、まず次の 4 つを見る。

- `docs/theme-design.md`
- `docs/theme-authoring.md`
- `docs/body-grid-design.md`
- `docs/multi-theme-visual-qa.md`
- `skills/references/workflow.md`

## 変更種類ごとの確認先

### 1. theme を追加した

確認する:

- `docs/theme-design.md`
- `docs/theme-authoring.md`
- `docs/multi-theme-visual-qa.md`
- `skills/SKILL.md`
- `skills/references/workflow.md`

必要なら更新する:

- `README.md`
- `skills/assets/sample-catalog.md`

### 2. theme defaults / token layer / shared CSS を変えた

確認する:

- `docs/theme-design.md`
- `docs/theme-authoring.md`
- `docs/multi-theme-visual-qa.md`
- `skills/references/workflow.md`

必要なら更新する:

- `docs/maintainer-change-guide.md`

### 3. template の装飾だけを変えた

例:

- `cover` にロゴ追加
- `section` や `end` の見た目調整

確認する:

- `docs/theme-authoring.md`
- `docs/multi-theme-visual-qa.md`
- `docs/maintainer-change-guide.md`

必要なら更新する:

- `skills/references/workflow.md`

### 4. 新 component を正式追加した

確認する:

- `docs/theme-design.md`
- `docs/body-grid-design.md`
- `docs/multi-theme-visual-qa.md`
- `docs/maintainer-change-guide.md`
- `skills/references/markdown-mapping.md`
- `skills/SKILL.md`
- `skills/references/workflow.md`
- `skills/assets/sample-catalog.md`

### 5. visual QA の手順や runner を変えた

確認する:

- `docs/multi-theme-visual-qa.md`
- `docs/theme-design.md`
- `docs/maintainer-change-guide.md`

必要なら更新する:

- `skills/references/workflow.md`
- `README.md`

### 6. maintainer 向け運用を変えた

確認する:

- `docs/maintainer-change-guide.md`
- `docs/theme-doc-update-checklist.md`

必要なら更新する:

- `docs/theme-design.md`

## 更新不要になりやすいもの

通常は不要:

- `skills/references/figma-capture.md`
- `docs/git-minimum-workflow.md`

theme の変更が Figma capture や git 運用そのものを変えない限りは触らない。

## 実務ルール

theme 関連の実装 PR では、最低でも「どの doc を確認し、どれを更新したか」を明示する。
