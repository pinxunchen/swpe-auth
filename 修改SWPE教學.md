# 修改 SWPE.exe — 免 Fiddler（精確步驟）

## 原理

SWPE.exe 在 `A.o` → `E` → `A` 結構體的 `MoveNext()` 方法中下載授權名單。
我們只需要把「解密 URL」改成「直接用你的 URL」就行了。

---

## 步驟

### 1. 備份

```
把 SWPE.exe 複製一份叫 SWPE.exe.bak
```

### 2. 開啟 dnSpy

把 **SWPE.exe** 拖進 dnSpy

### 3. 找到要改的方法

在左側展開：
```
SWPE (assembly)
  └─ A (namespace)
      └─ o (class)
          └─ E (nested class)
              └─ A (nested struct)
                  └─ MoveNext() : void
```

> 💡 如果找不到，可以用 dnSpy 的搜尋功能（Ctrl+Shift+K）搜尋 `GetAsync`

### 4. 找到關鍵程式碼

在 MoveNext() 的 C# 反編譯檢視中，你會看到類似：

```csharp
// 原始程式碼（大概長這樣）
string url = A.G.a(PrivateImplementationDetails.aCR(), PrivateImplementationDetails.aCr());
HttpResponseMessage response = await this.httpClient.GetAsync(url);
```

### 5. 編輯方法

1. **右鍵** `MoveNext()` → **Edit Method (C#)...**
2. 找到上面那行，改成：

```csharp
// 直接用你的 GitHub URL，跳過解密
string url = "https://raw.githubusercontent.com/pinxunchen/swpe-auth/main/Reliable/Reversible";
HttpResponseMessage response = await this.httpClient.GetAsync(url);
```

3. 點 **Compile** 編譯

> 如果 C# 編輯遇到錯誤，改用 **Edit IL Instructions**：
> 找到 `call aCR()` 和 `call aCr()` 和 `call A.G::a` 那三行，
> 全部替換成一行：
> ```
> ldstr "https://raw.githubusercontent.com/pinxunchen/swpe-auth/main/Reliable/Reversible"
> ```

### 6. 儲存

1. **File → Save Module...**
2. 選擇存檔位置（可以覆蓋原始檔或另存新檔）
3. 點 **OK**

### 7. 測試

1. 確認 **Fiddler 已關閉**
2. 執行修改後的 SWPE.exe
3. 如果正常運作 → 完成！以後不需要 Fiddler 了

---

## 日後更新名單

修改 SWPE.exe 是一次性的，之後只需要管理 GitHub 上的名單：

```powershell
cd c:\Users\User\Desktop\swpe\auth_repo

# 新增用戶
python manage.py add 用戶名 New::137 用戶ID 2030-12-31
python manage.py add pipiccc New::137 用戶ID 2099-12-31

# 移除用戶
python manage.py remove 用戶名

# 推送到 GitHub（必須執行才會生效）
python manage.py push
```

SWPE.exe 下次啟動就會自動讀到更新的名單。
