# 贡献指南

感谢你对 Nexus Caiwu Skill 项目的兴趣！本文档将帮助你了解如何为项目做出贡献。

## 如何贡献

### 报告 Bug

如果你发现了 Bug，请通过 [GitHub Issues](https://github.com/hhhh124hhhh/Nexus-caiwu-skill/issues) 提交报告。在提交之前，请：

1. 搜索现有的 Issues，确认该问题尚未被报告
2. 使用清晰的标题描述问题
3. 提供复现步骤
4. 说明你的环境（Python 版本、操作系统等）

### 提出新功能

欢迎提出新功能建议！请：

1. 通过 Issues 描述你的想法
2. 说明该功能的使用场景
3. 如果可能，提供实现思路

### 提交代码

#### 开发环境设置

```bash
# Fork 并克隆仓库
git clone https://github.com/YOUR_USERNAME/Nexus-caiwu-skill.git
cd Nexus-caiwu-skill

# 安装依赖
pip install akshare pandas

# 创建分支
git checkout -b feature/your-feature-name
```

#### 代码规范

- **Python**: 遵循 PEP 8 规范
- **注释**: 使用中文注释，保持代码可读性
- **函数文档**: 使用 docstring 描述函数功能

#### 提交规范

使用 Conventional Commits 格式：

```
<type>: <description>

[optional body]
```

类型：
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 其他修改

示例：
```
feat: 添加北交所股票支持
fix: 修复 ROE 计算错误
docs: 更新安装文档
```

#### Pull Request 流程

1. 确保代码通过测试
2. 更新相关文档
3. 创建 Pull Request，描述你的修改
4. 等待代码审查

## 代码结构

```
nexus-caiwu-skill/
├── nexus-caiwu-agent/
│   ├── scripts/           # 核心脚本
│   │   ├── fetch_data.py  # 数据获取与分析
│   │   ├── ppt_generator.py
│   │   └── baidu_skills_wrapper.py
│   ├── skills/            # 子技能
│   ├── references/        # 参考文档
│   └── docs/              # 文档
├── README.md
├── CONTRIBUTING.md
└── LICENSE
```

## 行为准则

- 尊重所有贡献者
- 保持专业和友好的交流
- 接受建设性批评

## 许可证

通过提交代码，你同意你的贡献将根据 [Apache-2.0](LICENSE) 许可证授权。

---

再次感谢你的贡献！
