import os
import datetime

def merge_and_sort_files():
    input_files = ['cf.090227.xyz.txt', 'vps789.com.txt', 'cf-speed-dns.txt']
    merged_data = {}
    duplicate_details = []
    source_counts = {name: 0 for name in input_files}
    total_raw_count = 0

    now_utc = datetime.datetime.utcnow()
    bj_time = now_utc + datetime.timedelta(hours=8)
    
    std_time = bj_time.strftime('%Y-%m-%d %H:%M:%S')
    data_tag = f"{bj_time.month}/{bj_time.day}/{bj_time.hour}:{bj_time.minute}"

    for file_name in input_files:
        if os.path.exists(file_name):
            with open(file_name, 'r', encoding='utf-8') as f:
                for line in f:
                    raw_line = line.replace('\n', '').replace('\r', '')
                    if not raw_line.strip():
                        continue
                    
                    total_raw_count += 1
                    source_counts[file_name] += 1
                    
                    if '#' in raw_line:
                        parts = raw_line.split('#', 1)
                        addr = parts[0]
                        remark = parts[1].strip()
                    else:
                        addr = raw_line
                        remark = ""

                    if addr not in merged_data:
                        merged_data[addr] = []
                    else:
                        duplicate_details.append(f"┃ ⚡ 重复地址: {addr} ➔ 来源: {file_name}")
                    
                    if remark and remark not in merged_data[addr]:
                        merged_data[addr].append(remark)

    groups = {
        '域名备注': [], '电信线路': [], '移动线路': [], 
        '联通线路': [], '其他备注': [], '纯净IP': [], '纯净域名': []
    }
    
    key_map = {
        'domain_remark': '域名备注', 'telecom': '电信线路', 'mobile': '移动线路',
        'unicom': '联通线路', 'ip_other': '其他备注', 'ip_none': '纯净IP', 'domain_none': '纯净域名'
    }

    for addr, remarks in merged_data.items():
        merged_remark = " | ".join(remarks) + f" | {data_tag}" if remarks else data_tag
        is_domain = any(c.isalpha() for c in addr)
        line_str = f"{addr}#{merged_remark}"

        if is_domain:
            target = '域名备注' if remarks else '纯净域名'
        else:
            raw_remarks_str = " ".join(remarks)
            if not remarks: target = '纯净IP'
            elif '电信' in raw_remarks_str: target = '电信线路'
            elif '移动' in raw_remarks_str: target = '移动线路'
            elif '联通' in raw_remarks_str: target = '联通线路'
            else: target = '其他备注'
        groups[target].append(line_str)

    final_output = []
    order = ['域名备注', '电信线路', '移动线路', '联通线路', '其他备注', '纯净IP', '纯净域名']
    for key in order:
        groups[key].sort(key=len)
        final_output.extend(groups[key])

    final_count = len(merged_data)
    
    log = []
    log.append("┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓")
    log.append(f"┃ 🚀 优选 IP 采集自动化控制台  [{std_time}] ┃")
    log.append("┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫")
    log.append(f"┃ 📊 数据统计概览:")
    log.append(f"┃ ┣ 📥 原始读取总量: {total_raw_count} 行")
    log.append(f"┃ ┣ 🛒 去重保留总量: {final_count} 行")
    log.append(f"┃ ┗ ✂️ 累计拦截重复: {len(duplicate_details)} 次")
    log.append("┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫")
    log.append("┃ 📂 文件来源分布:")
    for src, count in source_counts.items():
        log.append(f"┃ ┣ 📄 {src.ljust(18)} : {str(count).rjust(4)} 行")
    log.append("┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫")
    log.append("┃ 🔍 结果分类明细:")
    if final_count > 0:
        for key in order:
            count = len(groups[key])
            perc = (count / final_count) * 100
            log.append(f"┃ ┣ 🏷️ {key} : {str(count).rjust(4)} 项 ({perc:>5.1f}%)")
    log.append("┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫")
    log.append("┃ ⚠️ 重复项过滤审计清单:")
    if duplicate_details:
        log.extend(duplicate_details)
    else:
        log.append("┃ ┗ ✅ 此轮采集未发现任何重复数据")
    log.append("┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛")

    for line in log: print(line)

    with open('max.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(final_output) + '\n')

    with open('max.log', 'w', encoding='utf-8') as f:
        f.write('\n'.join(log) + '\n')

if __name__ == '__main__':
    merge_and_sort_files()
