# スプレッドシートIDのデフォルト設定方法

毎回スプレッドシートIDを入力するのが面倒な場合、`.streamlit/secrets.toml` にデフォルト値を設定できます。

## 設定方法

### 1. secrets.tomlを編集

`.streamlit/secrets.toml` ファイルを開き、以下の行を追加（または編集）します：

```toml
# スプレッドシートID（デフォルト値）
spreadsheet_id = "17s4l6eflZp74ZuiwIs7VJ4lc40JIRcobxl7PL9i1wDE"
```

**あなたのスプレッドシートID:**
```
17s4l6eflZp74ZuiwIs7VJ4lc40JIRcobxl7PL9i1wDE
```

### 2. アプリを再起動

設定を反映するために、Streamlitアプリを再起動してください：

1. ターミナルで `Ctrl+C` を押してアプリを停止
2. 再度起動：
   ```powershell
   .\venv\Scripts\Activate.ps1
   streamlit run app.py
   ```

### 3. 動作確認

アプリを起動すると：
- ✅ サイドバーの「GoogleスプレッドシートID」欄に、デフォルト値が自動的に入力されます
- ✅ 「💡 デフォルトのスプレッドシートIDが設定されています」というメッセージが表示されます
- ✅ 必要に応じて、サイドバーでIDを変更することもできます

## 複数のスプレッドシートを使い分ける場合

異なるスプレッドシートを使いたい場合は、サイドバーの入力欄でIDを変更できます。変更したIDは、そのセッション中は保持されます。

## デフォルト値を変更する場合

1. `.streamlit/secrets.toml` を開く
2. `spreadsheet_id` の値を新しいIDに変更
3. アプリを再起動

## 注意事項

- `secrets.toml` は機密情報を含むため、Gitにコミットされません（`.gitignore` に含まれています）
- デフォルト値を設定しても、サイドバーでいつでも変更可能です
- アプリを再起動すると、デフォルト値が再度読み込まれます
