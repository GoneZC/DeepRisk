package com.demo.config;

import org.springframework.amqp.core.*;
import org.springframework.amqp.rabbit.connection.ConnectionFactory;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.amqp.support.converter.Jackson2JsonMessageConverter;
import org.springframework.amqp.support.converter.MessageConverter;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class RabbitMQConfig {

    // 交换机和队列名称常量
    public static final String RISK_EXCHANGE = "risk.assessment.exchange";
    public static final String RISK_QUEUE = "risk.assessment.queue";
    public static final String RISK_ROUTING_KEY = "risk.assessment";
    
    public static final String RESULT_EXCHANGE = "risk.result.exchange";
    public static final String RESULT_QUEUE = "risk.result.queue";
    public static final String RESULT_ROUTING_KEY = "risk.result";

    // 创建风险评估请求队列
    @Bean
    public Queue riskQueue() {
        return new Queue(RISK_QUEUE, true); // 持久化队列
    }

    // 创建风险评估结果队列
    @Bean
    public Queue resultQueue() {
        return new Queue(RESULT_QUEUE, true);
    }

    // 创建交换机
    @Bean
    public DirectExchange riskExchange() {
        return new DirectExchange(RISK_EXCHANGE, true, false);
    }

    @Bean
    public DirectExchange resultExchange() {
        return new DirectExchange(RESULT_EXCHANGE, true, false);
    }

    // 绑定队列和交换机
    @Bean
    public Binding riskBinding(Queue riskQueue, DirectExchange riskExchange) {
        return BindingBuilder.bind(riskQueue).to(riskExchange).with(RISK_ROUTING_KEY);
    }

    @Bean
    public Binding resultBinding(Queue resultQueue, DirectExchange resultExchange) {
        return BindingBuilder.bind(resultQueue).to(resultExchange).with(RESULT_ROUTING_KEY);
    }

    // 配置消息转换器(JSON)
    @Bean
    public MessageConverter jsonMessageConverter() {
        return new Jackson2JsonMessageConverter();
    }

    // 配置RabbitTemplate
    @Bean
    public RabbitTemplate rabbitTemplate(ConnectionFactory connectionFactory) {
        final RabbitTemplate rabbitTemplate = new RabbitTemplate(connectionFactory);
        rabbitTemplate.setMessageConverter(jsonMessageConverter());
        rabbitTemplate.setBeforePublishPostProcessors(message -> {
            message.getMessageProperties().setContentType("application/json");
            return message;
        });
        return rabbitTemplate;
    }
} 