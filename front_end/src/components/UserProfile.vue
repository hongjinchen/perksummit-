<template>
  <v-app id="inspire">
    <v-app-bar flat>
      <v-container class="fill-height d-flex align-center">
        <v-avatar class="me-10 ms-4" color="grey-darken-1" size="32"></v-avatar>

        <v-btn variant="text" to="/">选课中心</v-btn>
        <v-btn variant="text" to="/user-profile">个人中心</v-btn>

        <v-spacer></v-spacer>

        <v-responsive max-width="260">
          <v-text-field density="compact" hide-details variant="solo"></v-text-field>
        </v-responsive>
      </v-container>
    </v-app-bar>

    <v-main class="bg-grey-lighten-3">
      <v-container>
        <v-row>
          <v-col cols="12">
            <v-sheet rounded="lg" class="pa-5">
              <h2 class="mb-3">个人中心</h2>
              <!-- 在这里显示用户的姓名 -->
              <h4 class="mb-2" v-if="user">{{ user.email }}</h4>

              <!-- 在这里显示用户所选的课程 -->
              <h3 class="mb-2">我的课程：</h3>
              <v-list rounded="lg" v-if="courses && courses.length">
                <v-list-item v-for="course in courses" :key="course.id" link>
                  <v-row>
                    <v-col cols="6" class="mb-1">
                      <v-list-item-title class="caption">
                        {{ course.name }}
                      </v-list-item-title>
                    </v-col>
                    <v-col cols="6">
                      <v-list-item-title class="caption">
                        <!-- 假设每个课程对象都有一个 'time' 属性 -->
                        {{ course.time }}
                      </v-list-item-title>
                    </v-col>
                  </v-row>
                </v-list-item>
              </v-list>
              <EmptyState v-else />
            </v-sheet>
          </v-col>
        </v-row>
      </v-container>
    </v-main>

    <v-btn class="submit-button" variant="text" @click="logout" :loading="isLoading">{{ isLoading ? '退出中...' : '退出登录' }}</v-btn>
  </v-app>
</template>

<script>
import Cookies from 'js-cookie'
import http from '../../http-common'
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import EmptyState from './EmptyState'

export default {
  components: {
    EmptyState  // 注册 EmptyState 组件
  },
  setup() {
    const router = useRouter()
    const user = ref(null)
    const courses = ref([])
    const editUser = ref({})
    const editMode = ref(false)
    const isLoading = ref(false)

    const fetchUser = async () => {
      isLoading.value = true // 开始加载

      const userId = Cookies.get('user_id')
      if (!userId) {
        router.push('/login')
        return
      }

      try {
        const response = await http.get(`/user/${userId}`) // Replace with your actual API endpoint
        user.value = response.data
      } catch (error) {
        console.error('Error fetching user:', error)
      }
      isLoading.value = false // 加载完成
    }

    const fetchCourses = async () => {
      isLoading.value = true // 开始加载
      const userId = Cookies.get('user_id')
      if (!userId) {
        router.push('/login')
        return
      }

      try {
        const response = await http.get(`/selectedCourses/${userId}`) // 使用新的 API 端点
        courses.value = response.data
        // console.log(courses.value)
      } catch (error) {
        console.error('Error fetching courses:', error)
      }
      isLoading.value = false // 加载完成
    }

    const saveChanges = () => {
      // Here you would typically make an API call to update the user data
      user.value = editUser.value
      editMode.value = false
    }

    const cancelEdit = () => {
      editMode.value = false
    }

    const logout = () => {
      isLoading.value = true // 开始加载
      Cookies.remove('token')  // remove the user cookie
      Cookies.remove('user_id')  // remove the user cookie
      // 删除 Authorization 头部
      delete http.defaults.headers.common['Authorization'];

      isLoading.value = false // 加载完成

      router.push('/login')
    }

    onMounted(() => {
      const userToken = Cookies.get('token')
      if (!userToken) {
        router.push('/login')
        return
      }

      fetchUser()
      fetchCourses()
      editUser.value = { ...user.value }
    })

    return {
      isLoading,
      user,
      courses,
      editUser,
      editMode,
      fetchUser,
      fetchCourses,
      saveChanges,
      cancelEdit,
      logout
    }
  }
}
</script>

<style scoped>
.no-underline {
  text-decoration: none;
}

.submit-button {
  position: fixed;
  bottom: 50px;
  left: 0;
  right: 0;
  height: 50px;
  line-height: 50px;
  /* 确保文字垂直居中 */
  text-align: center;
  /* 确保文字水平居中 */
  background-color: #333;
  color: #fff;
}</style>