<#
.SYNOPSIS
    Script otomatis untuk mendaftarkan / menjalankan Laporan Email Harian ke Windows Task Scheduler.
.DESCRIPTION
    Jadwal default: Pukul 07:00 WIB setiap pagi hari.
#>

param(
    [string]$Action = "run_now", # "register", "run_now", "status"
    [string]$TargetEmail = "muhammad.wyzer@gmail.com",
    [string]$DailyTime = "07:00"
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$rootDir = Split-Path -Parent $scriptDir
$pythonExe = (Get-Command python).Source
$runnerScript = Join-Path $scriptDir "send_daily_report.py"
$taskName = "DuaKelinci_DailyExecutiveReport"

if ($Action -eq "run_now") {
    Write-Host "Menjalankan laporan email sekarang..." -ForegroundColor Cyan
    & $pythonExe $runnerScript $TargetEmail
}
elseif ($Action -eq "register") {
    Write-Host "Mendaftarkan jadwal harian pada pukul $DailyTime WIB..." -ForegroundColor Yellow
    $trigger = "schtasks /create /tn `"$taskName`" /tr `"`"$pythonExe`" `"$runnerScript`" `"$TargetEmail`"`" /sc daily /st $DailyTime /f"
    Invoke-Expression $trigger
    Write-Host "Task Scheduler $taskName berhasil didaftarkan!" -ForegroundColor Green
}
elseif ($Action -eq "status") {
    schtasks /query /tn "$taskName" /fo LIST /v
}
