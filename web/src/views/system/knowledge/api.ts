import { request } from '/@/utils/service'; // 项目封装的axios请求工具
import {
  UserInfo,
  KnowledgeRepo,
  DocItem,
  MessageItem,
  KnowledgeStats
} from './types';

// 知识库详情页接口集合
export const knowledgeDetailApi = {
  /**
   * 1. 获取当前登录用户信息（顶部“王女士”展示）
   * @returns 用户基础信息
   */
  getUserInfo: () =>
    request<UserInfo>({
      url: '/api/user/current',
      method: 'GET'
    }),

  /**
   * 2. 获取知识库基础信息（名称、时间、收藏状态）
   * @param repoId 知识库ID（从路由参数获取）
   * @returns 知识库详情数据
   */
  getKnowledgeRepo: (repoId: string | number) =>
    request<KnowledgeRepo>({
      url: `/api/knowledge/repo/${repoId}`,
      method: 'GET'
    }),

  /**
   * 3. 获取知识库目录文档列表（左侧目录区域）
   * @param repoId 知识库ID
   * @returns 文档列表
   */
  getKnowledgeDocs: (repoId: string | number) =>
    request<DocItem[]>({
      url: `/api/knowledge/repo/${repoId}/docs`,
      method: 'GET'
    }),

  /**
   * 4. 获取最新消息通知（中间最新文档区域）
   * @param repoId 知识库ID
   * @param page 页码（默认1）
   * @param limit 每页条数（默认10）
   * @returns 消息列表
   */
  getLatestMessages: (
    repoId: string | number,
    page: number = 1,
    limit: number = 10
  ) =>
    request<{
      list: MessageItem[];
      total: number;
    }>({
      url: `/api/knowledge/repo/${repoId}/messages`,
      method: 'GET',
      params: { page, limit }
    }),

  /**
   * 5. 切换知识库收藏状态（收藏按钮点击）
   * @param repoId 知识库ID
   * @param isCollected 当前收藏状态（true=取消收藏，false=添加收藏）
   * @returns 操作结果（新的收藏状态）
   */
  toggleCollect: (repoId: string | number, isCollected: boolean) =>
    request<{ isCollected: boolean }>({
      url: `/api/knowledge/repo/${repoId}/collect`,
      method: 'POST',
      data: { isCollected: !isCollected } // 传反值实现“切换”
    }),

  /**
   * 6. 标记所有消息为已读（“全部已读”按钮点击）
   * @param repoId 知识库ID
   * @returns 操作结果提示
   */
  markAllRead: (repoId: string | number) =>
    request<{ msg: string }>({
      url: `/api/knowledge/repo/${repoId}/messages/mark-all-read`,
      method: 'POST'
    }),

  /**
   * 7. 获取知识库统计数据（统计入口展示）
   * @param repoId 知识库ID
   * @returns 统计信息
   */
  getKnowledgeStats: (repoId: string | number) =>
    request<KnowledgeStats>({
      url: `/api/knowledge/repo/${repoId}/stats`,
      method: 'GET'
    })
};