import os, sys, glob, time
import csv
import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

hojin_list = []
options = selenium.webdriver.ChromeOptions()
options.add_argument('--headless=new')
driver = selenium.webdriver.Chrome(options=options)

def read_hojin_csv():
    global hojin_list
    # 法人番号のCSVファイルを読込
    files = glob.glob('hojin-csv/*.csv')
    # print(files)
    for file in files:
        with open(file, 'r') as f:
            reader = csv.reader(f)
            hojin_list.extend(reader)

def get_hoken(hojin_id, pref_id):
    global driver
    result = []
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
    #hit_num = int(driver.find_element(By.CLASS_NAME, 'total').text.split('件')[0])
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
            continue
        else:
            result.append([tds_text[0], tds_text[1], tds_text[2], tds_text[3]])
    # 最初の列を削除
    return result[1:]

if __name__ == '__main__':
    # 開始行と終了行を引数で指定
    if len(sys.argv) != 3:
        start = 0
        end = -1
    else:
        start = int(sys.argv[1])
        end = int(sys.argv[2])

    # CSVファイルを読み込み
    print('load csv...', end='', flush=True)
    read_hojin_csv()
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
        
        result = get_hoken(hojin_id, pref_id)
        # 結果をCSVに書き込み
        with open(f'result-{start}-{end}.csv', 'a') as f:
            writer = csv.writer(f, lineterminator='\n')
            for row in result:
                writer.writerow([hojin_id] + row)
        time.sleep(0.8)
