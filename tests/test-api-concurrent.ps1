# High Concurrency API Test for PowerShell 7+
# Run with pwsh (PowerShell 7), not powershell (Windows PowerShell)

$concurrentUsers = 20   # Concurrent users
$requestsPerUser = 10   # Requests per user
$endpoint = "http://localhost:8080/api/async-risk-assessment/assess"  # Change port if needed

# Fixed request body
$body = @{
    doctorId = "D440305034671"
    date = "2024-08-31"
} | ConvertTo-Json

$results = @()
$startTime = Get-Date

# Create a runspace-safe synchronized collection for results
$syncResults = [System.Collections.Concurrent.ConcurrentBag[object]]::new()

# Run concurrent requests using PowerShell 7's ForEach-Object -Parallel
1..$concurrentUsers | ForEach-Object -ThrottleLimit $concurrentUsers -Parallel {
    $userId = $_
    $threadResults = @()
    
    # Import variables from parent scope
    $endpoint = $using:endpoint
    $body = $using:body
    $requestsPerUser = $using:requestsPerUser
    
    for ($i = 1; $i -le $requestsPerUser; $i++) {
        $start = Get-Date
        try {
            $response = Invoke-RestMethod -Uri $endpoint -Method Post -Body $body -ContentType "application/json"
            $end = Get-Date
            $timeMs = ($end - $start).TotalMilliseconds
            
            $result = [PSCustomObject]@{
                UserId = $userId
                RequestNumber = $i
                ResponseTime = $timeMs
                Success = $true
                Error = $null
            }
            
            # Add to thread-local results and thread-safe collection
            $threadResults += $result
            ($using:syncResults).Add($result)
            
            Write-Host "OK - User ${userId} - Req ${i} - ${timeMs}ms"
        } catch {
            $end = Get-Date
            $timeMs = ($end - $start).TotalMilliseconds
            
            $result = [PSCustomObject]@{
                UserId = $userId
                RequestNumber = $i
                ResponseTime = $timeMs
                Success = $false
                Error = $_.Exception.Message
            }
            
            # Add to thread-local results and thread-safe collection
            $threadResults += $result
            ($using:syncResults).Add($result)
            
            Write-Host "FAIL - User ${userId} - Req ${i} - $($_.Exception.Message)"
        }
        
        # Small random delay between requests from same user
        Start-Sleep -Milliseconds (Get-Random -Minimum 50 -Maximum 200)
    }
    
    return $threadResults
} | ForEach-Object { $results += $_ }

# Ensure all results are collected
$results = $syncResults.ToArray()

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

# Output detailed results
Write-Host ""
Write-Host "===== PERFORMANCE TEST RESULTS ====="
Write-Host "Total Requests: ${totalRequests}"
Write-Host "Successful Requests: ${successCount}"
Write-Host "Success Rate: ${successRate}%"
Write-Host "Average Response Time: ${avgResponseTime}ms"
Write-Host "Maximum Response Time: ${maxResponseTime}ms"
Write-Host "Minimum Response Time: ${minResponseTime}ms"
Write-Host "95% Response Time: ${p95ResponseTime}ms"
Write-Host "QPS (Queries Per Second): ${qps} req/s"
Write-Host "Total Execution Time: $([math]::Round($totalSeconds, 2))s"
Write-Host "===================================="

# Save results to CSV file for further analysis
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$results | Export-Csv -Path "performance-test-${timestamp}.csv" -NoTypeInformation
Write-Host "Results saved to performance-test-${timestamp}.csv" 