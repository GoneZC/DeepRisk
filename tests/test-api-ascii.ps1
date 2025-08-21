# Simple API Test Script - ASCII Only Version

$concurrentUsers = 5   # Number of users
$requestsPerUser = 5   # Requests per user
$endpoint = "http://localhost:8080/api/async-risk-assessment/assess"  # Change port if needed

# Fixed request body
$body = @{
    doctorId = "D440305034671"
    date = "2024-08-31"
} | ConvertTo-Json

$results = @()
$startTime = Get-Date

# Sequential execution
for ($u = 1; $u -le $concurrentUsers; $u++) {
    for ($i = 1; $i -le $requestsPerUser; $i++) {
        $start = Get-Date
        try {
            $response = Invoke-RestMethod -Uri $endpoint -Method Post -Body $body -ContentType "application/json"
            $end = Get-Date
            $timeMs = ($end - $start).TotalMilliseconds
            
            $results += [PSCustomObject]@{
                UserId = $u
                RequestNumber = $i
                ResponseTime = $timeMs
                Success = $true
                Error = $null
            }
            
            Write-Host "User ${u}, Request ${i}: Success (${timeMs}ms)"
        } catch {
            $end = Get-Date
            $timeMs = ($end - $start).TotalMilliseconds
            
            $results += [PSCustomObject]@{
                UserId = $u
                RequestNumber = $i
                ResponseTime = $timeMs
                Success = $false
                Error = $_.Exception.Message
            }
            
            Write-Host "User ${u}, Request ${i}: Failed - $($_.Exception.Message)"
        }
        
        Start-Sleep -Milliseconds 200
    }
}

$endTime = Get-Date
$totalSeconds = ($endTime - $startTime).TotalSeconds

# Results analysis
$totalRequests = $results.Count
if ($totalRequests -gt 0) {
    $successCount = ($results | Where-Object { $_.Success -eq $true }).Count
    $successRate = [math]::Round(($successCount / $totalRequests * 100), 2)
    $avgResponseTime = [math]::Round(($results | Measure-Object -Property ResponseTime -Average).Average, 2)
    $maxResponseTime = [math]::Round(($results | Measure-Object -Property ResponseTime -Maximum).Maximum, 2)
    $minResponseTime = [math]::Round(($results | Measure-Object -Property ResponseTime -Minimum).Minimum, 2)
    
    $sortedTimes = $results | Sort-Object ResponseTime
    $p95Index = [math]::Ceiling($totalRequests * 0.95) - 1
    $p95ResponseTime = [math]::Round($sortedTimes[$p95Index].ResponseTime, 2)
    
    $qps = [math]::Round($totalRequests / $totalSeconds, 2)
} else {
    $successCount = 0
    $successRate = 0
    $avgResponseTime = 0
    $maxResponseTime = 0
    $minResponseTime = 0
    $p95ResponseTime = 0
    $qps = 0
}

# Output results
Write-Host ""
Write-Host "===== Performance Test Results ====="
Write-Host "Total Requests: $totalRequests"
Write-Host "Successful Requests: $successCount"
Write-Host "Success Rate: ${successRate}%"
Write-Host "Average Response Time: ${avgResponseTime}ms"
Write-Host "Maximum Response Time: ${maxResponseTime}ms"
Write-Host "Minimum Response Time: ${minResponseTime}ms"
Write-Host "95% Response Time: ${p95ResponseTime}ms"
Write-Host "QPS (Queries Per Second): ${qps}req/s"
Write-Host "Total Execution Time: $([math]::Round($totalSeconds, 2))s"
Write-Host "=====================================" 