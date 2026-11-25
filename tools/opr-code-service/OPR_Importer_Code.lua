-- OPR short-code importer for a separate TTS object. Do not replace ForceOrg's Yellow Machine.
-- Configure server once, then paste OPR-XXXXXXXXX codes.
local server,code,models,current,name,status,busy="","",{},1,"No army","Enter Worker URL once, then an OPR code",false
local function refresh()
  local s="OPR CODE IMPORTER\n"..name.."\n"..status
  if #models>0 then s=s.."\n"..current.."/"..#models..": "..models[current].unit.."/"..tostring(models[current].model.name) end
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
    local nextModels={}
    for _,u in ipairs(data.listJson.units) do
      if type(u.modelDefinitions)=="table" then
        for _,m in ipairs(u.modelDefinitions) do table.insert(nextModels,{unit=tostring(u.name or "Unit"),unitId=tostring(u.unitId or ""),model=m}) end
      end
    end
    if #nextModels==0 then status="No model profiles found";refresh();return end
    models=nextModels;current=1;name=tostring(data.listJson.listName or "OPR army")
    status="Loaded "..#models.." model profiles";refresh()
  end)
end
function previous()if #models>0 then current=((current-2)%#models)+1;refresh()end end
function next()if #models>0 then current=(current%#models)+1;refresh()end end
function assign(o,player,alt)
  if #models==0 then return end
  local p=Player[player]
  if not p then return end
  local selection=p.getSelectedObjects()
  if #selection==0 then broadcastToColor("Select a miniature first",player,{1,0.6,0.2});return end
  local entry=models[current]
  for _,obj in ipairs(selection) do
    obj.setName(tostring(entry.model.ttsNameOutput or entry.model.name))
    obj.setDescription(tostring(entry.model.ttsDescriptionOutput or ""))
    if entry.unitId~="" then obj.addTag("OPR_"..entry.unitId:gsub("[^%w_]","_")) end
  end
  status="Assigned "..#selection.." miniature(s)";refresh()
end
