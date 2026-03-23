# 个人量化分析与交易系统

## 项目简介

个人量化分析与交易系统是一个基于Vue 3和FastAPI开发的完整量化交易平台，功能参考qbot，支持数据获取、策略开发、回测验证、模拟交易和实盘交易等核心功能。

## 系统架构

系统采用前后端分离架构：

### 前端技术栈
- Vue 3 + Vite
- Element Plus (UI组件库)
- ECharts (数据可视化)
- Pinia (状态管理)
- Axios (API调用)

### 后端技术栈
- FastAPI
- SQLAlchemy (ORM)
- PostgreSQL (数据库)
- JWT (认证)
- Pandas (数据处理)
- TA-Lib (技术指标计算)

## 核心功能

### 1. 数据管理
- 多源数据获取（Tushare、Binance、模拟数据）
- 数据存储和管理
- 数据可视化

### 2. 策略开发
- 策略创建和编辑
- 技术指标计算
- 策略回测

### 3. 回测系统
- 策略回测
- 绩效分析
- 回测结果可视化

### 4. 交易管理
- 模拟交易
- 实盘交易（支持Binance）
- 投资组合管理
- 交易统计

### 5. 用户管理
- 用户注册和登录
- 个人中心
- 系统设置

## 项目结构

```
quant_system/
├── backend/              # 后端代码
│   ├── api/              # API路由
│   ├── core/             # 核心配置
│   ├── services/         # 业务逻辑
│   ├── main.py           # 应用入口
│   ├── models.py         # 数据模型
│   └── requirements.txt  # 依赖管理
├── frontend/             # 前端代码
│   ├── src/              # 源代码
│   │   ├── api/          # API调用
│   │   ├── router/       # 路由配置
│   │   ├── store/        # 状态管理
│   │   ├── views/        # 页面组件
│   │   ├── App.vue       # 根组件
│   │   └── main.js       # 应用入口
│   ├── index.html        # HTML模板
│   ├── package.json      # 依赖管理
│   └── vite.config.js    # Vite配置
├── architecture.md       # 系统架构文档
└── README.md             # 项目说明
```

## 安装和启动

### 后端安装

1. 进入后端目录
```bash
cd quant_system/backend
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置环境变量
创建 `.env` 文件，配置以下内容：
```
DATABASE_URL=postgresql://username:password@localhost:5432/quant_system
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

4. 启动后端服务
```bash
uvicorn main:app --reload
```

### 前端安装

1. 进入前端目录
```bash
cd quant_system/frontend
```

2. 安装依赖
```bash
npm install
```

3. 启动前端开发服务器
```bash
npm run dev
```

### 访问系统

前端地址：`http://127.0.0.1:3000`
后端API地址：`http://localhost:8000/api`

### 前端质量校验

```bash
npm run lint
npm test
npm run build
```

### 后端测试

```bash
cd quant_system/backend
pip install -r requirements.txt -r requirements-dev.txt
python -m pytest -q
```

## 使用指南

### 1. 注册和登录
- 访问系统后，点击右上角的"登录"按钮
- 点击"立即注册"创建新账号
- 使用注册的账号登录系统

### 2. 数据管理
- 点击左侧菜单的"数据管理"
- 选择数据源（Tushare、Binance或模拟数据）
- 配置API密钥（在系统设置中）
- 获取市场数据

### 3. 策略开发
- 点击左侧菜单的"策略开发"
- 创建新策略或编辑现有策略
- 编写策略逻辑
- 保存策略

### 4. 回测系统
- 点击左侧菜单的"回测系统"
- 选择要回测的策略
- 设置回测参数（时间范围、初始资金等）
- 运行回测
- 查看回测结果和绩效分析

### 5. 交易管理
- 点击左侧菜单的"交易管理"
- 选择交易类型（模拟交易或实盘交易）
- 创建交易订单
- 查看交易历史和投资组合

### 6. 系统设置
- 点击左侧菜单的"系统设置"
- 配置API密钥（Tushare、Binance）
- 设置系统参数（数据更新频率、回测数据保存时间等）
- 查看系统信息

## 技术支持

### 常见问题

1. **无法获取数据**
   - 检查API密钥是否正确配置
   - 检查网络连接
   - 检查数据源是否可用

2. **回测失败**
   - 检查策略代码是否正确
   - 检查数据是否完整
   - 检查回测参数是否合理

3. **交易失败**
   - 检查API密钥权限
   - 检查账户资金是否充足
   - 检查网络连接

### 联系方式

如有问题或建议，请联系：
- 邮箱：support@quant-system.com
- GitHub：https://github.com/quant-system

## 版本历史

- v1.0.0 (2024-01-01)：初始版本，包含核心功能

## 许可证

MIT License
