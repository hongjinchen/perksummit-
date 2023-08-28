<template>
  <div>
    <v-overlay :value="isLoading">
      <v-progress-circular indeterminate size="64"></v-progress-circular>
    </v-overlay>
    <v-app id="inspire" class="page-content">
      <!-- <v-overlay :value="isLoading">
        <v-progress-circular indeterminate size="64"></v-progress-circular>
      </v-overlay> -->
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

            <!-- 切换现有课程 -->
            <v-col cols="12" sm="8" md="4" lg="2">
              <v-sheet rounded="lg">
                <v-btn :class="selectedCourseType === 'mini_class' ? 'selected-course-type' : 'unselected-course-type'"
                  @click="selectCourseType('mini_class')">
                  迷你课堂
                </v-btn>
                <v-btn
                  :class="selectedCourseType === 'zheng_ming_tang' ? 'selected-course-type' : 'unselected-course-type'"
                  @click="selectCourseType('zheng_ming_tang')">
                  争鸣堂
                </v-btn>
                <v-list rounded="lg">
                  <v-list-item v-for="course in filteredCourses" :key="course.id" link @click="selectedCourse = course">
                    <v-list-item-title>
                      {{ course.name }}
                    </v-list-item-title>
                  </v-list-item>
                </v-list>
              </v-sheet>
            </v-col>

            <!-- 显示课程详情 -->
            <v-col cols="12" sm="12" md="8" lg="8">
              <v-sheet min-height="55vh" rounded="lg" v-if="selectedCourse" class="pa-4">
                <h2 class="mb-3">{{ selectedCourse.name }}</h2>
                <p class="mb-3">讲师：{{ selectedCourse.lecturer_name }}</p>
                <!-- <p class="mb-3">课程类型：{{ getCourseTypeName(selectedCourse.course_type) }}</p> -->

                <p class="mb-3" v-if="selectedCourse.description">详细信息：{{ selectedCourse.description }}</p>
                <div v-for="time in selectedCourse.times" :key="time.time" class="d-flex align-center mb-3">
                  <v-row>
                    <v-col cols="4">
                      <p>{{ time.time }}</p>
                    </v-col>
                    <v-col cols="5">
                      <v-progress-linear :value="time.registered" :max="time.max" class="mb-1"></v-progress-linear>
                      <p>{{ time.registered }}/{{ time.max }}</p>
                    </v-col>
                    <v-col cols="3">
                      <div class="ellipsis">
                        <v-btn
                          :disabled="(time.registered >= time.max || isRegistered(selectedCourse, time)) && userLoggedIn"
                          @click="registerCourse(selectedCourse, time)">
                          {{ isRegistered(selectedCourse, time) ? '已选择' : '在此时间段注册' }}
                        </v-btn>
                      </div>
                    </v-col>
                  </v-row>
                </div>
              </v-sheet>
            </v-col>

            <v-col cols="12" sm="6" md="12" lg="2">
              <v-sheet rounded="lg">
                <h2 class="text-center">已选课程</h2>
                <v-list rounded="lg">
                  <template v-if="registeredCourses.length">
                    <v-list-item v-for="course in registeredCourses" :key="course.id" link>
                      <div class="mb-1">
                        <v-list-item-title>
                          {{ course.name }}
                        </v-list-item-title>
                      </div>
                      <div v-if="course.selectedTime">
                        <!-- 遍历 selectedTime 数组 -->
                        <div v-for="time in course.selectedTime" :key="time.id">
                          <div class="d-flex align-center justify-start">
                            <v-list-item-title class="flex-grow-1">
                              {{ time.time }} <!-- 请确保 time 对象中有正确的时间属性 -->
                            </v-list-item-title>
                            <v-btn @click="removeCourseTime(course, time)">取消</v-btn> <!-- 新增的删除按钮，需要时间参数 -->
                          </div>
                        </div>
                      </div>
                    </v-list-item>
                  </template>

                  <EmptyState v-else />
                </v-list>
              </v-sheet>
            </v-col>

          </v-row>
        </v-container>
      </v-main>

      <!-- 选择课程按钮-->
      <v-btn class="submit-button" :loading="isLoading" :disabled="registeredCourses.length > maxCourses"
        @click="submitCourseSelection">
        选择课程
      </v-btn>
    </v-app>
  </div>
</template>

<script setup>
import EmptyState from './EmptyState.vue';
import { useRouter } from 'vue-router'

import { ref, onMounted, computed } from 'vue';
import http from '../../http-common';
import Cookies from 'js-cookie';

let maxCourses = 6; // 最多选择的课程数量
let courses = ref([]);
let registeredCourses = ref([]);
let selectedCourse = ref(null);  // 初始化为 null
let userLoggedIn = ref(false);
let isLoading = ref(false);
let router = useRouter();
const selectedCourseType = ref('all'); // 默认显示所有课程

const selectCourseType = (type) => {
  selectedCourseType.value = type;
};

const filteredCourses = computed(() => {
  if (selectedCourseType.value === 'all') return courses.value;
  return courses.value.filter(course => course.course_type === selectedCourseType.value);
});

onMounted(async () => {
  isLoading.value = true; // 在请求开始之前，将isLoading设为true
  try {
    // 检查用户是否已经登录
    const token = Cookies.get('token');
    userLoggedIn.value = Boolean(token);
    if (!userLoggedIn.value) {
      alert('你还未登录，现在将提供一些基本的操作指南：\n1. 在课程列表中选择你感兴趣的课程。\n2. 你可以查看每个课程的详细信息和选择时间。\n3. 可以在已选课程模块中查看你已选择的课程。\n4. 最后点击下方的“选择课程”按钮来确认你的选择。\n5. 如果想要取消课程或者重新选择课程，请点击取消按钮把右边的课程取消掉，并且重新提交。');
    }

    // 获取全部课程
    const response = await http.get('/courses');
    courses.value = response.data;
    selectedCourse.value = courses.value[0];  // 当你获取到课程数据后再设置默认课程
    // 获取当前用户已选课程
    const userId = Cookies.get('user_id');
    if (userId) { // 检查 userId 是否存在
      const responseSelectedCourses = await http.get(`/selectedCourses/${userId}`);
      registeredCourses.value = responseSelectedCourses.data;
    } else {
      alert('你还未登录，无法获取已选课程');
    }
  } catch (error) {
    console.error('There has been a problem with your fetch operation:', error);
    alert('当前网络不稳定或服务器响应时间过长，请稍后再试！');
  } finally {
    isLoading.value = false; // 在请求结束之后，无论成功还是失败，都将isLoading设为false
  }
});

const getCourseTypeName = (courseType) => {
  if (courseType === 'mini_class') {
    return '迷你课堂';
  } else if (courseType === 'zheng_ming_tang') {
    return '争鸣堂';
  }
  return ''; // 可以返回默认值或空字符串
};

const registerCourse = (course, time) => {
  const user = Cookies.get('token');

  if (!user) {
    router.push('/login');
    return;
  }

  // 检查选择的时间是否已经满员
  if (time.registered >= time.max) {
    alert('此时间段的课程已满');
    return;
  }

  if (course.course_type === 'mini_class') {
    const miniClassCourses = registeredCourses.value.filter(
      registeredCourse => registeredCourse.course_type === 'mini_class'
    );

    if (miniClassCourses.length >= 5) {
      alert('迷你课堂类别的课程，每个用户最多只能选择五节');
      return;
    }

    // 检查用户已经注册的课程中是否有与当前选择的课程时间冲突的
    // console.log("miniClassCourses", miniClassCourses);
    const conflictCourse = miniClassCourses.find(
      registeredCourse => registeredCourse.selectedTime.some(selectedTime => selectedTime.time === time.time)
    );

    if (conflictCourse) {
      alert(`你已经在这个时间段选择了 ${conflictCourse.name}`);
      return;
    }

  } else if (course.course_type === 'zheng_ming_tang') {
    // 争鸣堂类别的课程，每个用户只能选一节
    const zhengMingTangCourses = registeredCourses.value.filter(
      registeredCourse => registeredCourse.course_type === 'zheng_ming_tang'
    );
    if (zhengMingTangCourses.length >= 1) {
      alert('争鸣堂类别的课程，每个用户只能选择一节');
      return;
    }
  }

  // 查找已注册的相同id的课程
  const existingCourse = registeredCourses.value.find(c => c.id === course.id);
  if (existingCourse) {
    // 更新已存在课程的选择时间
    existingCourse.selectedTime = existingCourse.selectedTime || [];
    existingCourse.selectedTime.push(time);
  } else {
    // 新课程，所以将其添加到已注册课程列表中
    course.selectedTime = course.selectedTime || [];
    course.selectedTime.push(time);
    registeredCourses.value.push(course);
  }
  time.registered++;
};


const removeCourseTime = (course, time) => {
  // 在 selectedTime 数组中找到并删除特定的时间
  const index = course.selectedTime.indexOf(time);
  if (index > -1) {
    course.selectedTime.splice(index, 1);
  }

  // 更新时间段的注册状态
  time.registered--;

  // 如果课程的 selectedTime 为空，则从 registeredCourses 中移除
  if (course.selectedTime.length === 0) {
    const courseIndex = registeredCourses.value.indexOf(course);
    if (courseIndex > -1) {
      registeredCourses.value.splice(courseIndex, 1);
    }
  }
};


const submitCourseSelection = async () => {
  const user = Cookies.get('token');

  if (!user) {
    router.push('/login');
    return;
  }

  if (registeredCourses.value.length <= maxCourses) {
    isLoading.value = true; // 开始加载
    try {
      const userId = Cookies.get('user_id');

      const courses = registeredCourses.value.flatMap(course => (
        course.selectedTime.map(time => ({
          course_id: course.id,
          course_time: time.time
        }))
      ));

      const response = await http.post('/courseSelection', {
        userId: userId,
        courses: courses
      });

      if (response.status === 200) {
        alert('课程选择已提交');
        window.location.reload();
      }
    } catch (error) {
      if (error.response && error.response.status === 403) {
        alert('还没有到选择课程的时间');
      } else {
        console.error('There has been a problem with your fetch operation:', error);
        alert(`提交失败：${error.message || '未知错误'}`);
      }
    } finally {
      isLoading.value = false; // 结束加载
    }
  } else {
    alert('最多只能选择5门课程');
  }
};


const isRegistered = (course, time) => {
  return registeredCourses.value.some(
    c => c.id === course.id && c.selectedTime && c.selectedTime.some(t => t.time === time.time)
  );
};

</script>

<style scoped>
.no-underline {
  text-decoration: none;
}

.page-content {
  padding-bottom: 200px;
  /* 提供足够的空间来防止按钮遮挡内容 */
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
}

.ellipsis {
  width: 100%;
  /* 确保宽度满足需求 */
  white-space: nowrap;
  /* 防止文本换行 */
  overflow: hidden;
  /* 隐藏超出的内容 */
  text-overflow: ellipsis;
  /* 用省略号显示超出的内容 */
}

.selected-course-type {
  box-shadow: inset 0 3px 5px rgba(0, 0, 0, 0.1);
  /* 内阴影产生凹陷效果 */
  /* border: 1px solid #aaa; */
  /* 可以添加或调整边框来增强效果 */
}

.unselected-course-type {
  box-shadow: none;
}
</style>