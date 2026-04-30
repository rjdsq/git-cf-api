import requests
import re
from bs4 import BeautifulSoup

def fetch_cfspeeddns_index_ips():
    url = "https://raw.githubusercontent.com/ZhiXuanWang/cf-speed-dns/main/index.html"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    parsed_data = []

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        for tr in soup.find_all('tr'):
            cols = tr.find_all('td')
            if len(cols) >= 6:
                ip_elem = cols[0].find('a')
                if not ip_elem:
                    continue
                ip = ip_elem.get_text(strip=True)
                
                latency_str = cols[4].get_text(strip=True)
                speed_str = cols[5].get_text(strip=True)
                
                if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", ip):
                    parsed_data.append({
                        'ip': ip,
                        'latency': latency_str,
                        'speed': speed_str
                    })

    except Exception as e:
        print(f"\n[错误] 获取失败: {e}")
        return

    txt_lines = []
    log_detail_lines = []

    for item in parsed_data:
        formatted_line = f"{item['ip']}#{item['latency']}ms | 速度:{item['speed']}"
        txt_lines.append(formatted_line)
        log_detail_lines.append(formatted_line)

    overview_lines = [
        "===================================",
        "      数据抓取运行日志概览",
        "===================================",
        f" 提取总计: {len(parsed_data)} 个优选节点",
        "==================================="
    ]

    for line in log_detail_lines:
        print(line)
        
    print("\n")
    for line in overview_lines:
        print(line)

    try:
        with open('cf-speed-dns.txt', 'w', encoding='utf-8') as f:
            for line in txt_lines:
                f.write(line + "\n")
    except:
        pass

    try:
        with open('cf-speed-dns.log', 'w', encoding='utf-8') as f:
            for line in overview_lines:
                f.write(line + "\n")
            f.write("\n")
            for line in log_detail_lines:
                f.write(line + "\n")
    except:
        pass

if __name__ == "__main__":
    fetch_cfspeeddns_index_ips()
