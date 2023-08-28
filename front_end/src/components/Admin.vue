<template>
    <v-container>
        <v-row>
            <v-col cols="12">
                <v-btn color="primary" :loading="loading" :disabled="loading" @click="exportExcel">导出为Excel</v-btn>
            </v-col>
        </v-row>

        <v-row>
            <v-col cols="12">
                <v-btn text @click="goToRegister">注册新账号</v-btn>
            </v-col>
        </v-row>
        <v-sheet class="mx-auto" max-width="500" style="height: 70vh; overflow-y: auto;">
            <v-card>
                <v-card-title>用户列表</v-card-title>
                <v-list>
                    <v-list-item v-for="(item, index) in users" :key="index" rounded="xl">
                        <v-row no-gutters>
                            <v-col cols="11">
                                <v-list-item-content>
                                    <v-list-item-title>{{ item.email }}</v-list-item-title>
                                </v-list-item-content>
                            </v-col>
                            <v-col cols="1">
                                <v-list-item-action>
                                    <v-icon small color="red" @click="confirmDelete(index)">mdi-delete</v-icon>
                                </v-list-item-action>
                            </v-col>
                        </v-row>
                    </v-list-item>
                </v-list>
            </v-card>
        </v-sheet>


        <v-dialog v-model="dialog" max-width="500px">
            <v-card>
                <v-card-title class="headline">你确定要删除该用户吗？</v-card-title>
                <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn color="green darken-1" text @click="dialog = false">取消</v-btn>
                    <v-btn color="red darken-1" text @click="deleteItem">删除</v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>

    </v-container>
</template>


<script>
import { saveAs } from 'file-saver';
import http from '../../http-common';
import Cookies from 'js-cookie'

export default {
    data() {
        return {
            headers: [
                { text: 'Email', value: 'email' },
                { text: 'Actions', value: 'actions' },
            ],
            courses: [],
            loading: false,
            users: [],
            dialog: false,
            currentItemIndex: null,
        };
    },
    methods: {
        async fetchUsers() {
            this.loading = true;
            const response = await http.get('/api/users');
            this.users = response.data.users;
            this.loading = false;
        },
        confirmDelete(index) {
            this.currentItemIndex = index;
            this.dialog = true;
        },
        async deleteItem() {
            const item = this.users[this.currentItemIndex];
            this.users.splice(this.currentItemIndex, 1);
            await http.delete(`/api/users/${item.id}`);
            this.dialog = false;
        },
        async fetchCourses() {
            const response = await http.get('/api/courses');
            this.courses = response.data;
        },
        async exportExcel() {
            this.loading = true;
            try {
                const response = await http.get('/api/export-courses', { responseType: 'blob' });
                const blob = new Blob([response.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
                saveAs(blob, 'courses.xlsx');
            } catch (error) {
                console.error('An error occurred:', error);
            } finally {
                this.loading = false;
            }
        },

        goToRegister() {
            this.$router.push('/register');
        },
    },
    created() {
        const userId = Cookies.get('user_id')
        if (!userId) {
            this.$router.push('/login');
            return
        }
        this.fetchCourses();
        this.fetchUsers();
    },
};
</script>

