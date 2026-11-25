# Skrip Pengaktifan Portal Operasional Terpadu PT Dua Kelinci
Write-Host "==========================================================" -ForegroundColor Red
Write-Host " Memulai Portal Operasional Terpadu - PT Dua Kelinci" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Red

# 1. Hentikan proses lama di port 8000 jika masih berjalan (gunakan nama variabel selain $PID bawaan PowerShell)
$existingConnections = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($existingConnections) {
    foreach ($conn in $existingConnections) {
        $procId = $conn.OwningProcess
        if ($procId -gt 0) {
            Write-Host "Menutup proses lama di port 8000 (Process ID: $procId)..." -ForegroundColor Gray
            Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
        }
    }
    Start-Sleep -Seconds 1
}

# 2. Jalankan Uvicorn FastAPI
$root = $PSScriptRoot
Start-Process -FilePath "python" -ArgumentList "-m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000" -WindowStyle Minimized
Start-Sleep -Seconds 2

# 3. Buka Dashboard Frontend di Browser Default
$indexPath = "$root\frontend\public\index.html"
Write-Host "Membuka Portal Dashboard di browser..." -ForegroundColor Green
Start-Process $indexPath

Write-Host "Server backend aktif di http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "Seluruh tab (Dashboard, AI Agent, Forecast, e-Sign, WMS) telah aktif." -ForegroundColor Yellow
