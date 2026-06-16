# 任意：役割を identity に固める

英語版：[../identity-hardening.md](../identity-hardening.md)

ゲートは**規約**として働きます——あなたとエージェントが守ると決めた役割と階層。まずはそれで十分だし、そこから始めるべきです。でも、散文の規律は破れます。夜11時、「実装役は自分の仕事を自分で承認しない」は、ひとキーで無視できる。

ゲートを**合意でなく強制**にしたくなったら、3つの役割を別々の identity に写し、違反はプラットフォームに拒否させます。

## 原則

| 役割 | identity | プラットフォームの強制 |
|---|---|---|
| 実装役 | bot/エージェント用アカウント | Write 権限。だが自分のPRは承認**できない**（GitHub が自己承認を禁止） |
| レビュー役 | **別の**アカウント | Write 権限。その承認が「Required approvals: 1」を満たす |
| 承認役 | あなた（人間オーナー） | 唯一の Admin。高リスクの merge / bypass ができる唯一の存在 |

実装役とレビュー役が別アカウントだから、「作者は自分の仕事を承認できない」は、覚えておくルールではなく、プラットフォームが強制する事実になります。

## GitHub の branch protection（執筆時点では無料枠でも動く — 最新の対象範囲は要確認）

`main` に対して、ルールセットで：

- **Require a pull request before merging** — ON
- **Required approvals** — 1（レビュー役の identity が満たす）
- **Dismiss stale approvals when new commits are pushed** — ON（修正後に再レビュー）
- **Require conversation resolution before merging** — ON
- **Block force pushes** — ON
- **Block deletions** — ON
- 初期は **bypass を誰にも許さない**——自分を含め全員に適用し、信用できるまで回す

**Admin は人間だけ。** エージェントのアカウントがルールセットを編集できたら、ゲートはまた口約束に戻ります。

## ローカルの identity 分離

identity ごとに clone（または認証設定）を分けると、コミットの取り違えを防げます。

- identity ごとに別の SSH 鍵 / host alias（`~/.ssh/config`）
- clone ごとの `git config user.name/email` を、各アカウントの検証済みメールに一致させる（コミットが正しく紐づき、「unverified」にならない）
- clone ごとの CLI 認証（例：GitHub CLI の `GH_CONFIG_DIR`）を `direnv` で固定し、切り替え忘れを防ぐ

## どこまでやるか

- **ソロ・低ステークス：** 規約としての役割だけ。アカウントを増やさない
- **ソロ・実ステークス（秘密情報・デプロイ・お金）：** レビュー役の identity ＋ branch protection を足す。**自己承認を不可能にする**——推奨でなく、構造的に。ここが効く一手
- **小チーム：** 同上に加え、実在の同僚を承認役に写す

規約から始める。ヒヤッとした日に、強制へ上げる——遅かれ早かれ、その日は来ます。
