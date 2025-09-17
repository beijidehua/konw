// 用户信息类型（顶部导航栏显示）
export interface UserInfo {
  name: string; // 用户名（如：王女士）
  avatar?: string; // 用户头像（可选）
  role?: string; // 用户角色（可选）
}

// 知识库基础信息类型（页面顶部展示）
export interface KnowledgeRepo {
  id: string | number; // 知识库ID
  name: string; // 知识库名称
  createTime: string; // 创建/更新时间（如：2025-09-30）
  isCollected: boolean; // 是否已收藏（控制收藏按钮状态）
  collectCount?: number; // 收藏数（可选）
  shareCount?: number; // 分享数（可选）
}

// 文档列表项类型（目录/最新文档区域）
export interface DocItem {
  id: string | number; // 文档ID
  title: string; // 文档标题
  content: string; // 文档内容（用于预览）
  createTime: string; // 创建时间（如：2025-09-03 14:25）
  isRead: boolean; // 是否已读（控制“全部已读”状态）
  author?: string; // 文档作者（可选）
  docType?: 'MarkDown' | 'Word' | 'Excel'; // 文档类型（可选）
}

// 消息通知类型（最新文档区域的消息项）
export interface MessageItem {
  id: string | number; // 消息ID
  content: string; // 消息内容
  createTime: string; // 消息时间（如：2025-09-03 14:25）
  readStatus: 'read' | 'unread'; // 阅读状态
  relatedDocId?: string | number; // 关联文档ID（可选，点击跳转文档）
}

// 知识库统计数据类型（统计入口展示）
export interface KnowledgeStats {
  docTotal: number; // 文档总数
  unreadDocCount: number; // 未读文档数
  messageTotal: number; // 消息总数
  lastUpdateTime: string; // 最后更新时间
}