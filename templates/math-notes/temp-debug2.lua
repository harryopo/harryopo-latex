function dump(o, indent)
  indent = indent or ''
  if type(o) == 'table' then
    for k, v in pairs(o) do
      local t = type(v)
      if t == 'table' then
        io.stderr:write(string.format('%s%s (table) {\n', indent, k))
        dump(v, indent .. '  ')
        io.stderr:write(string.format('%s}\n', indent))
      else
        io.stderr:write(string.format('%s%s = %s\n', indent, k, t))
      end
    end
  end
end
function Table(tbl)
  io.stderr:write('=== TABLE ===\n')
  dump(tbl)
  io.stderr:write('=== END ===\n')
  return tbl
end
return { {Table = Table} }
