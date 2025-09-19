<template>
  <div class="repository-list-container">
    <!-- 页面标题 + 新增按钮 -->
    <div class="page-header">
      <el-page-header content="知识库管理" />
      <el-button type="primary" @click="handleAdd">新增知识库</el-button>
    </div>

    <!-- 筛选条件 -->
    <el-card shadow="hover" class="filter-card">
      <el-form :model="filterForm" inline label-width="100px">
        <!-- 状态筛选 -->
        <el-form-item label="知识库状态">
          <el-select
            v-model="filterForm.status"
            placeholder="全部状态"
            @change="fetchRepoList"
          >
            <el-option label="全部" value="" />
            <el-option label="正常" value="normal" />
            <el-option label="归档" value="archived" />
          </el-select>
        </el-form-item>
        <!-- 类型筛选 -->
        <el-form-item label="知识库类型">
          <el-select
            v-model="filterForm.type_id"
            placeholder="全部类型"
            @change="fetchRepoList"
          >
            <el-option label="全部" value="" />
            <el-option label="产品文档" value="1" />
            <el-option label="技术文档" value="2" />
            <el-option label="培训资料" value="3" />
          </el-select>
        </el-form-item>
        <!-- 搜索框 -->
        <el-form-item>
          <el-input
            v-model="filterForm.search"
            placeholder="搜索知识库名称/描述"
            @keyup.enter="fetchRepoList"
            clearable
          >
            <template #append>
              <el-button icon="el-icon-search" @click="fetchRepoList" />
            </template>
          </el-input>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 知识库列表 -->
    <el-table
      v-loading="loading"
      :data="repoList"
      border
      stripe
      row-key="id"
      style="width: 100%; margin-top: 16px"
    >
      <el-table-column label="ID" prop="id" width="80" align="center" />
      <el-table-column label="知识库名称" prop="name">
        <template #default="scope">
          <el-link @click="handleViewDetail(scope.row.id)">{{ scope.row.name }}</el-link>
        </template>
      </el-table-column>
      <el-table-column label="类型" prop="type_id" width="120" align="center">
        <template #default="scope">
          <el-tag :type="getTypeTagType(scope.row.type_id)">
            {{ getTypeName(scope.row.type_id) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="负责人ID" prop="master" width="120" align="center" />
      <el-table-column label="可见范围" prop="limits_label" width="140" align="center">
        <template #default="scope">
          <el-tag :type="scope.row.limits === 0 ? 'success' : 'info'">
            {{ scope.row.limits_label }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" prop="status_label" width="120" align="center">
        <template #default="scope">
          <el-tag
            :type="
              scope.row.status === 'normal'
                ? 'success'
                : scope.row.recycle === 1
                  ? 'danger'
                  : 'warning'
            "
          >
            {{ scope.row.status_label }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="创建时间" prop="create_time" width="200" align="center" />
      <el-table-column label="操作" width="240" align="center">
        <template #default="scope">
          <!-- 编辑按钮 -->
          <el-button
            type="text"
            icon="el-icon-edit"
            @click="handleEdit(scope.row)"
            :disabled="scope.row.recycle === 1"
          >
            编辑
          </el-button>
          <!-- 归档/恢复按钮 -->
          <el-button
            type="text"
            :icon="scope.row.status === 'normal' ? 'el-icon-box' : 'el-icon-refresh-left'"
            :color="scope.row.status === 'normal' ? 'warning' : 'success'"
            @click="handleArchiveOrRestore(scope.row.id, scope.row.status)"
            :disabled="scope.row.recycle === 1"
          >
            {{ scope.row.status === 'normal' ? '归档' : '恢复正常' }}
          </el-button>
          <!-- 排序按钮（仅正常状态可排序） -->
          <el-button
            type="text"
            icon="el-icon-top"
            @click="handleSort(scope.row.id, 'up')"
            :disabled="scope.row.status !== 'normal' || scope.row.recycle === 1"
          />
          <el-button
            type="text"
            icon="el-icon-bottom"
            @click="handleSort(scope.row.id, 'down')"
            :disabled="scope.row.status !== 'normal' || scope.row.recycle === 1"
          />
          <!-- 删除/回收按钮 -->
          <el-button
            type="text"
            icon="el-icon-delete"
            color="danger"
            @click="handleDelete(scope.row.id)"
          >
            {{ scope.row.recycle === 1 ? '彻底删除' : '移至回收站' }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <el-pagination
      v-if="total > 0"
      :current-page="pageNum"
      :page-size="pageSize"
      :total="total"
      layout="total, sizes, prev, pager, next, jumper"
      @size-change="handlePageSizeChange"
      @current-change="handlePageNumChange"
      style="margin-top: 16px; text-align: right"
    />

    <!-- 新增/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? '新增知识库' : '编辑知识库'"
      width="600px"
    >
      <el-form
        ref="repoFormRef"
        :model="repoForm"
        label-width="120px"
        :rules="repoFormRules"
      >
        <el-form-item label="知识库名称" prop="name">
          <el-input v-model="repoForm.name" placeholder="请输入知识库名称" />
        </el-form-item>
        <el-form-item label="知识库类型" prop="type_id">
          <el-select v-model="repoForm.type_id" placeholder="请选择知识库类型">
            <el-option label="产品文档" value="1" />
            <el-option label="技术文档" value="2" />
            <el-option label="培训资料" value="3" />
          </el-select>
        </el-form-item>
        <el-form-item label="负责人ID" prop="master">
          <el-input v-model="repoForm.master" placeholder="请输入负责人用户ID" />
        </el-form-item>
        <el-form-item label="可见范围" prop="limits">
          <el-radio-group v-model="repoForm.limits">
            <el-radio label="0">无限制</el-radio>
            <el-radio label="1">有限制</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="图标路径" prop="icon_url">
          <el-input v-model="repoForm.icon_url" placeholder="输入图标路径" />
        </el-form-item>
        <el-form-item label="知识库描述" prop="description">
          <el-input
            v-model="repoForm.description"
            type="textarea"
            rows="3"
            placeholder="描述知识库用途"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleFormSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 归档原因弹窗 -->
    <el-dialog v-model="archiveDialogVisible" title="归档知识库" width="500px">
      <el-form :model="archiveForm" label-width="100px">
        <el-form-item label="归档原因">
          <el-input
            v-model="archiveForm.archived_desc"
            type="textarea"
            rows="3"
            placeholder="请输入归档原因"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="archiveDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleArchiveSubmit">确定归档</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, getCurrentInstance } from 'vue';
import { ElMessage, ElMessageBox, ElLoading } from 'element-plus';
import { repositoryApi } from './api';

// 页面状态
const loading = ref(false); // 列表加载中
const repoList = ref([]); // 知识库列表数据
const total = ref(0); // 总条数
const pageNum = ref(1); // 当前页码
const pageSize = ref(10); // 每页条数

// 筛选表单
const filterForm = reactive({
  status: '', // 状态筛选（normal/archived）
  type_id: '', // 类型筛选
  search: '' // 搜索关键词
});

// 新增/编辑弹窗
const dialogVisible = ref(false);
const dialogType = ref('add'); // add/edit
const repoFormRef = ref(null);
const repoForm = reactive({
  id: '',
  name: '',
  type_id: '',
  master: '',
  limits: 0, // 默认无限制
  icon_url: '',
  description: ''
});
// 表单校验规则
const repoFormRules = reactive({
  name: [{ required: true, message: '请输入知识库名称', trigger: 'blur' }],
  type_id: [{ required: true, message: '请选择知识库类型', trigger: 'change' }],
  master: [{ required: true, message: '请输入负责人ID', trigger: 'blur' }],
  limits: [{ required: true, message: '请选择可见范围', trigger: 'change' }]
});

// 归档弹窗
const archiveDialogVisible = ref(false);
const archiveForm = reactive({
  repo_id: '', // 待归档的知识库ID
  archived_desc: '' // 归档原因
});

// 页面加载时获取列表
onMounted(() => {
  fetchRepoList();
});

/**
 * 获取知识库列表（支持筛选、分页）
 */
const fetchRepoList = async () => {
  loading.value = true;
  try {
    const params = {
      page: pageNum.value,
      limit: pageSize.value,
      ...(filterForm.status && { status: filterForm.status }),
      ...(filterForm.type_id && { type_id: filterForm.type_id }),
      ...(filterForm.search && { search: filterForm.search }),
    };

    const res = await repositoryApi.getRepoList(params);

    // 适配后端响应格式：code=2000为成功，数据在data数组中
    if (res.code === 2000) {
      repoList.value = res.data;
      total.value = res.total;
    } else {
      ElMessage.error(res.msg || '获取知识库列表失败');
    }
  } catch (err) {
    console.error('获取知识库列表错误:', err);
    ElMessage.error('获取知识库列表失败：网络异常');
  } finally {
    loading.value = false;
  }
};

/**
 * 分页相关操作
 */
// 每页条数改变
const handlePageSizeChange = (val) => {
  pageSize.value = val;
  pageNum.value = 1; // 重置为第一页
  fetchRepoList();
};
// 当前页码改变
const handlePageNumChange = (val) => {
  pageNum.value = val;
  fetchRepoList();
};

/**
 * 新增/编辑操作
 */
// 打开新增弹窗
const handleAdd = () => {
  dialogType.value = 'add';
  // 重置表单
  repoForm.id = '';
  repoForm.name = '';
  repoForm.type_id = '';
  repoForm.master = '';
  repoForm.limits = 0;
  repoForm.icon_url = '';
  repoForm.description = '';
  dialogVisible.value = true;
};

// 打开编辑弹窗
const handleEdit = (row) => {
  dialogType.value = 'edit';
  // 回显数据
  repoForm.id = row.id;
  repoForm.name = row.name;
  repoForm.type_id = row.type_id;
  repoForm.master = row.master;
  repoForm.limits = row.limits;
  repoForm.icon_url = row.icon_url || '';
  repoForm.description = row.description || '';
  dialogVisible.value = true;
};
// 表单提交（新增/编辑）
const handleFormSubmit = async () => {
  const valid = await repoFormRef.value.validate();
  if (!valid) return;

  try {
    let res;
    if (dialogType.value === 'add') {
      res = await repositoryApi.createRepo(repoForm);
    } else {
      res = await repositoryApi.updateRepo(repoForm.id, repoForm);
    }

    if (res.code === 2000) {
      ElMessage.success(`${dialogType.value === 'add' ? '新增' : '编辑'}知识库成功！`);
      dialogVisible.value = false;
      fetchRepoList();
    } else {
      // 优化：显示后端返回的具体错误（如“负责人ID不存在”）
      ElMessage.error(`操作失败：${res.msg || '系统异常'}`);
    }
  } catch (err) {
    console.error(`${dialogType.value === 'add' ? '新增' : '编辑'}错误:`, err);
    // 优化：区分网络错误和其他错误
    if (err.message.includes('Network Error')) {
      ElMessage.error('操作失败：网络连接异常，请检查网络');
    } else {
      ElMessage.error('操作失败：系统内部错误，请联系管理员');
    }
  }
};
// const handleFormSubmit = async () => {
//   // 表单校验
//   const valid = await repoFormRef.value.validate();
//   if (!valid) return;
//
//   try {
//     let res;
//     if (dialogType.value === 'add') {
//       // 新增知识库
//       res = await repositoryApi.createRepo(repoForm);
//     } else {
//       // 编辑知识库（全量更新）
//       res = await repositoryApi.updateRepo(repoForm.id, repoForm);
//     }
//
//     // 处理响应
//     if (res.code === 2000) {
//       ElMessage.success(`${dialogType.value === 'add' ? '新增' : '编辑'}知识库成功！`);
//       dialogVisible.value = false;
//       fetchRepoList();
//     } else {
//       ElMessage.error(res.msg || `${dialogType.value === 'add' ? '新增' : '编辑'}失败`);
//     }
//   } catch (err) {
//     console.error(`${dialogType.value === 'add' ? '新增' : '编辑'}错误:`, err);
//     ElMessage.error(`${dialogType.value === 'add' ? '新增' : '编辑'}知识库失败：网络异常`);
//   }
// };

/**
 * 归档/恢复操作
 */
// 打开归档弹窗或直接恢复
const handleArchiveOrRestore = (repoId, status) => {
  if (status === 'normal') {
    // 正常状态 → 归档：需输入归档原因
    archiveForm.repo_id = repoId;
    archiveForm.archived_desc = '';
    archiveDialogVisible.value = true;
  } else {
    // 归档状态 → 恢复：直接调用接口
    handleRestore(repoId);
  }
};

// 提交归档
const handleArchiveSubmit = async () => {
  if (!archiveForm.archived_desc.trim()) {
    ElMessage.warning('请输入归档原因！');
    return;
  }

  try {
    const res = await repositoryApi.archiveRepo({
      repo_id: archiveForm.repo_id,
      archived_desc: archiveForm.archived_desc
    });

    if (res.code === 2000) {
      ElMessage.success('知识库归档成功！');
      archiveDialogVisible.value = false;
      fetchRepoList();
    } else {
      ElMessage.error(res.msg || '归档失败');
    }
  } catch (err) {
    console.error('归档错误:', err);
    ElMessage.error('归档失败：网络异常');
  }
};

// 恢复知识库（从归档/回收站）
const handleRestore = async (repoId) => {
  try {
    const res = await repositoryApi.restoreRepo({ repo_id: repoId });

    if (res.code === 2000) {
      ElMessage.success('知识库恢复成功！');
      fetchRepoList();
    } else {
      ElMessage.error(res.msg || '恢复失败');
    }
  } catch (err) {
    console.error('恢复错误:', err);
    ElMessage.error('恢复失败：网络异常');
  }
};

/**
 * 排序操作（上移/下移）
 */
const handleSort = async (repoId, direction) => {
  try {
    const res = await repositoryApi.sortRepo({ repo_id: repoId, direction });

    if (res.code === 2000) {
      ElMessage.success(`知识库${direction === 'up' ? '上移' : '下移'}成功！`);
      fetchRepoList(); // 刷新列表显示最新排序
    } else {
      ElMessage.error(res.msg || `排序失败：已到达${direction}移边界`);
    }
  } catch (err) {
    console.error('排序错误:', err);
    ElMessage.error('排序失败：网络异常');
  }
};

/**
 * 删除操作
 */
const handleDelete = async (repoId) => {
  // 确认弹窗
  const confirmResult = await ElMessageBox.confirm(
    '确定要执行此操作吗？删除后可能无法恢复！',
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).catch(() => false);

  if (!confirmResult) return;

  try {
    const res = await repositoryApi.deleteRepo(repoId);

    if (res.code === 2000) {
      ElMessage.success('操作成功！');
      fetchRepoList();
    } else {
      ElMessage.error(res.msg || '操作失败');
    }
  } catch (err) {
    console.error('删除错误:', err);
    ElMessage.error('操作失败：网络异常');
  }
};

/**
 * 辅助函数（类型名称/标签样式映射）
 */
// 根据type_id获取类型名称
const getTypeName = (typeId) => {
  const typeMap = {
    '1': '产品文档',
    '2': '技术文档',
    '3': '培训资料'
  };
  return typeMap[typeId] || '未知类型';
};

// 根据type_id获取标签样式
const getTypeTagType = (typeId) => {
  const typeTagMap = {
    '1': 'primary',
    '2': 'success',
    '3': 'info'
  };
  return typeTagMap[typeId] || 'default';
};

/**
 * 跳转详情页
 */
import { useRouter } from 'vue-router';

// 2. 在 setup 顶层获取路由实例（确保在组件上下文中）
const router = useRouter();
// 3. 在函数中直接使用路由实例
const handleViewDetail = (id) => {
  // 1. 解析目标路由的完整URL（基于路由配置生成）
  const detailRoute = router.resolve({
    name: 'mmOverview', // 目标详情页的路由名称（确保与路由配置一致）
    params: { id } // 传递知识库ID参数（与现有逻辑一致）
  });
  // 2. 新窗口打开详情页（_blank 表示新窗口）
  window.open(detailRoute.href, '_blank');
  // router.push({
  //   name: 'mmOverview',
  //   params: {id}
  // });
}
</script>

<style scoped>
.repository-list-container {
  padding: 20px;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.filter-card {
  margin-bottom: 16px;
}
</style>
