<template>
  <div class="doc-list-page">
    <!-- 顶部导航栏 -->
    <div class="top-nav">
      <div class="logo">知识库</div>
      <div class="user-info">
        <span>您好, {{ userName || '用户' }}</span>
        <button class="logout-btn" @click="handleLogout">退出</button>
      </div>
    </div>

    <!-- 页面头部信息 -->
    <div class="page-header">
      <div class="header-left">
        <h1>{{ repoName || '知识库名称' }}</h1>
        <div class="repo-meta">
          <span class="date">{{ currentDate }}</span>
          <span class="divider">|</span>
          <span class="owner">负责人：{{ repoOwner || '张三' }}</span>
        </div>
      </div>
      <div class="header-right">
        <button class="btn-icon" @click="handleCollect">
          <i class="fas fa-star"></i> 收藏
        </button>
        <button class="btn-icon" @click="handleShare">
          <i class="fas fa-share-alt"></i> 分享
        </button>
      </div>
    </div>

    <!-- 左侧导航与右侧内容区 -->
    <div class="main-container">
      <!-- 左侧导航 -->
      <div class="side-nav">
        <button class="nav-item" :class="{ active: currentNav === 'overview' }" @click="currentNav = 'overview'">
          <i class="fas fa-home"></i> 概述
        </button>
        <button class="nav-item active" :class="{ active: currentNav === 'documents' }" @click="currentNav = 'documents'">
          <i class="fas fa-file-alt"></i> 文档
        </button>
        <button class="nav-item" :class="{ active: currentNav === 'statistics' }" @click="currentNav = 'statistics'">
          <i class="fas fa-chart-bar"></i> 统计
        </button>
        <button class="nav-item" :class="{ active: currentNav === 'settings' }" @click="currentNav = 'settings'">
          <i class="fas fa-cog"></i> 设置
        </button>
        <button class="back-home-btn" @click="goToHome">
          <i class="fas fa-chevron-left"></i> 返回首页
        </button>
      </div>

      <!-- 右侧内容区 -->
      <div class="content-area">
        <!-- 操作栏 -->
        <div class="action-bar">
          <div class="search-box">
            <input
              type="text"
              v-model="searchKey"
              placeholder="请输入关键字 标题 搜索"
              @keyup.enter="fetchDocList"
            >
            <button class="search-btn" @click="fetchDocList">
              <i class="fas fa-search"></i>
            </button>
          </div>
          <div class="action-buttons">
            <button class="btn primary-btn" @click="handleAdd">
              <i class="fas fa-plus"></i> 添加
            </button>
            <button class="btn primary-btn" @click="handleUpload">
              <i class="fas fa-upload"></i> 上传
            </button>
          </div>
        </div>

        <!-- 目录与文档列表 -->
        <div class="doc-container">
          <!-- 目录列表 -->
          <div class="folder-list">
            <div
              v-for="folder in folderList"
              :key="folder.id"
              class="folder-item"
              :class="{ active: selectedFolderId === folder.id }"
              @click="handleFolderClick(folder.id)"
            >
              <i class="fas fa-folder"></i>
              <span class="folder-name">{{ folder.name }}</span>
            </div>
          </div>

          <!-- 文档列表 -->
          <div class="document-list">
            <div
              v-for="doc in docList"
              :key="doc.id"
              class="document-item"
            >
              <div class="doc-info">
                <div class="doc-title">{{ doc.name }}</div>
                <div class="doc-desc">{{ doc.detail_text || '无描述' }}</div>
              </div>
              <div class="doc-actions">
                <button class="btn-icon small-icon" @click="handleDocCollect(doc.id)">
                  <i class="fas fa-star"></i> 收藏
                </button>
                <button class="btn-icon small-icon" @click="handleDocShare(doc.id)">
                  <i class="fas fa-share-alt"></i> 分享
                </button>
                <button class="btn-icon small-icon" @click="handleDocEdit(doc.id)">
                  <i class="fas fa-edit"></i> 操作
                </button>
              </div>
            </div>

            <!-- 空状态 -->
            <div class="empty-state" v-if="docList.length === 0 && !loading">
              <i class="fas fa-file-alt"></i>
              <p>暂无文档数据</p>
            </div>

            <!-- 加载状态 -->
            <div class="loading-state" v-if="loading">
              <i class="fas fa-spinner fa-spin"></i>
              <p>加载中...</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
// 引入项目已有的API（需与index.vue保持一致）
import { detailApi, documentApi, categoryApi } from './api'; // 路径需根据项目实际结构调整
import { getBaseURL } from '../utils'; // 若项目有工具函数，需调整路径

// 1. 路由与导航相关
const route = useRoute();
const router = useRouter();
const currentNav = ref('documents'); // 当前激活的左侧导航项

// 2. 页面数据相关
const repoId = ref<number>(0); // 知识库ID（从路由参数获取）
const selectedFolderId = ref<number>(0); // 当前选中的目录ID
const repoName = ref(''); // 知识库名称
const repoOwner = ref(''); // 知识库负责人
const userName = ref(''); // 当前登录用户名
const currentDate = ref(''); // 当前日期
const searchKey = ref(''); // 搜索关键词

// 3. 列表数据相关
const folderList = ref<any[]>([]); // 目录列表
const docList = ref<any[]>([]); // 文档列表
const loading = ref(false); // 加载状态

// 4. 初始化日期
const initDate = () => {
  const now = new Date();
  currentDate.value = now.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  });
};

// 5. 获取当前登录用户信息（模拟，实际需对接项目接口）
const getUserInfo = () => {
  // 若项目有用户信息接口，可替换为真实请求
  const user = localStorage.getItem('userInfo');
  if (user) {
    const userData = JSON.parse(user);
    userName.value = userData.name || '王女士';
  }
};

// 6. 获取知识库基本信息
const fetchRepoInfo = async () => {
  try {
    const res = await detailApi.getDetail(repoId.value);
    if (res.code === 2000) {
      const repoData = Array.isArray(res.data) ? res.data[0] : res.data;
      repoName.value = repoData.title || '知识库名称';
      repoOwner.value = repoData.creatorName || '张三';
    }
  } catch (error) {
    console.error('获取知识库信息失败:', error);
    ElMessage.error('获取知识库信息失败');
  }
};

// 7. 获取目录列表
const fetchFolderList = async () => {
  try {
    const params = {
      repo_id: repoId.value,
      page: 1,
      size: 100
    };
    const res = await categoryApi.getCategoryList(params);
    if (res.code === 2000) {
      const data = Array.isArray(res.data) ? res.data : res.data.list;
      // 筛选出目录类型（根据dimension字段判断，与index.vue逻辑一致）
      folderList.value = data.filter(item => item.dimension !== undefined);
    }
  } catch (error) {
    console.error('获取目录列表失败:', error);
    ElMessage.error('获取目录列表失败');
  }
};

// 8. 获取文档列表（支持按目录和搜索关键词筛选）
const fetchDocList = async () => {
  loading.value = true;
  try {
    const params = {
      repo_id: repoId.value,
      category_id: selectedFolderId.value,
      keyword: searchKey.value,
      page: 1,
      size: 20
    };
    const res = await documentApi.getDocumentList(params);
    if (res.code === 2000) {
      docList.value = Array.isArray(res.data) ? res.data : res.data.list;
    }
  } catch (error) {
    console.error('获取文档列表失败:', error);
    ElMessage.error('获取文档列表失败');
  } finally {
    loading.value = false;
  }
};

// 9. 目录点击事件（切换目录并加载对应文档）
const handleFolderClick = (folderId: number) => {
  selectedFolderId.value = folderId;
  fetchDocList();
};

// 10. 操作按钮事件（添加/上传/收藏等，可根据实际需求扩展）
const handleAdd = () => {
  // 跳转到添加文档页面（若有），或弹出添加模态框
  router.push({
    path: '/knowledge/add-document',
    query: { repoId: repoId.value, folderId: selectedFolderId.value }
  });
};

const handleUpload = () => {
  // 弹出上传模态框（可参考index.vue的上传逻辑实现）
  ElMessage.info('上传功能待实现');
};

const handleCollect = () => {
  ElMessage.success('收藏成功');
};

const handleShare = () => {
  ElMessage.info('分享功能待实现');
};

const handleDocCollect = (docId: number) => {
  ElMessage.success(`文档 ${docId} 收藏成功`);
};

const handleDocShare = (docId: number) => {
  ElMessage.info(`文档 ${docId} 分享功能待实现`);
};

const handleDocEdit = (docId: number) => {
  // 跳转到文档编辑页面
  router.push({
    path: '/knowledge/edit-document',
    query: { docId, repoId: repoId.value }
  });
};

const handleLogout = () => {
  // 退出登录逻辑
  localStorage.removeItem('userInfo');
  router.push('/login');
};

const goToHome = () => {
  // 返回知识库首页（即之前的index.vue）
  router.push({
    path: '/knowledge',
    query: { id: repoId.value }
  });
};

// 11. 页面挂载时初始化
onMounted(() => {
  // 从路由参数获取知识库ID和目录ID（与index.vue跳转时传递的参数对应）
  const routeRepoId = route.query.repoId;
  const routeFolderId = route.query.folderId;

  if (routeRepoId) {
    repoId.value = Number(routeRepoId);
    // 初始化数据
    initDate();
    getUserInfo();
    fetchRepoInfo();
    fetchFolderList();

    // 若有目录ID，选中该目录并加载文档
    if (routeFolderId) {
      selectedFolderId.value = Number(routeFolderId);
      fetchDocList();
    } else {
      // 无目录ID时加载全部文档
      fetchDocList();
    }
  } else {
    // 无知识库ID时跳回首页
    router.push('/knowledge');
    ElMessage.error('请选择知识库');
  }
});
</script>

<style lang="scss" scoped>
.doc-list-page {
  width: 100%;
  min-height: 100vh;
  background-color: #f5f7fa;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
  color: #333;
}

/* 顶部导航栏 */
.top-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 60px;
  padding: 0 20px;
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);

  .logo {
    font-size: 18px;
    font-weight: bold;
    color: #1a56db;
  }

  .user-info {
    display: flex;
    align-items: center;
    gap: 15px;

    .logout-btn {
      padding: 5px 10px;
      border: 1px solid #ddd;
      border-radius: 4px;
      background-color: transparent;
      cursor: pointer;
      transition: all 0.2s;

      &:hover {
        background-color: #f5f5f5;
        color: #1a56db;
      }
    }
  }
}

/* 页面头部 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background-color: #fff;
  margin: 10px 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);

  .header-left {
    .repo-meta {
      margin-top: 8px;
      font-size: 14px;
      color: #666;
      display: flex;
      gap: 10px;

      .divider {
        color: #ddd;
      }
    }
  }

  .header-right {
    display: flex;
    gap: 10px;
  }
}

/* 主容器 */
.main-container {
  display: flex;
  padding: 0 20px 20px;
  gap: 20px;
}

/* 左侧导航 */
.side-nav {
  width: 200px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  padding: 15px 0;

  .nav-item {
    width: 100%;
    padding: 12px 20px;
    display: flex;
    align-items: center;
    gap: 10px;
    background-color: transparent;
    border: none;
    cursor: pointer;
    font-size: 14px;
    transition: all 0.2s;

    &:hover {
      background-color: #f5f7fa;
      color: #1a56db;
    }

    &.active {
      background-color: #f0f5ff;
      color: #1a56db;
      font-weight: 500;
    }
  }

  .back-home-btn {
    width: 100%;
    padding: 12px 20px;
    display: flex;
    align-items: center;
    gap: 10px;
    background-color: transparent;
    border: none;
    cursor: pointer;
    font-size: 14px;
    color: #666;
    margin-top: 20px;

    &:hover {
      color: #1a56db;
      background-color: #f5f7fa;
    }
  }
}

/* 右侧内容区 */
.content-area {
  flex: 1;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

/* 操作栏 */
.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #f5f5f5;

  .search-box {
    display: flex;
    align-items: center;
    width: 300px;
    border: 1px solid #ddd;
    border-radius: 4px;
    overflow: hidden;

    input {
      flex: 1;
      padding: 8px 12px;
      border: none;
      outline: none;
      font-size: 14px;
    }

    .search-btn {
      padding: 8px 12px;
      border: none;
      background-color: #f5f5f5;
      cursor: pointer;
      color: #666;

      &:hover {
        background-color: #eee;
      }
    }
  }

  .action-buttons {
    display: flex;
    gap: 10px;
  }
}

/* 目录与文档容器 */
.doc-container {
  display: flex;
  height: calc(100vh - 240px);
  overflow: hidden;
}

/* 目录列表 */
.folder-list {
  width: 220px;
  border-right: 1px solid #f5f5f5;
  padding: 15px;
  overflow-y: auto;

  .folder-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 10px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
    color: #666;

    &:hover {
      background-color: #f5f7fa;
      color: #333;
    }

    &.active {
      background-color: #f0f5ff;
      color: #1a56db;
      font-weight: 500;
    }

    .folder-name {
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
  }
}

/* 文档列表 */
.document-list {
  flex: 1;
  padding: 15px;
  overflow-y: auto;

  .document-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 15px;
    border-bottom: 1px solid #f5f5f5;
    transition: all 0.2s;

    &:hover {
      background-color: #f9fafb;
    }

    .doc-info {
      .doc-title {
        font-size: 15px;
        font-weight: 500;
        margin-bottom: 4px;
      }

      .doc-desc {
        font-size: 13px;
        color: #666;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 600px;
      }
    }

    .doc-actions {
      display: flex;
      gap: 8px;
    }
  }

  /* 空状态与加载状态 */
  .empty-state, .loading-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: #999;
    font-size: 14px;

    i {
      font-size: 48px;
      margin-bottom: 10px;
    }
  }

  .loading-state i {
    animation: spin 1s linear infinite;
  }
}

/* 通用按钮样式 */
.btn {
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  border: none;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;

  &.primary-btn {
    background-color: #1a56db;
    color: #fff;

    &:hover {
      background-color: #1e40af;
    }
  }

  &.icon-btn {
    padding: 8px;
    border-radius: 50%;
    background-color: #f5f5f5;
    color: #666;

    &:hover {
      background-color: #eee;
      color: #1a56db;
    }
  }

  &.small-icon {
    padding: 4px 8px;
    font-size: 12px;
    background-color: transparent;
    color: #666;

    &:hover {
      color: #1a56db;
      background-color: #f5f7fa;
    }
  }
}

/* 动画 */
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>