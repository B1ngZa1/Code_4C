import requests

# 测试根路径
print("测试根路径:")
try:
    response = requests.get('http://localhost:8000')
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
except Exception as e:
    print(f"错误: {e}")

# 测试登录
print("\n测试登录:")
try:
    response = requests.post('http://localhost:8000/api/auth/login', json={'username': 'admin', 'password': '123456'})
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
except Exception as e:
    print(f"错误: {e}")

# 测试获取用户信息
print("\n测试获取用户信息:")
try:
    # 先登录获取token
    login_response = requests.post('http://localhost:8000/api/auth/login', json={'username': 'admin', 'password': '123456'})
    token = login_response.json().get('access_token')
    
    if token:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get('http://localhost:8000/api/user/me', headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
    else:
        print("获取token失败")
except Exception as e:
    print(f"错误: {e}")

# 测试获取股票数据
print("\n测试获取股票数据:")
try:
    response = requests.get('http://localhost:8000/api/data/stocks')
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
except Exception as e:
    print(f"错误: {e}")

# 测试获取策略列表
print("\n测试获取策略列表:")
try:
    response = requests.get('http://localhost:8000/api/strategy/list')
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
except Exception as e:
    print(f"错误: {e}")

# 测试获取回测列表
print("\n测试获取回测列表:")
try:
    response = requests.get('http://localhost:8000/api/backtest/list')
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
except Exception as e:
    print(f"错误: {e}")

# 测试获取交易列表
print("\n测试获取交易列表:")
try:
    response = requests.get('http://localhost:8000/api/trading/list')
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
except Exception as e:
    print(f"错误: {e}")
