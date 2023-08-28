<template>
  <v-container fluid>
    <v-row justify="center">
      <v-col cols="12" sm="8" md="4">
        <v-card>
          <v-card-title class="headline">注册新的用户</v-card-title>
          <v-card-text>
            <v-form ref="form" @submit.prevent="register">
              <v-text-field label="姓名" v-model="email" required :rules="[value => !!value || '必填项']"></v-text-field>
              <v-text-field label="密码" type="password" v-model="password" required
                :rules="[value => !!value || '必填项']"></v-text-field>
              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn color="primary" @click="goBack">返回</v-btn>
                <v-btn type="submit" color="primary">注册</v-btn>
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
      password: ''
    }
  },
  methods: {
    goBack() {
      this.$router.go(-1);  // 返回上一页
    },
    async register() {
      if (this.$refs.form.validate()) {
        try {
          const response = await http.post('/register', {
            password: this.password,
            email: this.email
          });

          if (response.data.status === 'error') {
            if (response.data.message === 'Email already in use. Please use a different email.') {
              alert('名字已被使用。请使用其他名字注册。');
            } else {
              alert(response.data.message);
            }
          } else {
            alert('注册成功!');
            window.location.reload();
          }
        } catch (error) {
          console.error(error);
        }
      }
    }


  }
}
</script>
