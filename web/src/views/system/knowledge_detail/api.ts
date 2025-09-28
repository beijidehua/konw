import { request } from '/@/utils/service';

// -------------------------- 类型定义 --------------------------
// Document接口请求参数类型
export interface DocumentParams {
  repo_id?: number; // 知识库ID
  category_id?: number; // 目录ID
  page?: number; // 页码
  size?: number; // 每页条数
  ordering?: string; // 排序字段
  search?: string; // 搜索关键词
  doc_type?: string; // 文档类型
}

// Document接口响应类型
export interface Document {
  id: number;
  name: string;
  file_url: string;
  file_id: string;
  file_name: string;
  doc_type: string;
  category_id: number;
  repo_id: number;
  create_time: string;
  update_time: string;
  creator: number;
  updater?: number;
  status: 'normal' | 'archived';
}

// 知识库详情请求参数类型
export interface DetailListParams {
  repo_id?: number; // 知识库ID
  page?: number; // 页码
  size?: number; // 每页条数
  ordering?: string; // 排序字段
  search?: string; // 搜索关键词
}

// 知识库详情信息类型
export interface KnowledgeDetail {
  id: number;
  repo_id: number;
  title: string;
  content: string;
  create_time: string;
  update_time: string;
  creator: number;
  updater?: number;
  status: 'normal' | 'archived';
  views: number;
  likes: number;
  // 目录相关字段
  repository_id?: number; // 所属知识库ID
  parent_category_id?: number; // 父级目录ID
  master?: number; // 目录负责人ID
  sort?: number; // 排序值
  dimension?: number; // 目录深度
  tree_path?: string; // 上级目录路径
}

// 知识库详情统计信息
export interface DetailStatistics {
  total_views: number;
  total_likes: number;
  total_documents: number;
}

// 目录接口请求参数类型
export interface CategoryParams {
  repo_id?: number; // 知识库ID
  parent_id?: number; // 父级目录ID
  page?: number; // 页码
  size?: number; // 每页条数
  ordering?: string; // 排序字段
  search?: string; // 搜索关键词
}

// 目录接口响应类型
export interface Category {
  id: number;
  name: string;
  description?: string;
  repository_id: number;
  parent_category_id?: number;
  master: number;
  sort: number;
  dimension: number;
  tree_path: string;
  create_time: string;
  update_time: string;
  creator: number;
  updater?: number;
  status: 'normal' | 'archived';
}

// -------------------------- 知识库详情接口集合 --------------------------
export const detailApi = {
  // 1. 获取知识库详情列表
  getDetailList: (params: DetailListParams) =>
    request({
      url: '/api/system/knowledge_edit/',
      method: 'GET',
      params
    }),

  // 2. 获取单个知识详情
  getDetail: (id: number) =>
    request({
      url: `/api/system/knowledge_edit/${id}/`,
      method: 'GET'
    }),

  // 3. 创建目录
  createDetail: (data: Omit<KnowledgeDetail, 'id' | 'create_time' | 'update_time' | 'views' | 'likes'>) =>
    request({
      url: '/api/system/knowledge_category/',
      method: 'POST',
      data
    }),

  // 4. 更新知识详情
  updateDetail: (id: number, data: Partial<Omit<KnowledgeDetail, 'id' | 'create_time' | 'update_time'>>) =>
    request({
      url: `/api/system/knowledge_detail/${id}/`,
      method: 'PUT',
      data
    }),

  // 5. 删除知识详情
  deleteDetail: (id: number) =>
    request({
      url: `/api/system/knowledge_detail/${id}/`,
      method: 'DELETE',
    }),

  // 6. 获取知识库详情统计信息
  getDetailStatistics: (repoId: number) =>
    request({
      url: '/api/system/knowledge_detail/statistics/',
      method: 'GET',
      params: { repo_id: repoId }
    }),
  
  // 7. 点赞知识详情
  likeDetail: (detailId: number) =>
    request({
      url: '/api/system/knowledge_detail/like/',
      method: 'POST',
      data: { detail_id: detailId }
    }),
  
  // 8. 增加浏览量
  increaseViews: (detailId: number) =>
    request({
      url: '/api/system/knowledge_detail/view/',
      method: 'POST',
      data: { detail_id: detailId }
    })
};


// -------------------------- 目录接口集合 --------------------------
export const categoryApi = {
  // 1. 获取目录列表
  getCategoryList: (params: CategoryParams) =>
    request({
      url: '/api/system/knowledge_category/',
      method: 'GET',
      params
    }),

  // 2. 获取单个目录详情
  getCategory: (id: number) =>
    request({
      url: `/api/system/knowledge_category/${id}/`,
      method: 'GET'
    }),

  // 3. 创建目录
  createCategory: (data: Omit<Category, 'id' | 'create_time' | 'update_time'>) =>
    request({
      url: '/api/system/knowledge_category/',
      method: 'POST',
      data
    }),

  // 4. 更新目录
  updateCategory: (id: number, data: Partial<Omit<Category, 'id' | 'create_time' | 'update_time'>>) =>
    request({
      url: `/api/system/knowledge_category/${id}/`,
      method: 'PUT',
      data
    }),

  // 5. 删除目录
  deleteCategory: (id: number) =>
    request({
      url: `/api/system/knowledge_category/${id}/`,
      method: 'DELETE',
    }),
    
  // 6. 获取目录树结构
  getCategoryTree: (repoId: number) =>
    request({
      url: '/api/system/knowledge_category/tree/',
      method: 'GET',
      params: { repo_id: repoId }
    }),
    
  // 7. 移动目录
  moveCategory: (id: number, targetId: number) =>
    request({
      url: '/api/system/knowledge_category/move/',
      method: 'POST',
      data: { id, target_id: targetId }
    })
};

// -------------------------- 文档接口集合 --------------------------
export const documentApi = {
  // 1. 获取文档列表
  getDocumentList: (params: DocumentParams) =>
    request({
      url: '/api/system/document/',
      method: 'GET',
      params
    }),

  // 2. 获取单个文档详情
  getDocument: (id: number) =>
    request({
      url: `/api/system/document/${id}/`,
      method: 'GET'
    }),

  // 3. 创建文档
  createDocument: (data: Omit<Document, 'id' | 'create_time' | 'update_time'>) =>
    request({
      url: '/api/system/document/',
      method: 'POST',
      data
    }),

  // 4. 更新文档
  updateDocument: (id: number, data: Partial<Omit<Document, 'id' | 'create_time' | 'update_time'>>) =>
    request({
      url: `/api/system/document/${id}/`,
      method: 'PUT',
      data
    }),

  // 5. 删除文档
  deleteDocument: (id: number) =>
    request({
      url: `/api/system/document/${id}/`,
      method: 'DELETE',
    }),
    
  // 6. 批量删除文档
  batchDeleteDocuments: (ids: number[]) =>
    request({
      url: '/api/system/document/batch_delete/',
      method: 'POST',
      data: { ids }
    })
};


