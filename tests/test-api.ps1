# 简化版本 - 适用于任何PowerShell版本

$concurrentUsers = 5   # 减少并发数以便快速测试
$requestsPerUser = 5   # 每用户请求数
$endpoint = "http://localhost:8080/api/async-risk-assessment/assess"  # 替换正确端口

# 固定请求参数
$body = @{
    doctorId = "D440305034671"
    date = "2024-08-31"
} | ConvertTo-Json

$results = @()
$startTime = Get-Date

# 顺序执行请求
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
            
            Write-Host "用户 $u, 请求 $i: 成功 (${timeMs}ms)"
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
            
            Write-Host "用户 $u, 请求 $i: 失败 - $($_.Exception.Message)"
        }
        
        # 稍微延迟，避免请求太密集
        Start-Sleep -Milliseconds 200
    }
}

$endTime = Get-Date
$totalSeconds = ($endTime - $startTime).TotalSeconds

# 分析结果
$totalRequests = $results.Count
if ($totalRequests -gt 0) {
    $successCount = ($results | Where-Object { $_.Success -eq $true }).Count
    $successRate = [math]::Round(($successCount / $totalRequests * 100), 2)
    $avgResponseTime = [math]::Round(($results | Measure-Object -Property ResponseTime -Average).Average, 2)
    $maxResponseTime = [math]::Round(($results | Measure-Object -Property ResponseTime -Maximum).Maximum, 2)
    $minResponseTime = [math]::Round(($results | Measure-Object -Property ResponseTime -Minimum).Minimum, 2)
    
    # 安全处理95%计算
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

# 输出结果
Write-Host "`n===== 性能测试结果 ====="
Write-Host "总请求数: $totalRequests"
Write-Host "成功请求: $successCount"
Write-Host "成功率: ${successRate}%"
Write-Host "平均响应时间: ${avgResponseTime}ms"
Write-Host "最大响应时间: ${maxResponseTime}ms"
Write-Host "最小响应时间: ${minResponseTime}ms"
Write-Host "95%响应时间: ${p95ResponseTime}ms"
Write-Host "QPS(每秒查询率): ${qps}req/s"
Write-Host "总执行时间: $([math]::Round($totalSeconds, 2))秒"