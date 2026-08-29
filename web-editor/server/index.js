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

// ---------- 加载文档 ----------
app.get("/api/doc", (req, res) => {
  const name = String(req.query.name || "").replace(/[^\w\u4e00-\u9fff.-]/g, "");
  const file = path.join(DOCS_DIR, `${name}.md`);
  if (!fs.existsSync(file)) return res.status(404).json({ error: "NOT_FOUND" });
  res.json({ name, content: fs.readFileSync(file, "utf-8") });
});

// ---------- 保存文档 ----------
app.put("/api/doc", (req, res) => {
  const { name, content } = req.body || {};
  if (!name || typeof content !== "string") {
    return res.status(400).json({ error: "BAD_REQUEST" });
  }
  const safe = String(name).replace(/[^\w\u4e00-\u9fff.-]/g, "");
  const file = path.join(DOCS_DIR, `${safe}.md`);
  fs.writeFileSync(file, content, "utf-8");
  res.json({ ok: true, name: safe });
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
