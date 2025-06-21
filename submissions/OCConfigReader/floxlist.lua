local xmlparser = require("xmlParser")

local types

-- {"array", "dict", "data", "date", "true", "false", "real", "integer"}
-- Some types aren't supported, but that's okay. At least it works for OpenCore.

local function parse(plist)

	assert(plist:match("<plist version=\"[.0-9]+\">.+</plist>"), "Not a plist")
	
	local plist = xmlparser.parse(plist).children[1].children[1].children

	local function parseDict(data, array)
		local dict = {}
		for i = 1, #data, array and 1 or 2 do
			local key, vtype, value
			if array then
				vtype = data[i].tag
				value = data[i].children
			else
				key = data[i].children[1].text
				vtype = data[i+1].tag
				value = data[i+1].children
			end

			if vtype == "true" or vtype == "false" then
				value = vtype == "true" and true or false
				vtype = "boolean"
			elseif vtype == "array" then
				value = parseDict(value, true)
			elseif types[vtype] then
				value = types[vtype](value)
			else
				value = "Unknown type"
			end

			if array then
				table.insert(dict, value)
			else
				dict[key] = value
			end
		end

		return dict
	end

	types = {
		string = function(data)
			if not data[1] then
				return ""
			end
			return data[1].text or ""
		end,
		data = function(data) -- Decode base64 to hex
			if not data[1] then
				return ""
			end
			local data = data[1].text
			local b = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
			local t = {}
			for i = 1, 64 do
				t[b:sub(i, i)] = i - 1
			end
			local decoded = {}
			for i = 1, #data, 4 do
				local n = ((t[data:sub(i,i)] or 0) << 18)
						| ((t[data:sub(i+1,i+1)] or 0) << 12)
						| ((t[data:sub(i+2,i+2)] or 0) << 6)
						| (t[data:sub(i+3,i+3)] or 0)
				table.insert(decoded, string.format("%02x", (n >> 16) & 0xFF))
				if data:sub(i+2,i+2) ~= "=" then
					table.insert(decoded, string.format("%02x", (n >> 8) & 0xFF))
				end
				if data:sub(i+3,i+3) ~= "=" then
					table.insert(decoded, string.format("%02x", n & 0xFF))
				end
			end
			return string.upper(table.concat(decoded))
		end,
		dict = parseDict,
		integer = function(data)
			return tonumber(data[1].text)
		end
	}
	
	return(parseDict(plist))

end

return parse