import { request } from '/@/utils/service';

// -------------------------- 类型定义 --------------------------
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

  // 3. 创建知识详情
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