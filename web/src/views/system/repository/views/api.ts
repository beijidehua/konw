import { request } from '/@/utils/service';
/**
 * 获取知识库详情
 * @param kbId 知识库ID
 */
export const getKnowledgeBaseDetail = (kbId: string) => {
  return request({
    url: `/repository/${kbId}/overview/`,
    method: 'GET',
  });
};
