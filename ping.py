import subprocess
import concurrent.futures
import sys

def check_ping(line):
    line = line.strip()
    if not line:
        return None
    try:
        left_part = line.split('#')[0].strip()
        if left_part.startswith('['):
            host = left_part[1:].split(']')[0]
        else:
            host = left_part.split(':')[0]
        
        if ':' in host:
            cmd = ['ping6', '-c', '1', '-W', '2', host]
        else:
            cmd = ['ping', '-c', '1', '-W', '2', host]
            
        result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if result.returncode == 0:
            print(f"[保留] 连通成功: {host}")
            return line
        else:
            print(f"[丢弃] 无法连通: {host}")
            return None
    except:
        print(f"[错误] 解析失败或异常: {line}")
        return None

if __name__ == '__main__':
    print("=== 开始执行 Ping 清洗任务 ===")
    
    try:
        with open('max.txt', 'r', encoding='utf-8') as f:
            lines = [line for line in f.readlines() if line.strip()]
    except FileNotFoundError:
        print("错误: 找不到 max.txt 文件！")
        sys.exit(1)
        
    total_count = len(lines)
    print(f"-> 成功读取 max.txt，共发现 {total_count} 个待测目标。")
    print("-> 正在启动 50 线程并发检测...\n")
    
    valid_lines = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        for res in executor.map(check_ping, lines):
            if res:
                valid_lines.append(res)
                
    kept_count = len(valid_lines)
    discarded_count = total_count - kept_count
    
    print("\n=== 检测过程结束 ===")
    print(f"统计信息:")
    print(f"  - 初始目标总数: {total_count}")
    print(f"  - 成功保留数量: {kept_count}")
    print(f"  - 超时丢弃数量: {discarded_count}")
    
    with open('max.txt', 'w', encoding='utf-8') as f:
        for line in valid_lines:
            f.write(line + '\n')
            
    print("-> 存活的 IP/域名 已重新写入 max.txt。")
