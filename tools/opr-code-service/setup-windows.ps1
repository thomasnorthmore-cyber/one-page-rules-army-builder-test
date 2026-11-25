# Run this once on Windows PowerShell from the extracted service folder.
# Creates the KV namespace and deploys the same web app + API.
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
if (-not (Get-Command node -ErrorAction SilentlyContinue)) { throw "Node.js is required: https://nodejs.org/en/download" }
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) { throw "npm not found. Install Node.js." }
Write-Host "Installing local dependencies..." -ForegroundColor Cyan
npm install
if ($LASTEXITCODE -ne 0) { throw "npm install failed" }
Write-Host "Sign in to your Cloudflare account in the browser..." -ForegroundColor Cyan
npx wrangler login
if ($LASTEXITCODE -ne 0) { throw "Cloudflare login failed" }
$toml = Get-Content .\wrangler.toml -Raw
if ($toml.Contains("REPLACE_WITH_YOUR_KV_NAMESPACE_ID")) {
  Write-Host "Creating the 10-minute army storage namespace..." -ForegroundColor Cyan
  $response = npx wrangler kv namespace create ARMIES 2>&1 | Out-String
  if ($LASTEXITCODE -ne 0) { Write-Host $response; throw "Cloudflare KV namespace creation failed" }
  if ($response -notmatch '(?i)\bid\s*=\s*"([a-f0-9]{32})"') {
    Write-Host $response
    throw "Could not find the namespace ID; open wrangler.toml and enter the created namespace ID manually."
  }
  $id = $Matches[1]
  $toml = $toml.Replace("REPLACE_WITH_YOUR_KV_NAMESPACE_ID",$id)
  [System.IO.File]::WriteAllText((Join-Path $PSScriptRoot "wrangler.toml"),$toml)
}
Write-Host "Deploying the upload page and API..." -ForegroundColor Cyan
npm run deploy
if ($LASTEXITCODE -ne 0) { throw "Deployment failed" }
Write-Host "Deployment complete. Copy the https://...workers.dev URL shown above." -ForegroundColor Green
