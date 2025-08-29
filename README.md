# DeepRisk - 基于深度学习的风控平台

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Java](https://img.shields.io/badge/Java-17-orange.svg)](https://openjdk.org/)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.x-green.svg)](https://vuejs.org/)

## 前言

研究生期间校企合作项目改造而来的开源智能风控平台，出于简化考虑仅展示核心模块。

## 问题背景

数字化时代，金融、电商、医疗、互联网等行业面临日益复杂的风险挑战，传统规则引擎已无法适应多变的风险场景。主要痛点：

- **规则局限**: 难以覆盖复杂欺诈模式
- **适应性差**: 无法快速应对新兴风险
- **维护成本高**: 规则更新依赖人工干预

## 解决方案

DeepRisk通过多种神经网络模型提取用户行为特征，再利用ANN (Approximate Nearest Neighbor) 进行相似度匹配，实现数据驱动的风险识别。

![解决方案架构图](./解决方案.jpg)

## 项目架构


| 描述                     | 框架                       |
| ------------------------ | -------------------------- |
| 前端框架                 | Vue 3.4.0                  |
| UI组件库                 | Element Plus 2.3.14        |
| 图表库                   | ECharts 5.4.3              |
| HTTP客户端               | Axios 1.6.2                |
| 路由管理                 | Vue Router 4.2.5           |
| 后端API框架              | FastAPI 0.116.1            |
| Java后端框架             | Spring Boot 3.0.13         |
| ORM框架                  | Spring Data JPA 3.0.13     |
| 数据库                   | MySQL 8.0.33               |
| 缓存数据库               | Redis 5.0.8                |
| 向量数据库               | RediSearch 2.8             |
| 消息中间件               | RabbitMQ 3.13.7            |
| 消息中间件客户端(Python) | Pika 1.3.2                 |
| 消息中间件客户端(Java)   | Spring AMQP 3.0.13         |
| 深度学习框架             | PyTorch 2.1.0              |
| 数据处理                 | Pandas 2.0.3, NumPy 1.24.3 |
| 机器学习                 | Scikit-learn 1.3.0         |
| 配置中心                 | Nacos                      |
| 容器化                   | Docker                     |
| 反向代理                 | Nginx                      |

## 效果展示
