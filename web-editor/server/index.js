// harryopo-web 后端服务：MD 文档读写 + 导出（复用 office.py 渲染引擎）
// 运行：node server/index.js  （或 npm run server）
import express from 'express'
import cors from 'cors'
import path from 'node:path'
import fs from 'node:fs'
import { spawn } from 'node:child_process'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const PROJECT_ROOT = path.resolve(__dirname, '..', '..') // d:\ai\latex
const DOCS_DIR = path.join(PROJECT_ROOT, "output", "web-editor-docs");
const EXPORT_DIR = path.join(PROJECT_ROOT, "output", "web-editor-exports");
const OFFICE_SCRIPT = path.join(
  PROJECT_ROOT,
  ".trae", "skills", "harryopo-office", "scripts", "office.py",
);

const app = express();
app.use(cors());
app.use(express.json({ limit: "10mb" }));

fs.mkdirSync(DOCS_DIR, { recursive: true });
fs.mkdirSync(EXPORT_DIR, { recursive: true });

// ---------- 文档列表 ----------
app.get("/api/docs", (req, res) => {
  const files = fs.readdirSync(DOCS_DIR)
    .filter((f) => f.endsWith(".md"))
    .sort();
  res.json({ docs: files });
});

// ---------- 加载文档（path 支持子目录） ----------
app.get("/api/doc", (req, res) => {
  const p = String(req.query.path || req.query.name || "");
  if (!p.toLowerCase().endsWith(".md")) return res.status(400).json({ error: "BAD_REQUEST" });
  try {
    const rel = safeRel(p);
    const file = path.join(DOCS_DIR, rel);
    if (!fs.existsSync(file)) return res.status(404).json({ error: "NOT_FOUND" });
    res.json({ path: rel, content: fs.readFileSync(file, "utf-8") });
  } catch (e) {
    res.status(400).json({ error: e.message });
  }
});

// ---------- 保存文档（path 支持子目录） ----------
app.put("/api/doc", (req, res) => {
  const { path: p, name, content } = req.body || {};
  if (typeof content !== "string") return res.status(400).json({ error: "BAD_REQUEST" });
  const relName = p || `${name}.md`;
  if (!relName.toLowerCase().endsWith(".md")) return res.status(400).json({ error: "BAD_REQUEST" });
  try {
    const rel = safeRel(relName);
    const file = path.join(DOCS_DIR, rel);
    fs.mkdirSync(path.dirname(file), { recursive: true });
    fs.writeFileSync(file, content, "utf-8");
    res.json({ ok: true, path: rel });
  } catch (e) {
    res.status(400).json({ error: e.message });
  }
});

// ---------- 导出（调 office.py render）----------
app.post("/api/export", (req, res) => {
  const { name, format } = req.body || {};
  if (!name) return res.status(400).json({ error: "BAD_REQUEST" });
  const safe = String(name).replace(/[^\w\u4e00-\u9fff.-]/g, "");
  const mdFile = path.join(DOCS_DIR, `${safe}.md`);
  if (!fs.existsSync(mdFile)) return res.status(404).json({ error: "NOT_FOUND" });

  const formats = String(format || "word,paper")
    .split(",").map((f) => f.trim()).filter(Boolean).join(",");
  const outDir = path.join(EXPORT_DIR, `${safe}-${Date.now()}`);
  fs.mkdirSync(outDir, { recursive: true });

  const args = [
    OFFICE_SCRIPT, "render", mdFile,
    "--format", formats,
    "--output-dir", outDir,
    "--pdf",
  ];
  console.log("[export]", args.join(" "));
  const child = spawn("python", args, { cwd: PROJECT_ROOT });
  let out = "", err = "";
  child.stdout.on("data", (d) => (out += d));
  child.stderr.on("data", (d) => (err += d));
  child.on("close", (code) => {
    if (code !== 0) {
      return res.status(500).json({ error: "EXPORT_FAILED", log: err.slice(-500) });
    }
    const files = fs.readdirSync(outDir)
      .filter((f) => f.endsWith(".docx") || f.endsWith(".pdf"))
      .map((f) => ({ name: f, url: `/exports/${path.basename(outDir)}/${f}` }));
    res.json({ ok: true, files });
  });
});

// ---------- 文件树 / 多文档管理 ----------

/** 安全相对路径（防目录穿越） */
function safeRel(p) {
  const n = String(p || '').replace(/\\/g, '/').replace(/^\/+|\/+$/g, '')
  if (n.split('/').some((s) => s === '..' || s === '.')) throw new Error('BAD_PATH')
  return n
}

function walkTree(dir, rel = '') {
  return fs.readdirSync(dir, { withFileTypes: true })
    .filter((e) => e.isDirectory() || e.name.endsWith('.md'))
    .sort((a, b) => (a.isDirectory() === b.isDirectory() ? a.name.localeCompare(b.name) : a.isDirectory() ? -1 : 1))
    .map((e) => {
      const p = rel ? `${rel}/${e.name}` : e.name
      if (e.isDirectory()) {
        return { name: e.name, path: p, type: 'dir', children: walkTree(path.join(dir, e.name), p) }
      }
      return { name: e.name, path: p, type: 'md' }
    })
}

app.get('/api/tree', (req, res) => {
  res.json({ tree: walkTree(DOCS_DIR) })
})

// 新建 .md 文件（path 相对 docs 根，支持子目录）
app.post('/api/file', (req, res) => {
  const { path: p, content } = req.body || {}
  if (!p || !p.toLowerCase().endsWith('.md')) return res.status(400).json({ error: 'BAD_REQUEST' })
  try {
    const rel = safeRel(p)
    const abs = path.join(DOCS_DIR, rel)
    if (fs.existsSync(abs)) return res.status(409).json({ error: 'EXISTS' })
    fs.mkdirSync(path.dirname(abs), { recursive: true })
    fs.writeFileSync(abs, content ?? '# 新文档\n\n## 一、\n\n正文。', 'utf-8')
    res.json({ ok: true, path: rel })
  } catch (e) {
    res.status(400).json({ error: e.message })
  }
})

// 删除文件
app.delete('/api/file', (req, res) => {
  const p = String(req.query.path || '')
  try {
    const rel = safeRel(p)
    const abs = path.join(DOCS_DIR, rel)
    if (!fs.existsSync(abs)) return res.status(404).json({ error: 'NOT_FOUND' })
    fs.unlinkSync(abs)
    res.json({ ok: true })
  } catch (e) {
    res.status(400).json({ error: e.message })
  }
})

// ---------- 导出产物静态服务 ----------

const REGISTRY_DIR = path.join(PROJECT_ROOT, 'templates', 'registry')
const DOCX_TEMPLATE_SCRIPT = path.join(
  PROJECT_ROOT, '.trae', 'skills', 'harryopo-office', 'scripts', 'word', 'template', 'docx_template.py',
)
const WORD_TEMPLATE_DIR = path.dirname(DOCX_TEMPLATE_SCRIPT)

// 模板列表（docx 且已生成 schema）
app.get('/api/templates', (req, res) => {
  try {
    const manifest = JSON.parse(fs.readFileSync(path.join(REGISTRY_DIR, 'manifest.json'), 'utf-8'))
    const tpls = (manifest.templates || [])
      .filter((t) => t.format === 'docx' && t.schema_ref)
      .map((t) => ({ id: t.id, name: t.name, category: t.category, engine: t.engine }))
    res.json({ templates: tpls })
  } catch (e) {
    res.status(500).json({ error: e.message })
  }
})

// 模板 schema
app.get('/api/templates/:id/schema', (req, res) => {
  const id = String(req.params.id).replace(/[^\w-]/g, '')
  const file = path.join(REGISTRY_DIR, 'schemas', `${id}.schema.json`)
  if (!fs.existsSync(file)) return res.status(404).json({ error: 'NOT_FOUND' })
  res.json(JSON.parse(fs.readFileSync(file, 'utf-8')))
})

// 模板渲染：{data} → docxtpl render → docx 产物
app.post('/api/templates/:id/render', (req, res) => {
  const id = String(req.params.id).replace(/[^\w-]/g, '')
  const { data } = req.body || {}
  if (!data) return res.status(400).json({ error: 'BAD_REQUEST' })
  const manifest = JSON.parse(fs.readFileSync(path.join(REGISTRY_DIR, 'manifest.json'), 'utf-8'))
  const tpl = (manifest.templates || []).find((t) => t.id === id)
  if (!tpl || !tpl.schema_ref) return res.status(404).json({ error: 'NOT_FOUND' })
  const tplFile = path.join(REGISTRY_DIR, tpl.template_path)
  const schemaFile = path.join(REGISTRY_DIR, tpl.schema_ref)
  const outDir = path.join(EXPORT_DIR, `tpl-${id}-${Date.now()}`)
  fs.mkdirSync(outDir, { recursive: true })
  const dataFile = path.join(outDir, 'data.json')
  const outDocx = path.join(outDir, `${id}.docx`)
  fs.writeFileSync(dataFile, JSON.stringify(data), 'utf-8')
  const args = [
    DOCX_TEMPLATE_SCRIPT, 'render', tplFile,
    '-d', dataFile, '-o', outDocx,
    '--check', '-s', schemaFile,
  ]
  console.log('[tpl-render]', args.join(' '))
  const child = spawn('python', args, { cwd: WORD_TEMPLATE_DIR })
  let out = '', err = ''
  child.stdout.on('data', (d) => (out += d))
  child.stderr.on('data', (d) => (err += d))
  child.on('close', (code) => {
    if (code !== 0 || !fs.existsSync(outDocx)) {
      return res.status(500).json({ error: 'RENDER_FAILED', log: (err + out).slice(-500) })
    }
    res.json({ ok: true, url: `/exports/${path.basename(outDir)}/${path.basename(outDocx)}` })
  })
})

// ---------- 图表渲染（super-diagram，mermaid 走前端）----------
app.post('/api/diagram', (req, res) => {
  const { type, source } = req.body || {}
  if (!source) return res.status(400).json({ error: 'BAD_REQUEST' })
  const figDir = path.join(EXPORT_DIR, 'diagrams')
  fs.mkdirSync(figDir, { recursive: true })
  const tmpMd = path.join(EXPORT_DIR, `_diagram-${Date.now()}.md`)
  const fence = type === 'mermaid' ? 'mermaid' : 'super-diagram'
  fs.writeFileSync(tmpMd, `\`\`\`${fence}\n${source}\n\`\`\`\n`, 'utf-8')
  const script = path.join(PROJECT_ROOT, '.trae', 'skills', 'harryopo-office', 'scripts')
  const child = spawn('python', ['-c', `
import sys, os
sys.path.insert(0, ${JSON.stringify(script)})
from diagram_render import extract_and_render
out = extract_and_render(${JSON.stringify(tmpMd)}, ${JSON.stringify(figDir)})
for k in out: print(k, flush=True)
`], { cwd: PROJECT_ROOT })
  let out = '', err = ''
  child.stdout.on('data', (d) => (out += d))
  child.stderr.on('data', (d) => (err += d))
  child.on('close', (code) => {
    fs.unlinkSync(tmpMd)
    if (code !== 0) return res.status(500).json({ error: 'RENDER_FAILED', log: err.slice(-400) })
    // extract_and_render 输出一行：md 位置 → 实际文件（figDir 下）
    const pngName = out.trim().split(/\s+/).pop()
    const png = path.join(figDir, pngName)
    if (pngName && fs.existsSync(png)) {
      return res.json({ ok: true, url: `/exports/diagrams/${pngName}` })
    }
    res.status(500).json({ error: 'NO_OUTPUT', log: out })
  })
})

// ---------- 导出产物静态服务 ----------
app.use("/exports", express.static(EXPORT_DIR));

// ---------- 生产模式托管前端构建产物 ----------
const DIST = path.join(__dirname, "..", "dist");
if (fs.existsSync(DIST)) {
  app.use(express.static(DIST));
}

const PORT = 8080;
app.listen(PORT, () => {
  console.log(`harryopo-web server: http://127.0.0.1:${PORT}`);
  console.log(`docs: ${DOCS_DIR}`);
});
