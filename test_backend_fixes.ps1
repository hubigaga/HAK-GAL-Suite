# HAK-GAL BACKEND FIX TESTING - PowerShell Scripts
# ===================================================

Write-Host "🚀 HAK-GAL BACKEND FIX VALIDATION" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

# Test 1: API Status
Write-Host "`n📊 Test 1: API Status Check" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:5001/api/test" -Method GET
    Write-Host "✅ API Status: $($response.status)" -ForegroundColor Green
    Write-Host "✅ Backend Ready: $($response.backend_ready)" -ForegroundColor Green
} catch {
    Write-Host "❌ API nicht erreichbar: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "💡 Starte zuerst: python api.py" -ForegroundColor Yellow
    exit 1
}

# Test 2: BACKEND-7 Fix (asyncio) - Learn Command
Write-Host "`n🔧 Test 2: BACKEND-7 Fix - Learn Command (asyncio)" -ForegroundColor Yellow
try {
    $body = @{
        command = "learn"
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri "http://localhost:5001/api/command" -Method POST -Body $body -ContentType "application/json"
    
    if ($response.status -eq "success") {
        Write-Host "✅ BACKEND-7 FIX ERFOLGREICH - Learn command funktioniert!" -ForegroundColor Green
        Write-Host "Response: $($response.chatResponse)" -ForegroundColor Cyan
    } else {
        Write-Host "❌ BACKEND-7 FIX FEHLGESCHLAGEN" -ForegroundColor Red
        Write-Host "Error: $($response.error)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ BACKEND-7 TEST FEHLER: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: BACKEND-A Fix (metadata) - Ask Command  
Write-Host "`n🔧 Test 3: BACKEND-A Fix - Ask Command (metadata)" -ForegroundColor Yellow
try {
    $body = @{
        command = "ask critical components"
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri "http://localhost:5001/api/command" -Method POST -Body $body -ContentType "application/json"
    
    if ($response.status -eq "success") {
        Write-Host "✅ BACKEND-A FIX ERFOLGREICH - Ask command funktioniert!" -ForegroundColor Green
        Write-Host "Response: $($response.chatResponse)" -ForegroundColor Cyan
    } else {
        Write-Host "❌ BACKEND-A FIX FEHLGESCHLAGEN" -ForegroundColor Red
        Write-Host "Error: $($response.error)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ BACKEND-A TEST FEHLER: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: Explain Command (General functionality)
Write-Host "`n🔧 Test 4: Explain Command (General)" -ForegroundColor Yellow
try {
    $body = @{
        command = "explain machine learning"
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri "http://localhost:5001/api/command" -Method POST -Body $body -ContentType "application/json"
    
    if ($response.status -eq "success") {
        Write-Host "✅ EXPLAIN COMMAND FUNKTIONIERT" -ForegroundColor Green
    } else {
        Write-Host "⚠️ EXPLAIN COMMAND PROBLEM" -ForegroundColor Yellow
        Write-Host "Error: $($response.error)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ EXPLAIN TEST FEHLER: $($_.Exception.Message)" -ForegroundColor Red
}

# Summary
Write-Host "`n📊 TEST SUMMARY" -ForegroundColor Magenta
Write-Host "=================" -ForegroundColor Magenta
Write-Host "Nächste Schritte:"
Write-Host "1. Teste die Commands auch im Frontend"
Write-Host "2. Prüfe Sentry Dashboard: https://de.sentry.io/organizations/samui-science-lab/issues/"
Write-Host "3. Erwarte ZERO neue BACKEND-7 und BACKEND-A Events"

Write-Host "`n🎯 FRONTEND TESTING:" -ForegroundColor Yellow
Write-Host "  • learn"
Write-Host "  • ask about critical components" 
Write-Host "  • explain artificial intelligence"

Write-Host "`n📈 SENTRY VALIDATION:" -ForegroundColor Yellow
Write-Host "  • BACKEND-7: Sollte keine neuen Events haben"
Write-Host "  • BACKEND-A: Sollte keine neuen Events haben"
Write-Host "  • Error Rate: Sollte sinken"

Write-Host "`n✨ SUCCESS!" -ForegroundColor Green
