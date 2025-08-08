# PowerShell script to create desktop shortcut for Dynamic Catalogue Manager

# Get the desktop path
$DesktopPath = [Environment]::GetFolderPath("Desktop")

# Define shortcut properties
$ShortcutPath = Join-Path $DesktopPath "Dynamic Catalogue Manager.lnk"
$TargetPath = "e:\New TB zip drive transfer\Windsurf\CascadeProjects\crafting-catalogue\launch_catalogue.bat"
$WorkingDirectory = "e:\New TB zip drive transfer\Windsurf\CascadeProjects\crafting-catalogue"
$Description = "Dynamic Catalogue Manager - Create custom catalogues with user-defined columns"

# Create the shortcut
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $TargetPath
$Shortcut.WorkingDirectory = $WorkingDirectory
$Shortcut.Description = $Description
$Shortcut.IconLocation = "shell32.dll,21"  # Database/table icon
$Shortcut.Save()

Write-Host "Desktop shortcut created successfully!" -ForegroundColor Green
Write-Host "Location: $ShortcutPath" -ForegroundColor Yellow
Write-Host ""
Write-Host "You can now double-click the 'Dynamic Catalogue Manager' icon on your desktop to launch the application." -ForegroundColor Cyan
