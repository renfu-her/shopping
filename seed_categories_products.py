#!/usr/bin/env python3
"""
Script to seed categories and products data
Usage: python seed_categories_products.py
"""

from app import create_app, db
from app.models.category import Category
from app.models.product import Product
from app.utils.helpers import slugify
import json

def create_categories_and_products():
    """Create categories and products"""
    app = create_app()
    with app.app_context():
        # 定義大分類和小分類
        categories_data = {
            '3C': {
                'description': '3C產品專區',
                'children': [
                    {'name': '筆記電腦', 'description': '各種品牌筆記型電腦'},
                    {'name': '桌上電腦', 'description': '桌上型電腦主機'},
                    {'name': '商用電腦', 'description': '商用電腦設備'},
                    {'name': 'DIY 電腦', 'description': 'DIY組裝電腦零組件'},
                    {'name': 'LCD 螢幕', 'description': 'LCD顯示器'},
                    {'name': '外接硬碟/SSD', 'description': '外接式硬碟和SSD'},
                    {'name': 'SSD', 'description': '固態硬碟'},
                    {'name': '內接硬碟', 'description': '內接式硬碟'},
                    {'name': '網路硬碟', 'description': '網路儲存設備'},
                    {'name': 'CPU', 'description': '中央處理器'},
                    {'name': '主機板', 'description': '電腦主機板'},
                    {'name': '顯示卡', 'description': '顯示卡'},
                    {'name': '電源供應器', 'description': '電源供應器'},
                    {'name': '記憶體', 'description': '記憶體模組'},
                    {'name': '隨身碟', 'description': 'USB隨身碟'},
                    {'name': '記憶卡', 'description': '記憶卡'},
                ]
            },
            '週邊': {
                'description': '電腦週邊設備',
                'children': [
                    {'name': '鍵盤', 'description': '電腦鍵盤'},
                    {'name': '滑鼠', 'description': '電腦滑鼠'},
                    {'name': '電競耳機麥克風', 'description': '電競耳機和麥克風'},
                    {'name': '喇叭', 'description': '電腦喇叭'},
                    {'name': '電競椅', 'description': '電競專用座椅'},
                    {'name': 'Type C 周邊', 'description': 'Type C相關週邊'},
                    {'name': '線材', 'description': '各種連接線材'},
                    {'name': '延長線', 'description': '電源延長線'},
                    {'name': 'UPS不斷電系統', 'description': 'UPS不斷電系統'},
                    {'name': 'USB HUB/周邊', 'description': 'USB集線器和週邊'},
                    {'name': '電腦軟體', 'description': '電腦軟體'},
                    {'name': '雷射印表機', 'description': '雷射印表機'},
                    {'name': '噴墨印表機', 'description': '噴墨印表機'},
                    {'name': '筆電周邊/配件', 'description': '筆電週邊配件'},
                ]
            },
            '筆電': {
                'description': '筆記型電腦專區',
                'children': [
                    {'name': '電競筆電', 'description': '電競專用筆記型電腦'},
                    {'name': '商務筆電', 'description': '商務筆記型電腦'},
                    {'name': '輕薄筆電', 'description': '輕薄型筆記型電腦'},
                    {'name': '二合一筆電', 'description': '二合一筆記型電腦'},
                    {'name': 'MacBook', 'description': 'Apple MacBook'},
                    {'name': '筆電包/保護套', 'description': '筆電保護套和包包'},
                    {'name': '筆電散熱器', 'description': '筆電散熱底座'},
                    {'name': '筆電支架', 'description': '筆電支架'},
                ]
            },
            '通訊': {
                'description': '通訊產品專區',
                'children': [
                    {'name': '智慧型手機', 'description': '智慧型手機'},
                    {'name': '安卓手機', 'description': 'Android手機'},
                    {'name': '平板', 'description': '平板電腦'},
                    {'name': '行動電源', 'description': '行動電源'},
                    {'name': '手機殼貼', 'description': '手機保護殼和保護貼'},
                    {'name': 'APPLE周邊', 'description': 'Apple產品週邊'},
                    {'name': '充電/傳輸', 'description': '充電器和傳輸線'},
                    {'name': '智慧穿戴', 'description': '智慧手錶和穿戴裝置'},
                    {'name': '藍牙耳機', 'description': '藍牙無線耳機'},
                    {'name': '手機支架', 'description': '手機支架'},
                ]
            }
        }
        
        # 定義商品數據
        products_data = {
            '筆記電腦': [
                {'name': 'ASUS VivoBook 15 X1504ZA', 'description': '15.6吋筆記型電腦，Intel Core i5處理器，8GB記憶體，512GB SSD', 'price': 25900, 'stock': 15},
                {'name': 'Acer Aspire 5 A515', 'description': '15.6吋筆記型電腦，AMD Ryzen 5處理器，8GB記憶體，256GB SSD', 'price': 19900, 'stock': 20},
                {'name': 'Lenovo IdeaPad 3', 'description': '14吋筆記型電腦，Intel Core i3處理器，8GB記憶體，256GB SSD', 'price': 16900, 'stock': 12},
            ],
            'LCD 螢幕': [
                {'name': 'ASUS VG248QE 24吋電競螢幕', 'description': '24吋Full HD電競螢幕，144Hz刷新率，1ms反應時間', 'price': 5990, 'stock': 25},
                {'name': 'BenQ GW2480 24吋護眼螢幕', 'description': '24吋Full HD護眼螢幕，低藍光技術，不閃屏', 'price': 3990, 'stock': 30},
                {'name': 'LG 27吋 4K IPS螢幕', 'description': '27吋4K UHD IPS螢幕，99% sRGB色域', 'price': 8990, 'stock': 18},
            ],
            'SSD': [
                {'name': 'Samsung 980 PRO 1TB NVMe SSD', 'description': '1TB NVMe PCIe 4.0 SSD，讀取速度7000MB/s', 'price': 3990, 'stock': 50},
                {'name': 'WD Blue SN570 500GB SSD', 'description': '500GB NVMe PCIe 3.0 SSD，讀取速度3500MB/s', 'price': 1290, 'stock': 60},
                {'name': 'Crucial MX500 1TB SATA SSD', 'description': '1TB SATA 3 SSD，讀取速度560MB/s', 'price': 2490, 'stock': 45},
            ],
            '記憶體': [
                {'name': 'Kingston FURY Beast 16GB DDR4', 'description': '16GB DDR4-3200記憶體模組，雙通道', 'price': 1990, 'stock': 80},
                {'name': 'Corsair Vengeance LPX 32GB DDR4', 'description': '32GB DDR4-3200記憶體模組套裝', 'price': 3990, 'stock': 40},
                {'name': 'G.Skill Trident Z RGB 16GB DDR4', 'description': '16GB DDR4-3600 RGB記憶體', 'price': 2490, 'stock': 55},
            ],
            '鍵盤': [
                {'name': 'Logitech G213 RGB遊戲鍵盤', 'description': 'RGB背光遊戲鍵盤，防潑水設計', 'price': 1290, 'stock': 100},
                {'name': 'Corsair K70 RGB機械鍵盤', 'description': 'Cherry MX機械軸RGB鍵盤，鋁合金外殼', 'price': 4990, 'stock': 35},
                {'name': 'Razer BlackWidow V3機械鍵盤', 'description': 'Razer綠軸機械鍵盤，RGB背光', 'price': 3990, 'stock': 42},
            ],
            '滑鼠': [
                {'name': 'Logitech G502 HERO遊戲滑鼠', 'description': 'HERO 25K感應器，11個可編程按鍵', 'price': 1990, 'stock': 90},
                {'name': 'Razer DeathAdder V2遊戲滑鼠', 'description': 'Focus+ 20K感應器，8個可編程按鍵', 'price': 1790, 'stock': 75},
                {'name': 'Corsair Sabre RGB Pro遊戲滑鼠', 'description': '18,000 DPI光學感應器，RGB背光', 'price': 1490, 'stock': 65},
            ],
            '電競耳機麥克風': [
                {'name': 'HyperX Cloud II電競耳機', 'description': '7.1虛擬環繞音效，降噪麥克風', 'price': 2990, 'stock': 50},
                {'name': 'SteelSeries Arctis 7無線耳機', 'description': '2.4GHz無線連接，DTS音效', 'price': 4990, 'stock': 30},
                {'name': 'Razer Kraken V3 Pro電競耳機', 'description': 'THX空間音效，RGB背光', 'price': 5990, 'stock': 25},
            ],
            '電競筆電': [
                {'name': 'ASUS ROG Strix G15電競筆電', 'description': '15.6吋電競筆電，RTX 3060顯示卡，AMD Ryzen 7', 'price': 45900, 'stock': 10},
                {'name': 'MSI Katana GF66電競筆電', 'description': '15.6吋電競筆電，RTX 3050顯示卡，Intel Core i7', 'price': 35900, 'stock': 12},
                {'name': 'Acer Predator Helios 300', 'description': '15.6吋電競筆電，RTX 3070顯示卡，Intel Core i7', 'price': 54900, 'stock': 8},
            ],
            '智慧型手機': [
                {'name': 'Samsung Galaxy S23', 'description': '6.1吋智慧型手機，128GB儲存空間', 'price': 24900, 'stock': 20},
                {'name': 'iPhone 14', 'description': '6.1吋智慧型手機，128GB儲存空間', 'price': 27900, 'stock': 15},
                {'name': 'Xiaomi 13', 'description': '6.36吋智慧型手機，256GB儲存空間', 'price': 19900, 'stock': 25},
            ],
            '平板': [
                {'name': 'iPad Air 10.9吋', 'description': '10.9吋平板電腦，64GB儲存空間', 'price': 17900, 'stock': 18},
                {'name': 'Samsung Galaxy Tab S8', 'description': '11吋平板電腦，128GB儲存空間', 'price': 19900, 'stock': 15},
                {'name': 'Lenovo Tab P11 Plus', 'description': '11吋平板電腦，128GB儲存空間', 'price': 8990, 'stock': 22},
            ],
            '行動電源': [
                {'name': 'Anker PowerCore 10000行動電源', 'description': '10000mAh行動電源，支援快充', 'price': 890, 'stock': 100},
                {'name': 'Xiaomi 20000mAh行動電源', 'description': '20000mAh大容量行動電源', 'price': 990, 'stock': 80},
                {'name': 'AUKEY 20000mAh無線行動電源', 'description': '20000mAh無線充電行動電源', 'price': 1490, 'stock': 60},
            ],
        }
        
        # 創建大分類
        main_categories = {}
        for main_name, main_info in categories_data.items():
            # 檢查是否已存在
            existing = Category.query.filter_by(name=main_name, parent_id=None).first()
            if existing:
                print(f'大分類 "{main_name}" 已存在，跳過創建')
                main_categories[main_name] = existing
            else:
                category = Category(
                    name=main_name,
                    slug=slugify(main_name),
                    parent_id=None,
                    description=main_info['description'],
                    sort_order=len(main_categories),
                    is_active=True
                )
                db.session.add(category)
                db.session.flush()  # 獲取ID
                main_categories[main_name] = category
                print(f'創建大分類: {main_name} (ID: {category.id})')
        
        # 創建小分類
        sub_categories = {}
        for main_name, main_info in categories_data.items():
            parent_category = main_categories[main_name]
            for idx, child_info in enumerate(main_info['children']):
                child_name = child_info['name']
                # 檢查是否已存在
                existing = Category.query.filter_by(name=child_name, parent_id=parent_category.id).first()
                if existing:
                    print(f'  小分類 "{child_name}" 已存在，跳過創建')
                    sub_categories[child_name] = existing
                else:
                    child_category = Category(
                        name=child_name,
                        slug=slugify(child_name),
                        parent_id=parent_category.id,
                        description=child_info['description'],
                        sort_order=idx,
                        is_active=True
                    )
                    db.session.add(child_category)
                    db.session.flush()  # 獲取ID
                    sub_categories[child_name] = child_category
                    print(f'  創建小分類: {child_name} (ID: {child_category.id})')
        
        # 創建商品
        for category_name, products_list in products_data.items():
            if category_name not in sub_categories:
                print(f'警告: 找不到分類 "{category_name}"，跳過商品創建')
                continue
            
            category = sub_categories[category_name]
            for product_info in products_list:
                # 檢查是否已存在（根據名稱和分類）
                existing = Product.query.filter_by(name=product_info['name'], category_id=category.id).first()
                if existing:
                    print(f'    商品 "{product_info["name"]}" 已存在，跳過創建')
                    continue
                
                product = Product(
                    name=product_info['name'],
                    slug=slugify(product_info['name']),
                    description=product_info['description'],
                    price=product_info['price'],
                    stock=product_info['stock'],
                    category_id=category.id,
                    images=None,  # 沒有圖片，使用預設圖片
                    is_active=True
                )
                db.session.add(product)
                print(f'    創建商品: {product_info["name"]} - ${product_info["price"]}')
        
        # 提交所有更改
        try:
            db.session.commit()
            print('\n✅ 所有分類和商品創建成功！')
        except Exception as e:
            db.session.rollback()
            print(f'\n❌ 創建失敗: {str(e)}')
            raise

if __name__ == '__main__':
    create_categories_and_products()

