<template>
  <div class="knowledge-base-system">
    <!-- 左侧导航栏 -->
    <div class="side-nav">
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
      <!-- 底部按钮容器 -->
      <div class="bottom-buttons">
        <!-- 返回首页按钮 -->
        <div class="nav-item home-btn" @click="goToHome">
          <i class="fas fa-home"></i>
          <span>返回首页</span>
        </div>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 顶部操作栏 -->
      <div class="header">
        <div class="page-info">
          <h1>{{ repoDetail ? repoDetail.title : '知识库' }}</h1>
          <div class="date">{{ currentDate }} {{ currentTime }}</div>
          <div class="repo-name">当前你位于{{ repoDetail ? repoDetail.title : '未知知识库' }}知识库</div>
        </div>
        <div class="action-buttons">
          

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

          <!-- 用户信息显示 -->
          <div class="user-greeting">
            <div class="greeting-text">{{ getGreeting() }}，{{ state.personalForm.name || '用户' }}！欢迎使用知识库系统</div>
            <div class="user-info-top">
              <div class="user-avatar">
                <el-avatar :size="32" :src="state.personalForm.avatar ? getBaseURL(state.personalForm.avatar) : ''">{{ state.personalForm.name ? state.personalForm.name.substring(0, 1) : 'U' }}</el-avatar>
              </div>
              <div class="user-name">{{ state.personalForm.name || '用户' }}</div>
            </div>
          </div>

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
              <div class="card-title">目录结构</div>
            </div>
            <div class="folder-list">
              <div v-for="folder in folderList" :key="folder.id" class="folder-item" :style="{ marginLeft: `${(folder.dimension - 1) * 20}px` }">
                <div class="folder-icon">📁</div>
                <div class="folder-title">{{ folder.title }}</div>
              </div>
              <div v-if="folderList.length === 0" class="empty-message">暂无目录</div>
            </div>
          </div>
          <div class="sidebar-card">
            <div class="card-header">
              <div class="card-title">文档列表</div>
            </div>
            <div class="preview-list">
              <div v-for="doc in allDocs" :key="doc.id" class="preview-item">
                <div class="preview-title">{{ doc.title }}</div>
                <div class="preview-content">{{ doc.content || '' }}</div>
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
          <div class="form-group">
            <label>父级目录</label>
            <select v-model="newFolder.parentId">
              <option :value="0">顶级目录</option>
              <option v-for="folder in folderList" :key="folder.id" :value="folder.id">
                {{ folder.title }}
              </option>
            </select>
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

<script setup lang="ts">
import { reactive, ref, onMounted, onUnmounted } from 'vue';
import { detailApi, KnowledgeDetail } from './api';
import { useRoute } from 'vue-router';
import * as api from '../personal/api';

// 定义缺失的类型和函数
const dictionary = (type: string) => {
  // 模拟dictionary函数
  return [];
};

const useUserInfo = () => {
  // 模拟useUserInfo函数
  return { userInfo: {} };
};

const getBaseURL = (path: string) => {
  // 模拟getBaseURL函数
  return path ? path : '';
};

// 定义PersonalState接口
interface PersonalState {
  newsInfoList: any[];
  personalForm: {
    avatar: string;
    username: string;
    name: string;
    email: string;
    mobile: string;
    gender: string;
    dept_info: {
      dept_id: number;
      dept_name: string;
    };
    role_info: {
      id: number;
      name: string;
    }[];
  };
}
// 定义类型
interface NavItem {
  id: number;
  text: string;
  icon: string;
  active: boolean;
}

interface DocItem {
  id: number;
  title: string;
  date?: string;
  content?: string;
}

interface FolderItem extends KnowledgeDetail {
  dimension: number;
  tree_path: string;
}

interface PermissionItem {
  id: number;
  title: string;
  desc: string;
}

interface NewFolder {
  name: string;
  description: string;
  parentId: number;
}

interface NewDoc {
  title: string;
  content: string;
}

// 组件名称
const name = 'KnowledgeBaseSystem';

// 导航菜单
const navItems = ref<NavItem[]>([
  { id: 1, text: '概述', icon: 'fas fa-home', active: true },
  { id: 2, text: '文档', icon: 'fas fa-file-alt', active: false },
  { id: 3, text: '统计', icon: 'fas fa-chart-bar', active: false },
  { id: 4, text: '设置', icon: 'fas fa-cog', active: false }
]);

// 激活导航项
const activateNav = (id: number): void => {
  navItems.value.forEach(item => {
    item.active = item.id === id;
  });
};

// 当前日期和时间
const currentDate = ref('');
const currentTime = ref('');
let timeInterval: number | null = null;

// 更新日期和时间
const updateDateTime = (): void => {
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
const frequentDocs = ref<DocItem[]>([]);
const recentDocs = ref<DocItem[]>([]);
const allDocs = ref<DocItem[]>([]);
const permissions = ref<PermissionItem[]>([]);

// 知识库详情数据
const repoDetail = ref<KnowledgeDetail | null>(null);
const repoId = ref<number>(1); // 设置默认值为1，避免null值导致API调用错误

// 加载状态
const loading = ref({
  frequentDocs: true,
  recentDocs: true,
  allDocs: true,
  permissions: true
});

// 模态框状态
const showAddModal = ref(false);
const showFolderModal = ref(false);
const showMarkdownModal = ref(false);
const showUploadModal = ref(false);
const showAddDropdown = ref(false);

// 新文档数据
const newDoc = ref<NewDoc>({
  title: '',
  content: ''
});

// 新目录数据
const newFolder = ref<NewFolder>({
  name: '',
  description: '',
  parentId: 0 // 默认为顶级目录
});

// 目录列表
const folderList = ref<FolderItem[]>([]);

// 新Markdown数据
const newMarkdown = ref<NewDoc>({
  title: '',
  content: ''
});

// 文件上传相关
const fileInput = ref<HTMLInputElement | null>(null);
const selectedFile = ref<File | null>(null);

/**
 * 获取常用文档
 */
const fetchFrequentDocs = async (): Promise<void> => {
  try {
    loading.value.frequentDocs = true;
    const params = {
      repo_id: repoId.value,
      page: 1,
      size: 5,
      ordering: '-views' // 按浏览量排序
    };
    
    const res = await detailApi.getDetailList(params);
    
    // 适配后端响应格式
    if (res.code === 2000) {
      // 检查 res.data 是否为数组
      const dataArray = Array.isArray(res.data) ? res.data : (res.data?.data || []);
      frequentDocs.value = dataArray.map((item: any) => ({
        id: item.id,
        title: item.title || item.name || '',
        date: item.update_time || item.create_time || ''
      }));
    } else {
      console.error('获取常用文档失败:', res.msg);
    }
  } catch (error) {
    console.error('获取常用文档出错:', error);
  } finally {
    loading.value.frequentDocs = false;
  }
};

/**
 * 获取最新文档
 */
const fetchRecentDocs = async (): Promise<void> => {
  try {
    loading.value.recentDocs = true;
    const params = {
      repo_id: repoId.value,
      page: 1,
      size: 5,
      ordering: '-create_time' // 按创建时间倒序
    };
    
    const res = await detailApi.getDetailList(params);
    
    if (res.code === 2000) {
      // 检查 res.data 是否为数组
      const dataArray = Array.isArray(res.data) ? res.data : (res.data?.data || []);
      recentDocs.value = dataArray.map((item: any) => ({
        id: item.id,
        title: item.title || item.name || '',
        date: item.create_time || ''
      }));
    } else {
      console.error('获取最新文档失败:', res.msg);
    }
  } catch (error) {
    console.error('获取最新文档出错:', error);
  } finally {
    loading.value.recentDocs = false;
  }
};

/**
 * 获取所有文档
 */
const fetchAllDocs = async (): Promise<void> => {
  try {
    loading.value.allDocs = true;
    const params = {
      repo_id: repoId.value,
      page: 1,
      size: 10
    };
    
    const res = await detailApi.getDetailList(params);
    
    if (res.code === 2000) {
      // 检查 res.data 是否为数组
      const dataArray = Array.isArray(res.data) ? res.data : (res.data?.data || []);
      allDocs.value = dataArray.map((item: any) => ({
        id: item.id,
        title: item.title || item.name || '',
        content: (item.content || item.description || '').substring(0, 50) + '...' // 截取部分内容
      }));
    } else {
      console.error('获取所有文档失败:', res.msg);
    }
  } catch (error) {
    console.error('获取所有文档出错:', error);
  } finally {
    loading.value.allDocs = false;
  }
};

/**
 * 获取权限列表（示例函数，实际可能需要调整）
 */
const fetchPermissions = async (): Promise<void> => {
  try {
    loading.value.permissions = true;
    // 这里使用模拟数据，因为API中没有对应的权限接口
    permissions.value = [
      { id: 1, title: '编辑权限', desc: '允许编辑知识库文档' },
      { id: 2, title: '管理权限', desc: '允许管理知识库成员' },
      { id: 3, title: '删除权限', desc: '允许删除知识库文档' }
    ];
  } catch (error) {
    console.error('获取权限列表出错:', error);
  } finally {
    loading.value.permissions = false;
  }
};

// 切换添加下拉菜单
const toggleAddDropdown = (): void => {
  showAddDropdown.value = !showAddDropdown.value;
};

// 添加目录
const addFolder = (): void => {
  showAddDropdown.value = false;
  showFolderModal.value = true;
};

// 添加文档
const addDocument = (): void => {
  showAddDropdown.value = false;
  showAddModal.value = true;
};

// 添加Markdown
const addMarkdown = (): void => {
  showAddDropdown.value = false;
  showMarkdownModal.value = true;
};

// 确认添加目录
const confirmAddFolder = async (): Promise<void> => {
  if (!newFolder.value.name) {
    alert('请输入目录名称');
    return;
  }

  try {
    // 获取父级目录信息
    let parentDimension = 0;
    let parentTreePath = '';
    let parentId = newFolder.value.parentId;
    
    if (parentId > 0) {
      // 查找父级目录
      const parentFolder = folderList.value.find(folder => folder.id === parentId);
      if (parentFolder) {
        parentDimension = parentFolder.dimension || 0;
        parentTreePath = parentFolder.tree_path || '';
      }
    }
    
    // 计算当前目录深度和路径
    const dimension = parentDimension > 0 ? parentDimension + 1 : 1;
    const treePath = parentId > 0 ? 
      (parentTreePath ? `${parentTreePath},${parentId}` : `${parentId}`) : '';
    
    // 使用创建知识详情API，将目录作为特殊类型的知识详情
    const data = {
      repo_id: repoId.value,
      title: newFolder.value.name, // 修改name为title以匹配KnowledgeDetail接口
      content: newFolder.value.description,
      creator: 1, // 当前用户ID，实际应从用户状态获取
      status: 'normal' as 'normal' | 'archived',
      repository_id: repoId.value, // 添加 repository_id 字段
      master: 1, // 目录负责人ID
      parent_category_id: parentId, // 父级目录ID
      sort: 0, // 默认排序值
      dimension: dimension, // 目录深度
      tree_path: treePath // 上级目录路径
    };
    
    const res = await detailApi.createDetail(data);
    
    if (res.code === 2000) {
      alert(`已创建目录: ${newFolder.value.name}`);
      showFolderModal.value = false;
      newFolder.value = { name: '', description: '', parentId: 0 };
      
      // 刷新文档列表和目录列表
      fetchAllDocs();
      fetchFolderList();
    } else {
      console.error('创建目录失败:', res.msg);
      alert(`创建目录失败: ${res.msg}`);
    }
  } catch (error) {
    console.error('创建目录出错:', error);
    alert('创建目录失败，请重试');
  }
};

// 确认添加文档
const confirmAddDocument = async (): Promise<void> => {
  if (!newDoc.value.title || !newDoc.value.content) {
    alert('请填写文档标题和内容');
    return;
  }

  try {
    const data = {
      repo_id: repoId.value,
      title: newDoc.value.title,
      content: newDoc.value.content,
      creator: 1, // 当前用户ID，实际应从用户状态获取
      status: 'normal' as 'normal' | 'archived'
    };
    
    const res = await detailApi.createDetail(data);
    
    if (res.code === 2000) {
      alert(`文档添加成功: ${newDoc.value.title}`);
      newDoc.value = { title: '', content: '' };
      showAddModal.value = false;
      
      // 刷新文档列表
      fetchRecentDocs();
      fetchAllDocs();
    } else {
      console.error('添加文档失败:', res.msg);
      alert(`添加文档失败: ${res.msg}`);
    }
  } catch (error) {
    console.error('添加文档出错:', error);
    alert('添加文档失败，请重试');
  }
};

// 确认添加Markdown
const confirmAddMarkdown = async (): Promise<void> => {
  if (!newMarkdown.value.title || !newMarkdown.value.content) {
    alert('请填写文档标题和内容');
    return;
  }

  try {
    // 使用创建知识详情API
    const data = {
      repo_id: repoId.value,
      title: newMarkdown.value.title,
      content: newMarkdown.value.content,
      creator: 1,
      status: 'normal' as 'normal' | 'archived'
    };
    
    const res = await detailApi.createDetail(data);
    
    if (res.code === 2000) {
      alert(`Markdown文档添加成功: ${newMarkdown.value.title}`);
      newMarkdown.value = { title: '', content: '' };
      showMarkdownModal.value = false;
      
      // 刷新文档列表
      fetchRecentDocs();
      fetchAllDocs();
    } else {
      console.error('添加Markdown文档失败:', res.msg);
      alert(`添加Markdown文档失败: ${res.msg}`);
    }
  } catch (error) {
    console.error('添加Markdown文档出错:', error);
    alert('添加Markdown文档失败，请重试');
  }
};

// 触发文件选择
const triggerFileInput = (): void => {
  if (fileInput.value) {
    fileInput.value.click();
  }
};

// 处理文件选择
const handleFileUpload = (event: Event): void => {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    selectedFile.value = target.files[0];
    if (selectedFile.value) {
      alert(`已选择文件: ${selectedFile.value.name}`);
    }
  }
};

// 上传文档
const uploadDocument = async (): Promise<void> => {
  if (!selectedFile.value) {
    alert('请先选择要上传的文件');
    return;
  }

  try {
    // 模拟文件上传成功后创建知识详情
    // 实际项目中应先上传文件，然后用返回的URL创建知识详情
    const data = {
      repo_id: repoId.value,
      title: selectedFile.value.name,
      content: `上传的文件内容: ${selectedFile.value.name}`,
      creator: 1,
      status: 'normal' as 'normal' | 'archived'
    };
    
    const res = await detailApi.createDetail(data);
    
    if (res.code === 2000) {
      alert(`文档上传成功: ${selectedFile.value.name}`);
      selectedFile.value = null;
      showUploadModal.value = false;
      
      // 刷新文档列表
      fetchRecentDocs();
      fetchAllDocs();
    } else {
      console.error('上传文档失败:', res.msg);
      alert(`上传文档失败: ${res.msg}`);
    }
  } catch (error) {
    console.error('上传文档出错:', error);
    alert('上传文档失败，请重试');
  }
};

// 申请权限
const requestPermission = (permId: number): void => {
  alert(`已申请权限ID: ${permId}`);
};

// 从URL获取知识库ID
const getRepoIdFromUrl = (): void => {
  const route = useRoute();
  if (route.params.id) {
    repoId.value = Number(route.params.id);
  }
};

// 获取知识库详情
const fetchRepoDetail = async (): Promise<void> => {
  if (!repoId.value) return; // 如果没有有效的ID，则不发送请求
  
  try {
    const res = await detailApi.getDetail(repoId.value);
    if (res.code === 2000 && res.data && Array.isArray(res.data) && res.data.length > 0) {
      repoDetail.value = res.data[0];
      document.title = `${res.data[0].title || '知识库'} - 知识库系统`;
    } else if (res.code === 2000 && res.data) {
      // 处理直接返回对象的情况
      repoDetail.value = res.data;
      document.title = `${res.data.title || '知识库'} - 知识库系统`;
    } else {
      console.error('获取知识库详情失败:', res.msg);
    }
  } catch (error) {
    console.error('获取知识库详情出错:', error);
  }
};
//获取用户信息
/**
 * 获取用户个人信息
 */
const genderList = ref();
const state = reactive<PersonalState>({
	newsInfoList: [],
	personalForm: {
		avatar: '',
		username: '',
		name: '',
		email: '',
		mobile: '',
		gender: '',
		dept_info: {
			dept_id: 0,
			dept_name: '',
		},
		role_info: [
			{
				id: 0,
				name: '',
			},
		],
	},
});
const getUserInfo = function () {
	api.GetUserInfo({}).then((res: any) => {
		const { data } = res;
		genderList.value = dictionary('gender');
		state.personalForm.avatar = data.avatar || '';
		state.personalForm.username = data.username || '';
		state.personalForm.name = data.name || '';
		state.personalForm.email = data.email || '';
		state.personalForm.mobile = data.mobile || '';
		state.personalForm.gender = data.gender;
		state.personalForm.dept_info.dept_name = data.dept_info.dept_name || '';
		state.personalForm.role_info = data.role_info || [];
	});
};
// 获取问候语
const getGreeting = (): string => {
  const hour = new Date().getHours();
  if (hour < 6) return '凌晨好';
  if (hour < 9) return '早上好';
  if (hour < 12) return '上午好';
  if (hour < 14) return '中午好';
  if (hour < 18) return '下午好';
  if (hour < 22) return '晚上好';
  return '夜深了';
};

// 返回首页
const goToHome = (): void => {
  window.location.href = '/';
};



// 组件挂载时初始化
onMounted(() => {
  // 更新日期时间
  updateDateTime();
  timeInterval = window.setInterval(updateDateTime, 60000); // 每分钟更新一次

  // 从URL获取知识库ID
  getRepoIdFromUrl();
  
  // 获取知识库详情
  fetchRepoDetail();
  //获取用户信息
  getUserInfo();
  // 获取数据
  fetchFrequentDocs();
  fetchRecentDocs();
  fetchAllDocs();
  fetchFolderList(); // 获取目录列表
  fetchPermissions();

  // 点击外部关闭下拉菜单
  document.addEventListener('click', () => {
    showAddDropdown.value = false;
  });
});

// 组件卸载时清理
onUnmounted(() => {
  if (timeInterval) clearInterval(timeInterval);
  document.removeEventListener('click', () => {
    showAddDropdown.value = false;
  });
});

/**
 * 获取目录列表
 */
const fetchFolderList = async (): Promise<void> => {
  try {
    const params = {
      repo_id: repoId.value,
      page: 1,
      size: 100 // 获取足够多的目录
    };
    
    const res = await detailApi.getDetailList(params);
    
    if (res.code === 2000) {
      // 检查 res.data 是否为数组
      const dataArray = Array.isArray(res.data) ? res.data : (res.data?.data || []);
      // 过滤出目录类型的数据
      folderList.value = dataArray.filter((item: any) => item.dimension !== undefined) as FolderItem[];
    } else {
      console.error('获取目录列表失败:', res.msg);
    }
  } catch (error) {
    console.error('获取目录列表出错:', error);
  }
};
</script>

<style lang="scss" scoped>
.knowledge-base-system {
  display: flex;
  flex-direction: row;
  min-height: 100vh;
  background-color: #f5f7fa;
  color: #333;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

/* 左侧导航栏 */
.side-nav {
  background: linear-gradient(180deg, #1a56db, #1e40af);
  color: white;
  padding: 15px 0;
  display: flex;
  flex-direction: column;
  width: 220px;
  min-height: 100vh;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.logo {
  font-size: 20px;
  font-weight: bold;
  margin: 0 20px 15px 20px;
  text-align: center;
}

.nav-items {
  display: flex;
  flex-direction: column;
  flex: 1;
  margin: 0;
  padding-top: 10px;
}

.nav-item {
  padding: 10px 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  transition: background-color 0.2s;
  margin-bottom: 2px;
}

.nav-item i {
  margin-right: 10px;
  width: 20px;
  text-align: center;
}

.nav-item:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.nav-item.active {
  background-color: rgba(255, 255, 255, 0.2);
  font-weight: 500;
  border-left: 3px solid white;
}

/* 底部按钮容器 */
.bottom-buttons {
  margin-top: auto;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding-top: 10px;
  display: flex;
  flex-direction: column;
}

/* 左侧导航栏底部返回首页按钮 */
.home-btn {
  margin-top: 0;
  font-weight: 500;
}


/* 右上角用户信息样式 */
.user-greeting {
  display: flex;
  align-items: center;
  margin-right: 15px;
}

.greeting-text {
  margin-right: 15px;
  font-size: 14px;
  color: #666;
}

.user-info-top {
  display: flex;
  align-items: center;
  background-color: #f0f2f5;
  padding: 5px 10px;
  border-radius: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.user-avatar {
  margin-right: 8px;
}

.user-name {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

/* 主内容区调整 */
.main-content {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  height: 100vh;
}

/* 旧的顶部导航栏样式已被左侧导航栏替代 */

/* 主内容区 */
.main-content {
  flex: 1;
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

/* 顶部操作栏 */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.action-buttons {
  display: flex;
  align-items: center;
  gap: 10px;
}

.page-info h1 {
  font-size: 24px;
  margin: 0 0 5px;
  font-weight: 600;
}

.date {
  color: #666;
  font-size: 14px;
}

.repo-name {
  color: #1a56db;
  font-size: 16px;
  font-weight: 600;
  margin-top: 8px;
  background-color: #f0f5ff;
  padding: 5px 10px;
  border-radius: 4px;
  display: inline-block;
}

.action-buttons {
  display: flex;
  gap: 10px;
  align-items: center;
}

.btn {
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  border: none;
  transition: all 0.2s;
}

.btn-outline {
  background-color: transparent;
  border: 1px solid #ddd;
  color: #333;
}

.btn-outline:hover {
  background-color: #f5f5f5;
}

.btn-primary {
  background-color: #1a56db;
  color: white;
}

.btn-primary:hover {
  background-color: #1e40af;
}

.btn-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: transparent;
  border: 1px solid #ddd;
  color: #333;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-icon:hover {
  background-color: #f5f5f5;
}

/* 下拉菜单 */
.dropdown {
  position: relative;
}

.dropdown-toggle {
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  background-color: transparent;
  border: 1px solid #ddd;
  color: #333;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 5px;
  background-color: white;
  border-radius: 6px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  width: 150px;
  z-index: 10;
  display: none;
}

.dropdown-menu.show {
  display: block;
}

.dropdown-item {
  padding: 10px 15px;
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.dropdown-item:hover {
  background-color: #f5f7fa;
}

.dropdown-item i {
  color: #666;
}

/* 内容区域 */
.content {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 20px;
  max-height: calc(100vh - 100px);
  overflow-y: auto;
}

/* 左侧文档列表 */
.left-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-height: calc(100vh - 120px);
  overflow-y: auto;
}

.card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.card-header {
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
}

.doc-list {
  padding: 10px 0;
  max-height: 300px;
  overflow-y: auto;
}

.doc-item {
  padding: 10px 20px;
  border-bottom: 1px solid #f5f5f5;
  cursor: pointer;
  transition: background-color 0.2s;
}

.doc-item:last-child {
  border-bottom: none;
}

.doc-item:hover {
  background-color: #f9fafb;
}

.doc-title {
  font-size: 14px;
  margin-bottom: 5px;
}

.doc-date {
  font-size: 12px;
  color: #666;
}

/* 右侧边栏 */
.right-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-height: calc(100vh - 120px);
  overflow-y: auto;
}

.sidebar-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.perm-list {
  padding: 10px 0;
}

.perm-item {
  padding: 10px 20px;
  border-bottom: 1px solid #f5f5f5;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.perm-item:last-child {
  border-bottom: none;
}

.perm-title {
  font-size: 14px;
  margin-bottom: 3px;
}

.perm-desc {
  font-size: 12px;
  color: #666;
}

.perm-btn {
  padding: 5px 10px;
  background-color: #1a56db;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.perm-btn:hover {
  background-color: #1e40af;
}

.preview-list {
  padding: 10px 0;
  max-height: 300px;
  overflow-y: auto;
}

.preview-item {
  padding: 15px 20px;
  border-bottom: 1px solid #f5f5f5;
  cursor: pointer;
}

.preview-item:last-child {
  border-bottom: none;
}

.preview-title {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 5px;
}

.preview-content {
  font-size: 12px;
  color: #666;
  line-height: 1.5;
}

/* 模态框 */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  border-radius: 8px;
  width: 500px;
  max-width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.modal-header {
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
}

.modal-body {
  padding: 20px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-size: 14px;
  font-weight: 500;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.form-group textarea {
  min-height: 100px;
  resize: vertical;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

/* 上传区域 */
.upload-area {
  border: 2px dashed #ddd;
  border-radius: 8px;
  padding: 30px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
}

.upload-area:hover {
  border-color: #1a56db;
  background-color: #f9fafb;
}

.upload-area i {
  font-size: 48px;
  color: #1a56db;
  margin-bottom: 10px;
}

.upload-area p {
  margin: 0;
  color: #666;
}

.upload-area p span {
  color: #1a56db;
  font-weight: 500;
}
/* 目录列表样式 */
.folder-list {
  margin-top: 10px;
  max-height: 300px;
  overflow-y: auto;
}

.folder-item {
  display: flex;
  align-items: center;
  padding: 8px 10px;
  border-radius: 4px;
  margin-bottom: 5px;
  transition: background-color 0.2s;
}

.folder-item:hover {
  background-color: #f5f5f5;
  cursor: pointer;
}

.folder-icon {
  margin-right: 8px;
  font-size: 16px;
}

.folder-title {
  font-size: 14px;
  font-weight: 500;
}

.empty-message {
  color: #999;
  text-align: center;
  padding: 15px 0;
  font-size: 14px;
}
/* 顶部导航栏样式调整 */
.top-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  height: 60px;
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.logo {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.nav-items {
  display: flex;
  flex: 1;
  justify-content: center;
  margin: 0 20px;
  margin-top: -250px; 
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 0 15px;
  cursor: pointer;
  height: 60px;
  transition: all 0.3s;
}

.nav-item i {
  margin-right: 5px;
}

.nav-item.active {
  color: var(--el-color-primary);
  border-bottom: 2px solid var(--el-color-primary);
}

/* 用户信息样式 */
.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.user-avatar {
  margin-right: 8px;
}

.user-name {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

/* 顶部操作栏布局调整 */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
}

.page-info {
  flex: 1;
}

.action-buttons {
  display: flex;
  align-items: center;
}
/* 自定义滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>