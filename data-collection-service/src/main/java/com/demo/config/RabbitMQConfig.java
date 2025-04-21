@Configuration
public class RabbitMQConfig {
    
    @Bean
    public Queue emergencyQueryQueue() {
        Map<String, Object> args = new HashMap<>();
        args.put("x-max-length", 10000);           // 最多存储10000条消息
        args.put("x-max-length-bytes", 100000000); // 队列最大容量约100MB
        args.put("x-overflow", "reject-publish");  // 队列满时拒绝新消息
        
        return new Queue("emergency-query-queue", true, false, false, args);
    }
    
    @Bean
    public Queue routineQueryQueue() {
        return new Queue("routine-query-queue", true);
    }
    
    @Bean
    public Queue auditQueryQueue() {
        return new Queue("audit-query-queue", true);
    }
    
    @Bean
    public TopicExchange queryExchange() {
        return new TopicExchange("query-exchange");
    }
    
    @Bean
    public Binding emergencyBinding(Queue emergencyQueryQueue, TopicExchange queryExchange) {
        return BindingBuilder.bind(emergencyQueryQueue)
                 .to(queryExchange)
                 .with("data.query.*.emergency");
    }
    
    @Bean
    public Binding routineBinding(Queue routineQueryQueue, TopicExchange queryExchange) {
        return BindingBuilder.bind(routineQueryQueue)
                 .to(queryExchange)
                 .with("data.query.*.routine");
    }
    
    @Bean
    public Binding auditBinding(Queue auditQueryQueue, TopicExchange queryExchange) {
        return BindingBuilder.bind(auditQueryQueue)
                 .to(queryExchange)
                 .with("data.query.*.audit");
    }
} 