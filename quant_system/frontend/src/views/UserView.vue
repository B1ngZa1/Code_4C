<template>
  <div class="user-container">
    <el-card class="user-card">
      <template #header>
        <div class="user-header">
          <h2>个人中心</h2>
          <p>管理您的账户信息</p>
        </div>
      </template>
      <div v-if="userStore.user" class="user-info">
        <el-form :model="userForm" label-width="100px">
          <el-form-item label="用户名">
            <el-input v-model="userForm.username" disabled />
          </el-form-item>
          <el-form-item label="邮箱">
            <el-input v-model="userForm.email" disabled />
          </el-form-item>
          <el-form-item label="注册时间">
            <el-input v-model="userForm.created_at" disabled />
          </el-form-item>
          <el-form-item label="最后登录">
            <el-input v-model="userForm.last_login" disabled />
          </el-form-item>
        </el-form>
        <el-divider />
        <h3>账户安全</h3>
        <el-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef" label-width="100px">
          <el-form-item label="当前密码" prop="currentPassword">
            <el-input v-model="passwordForm.currentPassword" type="password" placeholder="请输入当前密码" show-password />
          </el-form-item>
          <el-form-item label="新密码" prop="newPassword">
            <el-input v-model="passwordForm.newPassword" type="password" placeholder="请输入新密码" show-password />
          </el-form-item>
          <el-form-item label="确认新密码" prop="confirmPassword">
            <el-input v-model="passwordForm.confirmPassword" type="password" placeholder="请确认新密码" show-password />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleUpdatePassword" :loading="loading">修改密码</el-button>
          </el-form-item>
        </el-form>
        <el-divider />
        <div class="logout-section">
          <el-button type="danger" @click="handleLogout">退出登录</el-button>
        </div>
      </div>
      <div v-else class="not-login">
        <el-empty description="请先登录" />
        <el-button type="primary" @click="navigateToLogin">去登录</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../store/user'

const router = useRouter()
const userStore = useUserStore()
const passwordFormRef = ref(null)
const loading = ref(false)

const userForm = reactive({
  username: '',
  email: '',
  created_at: '',
  last_login: ''
})

const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const passwordRules = {
  currentPassword: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== passwordForm.newPassword) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

onMounted(() => {
  if (userStore.user) {
    userForm.username = userStore.user.username
    userForm.email = userStore.user.email
    userForm.created_at = userStore.user.created_at
    userForm.last_login = userStore.user.last_login
  }
})

const handleUpdatePassword = async () => {
  if (!passwordFormRef.value) return
  await passwordFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        // 调用API更新密码
        // 这里需要实现密码更新逻辑
        console.log('更新密码:', passwordForm)
        // 模拟成功
        alert('密码更新成功')
        // 重置表单
        passwordForm.currentPassword = ''
        passwordForm.newPassword = ''
        passwordForm.confirmPassword = ''
      } catch (error) {
        console.error('密码更新失败:', error)
      } finally {
        loading.value = false
      }
    }
  })
}

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}

const navigateToLogin = () => {
  router.push('/login')
}
</script>

<style scoped>
.user-container {
  padding: 20px;
  background-color: #f5f5f5;
  min-height: 80vh;
}

.user-card {
  max-width: 800px;
  margin: 0 auto;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.user-header {
  text-align: center;
  margin-bottom: 20px;
}

.user-header h2 {
  margin-bottom: 10px;
  color: #1890ff;
}

.user-header p {
  color: #666;
  font-size: 14px;
}

.user-info {
  padding: 20px;
}

.not-login {
  text-align: center;
  padding: 40px 0;
}

.logout-section {
  margin-top: 20px;
  text-align: center;
}
</style>
