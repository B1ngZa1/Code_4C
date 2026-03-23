# 电商平台项目

## 项目概述

这是一个基于Vue 3 + FastAPI + SQLite的电商平台项目，旨在参加计算机设计大赛。项目包含商品展示、购物车、订单管理、用户管理等核心功能。

## 技术栈

- **前端**：Vue 3 + Vite + Element Plus + Vue Router + Pinia + Axios
- **后端**：FastAPI + SQLAlchemy + JWT
- **数据库**：SQLite

## 项目结构

```
ecommerce/
├── frontend/           # 前端项目
│   ├── src/            # 源代码
│   │   ├── components/ # 组件
│   │   ├── views/      # 页面
│   │   ├── router/     # 路由
│   │   ├── store/      # 状态管理
│   │   └── api/        # API调用
│   ├── package.json    # 依赖配置
│   └── vite.config.js  # Vite配置
├── backend/            # 后端项目
│   ├── api/            # API路由
│   ├── main.py         # 主应用
│   ├── database.py     # 数据库配置
│   ├── models.py       # 数据模型
│   └── requirements.txt # 依赖配置
└── db/                 # 数据库文件
```

## 核心功能

### 前端功能
1. **用户模块**：注册、登录、个人信息管理
2. **商品模块**：商品列表、商品详情、搜索、分类
3. **购物车模块**：添加商品、修改数量、删除商品
4. **订单模块**：创建订单、订单列表、订单详情
5. **支付模块**：模拟支付功能

### 后端功能
1. **用户服务**：用户认证、权限管理
2. **商品服务**：商品CRUD操作、库存管理
3. **订单服务**：订单创建、状态管理
4. **支付服务**：支付流程处理

## 环境搭建

### 前端环境
1. 安装Node.js和npm
2. 进入frontend目录
3. 安装依赖：`npm install`
4. 启动开发服务器：`npm run dev`

### 后端环境
1. 安装Python和pip
2. 进入backend目录
3. 创建虚拟环境：`python -m venv venv`
4. 激活虚拟环境：`venv\Scripts\activate`（Windows）
5. 安装依赖：`pip install -r requirements.txt`
6. 启动开发服务器：`python main.py`

## 数据库初始化

后端服务启动时会自动创建数据库表结构。可以通过API接口添加商品数据。

## API文档

启动后端服务后，可以访问 `http://localhost:8000/docs` 查看API文档。

## 项目亮点

1. **响应式设计**：支持多设备访问
2. **良好的用户体验**：直观的界面设计和流畅的交互
3. **高效的后端性能**：使用FastAPI框架，性能优异
4. **完整的功能实现**：涵盖电商平台的核心功能
5. **安全的用户认证**：使用JWT进行身份验证

## 注意事项

1. 本项目使用SQLite作为数据库，适合开发和测试环境
2. 生产环境建议使用PostgreSQL或MySQL等更强大的数据库
3. 支付功能为模拟实现，实际使用需要集成真实的支付网关
4. 项目中的SECRET_KEY需要在生产环境中替换为安全的密钥

## 启动步骤

1. 启动后端服务：`python main.py`
2. 启动前端服务：`npm run dev`
3. 访问前端页面：`http://localhost:3000`
4. 访问API文档：`http://localhost:8000/docs`