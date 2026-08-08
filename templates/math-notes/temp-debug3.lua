io.stderr:write('FILTER LOADED\n')
function Table(tbl)
  io.stderr:write('TABLE CALLED\n')
  io.stderr:write(string.format('type(tbl)=%s\n', type(tbl)))
  io.stderr:write(string.format('tbl.t=%s\n', tostring(tbl.t)))
  -- dump keys
  for k, v in pairs(tbl) do
    io.stderr:write(string.format('  %s -> %s\n', tostring(k), type(v)))
  end
  if tbl.head then
    io.stderr:write('  head present\n')
    for k, v in pairs(tbl.head) do
      io.stderr:write(string.format('    head.%s -> %s\n', tostring(k), type(v)))
    end
    if tbl.head.rows then
      io.stderr:write(string.format('    head.rows count: %d\n', #tbl.head.rows))
    end
  else
    io.stderr:write('  NO head\n')
  end
  if tbl.bodies then
    io.stderr:write(string.format('  bodies count: %d\n', #tbl.bodies))
    for i, body in ipairs(tbl.bodies) do
      io.stderr:write(string.format('  body[%d] type: %s\n', i, type(body)))
      for k, v in pairs(body) do
        io.stderr:write(string.format('    body.%s -> %s\n', tostring(k), type(v)))
      end
      io.stderr:write(string.format('    body.body count: %d\n', body.body and #body.body or -1))
    end
  end
  return tbl
end
return { {Table = Table} }
