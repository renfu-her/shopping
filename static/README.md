# Static Files Directory

這個目錄用於存放靜態文件（CSS、JavaScript、圖片等）。

## 獲取靜態文件

### 方法 1: 從 HTML 模板中提取（推薦）

如果你有完整的 Shopwise 模板包，請將以下文件夾複製到 `static/` 目錄：

- `assets/css/` → `static/css/`
- `assets/js/` → `static/js/`
- `assets/images/` → `static/images/`
- `assets/bootstrap/` → `static/bootstrap/`
- `assets/owlcarousel/` → `static/owlcarousel/`

### 方法 2: 使用 CDN（臨時方案）

如果暫時沒有靜態文件，可以修改模板使用 CDN 版本：

- Bootstrap: https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css
- jQuery: https://code.jquery.com/jquery-3.7.0.min.js
- Font Awesome: https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css

### 方法 3: 下載模板

從原始模板提供商下載完整的 Shopwise 模板包，然後複製靜態文件。

## 目錄結構

```
static/
├── css/              # CSS 樣式文件
├── js/               # JavaScript 文件
├── images/           # 圖片文件
├── bootstrap/        # Bootstrap 文件
└── owlcarousel/      # Owl Carousel 文件
```

## 注意事項

- 確保所有靜態文件路徑與模板中的引用一致
- 圖片文件（logo、favicon 等）需要放在 `static/images/` 目錄
- 如果文件不存在，頁面仍可運行，但樣式和功能會受影響

