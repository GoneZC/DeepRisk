// 定义事件
public class RuleCheckCompletedEvent extends ApplicationEvent {
    private Map<String, Object> checkResult;
    
    public RuleCheckCompletedEvent(Object source, Map<String, Object> checkResult) {
        super(source);
        this.checkResult = checkResult;
    }
    
    // Getters...
}

// 发布事件
@Component
public class EventPublisher {
    
    @Autowired
    private ApplicationEventPublisher publisher;
    
    public void publishRuleCheckCompleted(Map<String, Object> checkResult) {
        publisher.publishEvent(new RuleCheckCompletedEvent(this, checkResult));
    }
}

// 监听事件
@Component
public class RuleCheckEventListener {
    
    @EventListener
    public void handleRuleCheckCompletedEvent(RuleCheckCompletedEvent event) {
        // 处理事件
        Map<String, Object> checkResult = event.getCheckResult();
        // ...
    }
} 