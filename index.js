const fs = require('fs');
const https = require('https');
const http = require('http');

const fetchText = (url) => {
  return new Promise((resolve) => {
    if (!url.startsWith('http')) return resolve(url);
    const client = url.startsWith('https') ? https : http;
    const req = client.get(url, { timeout: 5000 }, (res) => {
      if (res.statusCode !== 200) return resolve("");
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve(data));
    });
    req.on('error', () => resolve(""));
    req.on('timeout', () => { req.destroy(); resolve(""); });
  });
};

async function main() {
  const config = JSON.parse(fs.readFileSync('config.json', 'utf-8'));
  const outDir = './output';
  if (!fs.existsSync(outDir)) fs.mkdirSync(outDir);

  const groupData = {}; 

  // 1. 并发抓取所有分组内容
  for (const group of config.groups || []) {
    const results = await Promise.all((group.urls || []).map(u => fetchText(u.trim())));
    const nodes = new Set();
    
    results.forEach(text => {
      const lines = text.split('\n').map(l => l.trim()).filter(l => l && !l.startsWith('<'));
      lines.forEach(line => {
        const parts = line.split('#');
        let hostPort = parts[0].trim().split(' ')[0];
        let name = parts[1] ? parts[1].trim() : group.name;
        
        let h = hostPort, p = "443";
        if (h.startsWith('[')) {
          const e = h.indexOf(']');
          if (e > -1) { 
            const hp = h.substring(e + 1); 
            h = h.substring(0, e + 1); 
            if (hp.startsWith(':')) p = hp.substring(1); 
          }
        } else {
          const pts = h.split(':');
          h = pts[0]; 
          if (pts[1]) p = pts[1];
        }
        nodes.add(`${h}:${p}#${name}`);
      });
    });
    groupData[group.id] = nodes;
  }

  // 2. 根据用户配置的路径，生成对应的 txt 订阅文件
  for (const pt of config.paths || []) {
    let pathNodes = new Set();
    
    if (pt.groupIds && pt.groupIds.includes('all')) {
      Object.values(groupData).forEach(set => set.forEach(n => pathNodes.add(n)));
    } else {
      (pt.groupIds || []).forEach(gid => {
        if (groupData[gid]) groupData[gid].forEach(n => pathNodes.add(n));
      });
    }

    const sorted = Array.from(pathNodes).sort();
    const filename = pt.path.endsWith('.txt') ? pt.path : `${pt.path}.txt`;
    fs.writeFileSync(`${outDir}/${filename}`, sorted.join('\n'));
    console.log(`Generated ${filename} with ${sorted.length} nodes.`);
  }
}

main();
