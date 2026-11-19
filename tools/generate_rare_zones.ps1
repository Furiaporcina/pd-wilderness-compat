#Requires -Version 5.1
<#
    DEPRECATED - superseded by tools\generate_wilderness_split.py.

    This script regenerates the old "remove every Wilderness guard" version of the zone
    files. That version predates the per-empire zone/job split, so running it would drop
    the 51 `zone_pd_*_wilderness` copies, the 51 job stubs, the split swap entries, the
    new concepts and the Wilderness-only localisation.

    It refuses to run unless -Force is passed. Use the Python generator instead:

        python tools\generate_wilderness_split.py

    The original body is kept for reference while the split is validated in game.
#>
param(
    [Parameter(Mandatory = $true)]
    [string]$PdRoot,
    [switch]$Force
)

if (-not $Force) {
    Write-Host "DEPRECATED: tools\generate_rare_zones.ps1 would overwrite the Wilderness zone split."
    Write-Host "Use: python tools\generate_wilderness_split.py"
    Write-Host "Pass -Force only if you intentionally want the old gate-free files back."
    exit 2
}

$ErrorActionPreference = "Stop"

$sourceZones    = Join-Path $PdRoot "planetary_diversity\common\zones\pd_rare_zones.txt"
$sourceUncommon = Join-Path $PdRoot "planetary_diversity\common\zones\pd_uncommon_zones.txt"
$sourceInline   = Join-Path $PdRoot "planetary_diversity\common\inline_scripts\zones\pd_rare_zone_common.txt"
$outRoot        = Join-Path $PSScriptRoot "..\pd_wilderness_compat"
$outZones       = Join-Path $outRoot "common\zones\zzz_pd_wilderness_rare_zones.txt"
$outUncommon    = Join-Path $outRoot "common\zones\zzz_pd_wilderness_uncommon_zones.txt"
$outInline      = Join-Path $outRoot "common\inline_scripts\zones\pd_rare_zone_common.txt"

foreach ($path in @($sourceZones, $sourceUncommon, $sourceInline)) {
    if (-not (Test-Path $path)) { throw "Not found: $path" }
}

# Matches only the guard line itself, so it can never swallow the surrounding trigger.
$gatePattern = '^\s*hidden_trigger\s*=\s*\{\s*exists\s*=\s*owner\s+owner\s*=\s*\{\s*is_wilderness_empire\s*=\s*no\s*\}\s*\}\s*$'

function Convert-PdFile {
    param(
        [string]$InPath,
        [string]$OutPath,
        [string]$Label
    )

    $lines   = [System.IO.File]::ReadAllLines($InPath)
    $removed = 0
    $kept    = New-Object System.Collections.Generic.List[string]

    foreach ($line in $lines) {
        if ($line -match $gatePattern) {
            $removed++
            continue
        }
        $kept.Add($line)
    }

    $outDir = Split-Path -Parent $OutPath
    if (-not (Test-Path $outDir)) {
        New-Item -ItemType Directory -Path $outDir -Force | Out-Null
    }

    $text = [string]::Join("`n", $kept)
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($OutPath, $text, $utf8NoBom)

    Write-Host ("{0}: removed {1} guard line(s) -> {2}" -f $Label, $removed, $OutPath)
    return $removed
}

$zonesRemoved    = Convert-PdFile -InPath $sourceZones    -OutPath $outZones    -Label "rare zones"
$uncommonRemoved = Convert-PdFile -InPath $sourceUncommon -OutPath $outUncommon -Label "uncommon zones"
$inlineRemoved   = Convert-PdFile -InPath $sourceInline   -OutPath $outInline   -Label "shared inline script"

$zoneCount     = (Select-String -Path $outZones     -Pattern '^zone_pd_[a-z_]+ = \{').Count
$uncommonCount = (Select-String -Path $outUncommon -Pattern '^zone_pd_[a-z_]+ = \{').Count

if ($zonesRemoved -ne 57) {
    throw "Expected 57 guard lines in pd_rare_zones.txt, found $zonesRemoved. Review the upstream file before shipping."
}
if ($uncommonRemoved -ne 9) {
    throw "Expected 9 guard lines in pd_uncommon_zones.txt, found $uncommonRemoved. Review the upstream file before shipping."
}
if ($inlineRemoved -ne 1) {
    throw "Expected 1 guard line in pd_rare_zone_common.txt, found $inlineRemoved. Review the upstream file before shipping."
}
if ($zoneCount -ne 54) {
    throw "Expected 54 rare zones in the output, found $zoneCount. Review the upstream file before shipping."
}
if ($uncommonCount -ne 9) {
    throw "Expected 9 uncommon zones in the output, found $uncommonCount. Review the upstream file before shipping."
}

Write-Host "OK: 54 rare + 9 uncommon zones copied; 57 + 9 zone guards and 1 inline-script guard removed."
