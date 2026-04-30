import requests
import re

def fetch_final_structure():
    urls = [
        "https://vps789.com/openApi/cfIpApi",
        "https://vps789.com/openApi/cfIpTop20"
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://vps789.com/'
    }

    line_order = ['电信', '移动', '联通']
    line_map = {'CT': '电信', 'CM': '移动', 'CU': '联通'}
    
    ip_buckets = {"电信": [], "移动": [], "联通": [], "纯IP": []}
    domain_bucket = []
    
    processed_addrs = set() 
    total_raw_count = 0

    def is_ip(address):
        return bool(re.match(r"^\d{1,3}(\.\d{1,3}){3}$", address))

    for url in urls:
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code != 200: continue
            data = response.json().get('data', {})
            
            for key, line_name in line_map.items():
                nodes = data.get(key, [])
                total_raw_count += len(nodes)
                for item in nodes:
                    addr = item.get('ip', '').strip()
                    if addr and addr not in processed_addrs:
                        ip_buckets[line_name].append(f"{addr}#{line_name}")
                        processed_addrs.add(addr)

            good_nodes = data.get('good', [])
            total_raw_count += len(good_nodes)
            for item in good_nodes:
                addr = item.get('ip', '').strip()
                if addr and addr not in processed_addrs:
                    if is_ip(addr):
                        ip_buckets["纯IP"].append(addr)
                    else:
                        domain_bucket.append(addr)
                    processed_addrs.add(addr)
        except:
            continue

    final_output_list = []
    
    for cat in (line_order + ["纯IP"]):
        sorted_ips = sorted(ip_buckets[cat], key=lambda x: (len(x), x))
        final_output_list.extend(sorted_ips)
    
    sorted_domains = sorted(domain_bucket, key=lambda x: (len(x), x))
    final_output_list.extend(sorted_domains)

    duplicate_count = total_raw_count - len(processed_addrs)
    
    overview_lines = [
        "===================================",
        "      数据抓取运行日志概览",
        "===================================",
        "【纯 IP 统计】",
        f" 电信节点: {len(ip_buckets['电信'])} 个",
        f" 移动节点: {len(ip_buckets['移动'])} 个",
        f" 联通节点: {len(ip_buckets['联通'])} 个",
        f" 优选IP  : {len(ip_buckets['纯IP'])} 个",
        f" 优选域名: {len(domain_bucket)} 个",
        "-----------------------------------",
        "【汇总统计】",
        f" 原始抓取: {total_raw_count} 条",
        f" 重复过滤: {duplicate_count} 条",
        f" 去重实有: {len(processed_addrs)} 个",
        "==================================="
    ]

    for content in final_output_list:
        print(content)
        
    print("\n")
    for line in overview_lines:
        print(line)

    try:
        with open('vps789.com.txt', 'w', encoding='utf-8') as f:
            for content in final_output_list:
                f.write(content + "\n")
    except Exception as e:
        print(f"\n[错误] TXT文件写入失败: {e}")

    try:
        with open('vps789.com.log', 'w', encoding='utf-8') as f:
            for line in overview_lines:
                f.write(line + "\n")
            f.write("\n")
            for content in final_output_list:
                f.write(content + "\n")
    except Exception as e:
        print(f"\n[错误] LOG文件写入失败: {e}")

if __name__ == "__main__":
    fetch_final_structure()
