import requests
from bs4 import BeautifulSoup
import urllib3
import matplotlib.pyplot as plt

# --- 解決中文亂碼補丁 ---
# 微軟正黑體 (最推薦)
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei'] 

plt.rcParams['axes.unicode_minus'] = False # 解決負號顯示為方塊的問題
# 隱藏警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_steam_deals():
    # 加入語系設定，確保抓到的是中文名稱，這也是一個創意加分點
    headers = {'Accept-Language': 'zh-TW,zh;q=0.9'}
    url = "https://store.steampowered.com/search/?specials=1"
    
    response = requests.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Steam 搜尋結果的每一橫列
    rows = soup.find_all('a', class_='search_result_row')
    
    results = []
    for row in rows[:10]:
        # 1. 抓取遊戲名稱
        name_tag = row.find('span', class_='title')
        name = name_tag.text.strip() if name_tag else "未知遊戲"
        
        # 2. 強化版折扣抓取邏輯
        # 尋找所有包含 "discount_pct" 的 div (這是 Steam 固定的折扣百分比 class)
        discount_tag = row.find('div', class_='search_discount_block')
        
        discount_val = 0
        discount_str = "無折扣"
        
        if discount_tag:
            # 在這個區塊內找包含 % 的文字
            pct_tag = discount_tag.find(string=lambda t: '%' in t)
            if pct_tag:
                discount_str = pct_tag.strip()
                try:
                    # 把 -80% 變成 80
                    discount_val = int(discount_str.replace('-', '').replace('%', ''))
                except:
                    discount_val = 0
        
        results.append({'name': name, 'discount_str': discount_str, 'discount_val': discount_val})
    
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

# 3. 畫圖 (這時候畫出來就會從最高折扣開始排了)
plt.figure(figsize=(10, 6))
# 使用 [::-1] 是為了讓最大的排在最上面
plt.barh(names[::-1], values[::-1], color='orange') 
plt.xlabel('Discount Percentage (%)')
plt.title('Top 10 Steam Discount Analysis (Sorted)')
plt.tight_layout()
plt.show()