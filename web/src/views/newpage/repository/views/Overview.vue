hello
<!--<template>-->
<!--  <div class="kb-overview-container">-->
<!--    &lt;!&ndash; 页面标题（带返回按钮） &ndash;&gt;-->
<!--    <div class="page-header">-->
<!--      <el-button-->
<!--        type="text"-->
<!--        icon="el-icon-arrow-left"-->
<!--        @click="handleGoBack"-->
<!--        class="back-btn"-->
<!--      >-->
<!--        返回知识库列表-->
<!--      </el-button>-->
<!--      <el-page-header :content="`${kbData.name || '知识库详情'}`" />-->
<!--    </div>-->

<!--    &lt;!&ndash; 加载状态 &ndash;&gt;-->
<!--    <el-skeleton-->
<!--      v-if="loading"-->
<!--      :count="6"-->
<!--      :rows="3"-->
<!--      style="width: 100%; margin-top: 20px;"-->
<!--    />-->

<!--    &lt;!&ndash; 错误提示 &ndash;&gt;-->
<!--    <el-empty-->
<!--      v-else-if="errorMsg"-->
<!--      description="获取知识库数据失败"-->
<!--      style="margin-top: 40px;"-->
<!--    >-->
<!--      <el-button type="primary" @click="fetchKbData">重试</el-button>-->
<!--    </el-empty>-->

<!--    &lt;!&ndash; 知识库详情内容（数据加载成功后显示） &ndash;&gt;-->
<!--    <div v-else class="kb-detail-content">-->
<!--      &lt;!&ndash; 1. 基础信息卡片 &ndash;&gt;-->
<!--      <el-card shadow="hover" class="base-info-card">-->
<!--        <div class="card-header">基础信息</div>-->
<!--        <div class="info-grid">-->
<!--          <div class="info-item">-->
<!--            <span class="info-label">知识库ID：</span>-->
<!--            <span class="info-value">{{ kbData.id }}</span>-->
<!--          </div>-->
<!--          <div class="info-item">-->
<!--            <span class="info-label">负责人：</span>-->
<!--            <span class="info-value">{{ kbData.masterName }}</span>-->
<!--          </div>-->
<!--          <div class="info-item">-->
<!--            <span class="info-label">创建时间：</span>-->
<!--            <span class="info-value">{{ kbData.createTime }}</span>-->
<!--          </div>-->
<!--          <div class="info-item">-->
<!--            <span class="info-label">当前状态：</span>-->
<!--            <el-tag :type="kbData.status === 'normal' ? 'success' : 'warning'">-->
<!--              {{ kbData.statusLabel }}-->
<!--            </el-tag>-->
<!--          </div>-->
<!--        </div>-->
<!--      </el-card>-->

<!--      &lt;!&ndash; 2. 描述信息 &ndash;&gt;-->
<!--      <el-card shadow="hover" class="desc-card" style="margin-top: 20px;">-->
<!--        <div class="card-header">知识库描述</div>-->
<!--        <div class="desc-content">-->
<!--          {{ kbData.description || '暂无描述' }}-->
<!--        </div>-->
<!--      </el-card>-->

<!--      &lt;!&ndash; 3. 统计数据卡片 &ndash;&gt;-->
<!--      <div class="stats-cards" style="margin-top: 20px; display: flex; gap: 20px;">-->
<!--        <el-card shadow="hover" class="stat-card">-->
<!--          <div class="stat-label">文档总数</div>-->
<!--          <div class="stat-value">{{ kbData.docCount }}</div>-->
<!--        </el-card>-->
<!--        <el-card shadow="hover" class="stat-card">-->
<!--          <div class="stat-label">总访问量</div>-->
<!--          <div class="stat-value">{{ kbData.viewCount }}</div>-->
<!--        </el-card>-->
<!--      </div>-->
<!--    </div>-->
<!--  </div>-->
<!--</template>-->

<!--<script setup lang="ts">-->
<!--import { ref, onMounted } from 'vue';-->
<!--import { useRoute, useRouter } from 'vue-router';-->
<!--import { ElMessage } from 'element-plus';-->
<!--// 导入知识库接口（需根据项目实际路径调整）-->
<!--import { getKnowledgeBaseDetail } from '/@/views/system/repository/views/api';-->

<!--// 1. 路由相关：获取当前知识库ID、控制页面跳转-->
<!--const route = useRoute();-->
<!--const router = useRouter();-->
<!--// 从路由动态参数中获取 kbId（对应路由配置的 /knowledgeEdit/:kbId/overview）-->
<!--const kbId = route.params.kbId as string;-->

<!--// 2. 状态管理：加载中、错误信息、知识库数据-->
<!--const loading = ref<boolean>(true); // 加载状态（初始为true，显示骨架屏）-->
<!--const errorMsg = ref<string>(''); // 错误信息（非空时显示错误提示）-->
<!--// 知识库数据结构（与接口响应的 data 字段对齐）-->
<!--const kbData = ref<{-->
<!--  id: string;-->
<!--  name: string;-->
<!--  description: string;-->
<!--  createTime: string;-->
<!--  masterName: string;-->
<!--  docCount: number;-->
<!--  viewCount: number;-->
<!--  status: 'normal' | 'archived';-->
<!--  statusLabel: string;-->
<!--}>({-->
<!--  id: '',-->
<!--  name: '',-->
<!--  description: '',-->
<!--  createTime: '',-->
<!--  masterName: '',-->
<!--  docCount: 0,-->
<!--  viewCount: 0,-->
<!--  status: 'normal',-->
<!--  statusLabel: '正常'-->
<!--});-->

<!--// 3. 核心方法：获取知识库详情数据-->
<!--const fetchKbData = async () => {-->
<!--  try {-->
<!--    // 重置状态：开始加载-->
<!--    loading.value = true;-->
<!--    errorMsg.value = '';-->

<!--    // 调用真实接口：传入 kbId 获取数据-->
<!--    const response = await getKnowledgeBaseDetail(kbId);-->

<!--    // 接口成功（根据后端约定的 code 判断）-->
<!--    if (response.code === 2000) {-->
<!--      kbData.value = response.data; // 将接口返回的数据赋值给 kbData-->
<!--    } else {-->
<!--      // 接口返回错误（如“知识库不存在”）-->
<!--      errorMsg.value = response.msg || '获取知识库数据失败';-->
<!--      ElMessage.error(errorMsg.value);-->
<!--    }-->
<!--  } catch (err) {-->
<!--    // 网络错误（如接口不可达、断网）-->
<!--    errorMsg.value = '网络异常，请检查网络连接';-->
<!--    console.error('获取知识库详情失败：', err);-->
<!--    ElMessage.error(errorMsg.value);-->
<!--  } finally {-->
<!--    // 结束加载（无论成功/失败，都隐藏骨架屏）-->
<!--    loading.value = false;-->
<!--  }-->
<!--};-->

<!--// 4. 页面挂载时自动加载数据-->
<!--onMounted(() => {-->
<!--  // 验证 kbId 是否存在（防止非法访问）-->
<!--  if (kbId || kbId === 'undefined' || kbId === 'null') {-->
<!--    ElMessage.warning('无效的知识库ID');-->
<!--    router.push('/knowledge_edit'); // 跳回知识库列表页-->
<!--    return;-->
<!--  }-->
<!--  // 加载知识库数据-->
<!--  fetchKbData();-->
<!--});-->

<!--// 5. 辅助方法：返回知识库列表页-->
<!--const handleGoBack = () => {-->
<!--  router.push('/knowledge_edit');-->
<!--};-->
<!--</script>-->

<!--<style scoped>-->
<!--.kb-overview-container {-->
<!--  padding: 20px;-->
<!--}-->

<!--.page-header {-->
<!--  display: flex;-->
<!--  align-items: center;-->
<!--  gap: 16px;-->
<!--  margin-bottom: 20px;-->
<!--}-->

<!--.back-btn {-->
<!--  color: #666;-->
<!--}-->

<!--.base-info-card, .desc-card {-->
<!--  width: 100%;-->
<!--}-->

<!--.card-header {-->
<!--  font-size: 16px;-->
<!--  font-weight: 500;-->
<!--  color: #1d2129;-->
<!--  margin-bottom: 16px;-->
<!--}-->

<!--.info-grid {-->
<!--  display: grid;-->
<!--  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));-->
<!--  gap: 16px;-->
<!--}-->

<!--.info-item {-->
<!--  display: flex;-->
<!--  align-items: center;-->
<!--  gap: 8px;-->
<!--}-->

<!--.info-label {-->
<!--  color: #86909c;-->
<!--  font-size: 14px;-->
<!--  width: 100px;-->
<!--}-->

<!--.info-value {-->
<!--  color: #1d2129;-->
<!--  font-size: 14px;-->
<!--}-->

<!--.desc-content {-->
<!--  color: #4e5969;-->
<!--  font-size: 14px;-->
<!--  line-height: 1.6;-->
<!--  white-space: pre-wrap; /* 保留换行符，优化描述显示 */-->
<!--}-->

<!--.stat-card {-->
<!--  flex: 1;-->
<!--  min-width: 200px;-->
<!--  text-align: center;-->
<!--  padding: 20px 0;-->
<!--}-->

<!--.stat-label {-->
<!--  color: #86909c;-->
<!--  font-size: 14px;-->
<!--  margin-bottom: 8px;-->
<!--}-->

<!--.stat-value {-->
<!--  color: #1d2129;-->
<!--  font-size: 24px;-->
<!--  font-weight: 500;-->
<!--}-->
<!--</style>-->