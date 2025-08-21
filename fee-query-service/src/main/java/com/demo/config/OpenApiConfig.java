package com.demo.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.servers.Server;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class OpenApiConfig {
    
    @Bean
    public OpenAPI customOpenAPI() {
        return new OpenAPI()
                .info(new Info()
                    .title("医保反欺诈系统API")
                    .version("1.0.0")
                    .description("提供医保费用查询、风险分析、门诊监管等功能的REST API接口文档")
                    .contact(new Contact()
                        .name("医保反欺诈系统")
                        .email("admin@medical-insurance.com")))
                .addServersItem(new Server()
                    .url("http://localhost:8081")
                    .description("开发环境"))
                .addServersItem(new Server()
                    .url("http://localhost:8082")
                    .description("网关环境"));
    }
} 