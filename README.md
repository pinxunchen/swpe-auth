# SWPE 授權名單管理系統

這是一個用來管理 SWPE.exe 授權名單的工具。
透過修改 `users.json`，你可以新增或移除授權用戶。

## 使用方式

1. 編輯 `users.json` 來管理用戶清單
2. 執行 `python manage.py` 產生加密檔案
3. 將 `Reversible` 推送到 GitHub
4. SWPE.exe 啟動時會讀取你的名單

## 檔案說明

- `users.json` - 用戶清單（明文，方便編輯）
- `manage.py` - 管理腳本（加密 + 推送）
- `Reliable/Reversible` - 加密後的授權檔案
