<template>
    <v-container fluid>
      <v-row justify="center">
        <v-col cols="12" sm="8" md="4">
          <v-card>
            <v-card-title class="headline">重设密码</v-card-title>
            <v-card-text>
              <v-form @submit.prevent="resetPassword">
                <v-text-field label="姓名" v-model="email" required></v-text-field>
                <v-text-field label="新密码" type="password" v-model="newPassword" required></v-text-field>
                <v-card-actions>
                  <v-spacer></v-spacer>
                  <v-btn type="submit" color="primary">重设密码</v-btn>
                  <v-btn text @click="goBack">返回</v-btn>
                </v-card-actions>
              </v-form>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </template>
  
  <script>
  import http from '../../http-common';
  
  export default {
    data() {
      return {
        email: '',
        newPassword: ''
      };
    },
    methods: {
      async resetPassword() {
        try {
          const response = await http.post('/resetpassword', {
            email: this.email,
            password: this.newPassword,
          });
  
          if (response.data.status === 'success') {
            // 密码重置成功，可以跳转到登录页面或者显示一个成功的消息
            this.$router.push('/login');
          } else {
            // 密码重置失败，显示错误消息
            this.error = response.data.message;
          }
        } catch (error) {
          // 请求失败，可能是网络问题或者服务器错误
          console.error('There has been a problem with your fetch operation:', error);
          alert(error);
        }
      },
      goBack() {
        this.$router.go(-1);
      }
    }
  }
  </script>
  