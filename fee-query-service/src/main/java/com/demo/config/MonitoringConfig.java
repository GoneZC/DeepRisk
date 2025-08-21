package com.demo.config;

import io.github.mweirauch.micrometer.jvm.extras.ProcessMemoryMetrics;
import io.github.mweirauch.micrometer.jvm.extras.ProcessThreadMetrics;
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Tags;
import io.micrometer.core.instrument.binder.MeterBinder;
import io.micrometer.core.instrument.binder.jvm.ClassLoaderMetrics;
import io.micrometer.core.instrument.binder.jvm.JvmGcMetrics;
import io.micrometer.core.instrument.binder.jvm.JvmMemoryMetrics;
import io.micrometer.core.instrument.binder.jvm.JvmThreadMetrics;
import io.micrometer.core.instrument.binder.system.ProcessorMetrics;
import io.micrometer.core.instrument.binder.system.UptimeMetrics;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.actuate.info.InfoContributor;
import org.springframework.boot.actuate.info.InfoEndpoint;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.scheduling.annotation.EnableScheduling;
import org.springframework.scheduling.annotation.Scheduled;

import javax.management.MBeanServer;
import javax.management.ObjectName;
import java.lang.management.ManagementFactory;
import java.lang.management.ThreadMXBean;
import java.util.HashMap;
import java.util.Map;

/**
 * 监控配置类
 * 用于定制和增强应用性能监控
 */
@Slf4j
@Configuration
@EnableScheduling
public class MonitoringConfig {

    @Value("${spring.application.name}")
    private String applicationName;

    // 移除重复的Bean定义，Spring Boot actuator 会自动配置这些监控指标

    /**
     * 增强的进程内存监控
     */
    @Bean
    public MeterBinder processMemoryMetrics() {
        return new ProcessMemoryMetrics();
    }

    /**
     * 增强的进程线程监控
     */
    @Bean
    public MeterBinder processThreadMetrics() {
        return new ProcessThreadMetrics();
    }

    /**
     * 自定义应用信息贡献者
     */
    @Bean
    public InfoContributor customInfoContributor() {
        return builder -> {
            Map<String, Object> details = new HashMap<>();
            
            // JVM信息
            Runtime runtime = Runtime.getRuntime();
            details.put("jvm.version", System.getProperty("java.version"));
            details.put("jvm.vendor", System.getProperty("java.vendor"));
            details.put("jvm.name", System.getProperty("java.vm.name"));
            
            // 内存信息
            details.put("memory.max", runtime.maxMemory());
            details.put("memory.total", runtime.totalMemory());
            details.put("memory.free", runtime.freeMemory());
            details.put("memory.used", runtime.totalMemory() - runtime.freeMemory());
            
            // 线程信息
            ThreadMXBean threadBean = ManagementFactory.getThreadMXBean();
            details.put("threads.total", threadBean.getThreadCount());
            details.put("threads.daemon", threadBean.getDaemonThreadCount());
            details.put("threads.peak", threadBean.getPeakThreadCount());
            
            // 处理器信息
            details.put("processors", runtime.availableProcessors());
            
            builder.withDetail("performance", details);
        };
    }

    /**
     * 定期记录系统性能指标到日志
     */
    @Scheduled(fixedRate = 60000) // 每分钟记录一次
    public void logPerformanceMetrics() {
        try {
            Runtime runtime = Runtime.getRuntime();
            ThreadMXBean threadBean = ManagementFactory.getThreadMXBean();
            
            long maxMemory = runtime.maxMemory();
            long totalMemory = runtime.totalMemory();
            long freeMemory = runtime.freeMemory();
            long usedMemory = totalMemory - freeMemory;
            
            int threadCount = threadBean.getThreadCount();
            int daemonThreadCount = threadBean.getDaemonThreadCount();
            int peakThreadCount = threadBean.getPeakThreadCount();
            
            // 获取CPU使用率（如果可用）
            double cpuUsage = getCpuUsage();
            
            log.info("=== 性能监控报告 ===");
            log.info("内存使用: {}MB / {}MB ({}%)", 
                usedMemory / 1024 / 1024, 
                maxMemory / 1024 / 1024,
                (usedMemory * 100 / maxMemory));
            log.info("线程统计: 总数={}, 守护={}, 峰值={}", 
                threadCount, daemonThreadCount, peakThreadCount);
            if (cpuUsage >= 0) {
                log.info("CPU使用率: {:.2f}%", cpuUsage * 100);
            }
            log.info("================");
            
        } catch (Exception e) {
            log.error("记录性能指标时出错", e);
        }
    }

    /**
     * 获取CPU使用率
     */
    private double getCpuUsage() {
        try {
            MBeanServer mbs = ManagementFactory.getPlatformMBeanServer();
            ObjectName name = ObjectName.getInstance("java.lang:type=OperatingSystem");
            Object attribute = mbs.getAttribute(name, "ProcessCpuLoad");
            return attribute instanceof Double ? (Double) attribute : -1;
        } catch (Exception e) {
            return -1;
        }
    }
} 