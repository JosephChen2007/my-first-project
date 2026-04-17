import requests
from bs4 import BeautifulSoup
import urllib3
import matplotlib.pyplot as plt


# --- 解決中文亂碼補丁 ---
# 微軟正黑體 
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei'] 

plt.rcParams['axes.unicode_minus'] = False # 解決負號顯示為方塊的問題
# 隱藏警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_steam_deals():
    # 加入語系設定，確保抓到的是中文名稱，
    headers = {'Accept-Language': 'zh-TW,zh;q=0.9'}
    url = "https://store.steampowered.com/search/?specials=1&sort_by=discount_DESC&category1=998"
    
    response = requests.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Steam 搜尋結果的每一橫列
    rows = soup.find_all('a', class_='search_result_row')

    results = []
    seen_names = set()

    for row in rows:
        name_tag = row.find('span', class_='title')
        name = name_tag.text.strip() if name_tag else ""
        
        if not name or name in seen_names:
            continue
            
        # --- 強化版：地毯式搜尋折扣數字 ---
        discount_val = 0
        discount_str = "無折扣"
        
        # 尋找所有可能藏有數字的地方 (包含 Bundle 和特殊特價區)
        # 把標籤內含有 '%' 這個符號抓出來
        possible_discount = row.find_all(string=lambda t: '%' in t)
        
        if possible_discount:
            # 取得最後一個符合的字串 
            raw_pct = possible_discount[-1].strip()
            try:
                # 處理 -90% 或 90% 的格式
                val = int(raw_pct.replace('-', '').replace('%', ''))
                if val > 0:
                    discount_val = val
                    discount_str = raw_pct
            except:
                pass

        # 進階過濾機制
        if discount_val > 50:
            results.append({'name': name, 'discount_str': discount_str, 'discount_val': discount_val})
            seen_names.add(name)
        
        if len(results) >= 10:
            break

    return results

# --- 執行並印出成果 ---
data = get_steam_deals()

# 1. 針對 discount_val 進行排序 (由大到小)
# reverse=True 代表從大到小排
data.sort(key=lambda x: x['discount_val'], reverse=True)

# 2. 重新整理畫圖用的資料
names = []
values = []

print(f"{'排名':<4} {'遊戲名稱':<30} {'折扣':<10}")
for i, item in enumerate(data, 1):
    print(f"{i:<4} {item['name']:<30} {item['discount_str']:<10}")
    if item['discount_val'] > 0:
        names.append(item['name'])
        values.append(item['discount_val'])

# 3. 畫圖
plt.figure(figsize=(10, 6))
# 使用 [::-1] 是為了讓最大的排在最上面
plt.barh(names[::-1], values[::-1], color='orange') 
plt.xlabel('Discount Percentage (%)')
plt.title('Top 10 Steam Discount Analysis (Sorted)')
plt.tight_layout()
plt.show()