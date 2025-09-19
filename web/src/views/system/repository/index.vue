<template>
       <div class="task-app">
         <!-- 页面标题 -->
         <h1>我的任务清单</h1>
     
         <!-- 任务添加区域 -->
         <div class="task-add">
           <input
             type="text"
             v-model="newTask"  
             placeholder="请输入新任务..."
             @keyup.enter="addTask" 
           >
           <button @click="addTask">添加任务</button>  <!-- 点击按钮触发添加任务 -->
         </div>
     
         <!-- 任务列表区域 -->
         <div class="task-list" v-if="tasks.length">  <!-- 条件渲染：有任务才显示列表 -->
           <ul>
             <!-- 列表渲染：循环展示 tasks 数组中的每一项 -->
             <li 
               v-for="(task, index) in tasks" 
               :key="index"  
               :class="{ completed: task.done }" 
               @click="toggleTask(index)" 
             >
               <!-- 任务文本 -->
               <span>{{ task.content }}</span>
               <!-- 删除按钮 -->
               <button @click.stop="deleteTask(index)">×</button>  <!-- stop 阻止事件冒泡到 li -->
             </li>
           </ul>
     
           <!-- 清空已完成任务按钮 -->
           <button 
             class="clear-btn" 
             @click="clearCompleted"
             :disabled="!hasCompleted" 
           >
             清空已完成任务
           </button>
         </div>
     
         <!-- 无任务提示 -->
         <div class="empty-tip" v-else>
           暂无任务，快来添加你的第一个任务吧！
         </div>
       </div>
     </template>
     
     <script setup>
     // Vue 3 组合式 API（setup 语法糖）
     import { ref, computed } from 'vue'
     
     // 1. 响应式数据：任务列表（数组）
     const tasks = ref([
       // 初始示例任务
       { content: '学习 Vue 基础', done: false },
       { content: '完成任务清单页面', done: true }
     ])
     
     // 2. 响应式数据：新任务输入框内容
     const newTask = ref('')
     
     // 3. 计算属性：是否有已完成任务（简化模板逻辑）
     const hasCompleted = computed(() => {
       return tasks.value.some(task => task.done)
     })
     
     // 4. 方法：添加任务
     const addTask = () => {
       // 过滤空任务（去除首尾空格后判断）
       const taskContent = newTask.value.trim()
       if (!taskContent) return
     
       // 添加新任务到数组
       tasks.value.push({
         content: taskContent,
         done: false  // 新任务默认未完成
       })
     
       // 清空输入框
       newTask.value = ''
     }
     
     // 5. 方法：切换任务完成状态
     const toggleTask = (index) => {
       tasks.value[index].done = !tasks.value[index].done
     }
     
     // 6. 方法：删除单个任务
     const deleteTask = (index) => {
       tasks.value.splice(index, 1)  // 从数组中删除对应索引的任务
     }
     
     // 7. 方法：清空所有已完成任务
     const clearCompleted = () => {
       tasks.value = tasks.value.filter(task => !task.done)  // 过滤出未完成的任务
     }
     </script>
     
     <style scoped>
     /* scoped：样式仅作用于当前组件，避免污染全局 */
     .task-app {
       max-width: 600px;
       margin: 40px auto;
       padding: 0 20px;
       font-family: 'Arial', sans-serif;
     }
     
     h1 {
       text-align: center;
       color: #333;
     }
     
     .task-add {
       display: flex;
       gap: 10px;
       margin-bottom: 20px;
     }
     
     .task-add input {
       flex: 1;
       padding: 10px;
       border: 1px solid #ddd;
       border-radius: 4px;
       font-size: 16px;
     }
     
     .task-add button, .clear-btn {
       padding: 10px 16px;
       border: none;
       border-radius: 4px;
       background: #42b983;  /* Vue 主题绿 */
       color: white;
       font-size: 16px;
       cursor: pointer;
       transition: background 0.2s;
     }
     
     .task-add button:hover, .clear-btn:hover {
       background: #359469;
     }
     
     .task-list ul {
       list-style: none;
       padding: 0;
       margin: 0 0 20px;
     }
     
     .task-list li {
       display: flex;
       justify-content: space-between;
       align-items: center;
       padding: 12px;
       margin-bottom: 8px;
       border: 1px solid #ddd;
       border-radius: 4px;
       background: #f9f9f9;
       cursor: pointer;
       transition: background 0.2s;
     }
     
     .task-list li:hover {
       background: #f5f5f5;
     }
     
     /* 任务完成样式：文本划线、变灰 */
     .task-list li.completed span {
       text-decoration: line-through;
       color: #888;
     }
     
     .task-list li button {
       border: none;
       background: transparent;
       color: #ff4444;
       font-size: 18px;
       cursor: pointer;
       padding: 4px 8px;
       border-radius: 50%;
       transition: background 0.2s;
     }
     
     .task-list li button:hover {
       background: #ffebee;
     }
     
     .clear-btn {
       background: #ff9800;  /* 橙色：区分添加按钮 */
       width: 100%;
       margin-top: 10px;
     }
     
     .clear-btn:hover {
       background: #e68900;
     }
     
     /* 禁用状态样式 */
     .clear-btn:disabled {
       background: #ccc;
       cursor: not-allowed;
     }
     
     .empty-tip {
       text-align: center;
       color: #888;
       font-size: 16px;
       padding: 20px;
       border: 1px dashed #ddd;
       border-radius: 4px;
     }
     </style>