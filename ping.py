import subprocess
import concurrent.futures

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
            return line
    except:
        pass
    return None

if __name__ == '__main__':
    with open('max.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    valid_lines = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        for res in executor.map(check_ping, lines):
            if res:
                valid_lines.append(res)
                
    with open('max.txt', 'w', encoding='utf-8') as f:
        for line in valid_lines:
            f.write(line + '\n')