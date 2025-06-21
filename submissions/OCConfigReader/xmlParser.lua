-- from https://github.com/jonathanpoelen/lua-xmlparser
--[[
MIT License

Copyright (c) 2016 Jonathan Poelen

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
]]--

local io, string, pairs = io, string, pairs

local slashchar = string.byte('/', 1)
local E = string.byte('E', 1)

--! Return the default entity table.
--! @return table
local function defaultEntityTable()
  return { quot='"', apos='\'', lt='<', gt='>', amp='&', tab='\t', nbsp=' ', }
end

--! @param[in] s string
--! @param[in] entities table : with entity name as key and value as replacement
--! @return string
local function replaceEntities(s, entities)
  return s:gsub('&([^;]+);', entities)
end

--! Add entities to resultEntities then return it.
--! Create new table when resultEntities is nul.
--! Create an entity table from the document entity table.
--! @param[in] docEntities table
--! @param[in,out] resultEntities table|nil
--! @return table
local function createEntityTable(docEntities, resultEntities)
  local entities = resultEntities or defaultEntityTable()
  for _,e in pairs(docEntities) do
    e.value = replaceEntities(e.value, entities)
    entities[e.name] = e.value
  end
  return entities
end

--! Return a document `table`.
--! @code
--!   document = {
--!     children = {
--!       { text=string } or
--!       { tag=string,
--!         attrs={ [name]=value ... },
--!         orderedattrs={ { name=string, value=string }, ... },
--!         children={ ... }
--!       },
--!       ...
--!     },
--!     entities = { { name=string, value=string }, ... },
--!     tentities = { name=value, ... } -- only if evalEntities = true
--!   }
--! @endcode
--! If `evalEntities` is `true`, the entities are replaced and
--! a `tentity` member is added to the document `table`.
--! @param[in] s string : xml data
--! @param[in] evalEntities boolean
--! @return table
local function parse(s, evalEntities)
  -- remove comments
  s = s:gsub('<!%-%-(.-)%-%->', '')

---@diagnostic disable-next-line: unbalanced-assignments
  local entities, tentities = {}

  if evalEntities then
    local pos = s:find('<[_%w]')
    if pos then
      s:sub(1, pos):gsub('<!ENTITY%s+([_%w]+)%s+(.)(.-)%2', function(name, _, entity)
        entities[#entities+1] = {name=name, value=entity}
      end)
      tentities = createEntityTable(entities)
      s = replaceEntities(s:sub(pos), tentities)
    end
  end

  local t, l = {}, {}

  local addtext = function(txt)
    txt = txt:match'^%s*(.*%S)' or ''
    if #txt ~= 0 then
      t[#t+1] = {text=txt}
    end
  end

  s:gsub('<([?!/]?)([-:_%w]+)%s*(/?>?)([^<]*)', function(type, name, closed, txt)
    -- open
    if #type == 0 then
      local attrs, orderedattrs = {}, {}
      if #closed == 0 then
        local len = 0
        for all,aname,_,value,starttxt in string.gmatch(txt, "(.-([-_%w]+)%s*=%s*(.)(.-)%3%s*(/?>?))") do
          len = len + #all
          attrs[aname] = value
          orderedattrs[#orderedattrs+1] = {name=aname, value=value}
          if #starttxt ~= 0 then
            txt = txt:sub(len+1)
            closed = starttxt
            break
          end
        end
      end
      t[#t+1] = {tag=name, attrs=attrs, children={}, orderedattrs=orderedattrs}

      if closed:byte(1) ~= slashchar then
        l[#l+1] = t
        t = t[#t].children
      end

      addtext(txt)
    -- close
    elseif '/' == type then
      t = l[#l]
      l[#l] = nil

      addtext(txt)
    -- ENTITY
    elseif '!' == type then
      if E == name:byte(1) then
        txt:gsub('([_%w]+)%s+(.)(.-)%2', function(name, _, entity)
          entities[#entities+1] = {name=name, value=entity}
        end, 1)
      end
    -- elseif '?' == type then
    --   print('?  ' .. name .. ' // ' .. attrs .. '$$')
    -- elseif '-' == type then
    --   print('comment  ' .. name .. ' // ' .. attrs .. '$$')
    -- else
    --   print('o  ' .. #p .. ' // ' .. name .. ' // ' .. attrs .. '$$')
    end
  end)

  return {children=t, entities=entities, tentities=tentities}
end

-- Return a tuple `document table, error file`.
-- @param filename[in] string
-- @param evalEntities[in] boolean : see \c parse()
-- @return table : see parse
local function parseFile(filename, evalEntities)
  local f, err = io.open(filename)
  if f then
    local content = f:read'*a'
    f:close()
    return parse(content, evalEntities), nil
  end
  return f, err
end

return {
  parse = parse,
  parseFile = parseFile,
  defaultEntityTable = defaultEntityTable,
  replaceEntities = replaceEntities,
  createEntityTable = createEntityTable,
}