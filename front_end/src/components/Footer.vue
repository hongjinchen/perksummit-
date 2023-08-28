<template>
    <div class="footer">
      © 2023 破壳文化交流中心.
      <a href="https://beian.miit.gov.cn/" target="_blank">备案号: </a>
      <a href="https://beian.miit.gov.cn/" target="_blank">渝ICP备2023007467号</a>
    </div>
  </template>
  
  <script>
  export default {
    name: 'Footer',
  }
  </script>
  
  <style scoped>
  .footer {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    background-color: #f8f9fa;
    color: #212529;
    text-align: center;
    padding: 10px 0;
  }
  .footer a {
    color: #212529;
    text-decoration: none;
  }
  </style>
  