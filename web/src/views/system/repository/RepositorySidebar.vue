<!--设计 “单个知识库系统” 的专属菜单栏-->
<template>
  <aside class="knowledge-sidebar">
    <!-- 知识库标题（动态显示当前知识库名称） -->
    <div class="kb-header">
      <h2>{{ currentKbName }}</h2>
      <span class="kb-id">ID: {{ kbId }}</span>
    </div>

    <!-- 知识库系统专属菜单 -->
    <ul class="kb-menu">
      <li :class="{ active: $route.path.endsWith('overview') }">
        <router-link :to="`/repository/${kbId}/overview`">
          <i class="iconfont icon-gailan"></i>
          <span>概述</span>
        </router-link>
      </li>
      <li :class="{ active: $route.path.endsWith('docs') }">
        <router-link :to="`/repository/${kbId}/docs`">
          <i class="iconfont icon-wendang"></i>
          <span>文档</span>
        </router-link>
      </li>
      <li :class="{ active: $route.path.endsWith('stats') }">
        <router-link :to="`/repository/${kbId}/stats`">
          <i class="iconfont icon-tongji"></i> <!-- 统计图标 -->
          <span>统计</span>
        </router-link>
      </li>
      <li :class="{ active: $route.path.endsWith('settings') }">
        <router-link :to="`/repository/${kbId}/settings`">
          <i class="iconfont icon-shezhi"></i>
          <span>设置</span>
        </router-link>
      </li>
    </ul>

    <!-- 返回原系统按钮 -->
    <div class="back-btn">
      <router-link to="/knowledge_edit">
<!--        返回原系统，路由要更改一下-->
        <i class="iconfont icon-fanhui"></i>
        <span>返回知识库列表</span>
      </router-link>
    </div>
  </aside>
</template>

<script setup>
import { useRoute } from 'vue-router';
import { ref, onMounted } from 'vue';

const route = useRoute();
const kbId = route.params.kbId; // 获取当前知识库ID
const currentKbName = ref('');

// // 模拟：根据ID获取知识库名称（实际项目中替换为接口请求）
// onMounted(() => {
//   // 示例：调用接口获取名称
//   // fetch(`/api/knowledge-base/${kbId}`).then(res => currentKbName.value = res.name);
//
//   // 临时模拟数据
//   currentKbName.value = `知识库${kbId}`;
// });

// 实际开发，后端接口请求
onMounted(async () => {
  try {
    const res = await repositoryApi.getRepoDetail(kbId); // 调用知识库详情API
    if (res.code === 2000) {
      currentKbName.value = res.data.name; // 赋值真实知识库名称
    } else {
      ElMessage.error('获取知识库名称失败'); // 错误提示
    }
  } catch (err) {
    console.error('接口请求错误:', err);
    ElMessage.error('网络异常');
  }
});
</script>

<style scoped>
.knowledge-sidebar {
  width: 220px;
  height: 100vh;
  background: #f5f7fa;
  border-right: 1px solid #e5e6eb;
  padding: 20px 0;
  box-sizing: border-box;
}

.kb-header {
  padding: 0 20px 20px;
  border-bottom: 1px solid #e5e6eb;
  margin-bottom: 20px;
}

.kb-header h2 {
  margin: 0 0 5px;
  font-size: 16px;
  color: #1d2129;
}

.kb-id {
  font-size: 12px;
  color: #86909c;
}

.kb-menu {
  list-style: none;
  padding: 0;
  margin: 0;
}

.kb-menu li {
  margin: 0;
}

.kb-menu a {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  color: #4e5969;
  text-decoration: none;
  font-size: 14px;
  transition: all 0.3s;
}

.kb-menu a:hover, .kb-menu li.active a {
  background: #e8f3ff;
  color: #1890ff;
}

.kb-menu i {
  margin-right: 10px;
  font-size: 16px;
}

.back-btn {
  margin-top: 20px;
  padding: 0 20px;
}

.back-btn a {
  display: flex;
  align-items: center;
  color: #86909c;
  text-decoration: none;
  font-size: 14px;
  padding: 8px 0;
}

.back-btn i {
  margin-right: 5px;
}
</style>