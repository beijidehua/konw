import { request } from '/@/utils/service';

/**
 * 知识库接口集合
 */
export const repositoryApi = {
  // 1. 基础CRUD接口（ModelViewSet默认接口）
  // 获取知识库列表（支持过滤、搜索、排序）
  getRepoList: (params) => request({
    url: '/api/repositories/',
    method: 'GET',
    params // params: { status: 'normal', search: '产品', ordering: '-create_time' }
  }),
  // 获取单个知识库详情
  getRepoDetail: (id) => request({
    url: `/api/repositories/${id}/`,
    method: 'GET'
  }),
  // 创建知识库
  createRepo: (data) => request({
    url: '/api/repositories/',
    method: 'POST',
    data // data: { name: '产品V3.0文档库', type_id: 1, master: 1001, limits: 0, ... }
  }),
  // 全量更新知识库
  updateRepo: (id, data) => request({
    url: `/api/repositories/${id}/`,
    method: 'PUT',
    data
  }),
  // 部分更新知识库（如仅修改名称）
  patchRepo: (id, data) => request({
    url: `/api/repositories/${id}/`,
    method: 'PATCH',
    data // data: { name: '产品V3.0文档库（更新）' }
  }),
  // 删除知识库（物理删除，若后端改逻辑删除可调整）
  deleteRepo: (id) => request({
    url: `/api/repositories/${id}/`,
    method: 'DELETE'
  }),

  // 2. 自定义接口（对应后端@action装饰的接口）
  // 获取所有正常状态的知识库
  getAllNormalRepo: () => request({
    url: '/api/repositories/all_normal_repo/',
    method: 'GET'
  }),
  // 单个知识库归档
  archiveRepo: (data) => request({
    url: '/api/repositories/archive_repo/',
    method: 'POST',
    data // data: { repo_id: 1, archived_desc: '产品停更，归档留存' }
  }),
  // 从归档/回收站恢复知识库
  restoreRepo: (data) => request({
    url: '/api/repositories/restore_repo/',
    method: 'POST',
    data // data: { repo_id: 1 }
  }),
  // 获取知识库详情（含统计）
  getRepoInfo: (repoId) => request({
    url: '/api/repositories/repo_info/',
    method: 'GET',
    params: { repo_id: repoId }
  }),
  // 知识库排序（上移/下移）
  sortRepo: (data) => request({
    url: '/api/repositories/sort_repo/',
    method: 'POST',
    data // data: { repo_id: 1, direction: 'up' }
  })
};