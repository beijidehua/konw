// 知识库列表项类型
export interface KnowledgeItem {
  id: string
  title: string
  creator: string
  createTime: string
}

// 分页请求参数
export interface PageParams {
  page: number
  limit: number
  keyword?: string
}

// 分页响应数据
export interface PageResult<T> {
  list: T[]
  total: number
}

interface KnowledgeItem {
  id: string | number;
  title: string;
  creator: string;
  createTime: string;
}


//
// // 222
// // 知识库列表项类型
// export interface KnowledgeItem {
//   id: string
//   title: string
//   category: string
//   visibility: string
//   description: string
//   creator: string
//   createTime: string
// }
//
// // 分页请求参数
// export interface PageParams {
//   page: number
//   limit: number
//   keyword?: string
// }
//
// // 分页响应数据
// export interface PageResult<T> {
//   list: T[]
//   total: number
// }