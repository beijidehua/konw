import { request } from '/@/utils/service';

/**
 * 根据知识库 ID 获取单条数据
 * @param {number} id - 知识库唯一 ID（对应表中的 id 字段）
 * @returns {Promise} - 返回请求 Promise 对象
 */
export const getKnowledgeBaseById = (id) => {
  // 后端接口路径需与后端协商，例如：/knowledge-base/:id（RESTful 风格）
  return request({
    url: `/knowledge-base/${id}`, // 完整请求地址：baseURL + /knowledge-base/:id
    method: 'GET' // GET 请求（获取数据用 GET）
  });
};

/**
 * 其他请求（可选，如新增、修改知识库）
 * 例如：修改知识库数据（后续表单提交可用）
 */
export const updateKnowledgeBase = (id, data) => {
  return request({
    url: `/knowledge-base/${id}`,
    method: 'PUT', // 修改数据用 PUT
    data: data // 表单提交的新数据
  });
};