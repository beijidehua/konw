<template>
  <div class="knowledge-base-system">
    <!-- 顶部导航栏 -->
    <div class="top-nav">
      <div class="logo">知识库系统</div>
      <div class="nav-items">
        <div
          v-for="item in navItems"
          :key="item.id"
          :class="['nav-item', item.active ? 'active' : '']"
          @click="activateNav(item.id)"
        >
          <i :class="item.icon"></i>
          <span>{{ item.text }}</span>
        </div>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 顶部操作栏 -->
      <div class="header">
        <div class="page-info">
          <h1>知识库</h1>
          <div class="date">{{ currentDate }} {{ currentTime }}</div>
        </div>
        <div class="action-buttons">
          <button class="btn btn-outline">
            <i class="fas fa-home"></i> 返回首页
          </button>

          <!-- 添加下拉菜单 -->
          <div class="dropdown">
            <button class="dropdown-toggle" @click.stop="toggleAddDropdown">
              <i class="fas fa-plus"></i> 添加
              <i class="fas fa-chevron-down" style="font-size: 12px;"></i>
            </button>
            <div class="dropdown-menu" :class="{ show: showAddDropdown }">
              <div class="dropdown-item" @click="addFolder">
                <i class="fas fa-folder"></i>
                <span>目录</span>
              </div>
              <div class="dropdown-item" @click="addDocument">
                <i class="fas fa-file-alt"></i>
                <span>文档</span>
              </div>
              <div class="dropdown-item" @click="addMarkdown">
                <i class="fab fa-markdown"></i>
                <span>Markdown</span>
              </div>
            </div>
          </div>

          <button class="btn btn-primary" @click="showUploadModal = true">
            <i class="fas fa-upload"></i> 上传
          </button>
          <button class="btn-icon">
            <i class="fas fa-star"></i>
          </button>
          <button class="btn-icon">
            <i class="fas fa-share-alt"></i>
          </button>
        </div>
      </div>

      <!-- 内容区域 -->
      <div class="content">
        <!-- 左侧文档列表 -->
        <div class="left-panel">
          <div class="card">
            <div class="card-header">
              <div class="card-title">常用文档</div>
            </div>
            <div class="doc-list">
              <div v-for="doc in frequentDocs" :key="doc.id" class="doc-item">
                <div class="doc-title">{{ doc.title }}</div>
                <div class="doc-date">{{ doc.date }}</div>
              </div>
            </div>
          </div>

          <div class="card">
            <div class="card-header">
              <div class="card-title">最新文档</div>
            </div>
            <div class="doc-list">
              <div v-for="doc in recentDocs" :key="doc.id" class="doc-item">
                <div class="doc-title">{{ doc.title }}</div>
                <div class="doc-date">{{ doc.date }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧边栏 -->
        <div class="right-panel">
          <div class="sidebar-card">
            <div class="card-header">
              <div class="card-title">权限申请</div>
            </div>
            <div class="perm-list">
              <div v-for="perm in permissions" :key="perm.id" class="perm-item">
                <div class="perm-info">
                  <div class="perm-title">{{ perm.title }}</div>
                  <div class="perm-desc">{{ perm.desc }}</div>
                </div>
                <button class="perm-btn" @click="requestPermission(perm.id)">申请</button>
              </div>
            </div>
          </div>

          <div class="sidebar-card">
            <div class="card-header">
              <div class="card-title">文档列表</div>
            </div>
            <div class="preview-list">
              <div v-for="doc in allDocs" :key="doc.id" class="preview-item">
                <div class="preview-title">{{ doc.title }}</div>
                <div class="preview-content">{{ doc.content }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加文档模态框 -->
    <div v-if="showAddModal" class="modal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>添加文档</h3>
          <button class="close-btn" @click="showAddModal = false">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>文档标题</label>
            <input type="text" v-model="newDoc.title" placeholder="请输入文档标题">
          </div>
          <div class="form-group">
            <label>文档内容</label>
            <textarea v-model="newDoc.content" placeholder="请输入文档内容"></textarea>
          </div>
          <div class="form-actions">
            <button class="btn btn-outline" @click="showAddModal = false">取消</button>
            <button class="btn btn-primary" @click="confirmAddDocument">确认</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加目录模态框 -->
    <div v-if="showFolderModal" class="modal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>添加目录</h3>
          <button class="close-btn" @click="showFolderModal = false">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>目录名称</label>
            <input type="text" v-model="newFolder.name" placeholder="请输入目录名称">
          </div>
          <div class="form-group">
            <label>目录描述</label>
            <textarea v-model="newFolder.description" placeholder="请输入目录描述"></textarea>
          </div>
          <div class="form-actions">
            <button class="btn btn-outline" @click="showFolderModal = false">取消</button>
            <button class="btn btn-primary" @click="confirmAddFolder">确认</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加Markdown模态框 -->
    <div v-if="showMarkdownModal" class="modal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>添加Markdown文档</h3>
          <button class="close-btn" @click="showMarkdownModal = false">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>文档标题</label>
            <input type="text" v-model="newMarkdown.title" placeholder="请输入文档标题">
          </div>
          <div class="form-group">
            <label>Markdown内容</label>
            <textarea v-model="newMarkdown.content" placeholder="请输入Markdown内容" rows="10"></textarea>
          </div>
          <div class="form-actions">
            <button class="btn btn-outline" @click="showMarkdownModal = false">取消</button>
            <button class="btn btn-primary" @click="confirmAddMarkdown">确认</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 上传文档模态框 -->
    <div v-if="showUploadModal" class="modal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>上传文档</h3>
          <button class="close-btn" @click="showUploadModal = false">&times;</button>
        </div>
        <div class="modal-body">
          <div class="upload-area" @click="triggerFileInput">
            <i class="fas fa-cloud-upload-alt"></i>
            <p>将文件拖到此处，或<span>点击上传</span></p>
            <input type="file" ref="fileInput" style="display: none;" @change="handleFileUpload">
          </div>
          <div class="form-actions">
            <button class="btn btn-outline" @click="showUploadModal = false">取消</button>
            <button class="btn btn-primary" @click="uploadDocument">开始上传</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue';

export default {
  name: 'KnowledgeBaseSystem',
  setup() {
    // 导航菜单
    const navItems = ref([
      { id: 1, text: '概述', icon: 'fas fa-home', active: true },
      { id: 2, text: '文档', icon: 'fas fa-file-alt', active: false },
      { id: 3, text: '统计', icon: 'fas fa-chart-bar', active: false },
      { id: 4, text: '设置', icon: 'fas fa-cog', active: false }
    ]);

    // 激活导航项
    const activateNav = (id) => {
      navItems.value.forEach(item => {
        item.active = item.id === id;
      });
    };

    // 当前日期和时间
    const currentDate = ref('');
    const currentTime = ref('');
    let timeInterval = null;

    // 更新日期和时间
    const updateDateTime = () => {
      const now = new Date();
      currentDate.value = now.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
      });
      currentTime.value = now.toLocaleTimeString('zh-CN', {
        hour: '2-digit',
        minute: '2-digit'
      });
    };

    // 文档数据 - 初始化为空数组
    const frequentDocs = ref([]);
    const recentDocs = ref([]);
    const allDocs = ref([]);
    const permissions = ref([]);

    // 加载状态
    const loading = ref({
      frequentDocs: true,
      recentDocs: true,
      allDocs: true,
      permissions: true
    });

    // API端点配置
    const API_BASE = 'https://api.example.com/knowledge-base';
    const API_ENDPOINTS = {
      FREQUENT_DOCS: `${API_BASE}/documents/frequent`,
      RECENT_DOCS: `${API_BASE}/documents/recent`,
      ALL_DOCS: `${API_BASE}/documents`,
      PERMISSIONS: `${API_BASE}/permissions`,
      ADD_DOCUMENT: `${API_BASE}/documents`,
      ADD_FOLDER: `${API_BASE}/folders`,
      ADD_MARKDOWN: `${API_BASE}/markdown`,
      UPLOAD_DOCUMENT: `${API_BASE}/upload`
    };

    // 获取常用文档
    const fetchFrequentDocs = async () => {
      try {
        loading.value.frequentDocs = true;
        const response = await fetch(API_ENDPOINTS.FREQUENT_DOCS);
        if (!response.ok) throw new Error('获取常用文档失败');
        frequentDocs.value = await response.json();
      } catch (error) {
        console.error('获取常用文档出错:', error);
        // 可以在这里添加备用数据或错误处理
      } finally {
        loading.value.frequentDocs = false;
      }
    };

    // 获取最新文档
    const fetchRecentDocs = async () => {
      try {
        loading.value.recentDocs = true;
        const response = await fetch(API_ENDPOINTS.RECENT_DOCS);
        if (!response.ok) throw new Error('获取最新文档失败');
        recentDocs.value = await response.json();
      } catch (error) {
        console.error('获取最新文档出错:', error);
      } finally {
        loading.value.recentDocs = false;
      }
    };

    // 获取所有文档
    const fetchAllDocs = async () => {
      try {
        loading.value.allDocs = true;
        const response = await fetch(API_ENDPOINTS.ALL_DOCS);
        if (!response.ok) throw new Error('获取文档列表失败');
        allDocs.value = await response.json();
      } catch (error) {
        console.error('获取文档列表出错:', error);
      } finally {
        loading.value.allDocs = false;
      }
    };

    // 获取权限列表
    const fetchPermissions = async () => {
      try {
        loading.value.permissions = true;
        const response = await fetch(API_ENDPOINTS.PERMISSIONS);
        if (!response.ok) throw new Error('获取权限列表失败');
        permissions.value = await response.json();
      } catch (error) {
        console.error('获取权限列表出错:', error);
      } finally {
        loading.value.permissions = false;
      }
    };

    // 模态框状态
    const showAddModal = ref(false);
    const showFolderModal = ref(false);
    const showMarkdownModal = ref(false);
    const showUploadModal = ref(false);
    const showAddDropdown = ref(false);

    // 新文档数据
    const newDoc = ref({
      title: '',
      content: ''
    });

    // 新目录数据
    const newFolder = ref({
      name: '',
      description: ''
    });

    // 新Markdown数据
    const newMarkdown = ref({
      title: '',
      content: ''
    });

    // 文件上传相关
    const fileInput = ref(null);
    const selectedFile = ref(null);

    // 切换添加下拉菜单
    const toggleAddDropdown = () => {
      showAddDropdown.value = !showAddDropdown.value;
    };

    // 添加目录
    const addFolder = () => {
      showAddDropdown.value = false;
      showFolderModal.value = true;
    };

    // 添加文档
    const addDocument = () => {
      showAddDropdown.value = false;
      showAddModal.value = true;
    };

    // 添加Markdown
    const addMarkdown = () => {
      showAddDropdown.value = false;
      showMarkdownModal.value = true;
    };

    // 确认添加目录
    const confirmAddFolder = async () => {
      if (!newFolder.value.name) {
        alert('请输入目录名称');
        return;
      }

      try {
        const response = await fetch(API_ENDPOINTS.ADD_FOLDER, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(newFolder.value)
        });
        
        if (!response.ok) throw new Error('创建目录失败');
        
        const result = await response.json();
        alert(`已创建目录: ${result.name}`);
        showFolderModal.value = false;
        newFolder.value = { name: '', description: '' };
        
        // 刷新文档列表
        fetchAllDocs();
      } catch (error) {
        console.error('创建目录出错:', error);
        alert('创建目录失败，请重试');
      }
    };

    // 确认添加文档
    const confirmAddDocument = async () => {
      if (!newDoc.value.title || !newDoc.value.content) {
        alert('请填写文档标题和内容');
        return;
      }

      try {
        const response = await fetch(API_ENDPOINTS.ADD_DOCUMENT, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(newDoc.value)
        });
        
        if (!response.ok) throw new Error('添加文档失败');
        
        const result = await response.json();
        alert(`文档添加成功: ${result.title}`);
        newDoc.value = { title: '', content: '' };
        showAddModal.value = false;
        
        // 刷新文档列表
        fetchRecentDocs();
        fetchAllDocs();
      } catch (error) {
        console.error('添加文档出错:', error);
        alert('添加文档失败，请重试');
      }
    };

    // 确认添加Markdown
    const confirmAddMarkdown = async () => {
      if (!newMarkdown.value.title || !newMarkdown.value.content) {
        alert('请填写文档标题和内容');
        return;
      }

      try {
        const response = await fetch(API_ENDPOINTS.ADD_MARKDOWN, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(newMarkdown.value)
        });
        
        if (!response.ok) throw new Error('添加Markdown文档失败');
        
        const result = await response.json();
        alert(`Markdown文档添加成功: ${result.title}`);
        newMarkdown.value = { title: '', content: '' };
        showMarkdownModal.value = false;
        
        // 刷新文档列表
        fetchRecentDocs();
        fetchAllDocs();
      } catch (error) {
        console.error('添加Markdown文档出错:', error);
        alert('添加Markdown文档失败，请重试');
      }
    };

    // 触发文件选择
    const triggerFileInput = () => {
      fileInput.value.click();
    };

    // 处理文件选择
    const handleFileUpload = (event) => {
      selectedFile.value = event.target.files[0];
      if (selectedFile.value) {
        alert(`已选择文件: ${selectedFile.value.name}`);
      }
    };

    // 上传文档
    const uploadDocument = async () => {
      if (!selectedFile.value) {
        alert('请先选择要上传的文件');
        return;
      }

      try {
        const formData = new FormData();
        formData.append('file', selectedFile.value);
        
        const response = await fetch(API_ENDPOINTS.UPLOAD_DOCUMENT, {
          method: 'POST',
          body: formData
        });
        
        if (!response.ok) throw new Error('上传文档失败');
        
        const result = await response.json();
        alert(`文档上传成功: ${result.filename}`);
        showUploadModal.value = false;
        selectedFile.value = null;
        
        // 刷新文档列表
        fetchRecentDocs();
        fetchAllDocs();
      } catch (error) {
        console.error('上传文档出错:', error);
        alert('上传文档失败，请重试');
      }
    };

    // 申请权限
    const requestPermission = async (permissionId) => {
      try {
        const permission = permissions.value.find(p => p.id === permissionId);
        if (!permission) return;
        
        const response = await fetch(`${API_BASE}/permissions/request`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ permissionId })
        });
        
        if (!response.ok) throw new Error('申请权限失败');
        
        alert(`已申请权限: ${permission.title}`);
      } catch (error) {
        console.error('申请权限出错:', error);
        alert('申请权限失败，请重试');
      }
    };

    // 点击外部关闭下拉菜单
    const closeDropdownOnClickOutside = (event) => {
      if (showAddDropdown.value && !event.target.closest('.dropdown')) {
        showAddDropdown.value = false;
      }
    };

    // 组件挂载时启动时钟并获取数据
    onMounted(() => {
      updateDateTime();
      timeInterval = setInterval(updateDateTime, 60000);
      document.addEventListener('click', closeDropdownOnClickOutside);
      
      // 获取初始数据
      fetchFrequentDocs();
      fetchRecentDocs();
      fetchAllDocs();
      fetchPermissions();
    });

    // 组件卸载时清除时钟
    onUnmounted(() => {
      if (timeInterval) clearInterval(timeInterval);
      document.removeEventListener('click', closeDropdownOnClickOutside);
    });

    return {
      navItems,
      activateNav,
      currentDate,
      currentTime,
      frequentDocs,
      recentDocs,
      allDocs,
      permissions,
      showAddModal,
      showFolderModal,
      showMarkdownModal,
      showUploadModal,
      showAddDropdown,
      newDoc,
      newFolder,
      newMarkdown,
      fileInput,
      loading,
      toggleAddDropdown,
      addFolder,
      addDocument,
      addMarkdown,
      confirmAddFolder,
      confirmAddDocument,
      confirmAddMarkdown,
      triggerFileInput,
      handleFileUpload,
      uploadDocument,
      requestPermission
    };
  }
}
</script>


<style scoped>
.knowledge-base-system {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: #f5f7fa;
  color: #333;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

/* 顶部导航栏 */
.top-nav {
  background: linear-gradient(135deg, #1a56db, #1e40af);
  color: white;
  padding: 0 20px;
  display: flex;
  align-items: center;
  height: 64px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.logo {
  font-size: 22px;
  font-weight: bold;
  margin-right: 30px;
}

.nav-items {
  display: flex;
  height: 100%;
}

.nav-item {
  padding: 0 20px;
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s;
  height: 100%;
  position: relative;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.1);
}

.nav-item.active {
  background: rgba(255, 255, 255, 0.2);
}

.nav-item.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: white;
}

.nav-item i {
  margin-right: 8px;
  font-size: 16px;
}

/* 主内容区 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

/* 顶部操作栏 */
.header {
  background: white;
  padding: 16px 24px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-info h1 {
  font-size: 22px;
  font-weight: 600;
  color: #1f2937;
}

.page-info .date {
  color: #6b7280;
  font-size: 14px;
  margin-top: 4px;
}

.action-buttons {
  display: flex;
  gap: 12px;
  position: relative;
}

.btn {
  padding: 8px 16px;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
}

.btn-primary {
  background: #1d4ed8;
  color: white;
  border: none;
}

.btn-primary:hover {
  background: #1e40af;
}

.btn-outline {
  background: white;
  border: 1px solid #d1d5db;
  color: #4b5563;
}

.btn-outline:hover {
  background: #f9fafb;
}

.btn-icon {
  padding: 8px 12px;
  border-radius: 6px;
  background: white;
  border: 1px solid #e5e7eb;
  color: #4b5563;
  cursor: pointer;
}

.btn-icon:hover {
  background: #f3f4f6;
}

/* 下拉菜单样式 */
.dropdown {
  position: relative;
  display: inline-block;
}

.dropdown-toggle {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: #1d4ed8;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.dropdown-toggle:hover {
  background: #1e40af;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
  background: white;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  min-width: 180px;
  z-index: 1000;
  overflow: hidden;
  margin-top: 8px;
  opacity: 0;
  transform: translateY(-10px);
  transition: all 0.3s ease;
  pointer-events: none;
}

.dropdown-menu.show {
  opacity: 1;
  transform: translateY(0);
  pointer-events: auto;
}

.dropdown-item {
  padding: 10px 16px;
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  transition: all 0.2s;
  color: #4b5563;
}

.dropdown-item:hover {
  background: #f3f4f6;
}

.dropdown-item i {
  width: 20px;
  text-align: center;
}

/* 内容区域 */
.content {
  flex: 1;
  padding: 24px;
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 24px;
  overflow-y: auto;
}

.card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 20px;
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f3f4f6;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.doc-list {
  display: flex;
  flex-direction: column;
}

.doc-item {
  padding: 12px 0;
  border-bottom: 1px solid #f3f4f6;
  cursor: pointer;
}

.doc-item:last-child {
  border-bottom: none;
}

.doc-item:hover {
  background: #f9fafb;
}

.doc-title {
  font-weight: 500;
  margin-bottom: 4px;
  color: #1f2937;
}

.doc-date {
  font-size: 12px;
  color: #6b7280;
}

.sidebar-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 20px;
  margin-bottom: 20px;
}

.perm-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f3f4f6;
}

.perm-info {
  flex: 1;
}

.perm-title {
  font-weight: 500;
  margin-bottom: 4px;
}

.perm-desc {
  font-size: 12px;
  color: #6b7280;
}

.perm-btn {
  background: #10b981;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
}

.preview-item {
  padding: 12px 0;
  border-bottom: 1px solid #f3f4f6;
}

.preview-title {
  font-weight: 500;
  margin-bottom: 6px;
  color: #1f2937;
}

.preview-content {
  font-size: 13px;
  color: #6b7280;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 模态框样式 */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 500px;
  max-width: 90%;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.modal-header {
  padding: 16px 24px;
  border-bottom: 1px solid #f3f4f6;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  font-size: 18px;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #6b7280;
}

.modal-body {
  padding: 24px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #374151;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
}

.form-group textarea {
  min-height: 100px;
  resize: vertical;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 20px;
}

.upload-area {
  border: 2px dashed #d1d5db;
  border-radius: 8px;
  padding: 40px 20px;
  text-align: center;
  background: #f9fafb;
  cursor: pointer;
  transition: all 0.3s;
}

.upload-area:hover {
  border-color: #3b82f6;
  background: #eff6ff;
}

.upload-area i {
  font-size: 48px;
  color: #9ca3af;
  margin-bottom: 16px;
}

.upload-area p {
  color: #6b7280;
}

.upload-area span {
  color: #3b82f6;
  text-decoration: underline;
}
</style>