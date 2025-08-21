# Fee Query Service 部署指南

## 🚀 快速部署（推荐方式）

### 方案一：JAR包直接部署

#### 1. 构建应用
```bash
# 在项目根目录执行
mvn clean package -DskipTests

# 或指定生产环境配置
mvn clean package -Pprod -DskipTests
```

#### 2. 创建用户和目录
```bash
# 创建应用用户
sudo useradd -r -s /bin/false feeservice

# 创建应用目录
sudo mkdir -p /opt/fee-query-service
sudo mkdir -p /var/log/fee-query-service
sudo mkdir -p /var/run

# 设置权限
sudo chown feeservice:feeservice /opt/fee-query-service
sudo chown feeservice:feeservice /var/log/fee-query-service
```

#### 3. 部署文件
```bash
# 复制JAR文件
sudo cp target/fee-query-service-1.0.0.jar /opt/fee-query-service/

# 复制配置文件
sudo cp application-prod.yml /opt/fee-query-service/

# 复制启动脚本
sudo cp deploy/start.sh /opt/fee-query-service/
sudo cp deploy/stop.sh /opt/fee-query-service/
sudo chmod +x /opt/fee-query-service/*.sh

# 复制systemd服务文件
sudo cp deploy/fee-query-service.service /etc/systemd/system/
```

#### 4. 配置环境变量
```bash
# 编辑环境变量
sudo vim /etc/environment

# 添加以下内容
DB_USERNAME=app_user
DB_PASSWORD=your_secure_password
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password
```

#### 5. 启动服务
```bash
# 使用systemd管理（推荐）
sudo systemctl daemon-reload
sudo systemctl enable fee-query-service
sudo systemctl start fee-query-service

# 检查状态
sudo systemctl status fee-query-service

# 查看日志
journalctl -u fee-query-service -f
```

### 方案二：Docker容器化部署

#### 1. 准备环境文件
```bash
# 创建.env文件
cat > .env << EOF
MYSQL_ROOT_PASSWORD=root123456
DB_PASSWORD=app_password
REDIS_PASSWORD=redis123456
EOF
```

#### 2. 启动所有服务
```bash
# 构建并启动
docker-compose up -d

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f fee-query-service
```

#### 3. 验证部署
```bash
# 健康检查
curl http://localhost:8081/actuator/health

# API文档
curl http://localhost:8081/swagger-ui.html
```

## 🔧 配置说明

### 环境变量配置
| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `DB_USERNAME` | app_user | 数据库用户名 |
| `DB_PASSWORD` | - | 数据库密码 |
| `REDIS_HOST` | localhost | Redis主机 |
| `REDIS_PORT` | 6379 | Redis端口 |
| `REDIS_PASSWORD` | - | Redis密码 |
| `SERVER_PORT` | 8081 | 应用端口 |
| `EUREKA_URL` | http://localhost:8761/eureka/ | 注册中心地址 |

### JVM调优参数
```bash
# 生产环境推荐参数
JAVA_OPTS="-Xms2g -Xmx4g -XX:+UseG1GC -XX:MaxGCPauseMillis=200 \
           -XX:+HeapDumpOnOutOfMemoryError \
           -XX:HeapDumpPath=/var/log/fee-query-service/ \
           -Dspring.profiles.active=prod"
```

## 📊 监控和运维

### 1. 健康检查
```bash
# 应用健康状态
curl http://localhost:8081/actuator/health

# 详细信息
curl http://localhost:9081/actuator/info
curl http://localhost:9081/actuator/metrics
```

### 2. 日志管理
```bash
# 查看应用日志
tail -f /var/log/fee-query-service/application.log

# 查看GC日志
tail -f /var/log/fee-query-service/gc.log

# 系统日志
journalctl -u fee-query-service -f
```

### 3. 性能监控
```bash
# JVM监控
jps -l
jstat -gc [pid] 1s

# 系统资源
top -p [pid]
iostat -x 1
```

## 🛡️ 安全配置

### 1. 防火墙设置
```bash
# 开放必要端口
sudo firewall-cmd --permanent --add-port=8081/tcp
sudo firewall-cmd --permanent --add-port=9081/tcp
sudo firewall-cmd --reload
```

### 2. SSL/TLS配置（生产环境）
```yaml
# application-prod.yml 添加
server:
  ssl:
    key-store: classpath:keystore.p12
    key-store-password: your_password
    key-store-type: PKCS12
    key-alias: fee-query-service
  port: 8443
```

## 🔄 升级和回滚

### 版本升级
```bash
# 备份当前版本
sudo cp /opt/fee-query-service/fee-query-service-1.0.0.jar \
        /opt/fee-query-service/fee-query-service-1.0.0.jar.backup

# 停止服务
sudo systemctl stop fee-query-service

# 替换新版本
sudo cp target/fee-query-service-1.1.0.jar /opt/fee-query-service/

# 更新服务文件中的JAR名称
sudo vim /etc/systemd/system/fee-query-service.service

# 重新加载并启动
sudo systemctl daemon-reload
sudo systemctl start fee-query-service
```

### 快速回滚
```bash
sudo systemctl stop fee-query-service
sudo cp /opt/fee-query-service/fee-query-service-1.0.0.jar.backup \
        /opt/fee-query-service/fee-query-service-1.0.0.jar
sudo systemctl start fee-query-service
```

## 🐛 故障排查

### 常见问题

1. **启动失败**
   ```bash
   # 检查日志
   journalctl -u fee-query-service --no-pager
   cat /var/log/fee-query-service/application.log
   ```

2. **数据库连接问题**
   ```bash
   # 测试数据库连接
   mysql -h localhost -u app_user -p shenzhen_medical
   ```

3. **Redis连接问题**
   ```bash
   # 测试Redis连接
   redis-cli -h localhost -p 6379 ping
   ```

4. **内存不足**
   ```bash
   # 检查内存使用
   free -h
   # 调整JVM参数
   sudo vim /etc/systemd/system/fee-query-service.service
   ```

### 性能调优建议

1. **数据库优化**
   - 添加适当索引
   - 调整连接池参数
   - 启用查询缓存

2. **Redis优化**
   - 调整内存策略
   - 配置持久化参数
   - 监控缓存命中率

3. **JVM调优**
   - 根据负载调整堆内存
   - 选择合适的垃圾收集器
   - 监控GC性能

## 📞 联系方式

如有问题，请联系运维团队或查看项目文档。 