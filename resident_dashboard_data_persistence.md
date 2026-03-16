# React 研修医一覧でのデータ保持方法

## 現状の課題

1. **resident_dashboard** は React 製で、`st.components.v1.html` の iframe 内で動作
2. ページ切り替えで iframe が再作成され、React のメモリ上の状態がリセットされる
3. resident_dashboard の JS は minify 済みで、localStorage の利用有無を直接確認しづらい
4. 期別リストは `kibetu_list_result` / `kibetu_list_filename` を localStorage で参照しており、同じデータ構造・キーを共有する可能性がある

---

## 解決策の候補

### 方法1: localStorage への安全な注入（Base64 エンコード）

**手順:**
- データを Base64 にエンコードして HTML に埋め込む（`</script>` などによる破損を防止）
- iframe の `<head>` 直後にスクリプトを挿入し、デコードして localStorage に設定
- 期別リストと同様、`kibetu_list_result` / `kibetu_list_filename` を利用

**メリット:**
- 既存の resident_dashboard が localStorage を読む前提なら、変更不要で動作する
- 特殊文字や長い JSON も安全に渡せる

**デメリット:**
- resident_dashboard が localStorage を参照していない場合、効果がない

---

### 方法2: window.__INITIAL_DATA__ による初期データ渡し

**手順:**
- `<head>` 内で `window.__RESIDENT_INITIAL_DATA__ = { ... }` を定義
- React 側を修正してマウント時にこの値を読む

**メリット:**
- 明示的な契約に基づく渡し方で、意図が明確

**デメリット:**
- resident_dashboard のソースがないと、React 側の修正ができない
- ビルド成果物のみの場合は適用不可

---

### 方法3: Streamlit + React のハイブリッド表示

**手順:**
- データがあるとき: Streamlit でカード表示（現在の実装）
- データがないとき: resident_dashboard を表示し、アップロード UI だけを利用

**メリット:**
- 表示・永続化は確実に動作する
- React の内部実装に依存しない

**デメリット:**
- React レイアウトと Streamlit レイアウトで UI が変わる

---

### 方法4: resident_dashboard を localStorage 対応で再ビルド

**手順:**
1. resident_dashboard のソースを取得
2. `useEffect` で `kibetu_list_result` / `kibetu_list_filename` を読み、初期状態に反映
3. データ読み込み時に localStorage へも保存するよう実装
4. 再ビルドして `index.html` / assets を更新

**メリット:**
- React の UI のまま、確実にデータ保持を実現できる
- 期別リストとデータ連携しやすい

**デメリット:**
- ソースコードとビルド環境が必要

---

### 方法5: Streamlit で静的 HTML を動的生成して React 相当の UI を再現

**手順:**
- resident_dashboard と同等の HTML/CSS を Streamlit 側で組み立てる
- `st.markdown(..., unsafe_allow_html=True)` で描画

**メリット:**
- React / iframe に依存せず、Streamlit のセッションのみで完結

**デメリット:**
- レイアウトの再実装が必要
- 複雑な UI はメンテコストが高い

---

## 推奨アプローチ

**第一案: 方法1（Base64 + localStorage 注入）を試す**

- 期別リストが localStorage を利用しているため、resident_dashboard も同様の想定で試すのが妥当
- 以前の注入が効かなかった原因として、データ内の `</script>` による HTML 破損が疑われる
- Base64 エンコードでその問題を避けつつ、localStorage に正しく渡す実装を試す

**第二案: resident_dashboard のソースがある場合、方法4を採用**

- ソースが利用可能なら、localStorage の読み書きを明示的に実装するのが最も確実

---

## 実装のポイント（方法1 の場合）

```python
# Base64 で安全に埋め込む
import base64
result_json = json.dumps(st.session_state.resident_data, ensure_ascii=False, default=str)
data_b64 = base64.b64encode(result_json.encode('utf-8')).decode('ascii')

init_script = f'''
<script>
(function() {{
    try {{
        var raw = atob("{data_b64}");
        var data = JSON.parse(decodeURIComponent(escape(raw)));
        localStorage.setItem("kibetu_list_result", JSON.stringify(data));
        localStorage.setItem("kibetu_list_filename", {json.dumps(filename)});
        if (window.parent && window.parent !== window) {{
            try {{
                window.parent.localStorage.setItem("kibetu_list_result", JSON.stringify(data));
                window.parent.localStorage.setItem("kibetu_list_filename", {json.dumps(filename)});
            }} catch(e) {{}}
        }}
    }} catch(e) {{ console.error("resident init error:", e); }}
}})();
</script>
'''
```

注意: `escape()` は非推奨だが、日本語など非 ASCII を扱う際に必要な場合がある。UTF-8 の場合は `TextDecoder` などでのデコードを検討する。
