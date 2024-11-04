import os, sys, glob, time
import csv
import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def read_hojin_csv(hojin_list=[]):
    # 法人番号のCSVファイルを読込
    files = glob.glob('hojin-csv/*.csv')
    # print(files)
    for file in files:
        try:
            with open(file, 'r') as f:
                reader = csv.reader(f)
                hojin_list.extend(reader)
        except:
            with open(file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                hojin_list.extend(reader)

def is_solo_ceo(hojin_id, pref_id):
    global driver
    url = 'https://chosyu-web.mhlw.go.jp/LIC_D/workplaceSearch'
    driver.get(url)
    # ページが開くまで待機
    WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located)
    # 都道府県の選択
    pref_id_input = driver.find_element(By.ID, 'prefCd')
    select = Select(pref_id_input)
    select.select_by_index(pref_id)
    # 法人番号の入力
    hojin_no_input = driver.find_element(By.ID, 'hojinNo')
    hojin_no_input.send_keys(hojin_id)
    # 検索ボタンクリック
    driver.find_element(By.NAME, 'go').click()
    # 結果が表示されるまで待機
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME, 'total')))
    # 件数
    hit_num = int(driver.find_element(By.CLASS_NAME, 'total').text.split('件')[0])
    if hit_num == 0:
        return False # 0件の場合はひとり社長ではない
    #print(hit_num)
    # 表を取得
    table = driver.find_element(By.ID, 'resultItem')
    rows = table.find_elements(By.TAG_NAME, 'tr')
    for row in rows:
        # tdで分割
        tds = row.find_elements(By.TAG_NAME, 'td')
        if len(tds) != 4:
            continue
        # tdsの文字列を取得
        tds_text = [''.join(td.text.strip().split("\n")) for td in tds]
        if '雇用保険' in tds_text[3]:
            return False # 雇用保険を含む場合はひとり社長ではない
    return True

if __name__ == '__main__':
    # 開始行と終了行を引数で指定
    if len(sys.argv) != 4:
        start = 0
        end = -1
        number = 0
    else:
        start = int(sys.argv[1])
        end = int(sys.argv[2])
        number = int(sys.argv[3])

    # ブラウザの起動
    hojin_list = []
    options = selenium.webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument(f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.3{number%10}")
    user_data_dir = os.path.join(os.getcwd(), f"user_data_{start}") # ユーザーディレクトリをstartにする
    options.add_argument(f"user-data-dir={user_data_dir}")
    driver = selenium.webdriver.Chrome(options=options)

    # CSVファイルを読み込み
    print('load csv...', end='', flush=True)
    read_hojin_csv(hojin_list)
    print(f'ok! {len(hojin_list)} 件')

    # 開始行と終了行を指定
    hojin_list = hojin_list[start:end]
    print(f'start: {start} end: {end} total: {len(hojin_list)}件')

    # 結果ファイルが存在する場合はリネーム
    if os.path.exists(f'result-{start}-{end}.csv'):
        os.rename(f'result-{start}-{end}.csv', f'result-{start}-{end}-{time.strftime("%Y%m%d%H%M%S")}.bak')

    # メインループ
    for idx, hojin in enumerate(hojin_list):
        try:
            hojin_id = int(hojin[1])
            pref_id = int(hojin[13])
        except:
            continue
        print(f'{idx+1}/{len(hojin_list)} {hojin_id} {pref_id}')
        
        result = is_solo_ceo(hojin_id, pref_id)
        if result: 
            # 結果をCSVに書き込み
            with open(f'result-{start}-{end}.csv', 'a') as f:
                writer = csv.writer(f, lineterminator='\n')
                writer.writerow(hojin)
        time.sleep(1.0)
