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
    
    log_time_std = bj_time.strftime('%Y-%m-%d %H:%M:%S')
    
    m, d, h, mi = bj_time.month, bj_time.day, bj_time.hour, bj_time.minute
    data_time_str = f"{m}/{d}/{h}:{mi}"

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
                        duplicate_details.append(f"重复项: 地址 [{addr}] 来源于 [{file_name}]")
                    
                    if remark and remark not in merged_data[addr]:
                        merged_data[addr].append(remark)

    groups = {
        'domain_remark': [], 'telecom': [], 'mobile': [], 
        'unicom': [], 'ip_other': [], 'ip_none': [], 'domain_none': []
    }

    for addr, remarks in merged_data.items():
        if remarks:
            merged_remark = " | ".join(remarks) + f" | {data_time_str}"
        else:
            merged_remark = data_time_str

        is_domain = any(c.isalpha() for c in addr)
        line_str = f"{addr}#{merged_remark}"

        if is_domain:
            if remarks: groups['domain_remark'].append(line_str)
            else: groups['domain_none'].append(line_str)
        else:
            raw_remarks_str = " ".join(remarks)
            if not remarks: groups['ip_none'].append(line_str)
            elif '电信' in raw_remarks_str: groups['telecom'].append(line_str)
            elif '移动' in raw_remarks_str: groups['mobile'].append(line_str)
            elif '联通' in raw_remarks_str: groups['unicom'].append(line_str)
            else: groups['ip_other'].append(line_str)

    final_output = []
    order = ['domain_remark', 'telecom', 'mobile', 'unicom', 'ip_other', 'ip_none', 'domain_none']
    for key in order:
        groups[key].sort(key=len)
        final_output.extend(groups[key])

    final_count = len(merged_data)
    
    log_content = [
        "==========================================",
        "          Cloudflare IP 采集日志          ",
        "==========================================",
        f"打印时间: {log_time_std}",
        f"数据标记: {data_time_str}",
        "------------------------------------------",
        "【数据概览】",
        f"原始读取总行数: {total_raw_count}",
        f"去重保留有效数: {final_count}",
        f"累计过滤重复数: {len(duplicate_details)}",
        "------------------------------------------",
        "【文件来源统计】"
    ]
    
    for src, count in source_counts.items():
        log_content.append(f"- {src}: {count} 行")
        
    log_content.append("------------------------------------------")
    log_content.append("【结果分类占比】")
    
    if final_count > 0:
        for key in order:
            count = len(groups[key])
            percent = (count / final_count) * 100
            log_content.append(f"- {key}: {count} 项 ({percent:.1f}%)")
    
    log_content.append("------------------------------------------")
    log_content.append("【详细过滤清单】")
    
    if duplicate_details:
        log_content.extend(duplicate_details)
    else:
        log_content.append("此轮运行未发现重复 IP 地址。")
    
    log_content.append("==========================================")

    for l in log_content: print(l)

    with open('max.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(final_output) + '\n')

    with open('max.log', 'w', encoding='utf-8') as f:
        f.write('\n'.join(log_content) + '\n')

if __name__ == '__main__':
    merge_and_sort_files()
