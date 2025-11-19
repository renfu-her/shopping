# 靜態文件設置指南

## 問題

應用運行時出現靜態文件 404 錯誤，因為缺少 CSS、JavaScript 和圖片文件。

## 解決方案

### 選項 1: 使用 CDN（快速解決）

修改 `app/views/frontend/base.html`，將本地靜態文件路徑替換為 CDN：

```html
<!-- Bootstrap CSS -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">

<!-- jQuery -->
<script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>

<!-- Bootstrap JS -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>

<!-- Font Awesome -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
```

### 選項 2: 從模板包複製靜態文件（完整方案）

1. 如果你有完整的 購物去 模板包
2. 將 `assets/` 目錄下的所有文件複製到 `static/` 目錄
3. 確保目錄結構如下：

```
static/
├── css/
│   ├── animate.css
│   ├── style.css
│   └── ...
├── js/
│   ├── jquery-3.7.0.min.js
│   ├── scripts.js
│   └── ...
├── images/
│   ├── logo_light.png
│   ├── logo_dark.png
│   └── ...
├── bootstrap/
│   ├── css/
│   └── js/
└── owlcarousel/
    ├── css/
    └── js/
```

### 選項 3: 簡化模板（最小方案）

如果只需要基本功能，可以簡化模板，只使用 Bootstrap CDN 和基本樣式。

## 當前狀態

- ✅ 模板路徑已修復
- ✅ 應用可以運行
- ⚠️ 靜態文件缺失（需要添加）

## 臨時解決方案

在開發階段，可以使用 CDN 來快速解決問題。生產環境建議使用本地靜態文件以獲得更好的性能和離線支持。

