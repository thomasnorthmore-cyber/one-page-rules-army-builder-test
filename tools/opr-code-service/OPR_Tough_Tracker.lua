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
  self.addContextMenuItem("Take 1 wound",function() changeWounds(-1) end,false)
  self.addContextMenuItem("Heal 1 wound",function() changeWounds(1) end,false)
  self.addContextMenuItem("Reset wounds",function() wounds=maxWounds;label() end,false)
  label()
end
function changeWounds(amount)
  wounds=math.max(0,math.min(maxWounds,wounds+amount))
  label()
end
function onSave()
  return JSON.encode({wounds=wounds,max=maxWounds,name=originalName})
end
