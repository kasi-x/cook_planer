# デプロイガイド

## 構成

- **フロントエンド**: Cloudflare Pages（無料）
- **バックエンドAPI**: Railway（GitHub Student: $5/月クレジット）
- **アクセス解析**: Cloudflare Web Analytics（無料）

---

## 1. Railway（バックエンドAPI）

### 1.1 デプロイ手順

1. [Railway](https://railway.app/) にGitHubでログイン
2. 「New Project」→「Deploy from GitHub repo」
3. このリポジトリを選択
4. 環境変数を設定:
   ```
   CORS_ALLOW_ALL=true
   ```
   または特定のドメインのみ許可:
   ```
   CORS_ORIGINS=https://your-project.pages.dev,https://yourdomain.com
   ```
5. デプロイ完了後、「Settings」→「Networking」→「Generate Domain」でURLを取得
   - 例: `https://cook-planer-production.up.railway.app`

### 1.2 確認

```bash
curl https://your-railway-url.up.railway.app/api/health
# {"status":"ok"} が返れば成功
```

---

## 2. Cloudflare Pages（フロントエンド）

### 2.1 デプロイ手順

1. [Cloudflare Dashboard](https://dash.cloudflare.com/) にログイン
2. 「Workers & Pages」→「Create」→「Pages」→「Connect to Git」
3. GitHubリポジトリを選択
4. ビルド設定:
   - **Framework preset**: `None`
   - **Build command**: `cd web && npm install && npm run build`
   - **Build output directory**: `web/dist`
5. 環境変数を設定:
   ```
   VITE_API_URL=https://your-railway-url.up.railway.app/api
   ```
6. 「Save and Deploy」

### 2.2 カスタムドメイン（オプション）

1. 「Custom domains」→「Set up a custom domain」
2. ドメインを入力（例: `nutrition.example.com`）
3. DNSレコードを設定（Cloudflareで管理していれば自動）

---

## 3. Cloudflare Web Analytics（アクセス解析）

### 3.1 有効化

1. Cloudflare Dashboard →「Analytics & Logs」→「Web Analytics」
2. 「Add a site」→ デプロイしたサイトを選択
3. 自動的にスクリプトが挿入される（Cloudflare Pages連携時）

### 3.2 手動設定（必要な場合）

`web/index.html` に追加:
```html
<!-- Cloudflare Web Analytics -->
<script defer src='https://static.cloudflareinsights.com/beacon.min.js'
        data-cf-beacon='{"token": "YOUR_TOKEN"}'></script>
```

---

## 環境変数まとめ

### Railway（API）
| 変数名 | 説明 | 例 |
|--------|------|-----|
| `CORS_ALLOW_ALL` | 全オリジン許可 | `true` |
| `CORS_ORIGINS` | 許可オリジン（カンマ区切り） | `https://example.pages.dev` |

### Cloudflare Pages（フロントエンド）
| 変数名 | 説明 | 例 |
|--------|------|-----|
| `VITE_API_URL` | APIのURL | `https://xxx.up.railway.app/api` |

---

## ローカル開発

```bash
# APIサーバー起動
docker compose up -d

# フロントエンド開発サーバー
cd web && npm run dev
```

---

## トラブルシューティング

### CORS エラー
- RailwayのCORS設定を確認
- `CORS_ALLOW_ALL=true` で一時的に全許可してテスト

### API接続エラー
- `VITE_API_URL` が正しいか確認
- Railwayのログを確認: Dashboard →「Deployments」→「View Logs」

### ビルドエラー
- Cloudflare Pagesのビルドログを確認
- ローカルで `cd web && npm run build` が成功するか確認
