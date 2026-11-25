-- OPR short-code importer for a separate TTS object. Do not replace ForceOrg's Yellow Machine.
-- Configure server once, then paste OPR-XXXXXXXXX codes.
local server,code,models,current,name,status,busy="","",{},1,"No army","Enter Worker URL once, then an OPR code",false
local function refresh()
  local s="OPR CODE IMPORTER\n"..name.."\n"..status
  if #models>0 then s=s.."\n"..current.."/"..#models..": "..models[current].unit.." — "..models[current].quantity.."x "..tostring(models[current].label) end
  self.editButton({index=0,label=s})
end
function noop() end
function onLoad(saved)
  if saved and saved~="" then local ok,x=pcall(JSON.decode,saved);if ok and type(x)=="table" then server=x.server or "";code=x.code or "" end end
  self.setLock(true);self.clearButtons();self.clearInputs()
  self.createButton({click_function="noop",function_owner=self,label="OPR CODE IMPORTER",position={0,0.75,0.2},width=5900,height=1300,font_size=225,color={0.12,0.22,0.27},font_color={1,1,1}})
  self.createInput({input_function="setServer",function_owner=self,label="SERVER HTTPS URL (once)",value=server,position={0,0.75,-1.5},width=5800,height=470,font_size=180})
  self.createInput({input_function="setCode",function_owner=self,label="ARMY CODE",value=code,position={0,0.75,-2.55},width=3700,height=500,font_size=210})
  self.createButton({click_function="importCode",function_owner=self,label="IMPORT CODE",position={2.0,0.75,-2.55},width=1900,height=500,font_size=195})
  self.createButton({click_function="previous",function_owner=self,label="PREVIOUS",position={-2,0.75,-3.65},width=1600,height=500,font_size=205})
  self.createButton({click_function="next",function_owner=self,label="NEXT",position={0,0.75,-3.65},width=1500,height=500,font_size=210})
  self.createButton({click_function="assign",function_owner=self,label="ASSIGN SELECTED",position={2.2,0.75,-3.65},width=2100,height=500,font_size=185})
  refresh()
end
function onSave()return JSON.encode({server=server,code=code})end
function setServer(o,p,v)if type(v)=="string" then server=v end end
function setCode(o,p,v)if type(v)=="string" then code=v end end
function importCode(o,p,alt)
  if busy then return end
  local base=server:gsub("%s+",""):gsub("/+$","")
  local key=code:upper():gsub("%s+","")
  if not base:match("^https://[%w%.%-]+") then status="Set HTTPS server URL first";refresh();return end
  if not key:match("^OPR%-[A-HJ-NP-Z2-9]+$") or #key~=13 then status="Invalid OPR code";refresh();return end
  busy=true;status="Loading roster...";refresh()
  WebRequest.get(base.."/api/army?code="..key,function(response)
    busy=false
    if response.is_error or (response.response_code and tonumber(response.response_code)~=200) then
      local ok,x=pcall(JSON.decode,response.text or "")
      status=ok and type(x)=="table" and tostring(x.error or "Network error") or "HTTP or network error"
      refresh();broadcastToAll("OPR import failed: "..status,{1,0.4,0.3});return
    end
    local ok,data=pcall(JSON.decode,response.text or "")
    if not ok or type(data)~="table" or type(data.listJson)~="table" or type(data.listJson.units)~="table" then status="Invalid roster response";refresh();return end
    -- Group identical model loadouts *within each unit*.
    -- 4 standard Battle Brothers become one 4x choice; the fifth specialist
    -- keeps its own choice even if equipped with the same weapon.
    local nextModels={}
    for _,u in ipairs(data.listJson.units) do
      if type(u.modelDefinitions)=="table" then
        local grouped={}
        for _,m in ipairs(u.modelDefinitions) do
          local rawName=tostring(m.name or "Model")
          local role=rawName:lower():find("fifth",1,true) and "specialist" or
                     rawName:lower():find("specialist",1,true) and "specialist" or
                     rawName:lower():find("customisable",1,true) and "specialist" or
                     rawName:lower():find("standard",1,true) and "standard" or
                     rawName:lower():find("fixed equipment",1,true) and "standard" or "normal"
          local loadout=tostring(m.loadoutCSV or "")
          -- Ignore numerical model labels, not equipment or model roles.
          local nameKey=rawName:lower():gsub("model%s+%d+","model #")
          local key=role.."|"..nameKey.."|"..loadout.."|"..
                    tostring(m.ttsDescriptionOutput or "").."|"..
                    tostring(m.originalToughValue or 0)
          local group=grouped[key]
          if group then
            group.quantity=group.quantity+1
          else
            local label=rawName
            if role=="standard" then label="Standard models"
            elseif role=="specialist" then label="Specialist model" end
            group={unit=tostring(u.name or "Unit"),unitId=tostring(u.unitId or ""),
                   model=m,quantity=1,label=label}
            grouped[key]=group
            table.insert(nextModels,group)
          end
        end
      end
    end
    if #nextModels==0 then status="No model profiles found";refresh();return end
    models=nextModels;current=1;name=tostring(data.listJson.listName or "OPR army")
    local total=0; for _,group in ipairs(models) do total=total+group.quantity end
    status="Loaded "..total.." models in "..#models.." equipment groups";refresh()
  end)
end
function previous()if #models>0 then current=((current-2)%#models)+1;refresh()end end
function next()if #models>0 then current=(current%#models)+1;refresh()end end
local OPR_TOUGH_SCRIPT = [==[
-- Original OPR Tough(X) tracker for TTS model objects.
-- On an un-scripted model, OPR importer substitutes __MAX__ and installs this.
local maxWounds = __MAX__
local wounds = maxWounds
local originalName = nil
local function label()
  local name=originalName or "OPR model"
  self.setName("[A4FF61]"..wounds.."/"..maxWounds.."[-] "..name)
end
function onLoad(saved)
  if saved and saved ~= "" then
    local ok,data = pcall(JSON.decode,saved)
    if ok and type(data)=="table" then
      maxWounds=tonumber(data.max) or maxWounds
      wounds=tonumber(data.wounds) or maxWounds
      originalName=data.name
    end
  end
  maxWounds=math.max(1,math.floor(maxWounds))
  wounds=math.max(0,math.min(maxWounds,math.floor(wounds)))
  if not originalName then
    originalName=self.getName():gsub("^%[[%x]+%]%d+/%d+%[%-%]%s*","")
  end
  self.clearContextMenu()
  self.addContextMenuItem("Take 1 wound (1)",function() changeWounds(-1) end,false)
  self.addContextMenuItem("Heal 1 wound (2)",function() changeWounds(1) end,false)
  self.addContextMenuItem("Reset wounds",function() wounds=maxWounds;label() end,false)
  label()
end
function changeWounds(amount)
  wounds=math.max(0,math.min(maxWounds,wounds+amount))
  label()
end

local function isHoveredBy(playerColor)
  local player = Player[playerColor]
  return player ~= nil and player.getHoverObject() == self
end

-- Numpad scripting buttons, while hovering the miniature.
function onScriptingButtonDown(index, playerColor)
  if not isHoveredBy(playerColor) then return end
  if index == 1 then changeWounds(-1)
  elseif index == 2 then changeWounds(1) end
end

-- Number-key typing on the miniature (may fire after a short delay).
function onNumberTyped(playerColor, number)
  if not isHoveredBy(playerColor) then return end
  if number == 1 then changeWounds(-1)
  elseif number == 2 then changeWounds(1) end
end

function onSave()
  return JSON.encode({wounds=wounds,max=maxWounds,name=originalName})
end

]==]

function assign(o,player,alt)
  if #models==0 then return end
  local p=Player[player]
  if not p then return end
  local selection=p.getSelectedObjects()
  if #selection==0 then broadcastToColor("Select a miniature first",player,{1,0.6,0.2});return end
  local entry=models[current]
  if #selection>entry.quantity then
    status="Selected "..#selection.." models, but this group has "..entry.quantity..". Select fewer.";refresh()
    broadcastToColor(status,player,{1,0.6,0.2})
    return
  end
  for _,obj in ipairs(selection) do
    obj.setName(tostring(entry.model.ttsNameOutput or entry.model.name))
    obj.setDescription(tostring(entry.model.ttsDescriptionOutput or ""))
    if entry.unitId~="" then obj.addTag("OPR_"..entry.unitId:gsub("[^%w_]","_")) end
    local tough=tonumber(entry.model.originalToughValue) or 0
    if tough>1 then
      -- Preserve any existing TTS/ForceOrg model script, avoiding destructive overwrites.
      local existing=obj.getLuaScript() or ""
      if existing:gsub("%s+","") == "" then
        local newScript=OPR_TOUGH_SCRIPT:gsub("__MAX__",tostring(tough))
        obj.setLuaScript(newScript)
        obj.reload()
      else
        broadcastToColor("OPR: model already has a script; Tough tracker not installed to avoid overwriting it.",player,{1,0.8,0.25})
      end
    end
  end
  status="Assigned "..#selection.." / "..entry.quantity.." matching miniatures";refresh()
end
