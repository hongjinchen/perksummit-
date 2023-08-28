<template>
  <v-container fluid>
    <v-row justify="center">
      <v-col cols="12" sm="8" md="4">
        <v-card>
          <v-card-title class="headline">登录</v-card-title>
          <v-card-text>
            <v-form ref="form" @submit.prevent="login">
              <v-text-field label="姓名" v-model="email" required :rules="[value => !!value || '必填项']"></v-text-field>
              <v-text-field label="密码" type="password" v-model="password" required
                :rules="[value => !!value || '必填项']"></v-text-field>
              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn type="submit" color="primary" :loading="isLoading" :disabled="isLoading">登录</v-btn>
                <!-- <v-btn text @click="goToRegister">注册新账号</v-btn> -->
                <v-btn text @click="goToResetPassword">忘记密码</v-btn>
                <v-btn text color="red" @click="goBack">返回</v-btn> <!-- 返回按钮 -->
              </v-card-actions>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-dialog v-model="dialog" persistent max-width="300">
      <v-card>
        <v-card-title class="headline">登录失败</v-card-title>
        <v-card-text>请检查您的姓名或密码是否正确</v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="green darken-1" text @click="dialog = false">关闭</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
import http from '../../http-common';
import Cookies from 'js-cookie';

export default {
  data() {
    return {
      email: '',
      password: '',
      dialog: false,
      isLoading: false, // 新增的加载状态
    };
  },
  methods: {
    async login() {
      this.isLoading = true; // 开始登录，设置isLoading为true
      if (this.$refs.form.validate()) {
        try {
          let response = await http.post('/login', {
            email: this.email,
            password: this.password,
          });
          if (response.data.status === 'success') {
            // 保存令牌到cookie
            Cookies.set('token', response.data.token);
            // 保存用户ID到cookie
            Cookies.set('user_id', response.data.user_id);
            // 保存is_admin状态到cookie
            Cookies.set('is_admin', response.data.is_admin);

            // 设置请求头
            http.defaults.headers.common['Authorization'] = `Bearer ${response.data.token}`;

            // 根据is_admin状态跳转到不同的页面
            if (response.data.is_admin) {
              this.$router.push('/admin');
            } else {
              this.$router.push('/');
            }
          } else {
            this.dialog = true;
          }
        } catch (error) {
          console.error('There has been a problem with your fetch operation:', error);
          alert('当前网络不稳定或服务器响应时间过长，请稍后再试！');
          this.dialog = true;
        } finally {
          this.isLoading = false; // 完成登录，设置isLoading为false
        }
      } else {
        this.isLoading = false; // 表单验证失败，设置isLoading为false
      }
    },

    goToRegister() {
      this.$router.push('/register');
    },
    goBack() {
      this.$router.push('/');
    },
    goToResetPassword() {
      this.$router.push('/reset-password');
    }
  }
}
</script>
