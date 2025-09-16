import { request } from '/@/utils/service';

// -------------------------- 类型定义（TS 新增）--------------------------
// 知识库列表请求参数类型（筛选、分页、排序）
export interface RepoListParams {
  status?: 'normal' | 'archived'; // 状态筛选（限定可选值）
  type_id?: number; // 类型ID
  search?: string; // 搜索关键词
  page?: number; // 页码
  size?: number; // 每页条数
  ordering?: string; // 排序字段（如 '-create_time'）
}

// 知识库基础信息类型（与后端返回字段对齐）
export interface Repository {
  id: number;
  name: string;
  type_id: number;
  master: number;
  limits: 0 | 1; // 0=公开，1=私有
  create_time: string; // 时间戳字符串（如 '2024-05-10 09:30:00'）
  icon_url?: string; // 可选字段
  status: 'normal' | 'archived';
  archived_time?: string;
  archived_user_id?: number;
  archived_desc?: string;
  recycle: 0 | 1;
  recycle_time?: string;
  recycle_user_id?: number;
  description?: string;
}

// 知识库详情返回类型（含统计信息）
export interface RepoInfoResponse {
  repo_base: Repository; // 基础信息
  doc_count: number; // 关联文档数
  member_count: number; // 关联成员数
}

// -------------------------- 知识库接口集合（从 repository.js 迁移）--------------------------
export const repositoryApi = {
  // 1. 获取知识库列表
  getRepoList: (params: RepoListParams) =>
    request<{ results: Repository[], count: number }>({ // TS 泛型：指定响应数据类型
      url: '/api/system/knowledge_edit/',
      method: 'GET',
      params
    }),

  // 2. 获取单个知识库详情
  getRepoDetail: (id: number) =>
    request<Repository>({
      url: `/api/system/knowledge_edit/${id}/`,
      method: 'GET'
    }),

  // 3. 创建知识库（请求参数类型）
  createRepo: (data: Omit<Repository, 'id' | 'create_time'>) => // Omit：排除无需手动传的字段
    request<Repository>({
      url: '/api/system/knowledge_edit/',
      method: 'POST',
      data
    }),

  // 4. 归档知识库（请求参数类型）
  archiveRepo: (data: { repo_id: number; archived_desc?: string }) =>
    request<{ msg: string }>({ // 响应类型：仅返回提示信息
      url: '/api/system/knowledge_edit/archive_repo/',
      method: 'POST',
      data
    }),

  // 5. 其他接口（恢复、排序、详情统计等）同理补充...
  restoreRepo: (data: { repo_id: number }) =>
    request<{ msg: string }>({
      url: '/api/system/knowledge_edit/restore_repo/',
      method: 'POST',
      data
    }),

  getRepoInfo: (repoId: number) =>
    request<RepoInfoResponse>({
      url: '/api/system/knowledge_edit/repo_info/',
      method: 'GET',
      params: { repo_id: repoId }
    })
};

// （可选）如果 api.ts 还整合了其他模块接口（如用户、部门），继续在这里添加
// export const userApi = { ... };
// export const deptApi = { ... };