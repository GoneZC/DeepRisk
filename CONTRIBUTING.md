# 贡献指南

感谢您对 DeepRisk 项目的关注！我们欢迎所有形式的贡献，包括但不限于：

- 🐛 报告 Bug
- 💡 提出新功能建议
- 📝 改进文档
- 🔧 提交代码修复
- ✨ 添加新功能

## 开始之前

在开始贡献之前，请确保您已经：

1. 阅读了项目的 [README.md](README.md)
2. 了解了项目的架构和技术栈
3. 搭建了本地开发环境

## 报告问题

如果您发现了 Bug 或有功能建议，请：

1. 检查 [Issues](../../issues) 页面，确认问题尚未被报告
2. 使用合适的 Issue 模板创建新的 Issue
3. 提供详细的问题描述和复现步骤
4. 如果是 Bug，请包含：
   - 操作系统和版本
   - 浏览器类型和版本
   - 错误截图或日志
   - 复现步骤

## 提交代码

### 开发流程

1. **Fork 仓库**
   ```bash
   # 点击页面右上角的 Fork 按钮
   ```

2. **克隆您的 Fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/DeepRisk_Server.git
   cd DeepRisk_Server
   ```

3. **添加上游仓库**
   ```bash
   git remote add upstream https://github.com/ORIGINAL_OWNER/DeepRisk_Server.git
   ```

4. **创建特性分支**
   ```bash
   git checkout -b feature/your-feature-name
   # 或者修复分支
   git checkout -b fix/your-fix-name
   ```

5. **进行开发**
   - 遵循项目的代码规范
   - 添加必要的测试
   - 确保代码通过所有测试

6. **提交更改**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

7. **同步上游更改**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

8. **推送到您的 Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

9. **创建 Pull Request**
   - 访问您的 Fork 页面
   - 点击 "New Pull Request"
   - 填写 PR 模板
   - 等待代码审查

### 提交信息规范

我们使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**类型 (type):**
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式化（不影响功能）
- `refactor`: 代码重构
- `test`: 添加或修改测试
- `chore`: 构建过程或辅助工具的变动

**示例:**
```
feat(auth): add JWT token validation

fix(api): resolve null pointer exception in user service

docs: update installation guide
```

## 代码规范

### Java 代码规范

- 使用 4 个空格缩进
- 类名使用 PascalCase
- 方法名和变量名使用 camelCase
- 常量使用 UPPER_SNAKE_CASE
- 添加适当的 Javadoc 注释

### Python 代码规范

- 遵循 PEP 8 规范
- 使用 4 个空格缩进
- 函数和变量名使用 snake_case
- 类名使用 PascalCase
- 添加类型注解

### JavaScript/Vue.js 代码规范

- 使用 2 个空格缩进
- 使用 ESLint 进行代码检查
- 组件名使用 PascalCase
- 方法名使用 camelCase
- 添加适当的注释

## 测试

在提交代码之前，请确保：

1. **运行所有测试**
   ```bash
   # Java 测试
   cd DeepRisk-audit-server
   mvn test
   
   # Python 测试
   cd DeepRisk-analyze-server
   python -m pytest
   
   # 前端测试
   cd DeepRisk-frontend
   npm run test
   ```

2. **添加新的测试用例**
   - 为新功能添加单元测试
   - 为 Bug 修复添加回归测试
   - 确保测试覆盖率不降低

3. **手动测试**
   - 在本地环境验证功能
   - 测试不同的使用场景
   - 确保不破坏现有功能

## 文档

如果您的更改涉及：

- 新功能：更新相关文档和 README
- API 变更：更新 API 文档
- 配置变更：更新配置说明
- 部署变更：更新部署指南

## 代码审查

所有的 Pull Request 都需要经过代码审查：

1. **自我审查**
   - 检查代码质量
   - 确保符合规范
   - 验证功能正确性

2. **同行审查**
   - 等待维护者或其他贡献者审查
   - 积极回应审查意见
   - 及时修复发现的问题

3. **持续集成**
   - 确保 CI 检查通过
   - 修复任何失败的测试
   - 解决代码质量问题

## 发布流程

项目维护者会定期发布新版本：

1. 合并所有准备好的 PR
2. 更新版本号和 CHANGELOG
3. 创建 Release Tag
4. 发布到相应的包管理器

## 社区

- 💬 讨论：使用 GitHub Discussions
- 🐛 问题：使用 GitHub Issues
- 📧 邮件：[your-email@example.com]

## 行为准则

请遵循我们的 [行为准则](CODE_OF_CONDUCT.md)，营造友好、包容的社区环境。

## 许可证

通过贡献代码，您同意您的贡献将在 [MIT License](LICENSE) 下发布。

---

再次感谢您的贡献！🎉