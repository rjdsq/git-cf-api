import os
import datetime

def merge_and_sort_files():
    input_files = ['cf.090227.xyz.txt', 'vps789.com.txt', 'cf-speed-dns.txt']
    merged_data = {}
    duplicate_details = [] # 详细记录每一次重复
    total_raw_count = 0

    # 修正时区并确保 24 小时制 (北京时间)
    bj_time = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
    time_str = bj_time.strftime('%Y/%m/%d/%H:%M')

    for file_name in input_files:
        if os.path.exists(file_name):
            with open(file_name, 'r', encoding='utf-8') as f:
                for line in f:
                    # 注意：保留原始行内容，仅去掉末尾换行符，确保IP格式原汁原味
                    raw_line = line.replace('\n', '').replace('\r', '')
                    if not raw_line.strip():
                        continue
                    
                    total_raw_count += 1
                    
                    # 拆分地址和备注
                    if '#' in raw_line:
                        parts = raw_line.split('#', 1)
                        addr = parts[0] # 完全保留原始格式，不 strip 空格
                        remark = parts[1].strip()
                    else:
                        addr = raw_line
                        remark = ""

                    # 核心去重与过滤详情记录
                    if addr not in merged_data:
                        merged_data[addr] = []
                    else:
                        # 只要 addr 已经存在，这就是一次重复，记录其原始格式和来源文件名
                        duplicate_details.append(f"重复详情: 地址 [{addr}] 在文件 [{file_name}] 中重复出现")
                    
                    if remark and remark not in merged_data[addr]:
                        merged_data[addr].append(remark)

    # 分类容器
    groups = {
        'domain_remark': [], 'telecom': [], 'mobile': [], 
        'unicom': [], 'ip_other': [], 'ip_none': [], 'domain_none': []
    }

    for addr, remarks in merged_data.items():
        # 组装备注，保留时间戳
        if remarks:
            merged_remark = " | ".join(remarks) + f" | {time_str}"
        else:
            merged_remark = time_str

        # 判断域名还是IP
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

    # 汇总输出 (一行一个，无空行)
    final_output = []
    order = ['domain_remark', 'telecom', 'mobile', 'unicom', 'ip_other', 'ip_none', 'domain_none']
    for key in order:
        groups[key].sort(key=len)
        final_output.extend(groups[key])

    final_count = len(merged_data)
    
    # 构造 max.log 内容
    log_content = [
        "========== 采集汇总 ==========",
        f"北京时间: {time_str} (24H)",
        f"总读取行数: {total_raw_count}",
        f"去重后总数: {final_count}",
        f"累计过滤重复次数: {len(duplicate_details)}",
        "---------- 详细过滤清单 ----------"
    ]
    if duplicate_details:
        log_content.extend(duplicate_details)
    else:
        log_content.append("此轮采集未发现重复项")
    log_content.append("----------------------------------")

    # 控制台打印
    for l in log_content: print(l)

    # 写入 max.txt
    with open('max.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(final_output) + '\n')

    # 写入 max.log
    with open('max.log', 'w', encoding='utf-8') as f:
        f.write('\n'.join(log_content) + '\n')

if __name__ == '__main__':
    merge_and_sort_files()
