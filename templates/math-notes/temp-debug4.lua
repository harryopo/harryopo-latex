local f = io.open('temp-debug4.txt', 'w')
f:write('FILTER LOADED\n')
function Table(tbl)
  f:write('TABLE CALLED\n')
  f:write(string.format('type(tbl)=%s\n', type(tbl)))
  for k, v in pairs(tbl) do
    f:write(string.format('  tbl[%s] -> %s\n', tostring(k), type(v)))
  end
  if tbl.head then
    f:write('  HAS head\n')
    for k, v in pairs(tbl.head) do
      f:write(string.format('    head[%s] -> %s\n', tostring(k), type(v)))
    end
  end
  if tbl.bodies then
    f:write(string.format('  bodies count: %d\n', #tbl.bodies))
    local body = tbl.bodies[1]
    if body then
      for k, v in pairs(body) do
        f:write(string.format('    body[%s] -> %s\n', tostring(k), type(v)))
      end
    end
  end
  return tbl
end
