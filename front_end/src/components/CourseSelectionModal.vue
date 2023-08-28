<template>
    <v-dialog v-model="dialogVal" max-width="500">
      <v-card>
        <v-card-title>
          <span class="text-h5">选择课程</span>
        </v-card-title>
  
        <v-card-text>
          <v-checkbox
            v-for="course in courses"
            :key="course.id"
            v-model="course.selected"
            :label="course.name"
          ></v-checkbox>
        </v-card-text>
  
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="blue darken-1" text @click="dialogVal = false">关闭</v-btn>
          <v-btn color="blue darken-1" text @click="confirm">确定</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </template>
  
  <script setup>
  import { ref, watchEffect } from 'vue';
  
  const props = defineProps({
    modelValue: Boolean,
    courses: Array
  });
  
  const emit = defineEmits(['update:modelValue', 'confirm']);
  
  let dialogVal = ref(props.modelValue);
  
  watchEffect(() => {
    dialogVal.value = props.modelValue;
  });
  
  watchEffect(() => {
    emit('update:modelValue', dialogVal.value);
  });
  
  const confirm = () => {
    let selectedCourses = props.courses.filter(course => course.selected);
    if (selectedCourses.length > 5) {
      // 这里可以添加一个提示，说明最多只能选择5门课程
      return;
    }
    emit('confirm', selectedCourses);
  };
  
  </script>
  