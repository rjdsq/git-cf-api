import requests
import re
from bs4 import BeautifulSoup

def fetch_four_blocks_structure():
    url = "https://cf.090227.xyz/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    global_seen = set()
    total_raw_count = 0

    cm_domains = []
    official_domains = []
    more_domains = []
    api_ips = []

    def add_item(addr, remark, target_list):
        nonlocal total_raw_count
        total_raw_count += 1
        addr = addr.replace('*.', 'cdn.').replace('*', 'cdn')
        if addr and addr not in global_seen:
            global_seen.add(addr)
            formatted = f"{addr}#{remark}" if remark else addr
            target_list.append(formatted)

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        sections = soup.find_all('section', class_='section')
        for sec in sections:
            title_elem = sec.find(['h2', 'h3'])
            title = title_elem.get_text() if title_elem else ""

            if "CM优选" in title:
                target_list = cm_domains
                keep_remark = True
            elif "官方优选" in title:
                target_list = official_domains
                keep_remark = True
            elif "更多优选" in title:
                target_list = more_domains
                keep_remark = False
            elif "API" in title:
                target_list = api_ips
                keep_remark = True
            else:
                continue

            cards = sec.find_all('div', class_='domain-card-content')
            for card in cards:
                remark = ""
                if keep_remark:
                    badges = card.find_all('span', class_='domain-badge')
                    valid_badges = [b.get_text().strip() for b in badges if b.get_text().strip() not in {'泛域名', '三网优选'}]
                    if valid_badges:
                        remark = "-".join(valid_badges)

                btn = card.find('button', class_='copy-domain')
                if btn:
                    match = re.search(r"copyDomain\('([^']+)'\)", btn.get('onclick', ''))
                    if match:
                        addr = match.group(1).strip()
                        if addr:
                            add_item(addr, remark, target_list)

            pre_tags = sec.find_all('pre')
            for pre in pre_tags:
                lines = pre.get_text().split('\n')
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split('#')
                    addr = parts[0].strip()
                    pre_remark = ""
                    if keep_remark and len(parts) > 1:
                        pre_remark = parts[1].strip()
                    add_item(addr, pre_remark, target_list)

            if "API" in title:
                api_list_ul = sec.find('ul', class_='api-list')
                if api_list_ul:
                    api_lis = api_list_ul.find_all('li')
                    for li in api_lis:
                        api_url = li.get_text().strip()
                        if not api_url.startswith('http'): 
                            continue

                        cat = ""
                        api_url_lower = api_url.lower()
                        if 'ct' in api_url_lower: 
                            cat = "电信"
                        elif 'cmcc' in api_url_lower: 
                            cat = "移动"
                        elif 'cu' in api_url_lower: 
                            cat = "联通"

                        try:
                            api_res = requests.get(api_url, headers=headers, timeout=15)
                            text = api_res.text
                            ips = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', text) + re.findall(r'(?:[A-Fa-f0-9]{1,4}:){2,7}[A-Fa-f0-9]{1,4}', text)
                            for ip in ips:
                                add_item(ip, cat, target_list)
                        except:
                            continue
    except Exception as e:
        print(f"\n[错误] {e}")

    detail_lines = []
    if cm_domains:
        detail_lines.extend(["", "【CM优选域名区块】"] + cm_domains)
    if official_domains:
        detail_lines.extend(["", "【官方优选域名区块】"] + official_domains)
    if more_domains:
        detail_lines.extend(["", "【更多优选域名区块】"] + more_domains)
    if api_ips:
        detail_lines.extend(["", "【第三方API区块】"] + api_ips)

    overview_lines = [
        "",
        "===================================",
        "      数据抓取运行日志概览",
        "===================================",
        f"CM优选域名  : {len(cm_domains)} 个",
        f"官方优选域名: {len(official_domains)} 个",
        f"更多优选域名: {len(more_domains)} 个",
        f"第三方API   : {len(api_ips)} 个",
        "===================================",
        f"原始抓取总计: {total_raw_count} 条",
        f"去除重复节点: {total_raw_count - len(global_seen)} 条",
        f"去重实有节点: {len(global_seen)} 个",
        "==================================="
    ]

    for line in detail_lines:
        print(line)
    for line in overview_lines:
        print(line)

    try:
        with open('cf.090227.xyz.txt', 'w', encoding='utf-8') as f:
            for lst in [cm_domains, official_domains, more_domains, api_ips]:
                for item in lst:
                    f.write(item + "\n")
    except Exception as e:
        print(f"\n[错误] 数据TXT写入失败: {e}")

    try:
        with open('cf.090227.xyz.log', 'w', encoding='utf-8') as log_f:
            for line in overview_lines:
                log_f.write(line + "\n")
            for line in detail_lines:
                log_f.write(line + "\n")
    except Exception as e:
        print(f"\n[错误] 日志LOG写入失败: {e}")

if __name__ == "__main__":
    fetch_four_blocks_structure()
