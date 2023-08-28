<template>
    <div class="empty-state">
      <v-icon class="empty-state__image" x-large>mdi-folder-open-outline</v-icon>
      <p class="empty-state__description">看起来你还没有选择任何课程。开始选择一些课程吧！</p>
    </div>
  </template>
  
  <script>
  export default {
    name: 'EmptyState'
  }
  </script>
  
  <style scoped>
  .empty-state {
    text-align: center;
    padding: 2em 0;
  }
  
  .empty-state__image {
    color: #999;
    margin: 0 auto;
  }
  
  .empty-state__title {
    margin-top: 1em;
    font-size: 1.5em;
  }
  
  .empty-state__description {
    color: #666;
    margin-top: 0.5em;
  }
  </style>
  