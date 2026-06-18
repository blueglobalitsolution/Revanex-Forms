$mysqlDir = "C:\Program Files\MySQL\MySQL Server 8.0\bin"
$mysqlExe = Join-Path $mysqlDir "mysql.exe"
$mysqldExe = Join-Path $mysqlDir "mysqld.exe"

# Stop MySQL service
net stop MySQL80
Start-Sleep -Seconds 2

# Kill any lingering mysqld processes
Get-Process mysqld -ErrorAction SilentlyContinue | Stop-Process -Force

# Start mysqld with skip-grant-tables in a new window
Start-Process -FilePath $mysqldExe -ArgumentList "--skip-grant-tables --skip-networking" -WindowStyle Hidden
Start-Sleep -Seconds 5

# Connect without password and reset root password
$resetSql = @"
FLUSH PRIVILEGES;
ALTER USER 'root'@'localhost' IDENTIFIED BY 'root';
FLUSH PRIVILEGES;
"@

$resetSql | & $mysqlExe -u root --skip-password mysql
Start-Sleep -Seconds 2

# Kill the safe-mode mysqld
$mysqldProcesses = Get-Process mysqld -ErrorAction SilentlyContinue
if ($mysqldProcesses) {
    $mysqldProcesses | Stop-Process -Force
}
Start-Sleep -Seconds 2

# Start the MySQL service normally
net start MySQL80

Write-Host "MySQL root password set to: root"
