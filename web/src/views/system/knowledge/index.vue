<template>
  <div class="knowledge-detail-container">
    <!-- 1. 顶部导航栏（用户信息 + 退出按钮） -->
    <el-header class="top-header">
      <div class="user-info">
        <span class="greeting">您好, {{ userInfo.name }}</span>
        <el-button
          type="text"
          class="logout-btn"
          @click="handleLogout"
        >
          退出
        </el-button>
      </div>
    </el-header>

    <!-- 2. 知识库基础信息栏（名称 + 收藏/分享 + 时间） -->
    <div class="repo-header">
      <div class="repo-name-bar">
        <h1 class="repo-name">{{ repoInfo.name }}</h1>
        <div class="repo-actions">
          <!-- 收藏按钮（切换图标） -->
          <el-button
            type="text"
            class="collect-btn"
            @click="handleToggleCollect"
          >
            <i
              :class="repoInfo.isCollected ? 'el-icon-star-on' : 'el-icon-star-off'"
              class="collect-icon"
            ></i>
            收藏
          </el-button>
          <!-- 分享按钮 -->
          <el-button
            type="text"
            class="share-btn"
            @click="handleShare"
          >
            <i class="el-icon-share"></i>
            分享
          </el-button>
        </div>
      </div>
      <!-- 知识库更新时间 -->
      <div class="repo-time">{{ repoInfo.createTime }}</div>
    </div>

    <!-- 3. 主体内容区（左侧目录 + 中间文档/消息 + 右侧统计/设置） -->
    <div class="main-content">
      <!-- 左侧：目录区域 -->
      <el-aside class="doc-catalog" width="260px">
        <div class="catalog-header">
          <h2>目录</h2>
          <div class="catalog-actions">
            <el-button type="text" size="small" @click="handleAddDoc">添加</el-button>
            <el-button type="text" size="small" @click="handleUploadDoc">上传</el-button>
          </div>
        </div>
        <!-- 目录列表 -->
        <el-menu class="catalog-menu" default-active="0">
          <el-menu-item
            v-for="(doc, index) in docList"
            :key="doc.id"
            :index="index.toString()"
            @click="handleOpenDoc(doc.id)"
          >
            <span class="doc-type-tag" :title="doc.docType">
              {{ doc.docType || '文档' }}
            </span>
            <span class="doc-title">{{ doc.title }}</span>
          </el-menu-item>
        </el-menu>
        <!-- 权限申请入口 -->
        <el-button
          type="text"
          class="permission-btn"
          @click="handlePermissionApply"
        >
          权限申请列
        </el-button>
      </el-aside>

      <!-- 中间：最新文档/消息区域 -->
      <el-main class="doc-message-area">
        <div class="message-header">
          <h2>最新文档</h2>
          <el-button
            type="text"
            class="mark-all-read-btn"
            @click="handleMarkAllRead"
          >
            全部已读
          </el-button>
        </div>
        <!-- 消息列表 -->
        <div class="message-list">
          <el-card
            v-for="(msg, index) in messageList"
            :key="msg.id"
            class="message-card"
            :class="{ 'unread-card': msg.readStatus === 'unread' }"
          >
            <div class="message-index">{{ index + 1 }}</div>
            <div class="message-content">
              <p class="content-text">{{ msg.content }}</p>
              <p class="content-time">{{ msg.createTime }}</p>
            </div>
          </el-card>
          <!-- 无消息提示 -->
          <div class="no-message" v-if="messageList.length === 0">
            暂无最新消息
          </div>
        </div>

        <!-- 文档内容预览区域（默认显示第一个文档） -->
        <div class="doc-preview" v-if="activeDoc">
          <h3 class="preview-title">{{ activeDoc.title }}</h3>
          <div class="preview-content">{{ activeDoc.content }}</div>
        </div>
      </el-main>

      <!-- 右侧：统计/设置入口 -->
      <el-aside class="stats-setting" width="200px">
        <el-menu class="side-menu" default-active="stats">
          <el-menu-item index="stats" @click="handleShowStats">
            <i class="el-icon-data-analysis"></i>
            <span>统计</span>
          </el-menu-item>
          <el-menu-item index="setting" @click="handleShowSetting">
            <i class="el-icon-setting"></i>
            <span>设置</span>
          </el-menu-item>
        </el-menu>

        <!-- 统计数据展示（默认显示） -->
        <div class="stats-content" v-if="showStats">
          <el-statistic
            v-for="(stat, key) in statsData"
            :key="key"
            :label="getStatLabel(key)"
            :value="stat"
            class="stat-item"
          />
        </div>

        <!-- 设置面板（点击“设置”显示） -->
        <div class="setting-content" v-if="showSetting">
          <el-form :model="settingForm" label-width="80px">
            <el-form-item label="知识库名称">
              <el-input v-model="settingForm.repoName" />
            </el-form-item>
            <el-form-item label="是否公开">
              <el-switch v-model="settingForm.isPublic" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleSaveSetting">保存</el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-aside>
    </div>

    <!-- 4. 底部返回首页按钮 -->
    <el-footer class="bottom-footer">
      <el-button
        type="primary"
        @click="handleBackHome"
      >
        返回首页
      </el-button>
    </el-footer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage, ElMessageBox, ElNotification } from 'element-plus';
import { knowledgeDetailApi } from './api';
import {
  UserInfo,
  KnowledgeRepo,
  DocItem,
  MessageItem,
  KnowledgeStats
} from './types';

// 路由与导航
const route = useRoute();
const router = useRouter();
const repoId = route.params.repoId; // 从路由获取知识库ID（需在路由配置中定义）

// 页面状态
const userInfo = ref<UserInfo>({ name: '' }); // 用户信息
const repoInfo = ref<KnowledgeRepo>({
  id: '',
  name: '',
  createTime: '',
  isCollected: false
}); // 知识库基础信息
const docList = ref<DocItem[]>([]); // 目录文档列表
const messageList = ref<MessageItem[]>([]); // 最新消息列表
const statsData = ref<KnowledgeStats>({
  docTotal: 0,
  unreadDocCount: 0,
  messageTotal: 0,
  lastUpdateTime: ''
}); // 统计数据
const activeDoc = ref<DocItem | null>(null); // 当前打开的文档
const showStats = ref(true); // 是否显示统计（默认true）
const showSetting = ref(false); // 是否显示设置（默认false）

// 设置表单数据
const settingForm = reactive({
  repoName: '',
  isPublic: true
});

// 页面加载时初始化数据
onMounted(async () => {
  await Promise.all([
    fetchUserInfo(),
    fetchRepoInfo(),
    fetchDocList(),
    fetchLatestMessages(),
    fetchStatsData()
  ]);
  // 默认打开第一个文档
  if (docList.value.length > 0) {
    activeDoc.value = docList.value[0];
  }
  // 初始化设置表单
  settingForm.repoName = repoInfo.value.name;
});

// -------------------------- 接口请求函数 --------------------------
/** 获取用户信息 */
const fetchUserInfo = async () => {
  try {
    const res = await knowledgeDetailApi.getUserInfo();
    userInfo.value = res.data;
  } catch (err) {
    console.error('获取用户信息失败:', err);
    ElMessage.error('获取用户信息失败，请刷新重试');
  }
};

/** 获取知识库基础信息 */
const fetchRepoInfo = async () => {
  try {
    const res = await knowledgeDetailApi.getKnowledgeRepo(repoId);
    repoInfo.value = res.data;
  } catch (err) {
    console.error('获取知识库信息失败:', err);
    ElMessage.error('获取知识库信息失败，请刷新重试');
  }
};

/** 获取目录文档列表 */
const fetchDocList = async () => {
  try {
    const res = await knowledgeDetailApi.getKnowledgeDocs(repoId);
    docList.value = res.data;
  } catch (err) {
    console.error('获取文档列表失败:', err);
    ElMessage.error('获取文档列表失败，请刷新重试');
  }
};

/** 获取最新消息 */
const fetchLatestMessages = async () => {
  try {
    const res = await knowledgeDetailApi.getLatestMessages(repoId);
    messageList.value = res.data.list;
  } catch (err) {
    console.error('获取最新消息失败:', err);
    ElMessage.error('获取最新消息失败，请刷新重试');
  }
};

/** 获取统计数据 */
const fetchStatsData = async () => {
  try {
    const res = await knowledgeDetailApi.getKnowledgeStats(repoId);
    statsData.value = res.data;
  } catch (err) {
    console.error('获取统计数据失败:', err);
    ElMessage.error('获取统计数据失败，请刷新重试');
  }
};

// -------------------------- 交互逻辑函数 --------------------------
/** 退出登录 */
const handleLogout = async () => {
  const confirm = await ElMessageBox.confirm(
    '确定要退出登录吗？',
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).catch(() => false);

  if (confirm) {
    // 调用退出接口（假设项目有统一退出逻辑）
    localStorage.removeItem('token');
    router.push('/login');
    ElMessage.success('退出成功');
  }
};

/** 切换收藏状态 */
const handleToggleCollect = async () => {
  try {
    const res = await knowledgeDetailApi.toggleCollect(
      repoId,
      repoInfo.value.isCollected
    );
    repoInfo.value.isCollected = res.data.isCollected;
    ElMessage.success(
      res.data.isCollected ? '收藏成功' : '取消收藏成功'
    );
  } catch (err) {
    console.error('切换收藏状态失败:', err);
    ElMessage.error('操作失败，请重试');
  }
};

/** 分享知识库（示例：打开分享弹窗） */
const handleShare = () => {
  ElMessageBox.prompt(
    '复制以下链接分享给他人：',
    '分享知识库',
    {
      confirmButtonText: '复制',
      cancelButtonText: '取消',
      inputValue: `${window.location.origin}/knowledge/${repoId}`,
      inputReadOnly: true
    }
  ).then(() => {
    // 复制到剪贴板（需引入clipboard.js或使用浏览器API）
    navigator.clipboard.writeText(`${window.location.origin}/knowledge/${repoId}`);
    ElMessage.success('链接已复制到剪贴板');
  });
};

/** 添加文档（跳转新增文档页） */
const handleAddDoc = () => {
  router.push(`/knowledge/${repoId}/doc/add`);
};

/** 上传文档（打开上传弹窗） */
const handleUploadDoc = () => {
  ElNotification.info({
    title: '提示',
    message: '请选择要上传的文档（支持MarkDown、Word、Excel格式）',
    duration: 3000
  });
  // 此处可集成Element Plus的Upload组件实现上传逻辑
};

/** 打开文档（更新当前活跃文档） */
const handleOpenDoc = (docId: string | number) => {
  const doc = docList.value.find(item => item.id === docId);
  if (doc) {
    activeDoc.value = doc;
    // 标记文档为已读（如果未读）
    if (doc.isRead === false) {
      doc.isRead = true;
      // 可调用接口更新已读状态（此处省略）
    }
  }
};

/** 标记所有消息为已读 */
const handleMarkAllRead = async () => {
  try {
    await knowledgeDetailApi.markAllRead(repoId);
    messageList.value.forEach(msg => {
      msg.readStatus = 'read';
    });
    ElMessage.success('所有消息已标记为已读');
  } catch (err) {
    console.error('标记已读失败:', err);
    ElMessage.error('操作失败，请重试');
  }
};

/** 显示统计面板 */
const handleShowStats = () => {
  showStats.value = true;
  showSetting.value = false;
};

/** 显示设置面板 */
const handleShowSetting = () => {
  showStats.value = false;
  showSetting.value = true;
  // 初始化设置表单（同步当前知识库名称）
  settingForm.repoName = repoInfo.value.name;
};

/** 保存设置 */
const handleSaveSetting = async () => {
  try {
    // 调用保存设置接口（此处省略，实际需传repoId和表单数据）
    repoInfo.value.name = settingForm.repoName;
    ElMessage.success('设置保存成功');
    handleShowStats(); // 保存后切回统计面板
  } catch (err) {
    console.error('保存设置失败:', err);
    ElMessage.error('保存失败，请重试');
  }
};

/** 返回首页 */
const handleBackHome = () => {
  router.push('/');
};

/** 统计标签映射（将statsData的key转为中文标签） */
const getStatLabel = (key: keyof KnowledgeStats) => {
  const labelMap = {
    docTotal: '文档总数',
    unreadDocCount: '未读文档数',
    messageTotal: '消息总数',
    lastUpdateTime: '最后更新时间'
  };
  return labelMap[key] || key;
};

// 监听repoId变化（如果路由参数更新，重新加载数据）
watch(
  () => route.params.repoId,
  (newId) => {
    if (newId && newId !== repoId) {
      window.location.reload(); // 简单处理：刷新页面重新加载数据
    }
  }
);
</script>

<style scoped>
/* 页面整体样式 */
.knowledge-detail-container {
  width: 100%;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
}

/* 顶部导航栏 */
.top-header {
  background-color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  padding: 0 20px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
}
.user-info {
  display: flex;
  align-items: center;
  gap: 20px;
}
.greeting {
  font-size: 14px;
  color: #333;
}
.logout-btn {
  color: #666;
}
.logout-btn:hover {
  color: #409eff;
}

/* 知识库信息栏 */
.repo-header {
  background-color: #fff;
  padding: 20px 30px;
  margin: 10px 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}
.repo-name-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}
.repo-name {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin: 0;
}
.repo-actions {
  display: flex;
  gap: 20px;
}
.collect-btn, .share-btn {
  color: #666;
  font-size: 14px;
}
.collect-btn:hover, .share-btn:hover {
  color: #409eff;
}
.collect-icon {
  margin-right: 4px;
}
.repo-time {
  font-size: 12px;
  color: #999;
}

/* 主体内容区 */
.main-content {
  display: flex;
  flex: 1;
  padding: 0 20px 20px;
  gap: 20px;
}

/* 左侧目录区域 */
.doc-catalog {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  padding: 15px;
}
.catalog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}
.catalog-header h2 {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0;
}
.catalog-actions {
  display: flex;
  gap: 10px;
}
.catalog-actions .el-button {
  font-size: 12px;
  padding: 0;
  color: #666;
}
.catalog-menu {
  border-right: none;
}
.catalog-menu .el-menu-item {
  height: 40px;
  line-height: 40px;
  font-size: 13px;
  padding-left: 10px !important;
}
.doc-type-tag {
  display: inline-block;
  padding: 2px 6px;
  background-color: #f0f7ff;
  color: #409eff;
  font-size: 10px;
  border-radius: 4px;
  margin-right: 8px;
}
.doc-title {
  color: #666;
}
.catalog-menu .el-menu-item.is-active .doc-title {
  color: #409eff;
  font-weight: 500;
}
.permission-btn {
  width: 100%;
  margin-top: 15px;
  color: #409eff;
  font-size: 13px;
}

/* 中间文档/消息区域 */
.doc-message-area {
  flex: 1;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  padding: 20px;
}
.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.message-header h2 {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0;
}
.mark-all-read-btn {
  color: #409eff;
  font-size: 13px;
}
.message-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 30px;
}
.message-card {
  border: none;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  padding: 15px;
  display: flex;
  align-items: flex-start;
  gap: 10px;
}
.unread-card {
  border-left: 3px solid #409eff;
}
.message-index {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background-color: #f0f7ff;
  color: #409eff;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.message-content {
  flex: 1;
}
.content-text {
  font-size: 13px;
  color: #333;
  margin: 0 0 5px;
  line-height: 1.5;
}
.content-time {
  font-size: 11px;
  color: #999;
  margin: 0;
}
.no-message {
  text-align: center;
  color: #999;
  font-size: 13px;
  padding: 30px 0;
}
.doc-preview {
  padding: 20px;
  border-top: 1px solid #f0f0f0;
}
.preview-title {
  font-size: 16px;
  color: #333;
  margin: 0 0 15px;
}
.preview-content {
  font-size: 14px;
  color: #666;
  line-height: 1.8;
  white-space: pre-line; /* 保留换行符 */
}

/* 右侧统计/设置区域 */
.stats-setting {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  padding: 15px;
}
.side-menu {
  border-right: none;
  margin-bottom: 20px;
}
.side-menu .el-menu-item {
  height: 45px;
  line-height: 45px;
  font-size: 14px;
  padding-left: 10px !important;
}
.stats-content {
  display: flex;
  flex-direction: column;
  gap: 15px;
}
.stat-item {
  font-size: 13px;
}
.stat-item .el-statistic__label {
  color: #999;
  margin-bottom: 5px;
}
.stat-item .el-statistic__value {
  color: #333;
  font-size: 16px;
}
.setting-content {
  padding: 10px 0;
}
.setting-content .el-form-item {
  margin-bottom: 15px;
}
.setting-content .el-input {
  width: 100%;
}

/* 底部返回首页按钮 */
.bottom-footer {
  padding: 20px;
  display: flex;
  justify-content: center;
}
.bottom-footer .el-button {
  padding: 8px 24px;
}
</style>