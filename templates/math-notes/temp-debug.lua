function Table(tbl)
  io.stderr:write("=== TABLE DEBUG ===\n")
  for k, v in pairs(tbl) do
    io.stderr:write(string.format("  %-10s = %s\n", k, type(v)))
  end
  if tbl.head then
    io.stderr:write(string.format("  head type = %s\n", type(tbl.head)))
    for k, v in pairs(tbl.head) do
      io.stderr:write(string.format("    head.%-10s = %s\n", k, type(v)))
    end
  end
  return tbl
end
return { {Table = Table} }
