<!-- src/views/KnowledgeBaseEdit.vue -->
<template>
  <div class="edit-form-container">
    <h2>编辑知识库</h2>
    <!-- 表单：使用 v-model 绑定数据，数据来自 knowledgeBaseForm -->
    <form @submit.prevent="handleSubmit">
      <!-- 1. 知识库名称（对应 name 字段） -->
      <div class="form-item">
        <label>知识库名称：</label>
        <input
          type="text"
          v-model="knowledgeBaseForm.name"
          required
          placeholder="请输入知识库名称"
        />
      </div>

      <!-- 2. 知识库类型（对应 type_id 字段，假设后端返回类型列表） -->
      <div class="form-item">
        <label>知识库类型：</label>
        <select v-model="knowledgeBaseForm.type_id" required>
          <option value="">请选择类型</option>
          <option v-for="type in typeList" :key="type.id" :value="type.id">
            {{ type.name }} <!-- 显示类型名称，提交时传 type_id -->
          </option>
        </select>
      </div>

      <!-- 3. 负责人（对应 master 字段，假设后端返回用户列表） -->
      <div class="form-item">
        <label>负责人：</label>
        <select v-model="knowledgeBaseForm.master" required>
          <option value="">请选择负责人</option>
          <option v-for="user in userList" :key="user.id" :value="user.id">
            {{ user.name }} <!-- 显示用户名，提交时传 master（用户ID） -->
          </option>
        </select>
      </div>

      <!-- 4. 可见范围（对应 limits 字段，枚举：0=公开可编辑，1=私有仅成员编辑） -->
      <div class="form-item">
        <label>可见范围：</label>
        <label>
          <input
            type="radio"
            value="0"
            v-model="knowledgeBaseForm.limits"
          />
          公开可编辑
        </label>
        <label>
          <input
            type="radio"
            value="1"
            v-model="knowledgeBaseForm.limits"
          />
          私有仅成员编辑
        </label>
      </div>

      <!-- 5. 知识库状态（对应 status 字段，枚举：normal=正常，archived=已归档） -->
      <div class="form-item">
        <label>状态：</label>
        <select v-model="knowledgeBaseForm.status" required>
          <option value="normal">正常</option>
          <option value="archived">已归档</option>
        </select>
      </div>

      <!-- 6. 图标URL（对应 icon_url 字段，可选） -->
      <div class="form-item">
        <label>图标URL：</label>
        <input
          type="text"
          v-model="knowledgeBaseForm.icon_url"
          placeholder="请输入图标访问路径（可选）"
        />
      </div>

      <!-- 7. 知识库描述（对应 description 字段，长文本，可选） -->
      <div class="form-item">
        <label>描述：</label>
        <textarea
          v-model="knowledgeBaseForm.description"
          rows="4"
          placeholder="请输入知识库描述（可选）"
        ></textarea>
      </div>

      <!-- 提交按钮 -->
      <button type="submit">保存修改</button>
    </form>
  </div>
</template>

<script setup>
// 1. 引入所需依赖和 API 函数
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router'; // 用于从路由参数中获取知识库 ID
import { getKnowledgeBaseById, updateKnowledgeBase } from './api';

// 2. 定义表单数据（字段与 knowledge_base 表一一对应，初始值为空或默认值）
const knowledgeBaseForm = ref({
  id: '', // 知识库 ID（用于后续修改请求，不显示在表单中）
  name: '', // 知识库名称（非空）
  type_id: '', // 类型 ID（非空）
  master: '', // 负责人 ID（非空）
  limits: 0, // 可见范围（默认公开，枚举 0/1）
  status: 'normal', // 状态（默认正常，枚举 normal/archived）
  icon_url: '', // 图标 URL（可选）
  description: '', // 描述（可选）
  // 归档/回收相关字段（如果不需要编辑，可不在表单中显示）
  archived_time: '',
  archived_user_id: '',
  archived_desc: '',
  recycle: 0,
  recycle_time: '',
  recycle_user_id: ''
});

// 3. 辅助数据（类型列表、用户列表，假设从后端获取，此处简化为模拟数据）
const typeList = ref([
  { id: 1, name: '技术文档' },
  { id: 2, name: '产品手册' },
  { id: 3, name: '运营资料' }
]);
const userList = ref([
  { id: 101, name: '张三' },
  { id: 102, name: '李四' },
  { id: 103, name: '王五' }
]);

// 4. 从路由参数中获取知识库 ID（假设路由配置为 /knowledge-base/edit/:id）
const route = useRoute();
const knowledgeId = route.params.id; // 路由参数中的 ID

// 5. 核心：请求数据并填充到表单
const fetchKnowledgeBaseData = async () => {
  try {
    // 调用 API 函数，传入知识库 ID
    const data = await getKnowledgeBaseById(knowledgeId);
    
    // 将后端返回的数据赋值给表单（自动填充）
    // 注意：后端返回的字段名需与 knowledgeBaseForm 的字段名一致
    knowledgeBaseForm.value = {
      ...knowledgeBaseForm.value, // 保留初始默认值（如未返回的字段）
      ...data // 用后端数据覆盖表单
    };
  } catch (error) {
    console.error('获取知识库数据失败：', error);
  }
};

// 6. 生命周期钩子：组件挂载时触发请求（页面加载即获取数据）
onMounted(() => {
  fetchKnowledgeBaseData();
});

// 7. 表单提交（可选，修改数据后提交到后端）
const handleSubmit = async () => {
  try {
    // 调用修改 API，传入知识库 ID 和表单数据
    await updateKnowledgeBase(knowledgeId, knowledgeBaseForm.value);
    alert('修改成功！');
    // 提交成功后可跳转页面（如返回列表页）
    // router.push('/knowledge-base/list');
  } catch (error) {
    console.error('提交修改失败：', error);
  }
};
</script>

<style scoped>
/* 简单样式，美化表单 */
.edit-form-container {
  width: 600px;
  margin: 20px auto;
  padding: 20px;
  border: 1px solid #eee;
  border-radius: 8px;
}
.form-item {
  margin-bottom: 16px;
}
.form-item label {
  display: inline-block;
  width: 120px;
  margin-right: 8px;
  text-align: right;
}
.form-item input,
.form-item select,
.form-item textarea {
  width: 400px;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}
button {
  margin-left: 128px;
  padding: 8px 24px;
  background: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
button:hover {
  background: #359469;
}
</style>