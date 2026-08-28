-- ============================================================
--  harryopo-mathnotes Pandoc Lua Filter — 智能表格
--  Pandoc 3.x AST 兼容
--  功能：
--    1. tabularx 比例 X 列（自动换行，无 Overfull hbox）
--    2. 基于内容宽度智能分配列宽比例
--    3. 数字列自动居中
--    4. 表格标题放在表格下方
--    5. booktabs 三线表风格
--  用法: pandoc input.md -L pandoc/mathnotes-table.lua
--        --template=pandoc/mathnotes-template.latex -o output.pdf
-- ============================================================

-- ==================== Cell -> LaTeX (preserves math/Bold/etc) ====================

-- Convert a Cell's contents to proper LaTeX string
-- Uses pandoc.write for correct math ($...$) and inline formatting
local function cell_to_latex(cell)
  if not cell or not cell.contents then
    return ""
  end
  -- Wrap blocks in a temporary Pandoc doc and write to LaTeX
  local doc = pandoc.Pandoc(cell.contents)
  local latex = pandoc.write(doc, "latex")
  -- Strip leading/trailing whitespace and newlines
  latex = latex:gsub("^%s+", ""):gsub("%s+$", ""):gsub("\n", " ")
  return latex
end

-- Compute plain-text character width for column sizing (not LaTeX output)
local function cell_plain_text(cell)
  return pandoc.utils.stringify(cell):gsub("%s+", "")
end

-- 计算 Unicode-aware 字符宽度（中文=2, ASCII=1）
local function cell_width(text)
  local w = 0
  for ch in text:gmatch("[%z\1-\127\194-\244][\128-\191]*") do
    if #ch == 1 then
      w = w + 1
    else
      w = w + 2
    end
  end
  return w
end

-- 判断是否主要为数字列
local function is_numeric_column(all_rows, col_idx)
  local num_count, total = 0, 0
  for _, row in ipairs(all_rows) do
    if row.cells[col_idx] then
      total = total + 1
      local text = pandoc.utils.stringify(row.cells[col_idx]):gsub("%s+", "")
      if text:match("^[-–]?%d+[.]?%d*$") then
        num_count = num_count + 1
      end
    end
  end
  return total > 0 and (num_count / total) > 0.6
end

function Table(tbl)
  -- Collect all rows: head rows + body rows
  local all_rows = {}

  -- Header rows (tbl.head is a TableHead userdata, .rows is the list)
  if tbl.head and tbl.head.rows then
    for _, row in ipairs(tbl.head.rows) do
      table.insert(all_rows, row)
    end
  end

  -- Body rows (tbl.bodies is a list of TableBody, each has .body)
  if tbl.bodies then
    for _, body_obj in ipairs(tbl.bodies) do
      if body_obj.body then
        for _, row in ipairs(body_obj.body) do
          table.insert(all_rows, row)
        end
      end
      if body_obj.head then
        for _, row in ipairs(body_obj.head) do
          table.insert(all_rows, row)
        end
      end
    end
  end

  if #all_rows == 0 then
    return tbl
  end

  -- Determine ncols from first row's cells
  local ncols = 0
  if #all_rows > 0 then
    ncols = #all_rows[1].cells
  end

  -- Calculate max width per column (use plain text for sizing)
  local max_lens = {}
  for i = 1, ncols do max_lens[i] = 0 end
  for _, row in ipairs(all_rows) do
    for i = 1, math.min(#row.cells, ncols) do
      local text = cell_plain_text(row.cells[i])
      local w = cell_width(text)
      if w > max_lens[i] then max_lens[i] = w end
    end
  end

  -- Calculate ratios
  local total = 0
  for i = 1, ncols do total = total + max_lens[i] end
  if total == 0 then total = ncols end

  -- Build proportional X column spec
  -- Rule: sum of \hsize across X columns must equal ncols
  local colspec_parts = {}
  for i = 1, ncols do
    local ratio = max_lens[i] / total
    local hfactor = ratio * ncols
    local align = ""
    if is_numeric_column(all_rows, i) then
      align = "\\centering\\arraybackslash"
    else
      align = "\\raggedright\\arraybackslash"
    end
    colspec_parts[i] = string.format(
      ">{\\hsize=%.3f\\hsize\\linewidth=\\hsize%s}X",
      hfactor, align
    )
  end
  local colspec = table.concat(colspec_parts, "")

  -- Build LaTeX output
  local lines = {}
  table.insert(lines, "\\begin{table}[htbp]")
  table.insert(lines, "\\centering")
  table.insert(lines, "\\begin{tabularx}{\\textwidth}{" .. colspec .. "}")
  table.insert(lines, "\\toprule")

  -- Header rows
  if tbl.head and tbl.head.rows then
    for _, row in ipairs(tbl.head.rows) do
      local hcells = {}
      for i = 1, ncols do
        if row.cells[i] then
          hcells[i] = "\\textbf{" .. cell_to_latex(row.cells[i]) .. "}"
        else
          hcells[i] = ""
        end
      end
      table.insert(lines, table.concat(hcells, " & ") .. " \\\\")
    end
    table.insert(lines, "\\midrule")
  end

  -- Body rows
  if tbl.bodies then
    for _, body_obj in ipairs(tbl.bodies) do
      if body_obj.head then
        for _, row in ipairs(body_obj.head) do
          local cells = {}
          for i = 1, ncols do
            cells[i] = row.cells[i] and cell_to_latex(row.cells[i]) or ""
          end
          table.insert(lines, table.concat(cells, " & ") .. " \\\\")
        end
      end
      if body_obj.body then
        for _, row in ipairs(body_obj.body) do
          local cells = {}
          for i = 1, ncols do
            cells[i] = row.cells[i] and cell_to_latex(row.cells[i]) or ""
          end
          table.insert(lines, table.concat(cells, " & ") .. " \\\\")
        end
      end
    end
  end

  table.insert(lines, "\\bottomrule")
  table.insert(lines, "\\end{tabularx}")

  -- Caption below table
  if tbl.caption then
    local cap_text = pandoc.utils.stringify(tbl.caption)
    if cap_text ~= "" then
      table.insert(lines, "\\caption{" .. cap_text .. "}")
    end
  end

  table.insert(lines, "\\end{table}")

  return pandoc.RawBlock("latex", table.concat(lines, "\n"))
end

return {
  {Table = Table}
}
