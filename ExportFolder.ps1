param(
    [Parameter(Mandatory=$true)]
    [string]$Folder
)

$FolderPath = Join-Path (Get-Location) $Folder

if (!(Test-Path $FolderPath)) {
    Write-Host "Folder '$Folder' not found." -ForegroundColor Red
    exit
}

$OutputFile = "${Folder}_Review.txt"

if (Test-Path $OutputFile) {
    Remove-Item $OutputFile
}

# ------------------------------------------------------------
# Extensions to include
# ------------------------------------------------------------
$IncludeExtensions = @(
    ".py",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".cfg",
    ".conf",
    ".txt",
    ".md",
    ".sql",
    ".xml",
    ".html",
    ".css",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".bat",
    ".ps1",
    ".sh"
)

# ------------------------------------------------------------
# Folders to ignore
# ------------------------------------------------------------
$ExcludeFolders = @(
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".git",
    ".idea",
    ".vscode",
    "node_modules",
    "venv",
    ".venv",
    "env",
    "dist",
    "build"
)

Get-ChildItem $FolderPath -Recurse -File |
Where-Object {

    # Skip excluded folders
    $skip = $false

    foreach($folder in $ExcludeFolders)
    {
        if($_.FullName -match "\\$folder\\")
        {
            $skip = $true
            break
        }
    }

    if($skip){ return $false }

    # Skip Python compiled files
    if($_.Extension -eq ".pyc"){ return $false }

    # Skip hidden/system files
    if($_.Attributes -match "Hidden"){ return $false }

    # Export only source/config/docs
    return ($IncludeExtensions -contains $_.Extension)

} |
Sort-Object FullName |
ForEach-Object {

    @"
======================================================================
FILE : $($_.Name)
PATH : $($_.FullName)
======================================================================

"@ | Out-File $OutputFile -Append -Encoding UTF8

    Get-Content $_.FullName |
        Out-File $OutputFile -Append -Encoding UTF8

    "" | Out-File $OutputFile -Append -Encoding UTF8
}

Write-Host ""
Write-Host "==============================================" -ForegroundColor Green
Write-Host "Export Completed Successfully" -ForegroundColor Green
Write-Host "==============================================" -ForegroundColor Green
Write-Host "Output : $OutputFile" -ForegroundColor Yellow