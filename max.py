import os
import re

def merge_and_sort_files():
    input_files = ['Cf.090227.xyz.txt', 'vps789.com.txt', 'cf-speed-dns.txt']
    merged_data = {}
    total_raw_count = 0

    for file_name in input_files:
        if os.path.exists(file_name):
            with open(file_name, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    total_raw_count += 1
                    
                    # 增强版分割逻辑：兼容没有#的情况，也兼容备注里有多个#的情况
                    if '#' in line:
                        parts = line.split('#', 1)
                        addr = parts[0].strip()
                        remark = parts[1].strip()
                    else:
                        addr = line.strip()
                        remark = ""

                    if not addr:
                        continue

                    if addr not in merged_data:
                        merged_data[addr] = []
                    
                    if remark and remark not in merged_data[addr]:
                        merged_data[addr].append(remark)

    groups = {
        'domain_remark': [],
        'telecom': [],
        'mobile': [],
        'unicom': [],
        'pure_ip_other': [],
        'pure_ip_none': [],
        'domain_no_remark': []
    }

    for addr, remarks in merged_data.items():
        merged_remark = " | ".join(remarks)
        # 兼容性IP判断正则
        is_pure_ip = bool(re.match(r"^\d{1,3}(\.\d{1,3}){3}$", addr))

        if merged_remark:
            line_str = f"{addr}#{merged_remark}"
        else:
            line_str = addr

        if not is_pure_ip:
            if merged_remark:
                groups['domain_remark'].append(line_str)
            else:
                groups['domain_no_remark'].append(line_str)
        else:
            if not merged_remark:
                groups['pure_ip_none'].append(line_str)
            elif '电信' in merged_remark:
                groups['telecom'].append(line_str)
            elif '移动' in merged_remark:
                groups['mobile'].append(line_str)
            elif '联通' in merged_remark:
                groups['unicom'].append(line_str)
            else:
                groups['pure_ip_other'].append(line_str)

    # 各组内按长度排序
    for key in groups:
        groups[key].sort(key=len)

    final_output = []
    final_output.extend(groups['domain_remark'])
    final_output.extend(groups['telecom'])
    final_output.extend(groups['mobile'])
    final_output.extend(groups['unicom'])
    final_output.extend(groups['pure_ip_other'])
    final_output.extend(groups['pure_ip_none'])
    final_output.extend(groups['domain_no_remark'])

    final_count = len(final_output)
    duplicate_count = total_raw_count - final_count

    overview_lines = [
        "========== 采集汇总 ==========",
        f"项目原始总数: {total_raw_count}",
        f"重复过滤数量: {duplicate_count}",
        f"最终保留总数: {final_count}",
        "---------- 详细分类 ----------",
        f"1.域名带备注: {len(groups['domain_remark'])}",
        f"2.纯IP-电信: {len(groups['telecom'])}",
        f"3.纯IP-移动: {len(groups['mobile'])}",
        f"4.纯IP-联通: {len(groups['unicom'])}",
        f"5.纯IP-其他: {len(groups['pure_ip_other'])}",
        f"6.纯IP-无注: {len(groups['pure_ip_none'])}",
        f"7.域名-无注: {len(groups['domain_no_remark'])}",
        "=============================="
    ]

    for line in overview_lines:
        print(line)

    with open('max.txt', 'w', encoding='utf-8') as f:
        for line in final_output:
            f.write(line + '\n')

    with open('max.log', 'w', encoding='utf-8') as f:
        for line in overview_lines:
            f.write(line + '\n')

if __name__ == '__main__':
    merge_and_sort_files()
