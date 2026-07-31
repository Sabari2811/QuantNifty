$OutputFile = "project_inventory.txt"

Get-ChildItem -Recurse -File -Include *.py |
Where-Object {
    $_.FullName -notmatch "\\venv\\" -and
    $_.FullName -notmatch "\\__pycache__\\" -and
    $_.FullName -notmatch "\\.git\\" -and
    $_.FullName -notmatch "\\logs\\"
} |
ForEach-Object {

    $file = $_
    $content = Get-Content $file.FullName

    Add-Content $OutputFile ("=" * 100)
    Add-Content $OutputFile ("FILE : " + $file.FullName)
    Add-Content $OutputFile ("SIZE : " + [math]::Round($file.Length/1KB,2) + " KB")
    Add-Content $OutputFile ("LINES: " + $content.Count)
    Add-Content $OutputFile ""

    Add-Content $OutputFile "IMPORTS"
    $content | Select-String '^\s*(import|from)\s+' | ForEach-Object {
        Add-Content $OutputFile $_.Line
    }

    Add-Content $OutputFile ""
    Add-Content $OutputFile "CLASSES"
    $content | Select-String '^\s*class\s+' | ForEach-Object {
        Add-Content $OutputFile $_.Line
    }

    Add-Content $OutputFile ""
    Add-Content $OutputFile "FUNCTIONS"
    $content | Select-String '^\s*def\s+' | ForEach-Object {
        Add-Content $OutputFile $_.Line
    }

    Add-Content $OutputFile ""
}