import * as api from './api';
import {
  dict,
  compute,
  CreateCrudOptionsProps,
  CreateCrudOptionsRet
} from '@fast-crud/fast-crud';
import { successMessage, errorMessage } from '/@/utils/message';
import { auth } from '/@/utils/authFunction';
import { ElMessageBox, ElMessage } from 'element-plus';
import { commonCrudConfig } from "/@/utils/commonCrud";

export const createKnowledgeCrudOptions = function ({ crudExpose }: CreateCrudOptionsProps): CreateCrudOptionsRet {
  // 列表请求
  const pageRequest = async (query) => {
    const response = await api.GetKnowledgeList(query);
    return {
      list: response.data.items,
      total: response.data.total,
    };
  };

  // 编辑请求
  const editRequest = async ({ form, row }) => {
    form.id = row.id;
    return await api.UpdateKnowledgeObj(form);
  };

  // 删除请求
  const delRequest = async ({ row }) => {
    return await api.DelKnowledgeObj(row.id);
  };

  // 添加请求
  const addRequest = async ({ form }) => {
    return await api.AddKnowledgeObj(form);
  };

  // 导出请求
  const exportRequest = async (query) => {
    try {
      const response = await api.exportKnowledgeData(query);
      const blob = new Blob([response.data], { type: 'application/vnd.ms-excel' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = '知识库数据_' + new Date().getTime() + '.xlsx';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      successMessage('导出成功');
    } catch (error) {
      errorMessage('导出失败');
      console.error('导出错误:', error);
    }
  };

  return {
		crudOptions: {
			table: {
				title: '知识库管理',
				border: true,
				stripe: true,
				remove: {
					confirmMessage: '确定要删除该知识库吗？',
				},
			},
			request: {
				pageRequest,
				addRequest,
				editRequest,
				delRequest,
			},
			actionbar: {
				buttons: {
					add: {
						show: auth('knowledge:add'),
						text: '新增知识库',
						type: 'primary',
					},
					export: {
						text: '导出',
						icon: 'Download',
						show: auth('knowledge:export'),
						click: (ctx) => {
							ElMessageBox.confirm('确定要导出知识库数据吗？', '提示', {
								confirmButtonText: '确定',
								cancelButtonText: '取消',
								type: 'warning',
							}).then(() => {
								exportRequest(ctx.getQueryParams());
							});
						},
					},
				},
			},
			rowHandle: {
				width: 220,
				buttons: {
					view: {
						show: false,
					},
					edit: {
						show: auth('knowledge:edit'),
						text: '编辑',
						type: 'primary',
						size: 'small',
					},
					remove: {
						show: auth('knowledge:delete'),
						text: '删除',
						type: 'danger',
						size: 'small',
					},
					publish: {
						text: '发布',
						type: 'success',
						size: 'small',
						show: compute(({ row }) => {
							return auth('knowledge:publish') && row.status !== 'published';
						}),
						click: async ({ row }) => {
							try {
								await api.UpdateKnowledgeObj({
									id: row.id,
									status: 'published',
								});
								successMessage('发布成功');
								crudExpose.doRefresh();
							} catch (error) {
								errorMessage('发布失败');
								console.error('发布错误:', error);
							}
						},
					},
				},
			},
			columns: {
				_index: {
					title: '序号',
					form: { show: false },
					column: {
						type: 'index',
						align: 'center',
						width: 60,
					},
				},
				title: {
					title: '知识库标题',
					search: { show: true, placeholder: '请输入标题' },
					type: 'input',
					column: {
						minWidth: 200,
						showOverflowTooltip: true,
					},
					form: {
						rules: [{ required: true, message: '请输入知识库标题' }],
						component: { placeholder: '请输入知识库标题' },
					},
				},
				category: {
					title: '所属分类',
					search: { show: true },
					type: 'dict-select',
					dict: dict({
						data: [
							{ label: '技术文档', value: 'tech' },
							{ label: '产品说明', value: 'product' },
							{ label: '操作指南', value: 'guide' },
							{ label: '常见问题', value: 'faq' },
							{ label: '其他', value: 'other' },
						],
					}),
					form: {
						rules: [{ required: true, message: '请选择所属分类' }],
						component: { placeholder: '请选择所属分类' },
					},
				},
				status: {
					title: '状态',
					search: { show: true },
					type: 'dict-select',
					dict: dict({
						data: [
							{ label: '草稿', value: 'draft', color: 'gray' },
							{ label: '已发布', value: 'published', color: 'green' },
							{ label: '已归档', value: 'archived', color: 'orange' },
						],
					}),
					column: {
						component: {
							name: 'dict-tag',
						},
					},
					form: {
						rules: [{ required: true, message: '请选择状态' }],
					},
				},
				content: {
					title: '内容摘要',
					type: 'textarea',
					column: {
						minWidth: 300,
						formatter: ({ row }) => {
							if (!row.content) return '';
							return row.content.length > 50 ? row.content.substring(0, 50) + '...' : row.content;
						},
					},
					form: {
						rules: [{ required: true, message: '请输入知识库内容' }],
						component: {
							placeholder: '请输入知识库详细内容',
							rows: 6,
						},
					},
				},
				attachments: {
					title: '附件',
					form: {
						type: 'upload',
						component: {
							action: '/api/system/knowledge/upload_attachment/',
							name: 'file',
							limit: 5,
							accept: '.jpg,.jpeg,.png,.pdf,.doc,.docx',
							tip: '支持上传jpg、png、pdf、doc等格式，最多5个文件，单个不超过10MB',
						},
					},
					column: {
						formatter: ({ row }) => {
							if (!row.attachments || row.attachments.length === 0) return '-';
							return row.attachments.map((file) => (
								<el-link key={file.id} href={file.file_url} target="_blank">
									{file.file_name}
								</el-link>
							));
						},
					},
				},
				...commonCrudConfig(),
			},
		},
	};
};


//
// // 222
// import * as api from './api';
// import {
//   dict,
//   compute,
//   CreateCrudOptionsProps,
//   CreateCrudOptionsRet
// } from '@fast-crud/fast-crud';
// import { successMessage, errorMessage } from '/@/utils/message';
// import { auth } from '/@/utils/authFunction';
// import { ElMessageBox, ElMessage } from 'element-plus';
// import { commonCrudConfig } from "/@/utils/commonCrud";
//
// export const createKnowledgeCrudOptions = function ({ crudExpose }: CreateCrudOptionsProps): CreateCrudOptionsRet {
//   // 列表请求
//   const pageRequest = async (query) => {
//     const response = await api.getKnowledgeList(query);
//     return {
//       list: response.data.items,
//       total: response.data.total,
//     };
//   };
//
//   // 编辑请求
//   const editRequest = async ({ form, row }) => {
//     form.id = row.id;
//     return await api.updateKnowledge(form.id, form);
//   };
//
//   // 删除请求
//   const delRequest = async ({ row }) => {
//     return await api.deleteKnowledge(row.id);
//   };
//
//   // 添加请求
//   const addRequest = async ({ form }) => {
//     return await api.createKnowledge(form);
//   };
//
//   // 导出请求
//   const exportRequest = async (query) => {
//     try {
//       const response = await api.exportKnowledgeData(query);
//       const blob = new Blob([response.data], { type: 'application/vnd.ms-excel' });
//       const url = window.URL.createObjectURL(blob);
//       const a = document.createElement('a');
//       a.href = url;
//       a.download = '知识库数据_' + new Date().getTime() + '.xlsx';
//       document.body.appendChild(a);
//       a.click();
//       window.URL.revokeObjectURL(url);
//       document.body.removeChild(a);
//       successMessage('导出成功');
//     } catch (error) {
//       errorMessage('导出失败');
//       console.error('导出错误:', error);
//     }
//   };
//
//   return {
//     crudOptions: {
//       table: {
//         title: '知识库管理',
//         border: true,
//         stripe: true,
//         remove: {
//           confirmMessage: '确定要删除该知识库吗？',
//         },
//       },
//       request: {
//         pageRequest,
//         addRequest,
//         editRequest,
//         delRequest,
//       },
//       actionbar: {
//         buttons: {
//           add: {
//             show: auth('knowledge:add'),
//             text: '新增知识库',
//             type: 'primary',
//           },
//           export: {
//             text: '导出',
//             icon: 'Download',
//             show: auth('knowledge:export'),
//             click: (ctx) => {
//               ElMessageBox.confirm('确定要导出知识库数据吗？', '提示', {
//                 confirmButtonText: '确定',
//                 cancelButtonText: '取消',
//                 type: 'warning',
//               }).then(() => {
//                 exportRequest(ctx.getQueryParams());
//               });
//             },
//           },
//         },
//       },
//       rowHandle: {
//         width: 220,
//         buttons: {
//           view: {
//             show: false,
//           },
//           edit: {
//             show: auth('knowledge:edit'),
//             text: '编辑',
//             type: 'primary',
//             size: 'small',
//           },
//           remove: {
//             show: auth('knowledge:delete'),
//             text: '删除',
//             type: 'danger',
//             size: 'small',
//           },
//           publish: {
//             text: '发布',
//             type: 'success',
//             size: 'small',
//             show: compute(({ row }) => {
//               return auth('knowledge:publish') && row.status !== 'published';
//             }),
//             click: async ({ row }) => {
//               try {
//                 await api.updateKnowledge(row.id, {
//                   id: row.id,
//                   status: 'published',
//                 });
//                 successMessage('发布成功');
//                 crudExpose.doRefresh();
//               } catch (error) {
//                 errorMessage('发布失败');
//                 console.error('发布错误:', error);
//               }
//             },
//           },
//         },
//       },
//       columns: {
//         _index: {
//           title: '序号',
//           form: { show: false },
//           column: {
//             type: 'index',
//             align: 'center',
//             width: 60,
//           },
//         },
//         title: {
//           title: '知识库标题',
//           search: { show: true, placeholder: '请输入标题' },
//           type: 'input',
//           column: {
//             minWidth: 200,
//             showOverflowTooltip: true,
//           },
//           form: {
//             rules: [{ required: true, message: '请输入知识库标题' }],
//             component: { placeholder: '请输入知识库标题' },
//           },
//         },
//         category: {
//           title: '所属分类',
//           search: { show: true },
//           type: 'dict-select',
//           dict: dict({
//             data: [
//               { label: '技术文档', value: 'tech' },
//               { label: '产品说明', value: 'product' },
//               { label: '操作指南', value: 'guide' },
//               { label: '常见问题', value: 'faq' },
//               { label: '其他', value: 'other' },
//             ],
//           }),
//           form: {
//             rules: [{ required: true, message: '请选择所属分类' }],
//             component: { placeholder: '请选择所属分类' },
//           },
//         },
//         visibility: {
//           title: '可见范围',
//           search: { show: true },
//           type: 'dict-radio',
//           dict: dict({
//             data: [
//               { label: '公共', value: 'public' },
//               { label: '私密', value: 'private' },
//             ],
//           }),
//           form: {
//             rules: [{ required: true, message: '请选择可见范围' }],
//             component: {
//               props: {
//                 type: 'radio',
//               },
//             },
//           },
//           column: {
//             component: {
//               name: 'dict-tag',
//             },
//           },
//         },
//         description: {
//           title: '知识库描述',
//           type: 'textarea',
//           column: {
//             minWidth: 200,
//             showOverflowTooltip: true,
//           },
//           form: {
//             rules: [{ required: true, message: '请输入知识库描述' }],
//             component: {
//               placeholder: '请输入知识库描述',
//               rows: 3,
//             },
//           },
//         },
//         ...commonCrudConfig(),
//       },
//     },
//   };
// };