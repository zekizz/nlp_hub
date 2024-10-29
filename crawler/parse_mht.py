"""
save as mhtml
"""

from email import policy
from email.parser import BytesParser
from bs4 import BeautifulSoup
import json


def parse_content(html_content, class_name='css-iovd7k'):
    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    result = {}
    # 提取“利润：7D 交易数”
    profit_div = soup.find('div', class_=class_name)
    profit_text = profit_div.get_text(strip=True)
    result['利润'] = profit_text

    # 假设我们要提取所有带有css-1r6lea类的div标签内的信息
    elements = soup.find_all('div', class_='css-1r6lea')
    for element in elements:
        try:
            title = element.find('div', class_='css-kiugb7').text.strip()

            value = element.find('div', class_='css-1pjn4fe').text.strip() if element.find('div',
                                                                                           class_='css-1pjn4fe') else element.find(
                'div', class_='css-13k40wa').text.strip()

            # print(f'{title}: {value}')
            result[title] = value
        except:
            pass

    # 提取“SOL 余额”
    sol_balance_div = soup.find('div', class_='css-qq3v8v')
    sol_balance_text = sol_balance_div.get_text(strip=True).replace('&nbsp;', ' ').split(' (')[0]
    # print('sol_balance_text:', sol_balance_text)
    result['SOL 余额'] = sol_balance_text

    return result


def extract_and_parse(file_path):
    # 读取 MHT 文件
    with open(file_path, 'rb') as f:
        msg = BytesParser(policy=policy.default).parse(f)

    # 寻找 HTML 部分
    for part in msg.walk():
        if part.get_content_type() == "text/html":
            # charset = part.get_content_charset('utf-8')  # 获取字符集，默认为 utf-8
            # html_content = part.get_content(decode=True).decode(charset)
            html_content = part.get_payload(decode=True).decode()  # type: ignore[union-attr]
            break
    else:
        raise ValueError("No HTML part found in MHT file")

    # result = parse_content(html_content)
    # return result
    return html_content


def extract_account_info(file_path=None):
    """提取一个账号的信息"""
    if not file_path:
        file_path = '/Users/4paradigm/Downloads/[gmgn.ai] 2024.10.28.mht'
    html_content = extract_and_parse(file_path)
    result = parse_content(html_content)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    """
    {
      "利润": "30D 交易数20/9",
      "总盈亏": "+$237.4K (+196.81%)",
      "未实现利润": "$85.7K",
      "30D 买入总成本": "$42.8K",
      "30D 代币平均买入成本": "$3,894.09",
      "30D 代币平均实现利润": "+$1,177.26",
      "SOL 余额": "11.45 SOL($2,006.09)"
    }
    """
    return result


def extract_by_root():
    """种子页面获取，提取持有人账号"""
    file_path = '/Users/4paradigm/Downloads/[gmgn.ai] 2024.10.28—EYE $0.0049207, EYE Am Watching You, price chart - GMGN.AI Discover faster, Trading in seconds. On-chain at the speed of light. Click to trade..mht'
    # xpath_query = '//*[@id="tabs-:r16:--tabpanel-4"]/div/div[2]/div/div/div/div/div/table/tbody'
    xpath_table = '//*[@id="tabs-:r16:--tabpanel-4"]/div/div[2]/div/div/div/div/div/table/tbody'

    html_content = extract_and_parse(file_path)
    # print(html_content)

    # 创建BeautifulSoup对象
    soup = BeautifulSoup(html_content, 'html.parser')

    # 定位到特定的表格
    target_div = soup.find(id='tabs-:r16:--tabpanel-4')
    if target_div:
        table = target_div.find('div', class_='g-table-content').find('table')
        if table:
            # 获取表头信息
            headers = [header.get_text() for header in table.find('thead').find_all('th')]
            print("Headers:", headers)

            # 获取每一行的数据
            rows = table.find('tbody').find_all('tr', class_='g-table-row')
            for row in rows:
                row_data = {}
                row_key = row.get('data-row-key')
                if row_key:
                    cells = row.find_all('td')
                    for header, cell in zip(headers, cells):
                        row_data[header] = cell.get_text(strip=True)
                    print(f"Row Key: {row_key}, Data: {row_data}")
        else:
            print("Target table not found.")
    else:
        print("Target div not found.")


# extract_account_info()
extract_by_root()
