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
  const outDir = './api';
  if (!fs.existsSync(outDir)) fs.mkdirSync(outDir);

  const templates = config.templates || [];
  const globalConf = config.global || { filename: "max", tid: templates[0]?.id };
  let allNodesMap = new Map();

  for (const group of config.groups || []) {
    const results = await Promise.all((group.urls || []).map(u => fetchText(u.trim())));
    const groupNodesMap = new Map();
    
    results.forEach(text => {
      const lines = text.split('\n').map(l => l.trim()).filter(l => l && !l.startsWith('<'));
      lines.forEach(line => {
        const parts = line.split('#');
        let hostPort = parts[0].trim().split(' ')[0];
        let originalName = parts[1] ? parts[1].trim() : group.name;
        
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
        
        const hpKey = `${h}:${p}`;
        if (!groupNodesMap.has(hpKey)) {
          groupNodesMap.set(hpKey, { h, p, originalName });
        }
        if (!allNodesMap.has(hpKey)) {
          allNodesMap.set(hpKey, { h, p, originalName });
        }
      });
    });

    const tpl = templates.find(t => t.id === group.tid) || templates[0];
    const sortedNodes = Array.from(groupNodesMap.values()).sort((a, b) => a.h.localeCompare(b.h));
    
    const outLines = sortedNodes.map((node, index) => {
      let nameStr = "";
      if (tpl) {
        tpl.fmt.forEach(tk => {
          if (tk === 'ip_domain') nameStr += node.h;
          else if (tk === 'original') nameStr += node.originalName;
          else if (tk === 'space') nameStr += ' ';
          else if (tk === 'inc') nameStr += (index + 1);
          else if (tk === 'inc01') nameStr += (index + 1).toString().padStart(2, '0');
          else if (tk.startsWith('txt:')) nameStr += tk.substring(4);
        });
      } else {
        nameStr = node.originalName;
      }
      return `${node.h}:${node.p}#${nameStr}`;
    });

    const fname = group.filename || group.name;
    fs.writeFileSync(`${outDir}/${fname}.txt`, outLines.join('\n'));
  }

  const globalTpl = templates.find(t => t.id === globalConf.tid) || templates[0];
  const sortedAll = Array.from(allNodesMap.values()).sort((a, b) => a.h.localeCompare(b.h));
  
  const maxLines = sortedAll.map((node, index) => {
    let nameStr = "";
    if (globalTpl) {
      globalTpl.fmt.forEach(tk => {
        if (tk === 'ip_domain') nameStr += node.h;
        else if (tk === 'original') nameStr += node.originalName;
        else if (tk === 'space') nameStr += ' ';
        else if (tk === 'inc') nameStr += (index + 1);
        else if (tk === 'inc01') nameStr += (index + 1).toString().padStart(2, '0');
        else if (tk.startsWith('txt:')) nameStr += tk.substring(4);
      });
    } else {
      nameStr = node.originalName;
    }
    return `${node.h}:${node.p}#${nameStr}`;
  });

  fs.writeFileSync(`${outDir}/${globalConf.filename}.txt`, maxLines.join('\n'));
}

main();
