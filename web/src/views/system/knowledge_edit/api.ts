import { request } from '/@/utils/service';

// 获取知识库列表
export function getKnowledgeList(params: any) {
  return request({
    url: '/api/system/knowledge_edit/',
    method: 'get',
    params
  })
}

// 获取知识库详情
export function getKnowledgeDetail(id: string) {
  return request({
    url: `/api/system/knowledge_edit/${id}/`,
    method: 'get'
  })
}

// 新增知识库
export function createKnowledge(data: any) {
  return request({
    url: '/api/system/knowledge_edit/',
    method: 'post',
    data
  })
}

// 更新知识库
export function updateKnowledge(id: string, data: any) {
  return request({
    url: `/api/system/knowledge_edit/${id}/`,
    method: 'put',
    data
  })
}

// 删除知识库
export function deleteKnowledge(id: string) {
  return request({
    url: `/api/system/knowledge_edit/${id}/`,
    method: 'delete'
  })
}

