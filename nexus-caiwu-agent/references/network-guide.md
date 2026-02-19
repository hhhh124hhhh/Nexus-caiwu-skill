# 网络配置指南

## 概述

nexus-caiwu-agent 现在支持三种网络模式：

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| `auto` | 自动检测网络状态 | 不确定网络环境时 |
| `direct` | 国内直连 | 在中国大陆使用 |
| `proxy` | 使用代理 | 在海外或需要代理访问 |

## 快速开始

### 1. 自动检测（推荐首次使用）

```bash
python scripts/fetch_data.py --detect-network
```

输出示例：
```
[检测] 网络连接状态...
  [OK] 百度 连接正常
[结论] 国内网络直连可用，建议使用 direct 模式

检测到的网络模式: direct
```

### 2. 基本使用

```bash
# 使用自动模式
python scripts/fetch_data.py 600519 贵州茅台 --analyze --save

# 指定直连模式
python scripts/fetch_data.py 600519 --mode direct

# 指定代理模式
python scripts/fetch_data.py 600519 --mode proxy --proxy http://127.0.0.1:7890
```

## 代理配置

### HTTP/HTTPS 代理

```bash
# 临时使用（命令行参数）
python scripts/fetch_data.py 600519 --proxy http://127.0.0.1:7890

# 临时使用（环境变量）
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890
python scripts/fetch_data.py 600519
```

### SOCKS5 代理

```bash
# 命令行参数
python scripts/fetch_data.py 600519 --proxy socks5://127.0.0.1:1080

# 使用网络配置工具
python scripts/network_client.py --set-proxy socks5://127.0.0.1:1080
```

### 测试代理连接

```bash
python scripts/fetch_data.py --test-proxy http://127.0.0.1:7890
python scripts/fetch_data.py --test-proxy socks5://127.0.0.1:1080
```

## 持久化配置

### 方法 1: 配置文件

复制示例配置：
```bash
cp config/network.json.example config/network.json
```

编辑 `config/network.json`：
```json
{
  "mode": "proxy",
  "proxy": {
    "http": "http://127.0.0.1:7890",
    "https": "http://127.0.0.1:7890"
  },
  "timeout": 30,
  "retry": 3
}
```

### 方法 2: 环境变量

在 `~/.bashrc` 或 `~/.zshrc` 中添加：
```bash
export NET_MODE=proxy
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890
export NET_TIMEOUT=30
export NET_RETRY=3
```

### 方法 3: 网络配置工具

```bash
# 设置模式
python scripts/network_client.py --set-mode direct

# 设置代理
python scripts/network_client.py --set-proxy http://127.0.0.1:7890

# 设置超时
python scripts/network_client.py --timeout 60

# 设置重试次数
python scripts/network_client.py --retry 5

# 查看当前配置
python scripts/network_client.py --show-config
```

## 常见问题

### Q1: 数据获取超时

**解决方案**：
1. 增加超时时间：
   ```bash
   python scripts/fetch_data.py 600519 --mode direct --timeout 60
   ```

2. 增加重试次数：
   ```bash
   python scripts/fetch_data.py 600519 --retry 5
   ```

3. 使用代理：
   ```bash
   python scripts/fetch_data.py 600519 --mode proxy --proxy http://127.0.0.1:7890
   ```

### Q2: 代理连接失败

**排查步骤**：
1. 测试代理是否可用：
   ```bash
   python scripts/fetch_data.py --test-proxy http://127.0.0.1:7890
   ```

2. 检查代理软件是否开启

3. 确认代理地址和端口正确

4. 尝试切换代理类型（HTTP/HTTPS → SOCKS5）

### Q3: 国内网络无法访问

**解决方案**：
1. 检测网络状态：
   ```bash
   python scripts/fetch_data.py --detect-network
   ```

2. 如果检测失败，强制使用直连模式：
   ```bash
   python scripts/fetch_data.py 600519 --mode direct
   ```

3. 检查防火墙设置

### Q4: 自动模式检测不准确

**解决方案**：
手动指定模式而不是使用自动模式：
```bash
python scripts/fetch_data.py 600519 --mode direct
```

## API 使用

### Python 代码中直接使用

```python
from scripts.network_client import NetworkClient

# 自动模式
client = NetworkClient(mode='auto')
data = client.fetch_financial_data('600519', '贵州茅台')

# 直连模式
client = NetworkClient(mode='direct')
data = client.fetch_financial_data('600519')

# 代理模式
client = NetworkClient(
    mode='proxy',
    proxy_url='http://127.0.0.1:7890',
    timeout=60,
    retry=5
)
data = client.fetch_financial_data('600519')
```

### 使用 fetch_data.py 的函数

```python
from scripts.fetch_data import get_financial_data

# 使用直连模式
data = get_financial_data(
    '600519',
    '贵州茅台',
    network_mode='direct'
)

# 使用代理模式
data = get_financial_data(
    '600519',
    '贵州茅台',
    network_mode='proxy',
    proxy_url='socks5://127.0.0.1:1080'
)
```

## 网络配置工具完整命令

```bash
# 显示帮助
python scripts/network_client.py --help

# 检测网络模式
python scripts/network_client.py --detect

# 设置网络模式
python scripts/network_client.py --set-mode auto
python scripts/network_client.py --set-mode direct
python scripts/network_client.py --set-mode proxy

# 设置代理
python scripts/network_client.py --set-proxy http://127.0.0.1:7890
python scripts/network_client.py --set-proxy socks5://127.0.0.1:1080

# 测试代理
python scripts/network_client.py --test-proxy http://127.0.0.1:7890

# 设置超时和重试
python scripts/network_client.py --timeout 60
python scripts/network_client.py --retry 5

# 显示当前配置
python scripts/network_client.py --show-config
```

## 技术细节

### 重试机制

- 默认重试 3 次
- 每次重试延迟递增：2秒、4秒、6秒
- 可自定义重试次数和延迟

### 代理支持

- HTTP/HTTPS 代理
- SOCKS5 代理（需要 PySocks 库）
- 透明代理设置（自动应用到 requests/urllib）

### SSL 验证

- 默认启用 SSL 验证
- 可在配置文件中禁用（不推荐）
