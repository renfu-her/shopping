# Clean Code Practices

本專案遵循 Clean Code 原則，以下是已實施的改進：

## 1. 常量管理 (Constants)

所有魔術數字和字符串都定義在 `app/constants.py` 中：

- **訂單狀態**: `ORDER_STATUS_PENDING`, `ORDER_STATUS_PROCESSING` 等
- **用戶角色**: `USER_ROLE_ADMIN`, `USER_ROLE_CUSTOMER`
- **排序選項**: `SORT_NEWEST`, `SORT_PRICE_ASC` 等
- **分頁大小**: `PRODUCTS_PER_PAGE_FRONTEND`, `PRODUCTS_PER_PAGE_ADMIN` 等
- **Flash 訊息類型**: `FLASH_SUCCESS`, `FLASH_ERROR` 等

**好處**:
- 避免拼寫錯誤
- 易於維護和修改
- IDE 自動完成支持

## 2. 服務層 (Service Layer)

業務邏輯從控制器中分離到服務層：

### CartService (`app/services/cart_service.py`)
- `add_item()` - 添加商品到購物車
- `update_item()` - 更新購物車商品數量
- `remove_item()` - 移除購物車商品
- `get_cart_items()` - 獲取購物車商品列表
- `calculate_total()` - 計算購物車總額
- `clear_cart()` - 清空購物車
- `is_empty()` - 檢查購物車是否為空

### OrderService (`app/services/order_service.py`)
- `create_order()` - 創建訂單
- `update_status()` - 更新訂單狀態

**好處**:
- 控制器只負責 HTTP 請求和響應
- 業務邏輯可重用
- 易於測試
- 單一職責原則

## 3. 驗證工具 (Validators)

`app/utils/validators.py` 提供統一的驗證函數：

- `validate_email()` - 驗證電子郵件格式
- `validate_phone()` - 驗證電話號碼
- `validate_required()` - 驗證必填字段

**好處**:
- 統一的驗證邏輯
- 易於維護和擴展

## 4. 類型提示 (Type Hints)

服務層函數使用類型提示：

```python
def add_item(product_id: int, quantity: int = 1) -> Tuple[bool, str]:
    ...
```

**好處**:
- 提高代碼可讀性
- IDE 更好的自動完成
- 靜態類型檢查支持

## 5. 錯誤處理

統一的錯誤處理模式：

```python
success, message = CartService.add_item(product_id, quantity)
if success:
    flash(message, FLASH_SUCCESS)
else:
    flash(message, FLASH_ERROR)
```

**好處**:
- 一致的錯誤處理
- 更好的用戶體驗

## 6. 代碼組織

### 目錄結構
```
app/
├── constants.py          # 常量定義
├── models/              # 數據模型
├── controllers/         # 控制器（路由處理）
├── services/            # 業務邏輯服務
├── utils/               # 工具函數
└── views/               # 模板文件
```

### 命名規範
- **類**: PascalCase (`CartService`, `OrderService`)
- **函數/變量**: snake_case (`add_item`, `cart_items`)
- **常量**: UPPER_SNAKE_CASE (`ORDER_STATUS_PENDING`)

## 7. 文檔字符串

所有公共函數都有文檔字符串：

```python
def add_item(product_id: int, quantity: int = 1) -> Tuple[bool, str]:
    """
    Add product to cart
    
    Returns:
        Tuple[bool, str]: (success, message)
    """
```

## 8. DRY 原則 (Don't Repeat Yourself)

- 購物車計算邏輯統一在 `CartService` 中
- 訂單創建邏輯統一在 `OrderService` 中
- 重複代碼已提取到服務層

## 9. 單一職責原則

- **控制器**: 只處理 HTTP 請求和響應
- **服務層**: 處理業務邏輯
- **模型**: 數據結構和數據庫操作
- **工具函數**: 通用功能

## 10. 改進建議

未來可以進一步改進：

1. **添加單元測試**: 為服務層添加測試
2. **日誌記錄**: 添加結構化日誌
3. **API 文檔**: 使用 Swagger/OpenAPI
4. **緩存層**: 添加 Redis 緩存
5. **異步任務**: 使用 Celery 處理後台任務

## 使用範例

### 控制器中使用服務層

```python
from app.services.cart_service import CartService
from app.constants import FLASH_SUCCESS, FLASH_ERROR

@frontend_bp.route('/cart/add', methods=['POST'])
def cart_add():
    product_id = request.form.get('product_id', type=int)
    quantity = request.form.get('quantity', 1, type=int)
    
    success, message = CartService.add_item(product_id, quantity)
    flash(message, FLASH_SUCCESS if success else FLASH_ERROR)
    
    return redirect(url_for('frontend.product_list'))
```

### 使用常量

```python
from app.constants import ORDER_STATUS_PENDING, FLASH_SUCCESS

order.status = ORDER_STATUS_PENDING
flash('Order created', FLASH_SUCCESS)
```

