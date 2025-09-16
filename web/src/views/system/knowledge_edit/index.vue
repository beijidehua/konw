<!--<template>-->
<!--  <div class="knowledge-container">-->
<!--    &lt;!&ndash; 顶部操作区域 &ndash;&gt;-->
<!--    <div class="header-actions">-->
<!--      <div class="left">-->
<!--        <el-input-->
<!--          v-model="searchKeyword"-->
<!--          placeholder="请输入知识库名称"-->
<!--          class="search-input"-->
<!--          @keyup.enter="handleSearch"-->
<!--        >-->
<!--          <template #suffix>-->
<!--            <el-icon><Search /></el-icon>-->
<!--          </template>-->
<!--        </el-input>-->
<!--      </div>-->
<!--      <div class="right">-->
<!--        <el-button type="primary" @click="handleAdd">-->
<!--          <el-icon><Plus /></el-icon>新增知识库-->
<!--        </el-button>-->
<!--      </div>-->
<!--    </div>-->

<!--    &lt;!&ndash; 知识库列表 &ndash;&gt;-->
<!--    <div class="knowledge-list">-->
<!--      <el-table :data="tableData" style="width: 100%">-->
<!--        <el-table-column prop="icon" label="" width="60">-->
<!--          <template #default>-->
<!--            <el-icon size="20" color="#409EFF"><Document /></el-icon>-->
<!--          </template>-->
<!--        </el-table-column>-->
<!--        <el-table-column prop="title" label="知识库名称" />-->
<!--        <el-table-column prop="creator" label="创建人" width="120" />-->
<!--        <el-table-column prop="createTime" label="创建时间" width="180" />-->
<!--        <el-table-column label="操作" width="180">-->
<!--          <template #default="scope">-->
<!--            <el-button text @click="handleEdit(scope.row)" v-auth="permission.edit">编辑</el-button>-->
<!--            <el-button text @click="handleView(scope.row)">查看</el-button>-->
<!--            <el-button text type="danger" @click="handleDelete(scope.row)" v-auth="permission.delete">删除</el-button>-->
<!--          </template>-->
<!--        </el-table-column>-->
<!--      </el-table>-->

<!--      &lt;!&ndash; 分页 &ndash;&gt;-->
<!--      <div class="pagination">-->
<!--        <el-pagination-->
<!--          v-model:current-page="currentPage"-->
<!--          v-model:page-size="pageSize"-->
<!--          :total="total"-->
<!--          :page-sizes="[10, 20, 50, 100]"-->
<!--          @size-change="handleSizeChange"-->
<!--          @current-change="handleCurrentChange"-->
<!--          layout="total, sizes, prev, pager, next"-->
<!--        />-->
<!--      </div>-->
<!--    </div>-->

<!--    &lt;!&ndash; 新增/编辑对话框 &ndash;&gt;-->
<!--    <el-dialog-->
<!--      v-model="dialogVisible"-->
<!--      :title="dialogTitle"-->
<!--      width="600px"-->
<!--      :close-on-click-modal="false"-->
<!--    >-->
<!--      <el-form-->
<!--        ref="formRef"-->
<!--        :model="formData"-->
<!--        :rules="formRules"-->
<!--        label-width="100px"-->
<!--      >-->
<!--        <el-form-item label="名称" prop="title">-->
<!--          <el-input v-model="formData.title" placeholder="请输入知识库名称" />-->
<!--        </el-form-item>-->
<!--        <el-form-item label="描述" prop="description">-->
<!--          <el-input-->
<!--            v-model="formData.description"-->
<!--            type="textarea"-->
<!--            :rows="3"-->
<!--            placeholder="请输入知识库描述"-->
<!--          />-->
<!--        </el-form-item>-->
<!--        <el-form-item label="文件" prop="file">-->
<!--          <el-upload-->
<!--            class="upload-demo"-->
<!--            action="/api/upload"-->
<!--            :on-success="handleUploadSuccess"-->
<!--            :before-upload="beforeUpload"-->
<!--            multiple-->
<!--            :limit="5"-->
<!--          >-->
<!--            <el-button type="primary">点击上传</el-button>-->
<!--            <template #tip>-->
<!--              <div class="el-upload__tip">支持 pdf、word、txt 格式，单个文件不超过 10MB</div>-->
<!--            </template>-->
<!--          </el-upload>-->
<!--        </el-form-item>-->
<!--      </el-form>-->
<!--      <template #footer>-->
<!--        <el-button @click="dialogVisible = false">取消</el-button>-->
<!--        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">确定</el-button>-->
<!--      </template>-->
<!--    </el-dialog>-->
<!--  </div>-->
<!--</template>-->

<!--<script lang="ts" setup name="Knowledge">-->
<!--import { ref, onMounted } from 'vue'-->
<!--import type { FormInstance, FormRules, UploadProps } from 'element-plus'-->
<!--import { Search, Plus, Document } from '@element-plus/icons-vue'-->
<!--import { getKnowledgeList, createKnowledge, deleteKnowledge } from './api'-->
<!--import { ElMessageBox, ElMessage } from 'element-plus'-->
<!--import { successMessage } from '/@/utils/message'-->

<!--// 权限定义-->
<!--const permission = {-->
<!--  add: 'knowledge:add',-->
<!--  edit: 'knowledge:edit',-->
<!--  delete: 'knowledge:delete'-->
<!--}-->

<!--const searchKeyword = ref('')-->
<!--const currentPage = ref(1)-->
<!--const pageSize = ref(10)-->
<!--const total = ref(0)-->
<!--const tableData = ref([])-->
<!--// 在原有的 ref 定义下添加-->
<!--const dialogVisible = ref(false)-->
<!--const dialogTitle = ref('新增知识库')-->
<!--const formRef = ref<FormInstance>()-->
<!--const submitLoading = ref(false)-->

<!--// 获取列表数据-->
<!--const loadData = async () => {-->
<!--  const params = {-->
<!--    page: currentPage.value,-->
<!--    limit: pageSize.value,-->
<!--    keyword: searchKeyword.value-->
<!--  }-->
<!--  const res = await getKnowledgeList(params)-->
<!--  tableData.value = res.data.list-->
<!--  total.value = res.data.total-->
<!--}-->
<!--// 表单数据-->
<!--const formData = ref({-->
<!--  title: '',-->
<!--  description: '',-->
<!--  files: [] as string[]-->
<!--})-->
<!--// 表单校验规则-->
<!--const formRules: FormRules = {-->
<!--  title: [-->
<!--    { required: true, message: '请输入知识库名称', trigger: 'blur' },-->
<!--    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }-->
<!--  ],-->
<!--  description: [-->
<!--    { required: true, message: '请输入知识库描述', trigger: 'blur' }-->
<!--  ]-->
<!--}-->
<!--// 文件上传前的验证-->
<!--const beforeUpload: UploadProps['beforeUpload'] = (file) => {-->
<!--  const allowTypes = ['application/pdf', 'application/msword', 'text/plain']-->
<!--  const isValidType = allowTypes.includes(file.type)-->
<!--  if (!isValidType) {-->
<!--    ElMessage.error('只能上传 PDF/Word/TXT 格式的文件!')-->
<!--    return false-->
<!--  }-->

<!--  const isLt10M = file.size / 1024 / 1024 < 10-->
<!--  if (!isLt10M) {-->
<!--    ElMessage.error('文件大小不能超过 10MB!')-->
<!--    return false-->
<!--  }-->
<!--  return true-->
<!--}-->
<!--// 文件上传成功的回调-->
<!--const handleUploadSuccess: UploadProps['onSuccess'] = (response) => {-->
<!--  formData.value.files.push(response.data)-->
<!--}-->
<!--// 搜索-->
<!--const handleSearch = () => {-->
<!--  currentPage.value = 1-->
<!--  loadData()-->
<!--}-->

<!--// 新增-->
<!--// 修改原有的 handleAdd 方法-->
<!--const handleAdd = () => {-->
<!--  dialogVisible.value = true-->
<!--  dialogTitle.value = '新增知识库'-->
<!--  formData.value = {-->
<!--    title: '',-->
<!--    description: ''-->
<!--  }-->
<!--}-->
<!--// 表单提交-->
<!--const handleSubmit = async () => {-->
<!--  if (!formRef.value) return-->

<!--  await formRef.value.validate(async (valid) => {-->
<!--    if (valid) {-->
<!--      submitLoading.value = true-->
<!--      try {-->
<!--        await createKnowledge(formData.value)-->
<!--        successMessage('创建成功')-->
<!--        dialogVisible.value = false-->
<!--        loadData()-->
<!--      } catch (error) {-->
<!--        console.error(error)-->
<!--      } finally {-->
<!--        submitLoading.value = false-->
<!--      }-->
<!--    }-->
<!--  })-->
<!--}-->
<!--// 编辑-->
<!--const handleEdit = (row) => {-->
<!--  router.push(`/system/knowledge/edit?id=${row.id}`)-->
<!--}-->

<!--// 查看-->
<!--const handleView = (row) => {-->
<!--  router.push(`/system/knowledge/view?id=${row.id}`)-->
<!--}-->

<!--// 删除-->
<!--const handleDelete = async (row) => {-->
<!--  await ElMessageBox.confirm('确认删除该知识库?', '提示', {-->
<!--    type: 'warning'-->
<!--  })-->
<!--  await deleteKnowledge(row.id)-->
<!--  successMessage('删除成功')-->
<!--  loadData()-->
<!--}-->

<!--// 分页-->
<!--const handleSizeChange = (val: number) => {-->
<!--  pageSize.value = val-->
<!--  loadData()-->
<!--}-->

<!--const handleCurrentChange = (val: number) => {-->
<!--  currentPage.value = val-->
<!--  loadData()-->
<!--}-->

<!--onMounted(() => {-->
<!--  loadData()-->
<!--})-->
<!--</script>-->

<!--<style lang="scss" scoped>-->
<!--.knowledge-container {-->
<!--  padding: 20px;-->
<!--  background: #f5f7fa;-->
<!--  min-height: calc(100vh - 84px);-->

<!--  .header-actions {-->
<!--    display: flex;-->
<!--    justify-content: space-between;-->
<!--    align-items: center;-->
<!--    margin-bottom: 16px;-->

<!--    .left {-->
<!--      .search-input {-->
<!--        width: 300px;-->
<!--      }-->
<!--    }-->
<!--  }-->

<!--  .knowledge-list {-->
<!--    background: #fff;-->
<!--    padding: 20px;-->
<!--    border-radius: 4px;-->
<!--  }-->

<!--  .pagination {-->
<!--    margin-top: 16px;-->
<!--    display: flex;-->
<!--    justify-content: flex-end;-->
<!--  }-->
<!--}-->

<!--.upload-demo {-->
<!--  :deep(.el-upload-list) {-->
<!--    width: 100%;-->
<!--  }-->
<!--}-->
<!--</style>-->



<!--&lt;!&ndash;222&ndash;&gt;-->
<!--<template>-->
<!--  <div class="knowledge-container">-->
<!--    &lt;!&ndash; 顶部操作区域 &ndash;&gt;-->
<!--    <div class="header-actions">-->
<!--      <div class="left">-->
<!--        <el-input-->
<!--          v-model="searchKeyword"-->
<!--          placeholder="请输入知识库名称"-->
<!--          class="search-input"-->
<!--          @keyup.enter="handleSearch"-->
<!--        >-->
<!--          <template #suffix>-->
<!--            <el-icon><Search /></el-icon>-->
<!--          </template>-->
<!--        </el-input>-->
<!--      </div>-->
<!--      <div class="right">-->
<!--        <el-button type="primary" @click="handleAdd">-->
<!--          <el-icon><Plus /></el-icon>新增知识库-->
<!--        </el-button>-->
<!--      </div>-->
<!--    </div>-->

<!--    &lt;!&ndash; 知识库列表 &ndash;&gt;-->
<!--    <div class="knowledge-list">-->
<!--      <el-table :data="tableData" style="width: 100%">-->
<!--        <el-table-column prop="icon" label="" width="60">-->
<!--          <template #default>-->
<!--            <el-icon size="20" color="#409EFF"><Document /></el-icon>-->
<!--          </template>-->
<!--        </el-table-column>-->
<!--        <el-table-column prop="title" label="知识库名称" />-->
<!--        <el-table-column prop="category" label="分类" width="120" />-->
<!--        <el-table-column prop="visibility" label="可见范围" width="120" />-->
<!--        <el-table-column prop="creator" label="创建人" width="120" />-->
<!--        <el-table-column prop="createTime" label="创建时间" width="180" />-->
<!--        <el-table-column label="操作" width="180">-->
<!--          <template #default="scope">-->
<!--            <el-button text @click="handleEdit(scope.row)" v-auth="permission.edit">编辑</el-button>-->
<!--            <el-button text @click="handleView(scope.row)">查看</el-button>-->
<!--            <el-button text type="danger" @click="handleDelete(scope.row)" v-auth="permission.delete">删除</el-button>-->
<!--          </template>-->
<!--        </el-table-column>-->
<!--      </el-table>-->

<!--      &lt;!&ndash; 分页 &ndash;&gt;-->
<!--      <div class="pagination">-->
<!--        <el-pagination-->
<!--          v-model:current-page="currentPage"-->
<!--          v-model:page-size="pageSize"-->
<!--          :total="total"-->
<!--          :page-sizes="[10, 20, 50, 100]"-->
<!--          @size-change="handleSizeChange"-->
<!--          @current-change="handleCurrentChange"-->
<!--          layout="total, sizes, prev, pager, next"-->
<!--        />-->
<!--      </div>-->
<!--    </div>-->

<!--    &lt;!&ndash; 新增/编辑对话框 &ndash;&gt;-->
<!--    <el-dialog-->
<!--      v-model="dialogVisible"-->
<!--      :title="dialogTitle"-->
<!--      width="600px"-->
<!--      :close-on-click-modal="false"-->
<!--    >-->
<!--      <el-form-->
<!--        ref="formRef"-->
<!--        :model="formData"-->
<!--        :rules="formRules"-->
<!--        label-width="100px"-->
<!--      >-->
<!--        <el-form-item label="知识库名称" prop="title">-->
<!--          <el-input v-model="formData.title" placeholder="请输入知识库名称" />-->
<!--        </el-form-item>-->
<!--        <el-form-item label="知识库分类" prop="category">-->
<!--          <el-select v-model="formData.category" placeholder="请选择知识库分类">-->
<!--            <el-option label="技术文档" value="tech" />-->
<!--            <el-option label="产品说明" value="product" />-->
<!--            <el-option label="操作指南" value="guide" />-->
<!--            <el-option label="常见问题" value="faq" />-->
<!--            <el-option label="其他" value="other" />-->
<!--          </el-select>-->
<!--        </el-form-item>-->
<!--        <el-form-item label="可见范围" prop="visibility">-->
<!--          <el-radio-group v-model="formData.visibility">-->
<!--            <el-radio label="public">公共</el-radio>-->
<!--            <el-radio label="private">私密</el-radio>-->
<!--          </el-radio-group>-->
<!--          <div class="visibility-tips">-->
<!--            <div v-if="formData.visibility === 'public'">-->
<!--              公共知识库，初次创建后所有人可查看，仅自己可编辑，其余人员可申请编辑权限。-->
<!--            </div>-->
<!--            <div v-else>-->
<!--              私密知识库，初次创建后仅自己可查看，仅自己可编辑，其余人员可申请查看权限。-->
<!--            </div>-->
<!--          </div>-->
<!--        </el-form-item>-->
<!--        <el-form-item label="知识库描述" prop="description">-->
<!--          <el-input-->
<!--            v-model="formData.description"-->
<!--            type="textarea"-->
<!--            :rows="3"-->
<!--            placeholder="请输入知识库描述"-->
<!--          />-->
<!--        </el-form-item>-->
<!--      </el-form>-->
<!--      <template #footer>-->
<!--        <el-button @click="dialogVisible = false">取消</el-button>-->
<!--        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">确认</el-button>-->
<!--      </template>-->
<!--    </el-dialog>-->
<!--  </div>-->
<!--</template>-->

<!--<script lang="ts" setup name="Knowledge">-->
<!--import { ref, onMounted } from 'vue'-->
<!--import type { FormInstance, FormRules } from 'element-plus'-->
<!--import { Search, Plus, Document } from '@element-plus/icons-vue'-->
<!--import { getKnowledgeList, createKnowledge, deleteKnowledge } from './api'-->
<!--import { ElMessageBox, ElMessage } from 'element-plus'-->
<!--import { successMessage } from '/@/utils/message'-->

<!--// 权限定义-->
<!--const permission = {-->
<!--  add: 'knowledge:add',-->
<!--  edit: 'knowledge:edit',-->
<!--  delete: 'knowledge:delete'-->
<!--}-->

<!--const searchKeyword = ref('')-->
<!--const currentPage = ref(1)-->
<!--const pageSize = ref(10)-->
<!--const total = ref(0)-->
<!--const tableData = ref([])-->
<!--const dialogVisible = ref(false)-->
<!--const dialogTitle = ref('新建知识库')-->
<!--const formRef = ref<FormInstance>()-->
<!--const submitLoading = ref(false)-->

<!--// 获取列表数据-->
<!--const loadData = async () => {-->
<!--  const params = {-->
<!--    page: currentPage.value,-->
<!--    limit: pageSize.value,-->
<!--    keyword: searchKeyword.value-->
<!--  }-->
<!--  const res = await getKnowledgeList(params)-->
<!--  tableData.value = res.data.list-->
<!--  total.value = res.data.total-->
<!--}-->

<!--// 表单数据-->
<!--const formData = ref({-->
<!--  title: '',-->
<!--  category: '',-->
<!--  visibility: 'public',-->
<!--  description: ''-->
<!--})-->

<!--// 表单校验规则-->
<!--const formRules: FormRules = {-->
<!--  title: [-->
<!--    { required: true, message: '请输入知识库名称', trigger: 'blur' },-->
<!--    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }-->
<!--  ],-->
<!--  category: [-->
<!--    { required: true, message: '请选择知识库分类', trigger: 'change' }-->
<!--  ],-->
<!--  visibility: [-->
<!--    { required: true, message: '请选择可见范围', trigger: 'change' }-->
<!--  ],-->
<!--  description: [-->
<!--    { required: true, message: '请输入知识库描述', trigger: 'blur' }-->
<!--  ]-->
<!--}-->

<!--// 搜索-->
<!--const handleSearch = () => {-->
<!--  currentPage.value = 1-->
<!--  loadData()-->
<!--}-->

<!--// 新增-->
<!--const handleAdd = () => {-->
<!--  dialogVisible.value = true-->
<!--  dialogTitle.value = '新建知识库'-->
<!--  formData.value = {-->
<!--    title: '',-->
<!--    category: '',-->
<!--    visibility: 'public',-->
<!--    description: ''-->
<!--  }-->
<!--}-->

<!--// 表单提交-->
<!--const handleSubmit = async () => {-->
<!--  if (!formRef.value) return-->

<!--  await formRef.value.validate(async (valid) => {-->
<!--    if (valid) {-->
<!--      submitLoading.value = true-->
<!--      try {-->
<!--        await createKnowledge(formData.value)-->
<!--        successMessage('创建成功')-->
<!--        dialogVisible.value = false-->
<!--        loadData()-->
<!--      } catch (error) {-->
<!--        console.error(error)-->
<!--      } finally {-->
<!--        submitLoading.value = false-->
<!--      }-->
<!--    }-->
<!--  })-->
<!--}-->

<!--// 编辑-->
<!--const handleEdit = (row) => {-->
<!--  // 这里需要实现编辑功能-->
<!--  console.log('编辑', row)-->
<!--}-->

<!--// 查看-->
<!--const handleView = (row) => {-->
<!--  // 这里需要实现查看功能-->
<!--  console.log('查看', row)-->
<!--}-->

<!--// 删除-->
<!--const handleDelete = async (row) => {-->
<!--  await ElMessageBox.confirm('确认删除该知识库?', '提示', {-->
<!--    type: 'warning'-->
<!--  })-->
<!--  await deleteKnowledge(row.id)-->
<!--  successMessage('删除成功')-->
<!--  loadData()-->
<!--}-->

<!--// 分页-->
<!--const handleSizeChange = (val: number) => {-->
<!--  pageSize.value = val-->
<!--  loadData()-->
<!--}-->

<!--const handleCurrentChange = (val: number) => {-->
<!--  currentPage.value = val-->
<!--  loadData()-->
<!--}-->

<!--onMounted(() => {-->
<!--  loadData()-->
<!--})-->
<!--</script>-->

<!--<style lang="scss" scoped>-->
<!--.knowledge-container {-->
<!--  padding: 20px;-->
<!--  background: #f5f7fa;-->
<!--  min-height: calc(100vh - 84px);-->

<!--  .header-actions {-->
<!--    display: flex;-->
<!--    justify-content: space-between;-->
<!--    align-items: center;-->
<!--    margin-bottom: 16px;-->

<!--    .left {-->
<!--      .search-input {-->
<!--        width: 300px;-->
<!--      }-->
<!--    }-->
<!--  }-->

<!--  .knowledge-list {-->
<!--    background: #fff;-->
<!--    padding: 20px;-->
<!--    border-radius: 4px;-->
<!--  }-->

<!--  .pagination {-->
<!--    margin-top: 16px;-->
<!--    display: flex;-->
<!--    justify-content: flex-end;-->
<!--  }-->
<!--}-->

<!--.visibility-tips {-->
<!--  margin-top: 8px;-->
<!--  font-size: 12px;-->
<!--  color: #909399;-->
<!--  line-height: 1.5;-->
<!--}-->
<!--</style>-->



<!--333-->
<!--<template>-->
<!--  <div class="knowledge-container">-->
<!--    &lt;!&ndash; 顶部操作区域 &ndash;&gt;-->
<!--    <div class="header-actions">-->
<!--      <div class="left">-->
<!--        <el-input-->
<!--          v-model="searchKeyword"-->
<!--          placeholder="请输入知识库名称"-->
<!--          class="search-input"-->
<!--          @keyup.enter="handleSearch"-->
<!--        >-->
<!--          <template #suffix>-->
<!--            <el-icon><Search /></el-icon>-->
<!--          </template>-->
<!--        </el-input>-->
<!--      </div>-->
<!--      <div class="right">-->
<!--        <el-button type="primary" @click="handleAdd">-->
<!--          <el-icon><Plus /></el-icon>新增知识库-->
<!--        </el-button>-->
<!--      </div>-->
<!--    </div>-->

<!--    &lt;!&ndash; 知识库列表 &ndash;&gt;-->
<!--    <div class="knowledge-list">-->
<!--      <el-table :data="tableData" style="width: 100%">-->
<!--        <el-table-column prop="icon" label="" width="60">-->
<!--          <template #default>-->
<!--            <el-icon size="20" color="#409EFF"><Document /></el-icon>-->
<!--          </template>-->
<!--        </el-table-column>-->
<!--        <el-table-column prop="title" label="知识库名称" />-->
<!--        <el-table-column prop="category" label="分类" width="120" />-->
<!--        <el-table-column prop="visibility" label="可见范围" width="120" />-->
<!--        <el-table-column prop="creator" label="创建人" width="120" />-->
<!--        <el-table-column prop="createTime" label="创建时间" width="180" />-->
<!--        <el-table-column label="操作" width="180">-->
<!--          <template #default="scope">-->
<!--            <el-button text @click="handleEdit(scope.row)" v-auth="permission.edit">编辑</el-button>-->
<!--            <el-button text @click="handleView(scope.row)">查看</el-button>-->
<!--            <el-button text type="danger" @click="handleDelete(scope.row)" v-auth="permission.delete">删除</el-button>-->
<!--          </template>-->
<!--        </el-table-column>-->
<!--      </el-table>-->

<!--      &lt;!&ndash; 分页 &ndash;&gt;-->
<!--      <div class="pagination">-->
<!--        <el-pagination-->
<!--          v-model:current-page="currentPage"-->
<!--          v-model:page-size="pageSize"-->
<!--          :total="total"-->
<!--          :page-sizes="[10, 20, 50, 100]"-->
<!--          @size-change="handleSizeChange"-->
<!--          @current-change="handleCurrentChange"-->
<!--          layout="total, sizes, prev, pager, next"-->
<!--        />-->
<!--      </div>-->
<!--    </div>-->

<!--    &lt;!&ndash; 新增/编辑对话框 &ndash;&gt;-->
<!--    <el-dialog-->
<!--      v-model="dialogVisible"-->
<!--      :title="dialogTitle"-->
<!--      width="600px"-->
<!--      :close-on-click-modal="false"-->
<!--    >-->
<!--      <el-form-->
<!--        ref="formRef"-->
<!--        :model="formData"-->
<!--        :rules="formRules"-->
<!--        label-width="100px"-->
<!--      >-->
<!--        <el-form-item label="知识库名称" prop="title">-->
<!--          <el-input v-model="formData.title" placeholder="请输入知识库名称" />-->
<!--        </el-form-item>-->
<!--        <el-form-item label="知识库分类" prop="category">-->
<!--          <el-select v-model="formData.category" placeholder="请选择知识库分类">-->
<!--            <el-option label="技术文档" value="tech" />-->
<!--            <el-option label="产品说明" value="product" />-->
<!--            <el-option label="操作指南" value="guide" />-->
<!--            <el-option label="常见问题" value="faq" />-->
<!--            <el-option label="其他" value="other" />-->
<!--          </el-select>-->
<!--        </el-form-item>-->
<!--        <el-form-item label="可见范围" prop="visibility">-->
<!--          <div class="visibility-options">-->
<!--            <div class="visibility-option">-->
<!--              <el-radio v-model="formData.visibility" label="public" class="visibility-radio">-->
<!--                公共-->
<!--              </el-radio>-->
<!--              <div class="visibility-description">-->
<!--                公共知识库，初次创建后所有人员可查看，仅自己可编辑，其余人员可申请编辑权限。-->
<!--              </div>-->
<!--            </div>-->
<!--            <div class="visibility-option">-->
<!--              <el-radio v-model="formData.visibility" label="private" class="visibility-radio">-->
<!--                私密-->
<!--              </el-radio>-->
<!--              <div class="visibility-description">-->
<!--                私密知识库，初次创建后仅自己可查看，仅自己可编辑，其余人员可申请查看权限。-->
<!--              </div>-->
<!--            </div>-->
<!--          </div>-->
<!--        </el-form-item>-->
<!--        <el-form-item label="知识库描述" prop="description">-->
<!--          <el-input-->
<!--            v-model="formData.description"-->
<!--            type="textarea"-->
<!--            :rows="3"-->
<!--            placeholder="请输入知识库描述"-->
<!--          />-->
<!--        </el-form-item>-->
<!--      </el-form>-->
<!--      <template #footer>-->
<!--        <el-button @click="dialogVisible = false">取消</el-button>-->
<!--        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">确认</el-button>-->
<!--      </template>-->
<!--    </el-dialog>-->
<!--  </div>-->
<!--</template>-->

<!--<script lang="ts" setup name="Knowledge">-->
<!--import { ref, onMounted } from 'vue'-->
<!--import type { FormInstance, FormRules } from 'element-plus'-->
<!--import { Search, Plus, Document } from '@element-plus/icons-vue'-->
<!--import { getKnowledgeList, createKnowledge, deleteKnowledge } from './api'-->
<!--import { ElMessageBox, ElMessage } from 'element-plus'-->
<!--import { successMessage } from '/@/utils/message'-->

<!--// 权限定义-->
<!--const permission = {-->
<!--  add: 'knowledge:add',-->
<!--  edit: 'knowledge:edit',-->
<!--  delete: 'knowledge:delete'-->
<!--}-->

<!--const searchKeyword = ref('')-->
<!--const currentPage = ref(1)-->
<!--const pageSize = ref(10)-->
<!--const total = ref(0)-->
<!--const tableData = ref([])-->
<!--const dialogVisible = ref(false)-->
<!--const dialogTitle = ref('新建知识库')-->
<!--const formRef = ref<FormInstance>()-->
<!--const submitLoading = ref(false)-->

<!--// 获取列表数据-->
<!--const loadData = async () => {-->
<!--  const params = {-->
<!--    page: currentPage.value,-->
<!--    limit: pageSize.value,-->
<!--    keyword: searchKeyword.value-->
<!--  }-->
<!--  const res = await getKnowledgeList(params)-->
<!--  tableData.value = res.data.list-->
<!--  total.value = res.data.total-->
<!--}-->

<!--// 表单数据-->
<!--const formData = ref({-->
<!--  title: '',-->
<!--  category: '',-->
<!--  visibility: 'public',-->
<!--  description: ''-->
<!--})-->

<!--// 表单校验规则-->
<!--const formRules: FormRules = {-->
<!--  title: [-->
<!--    { required: true, message: '请输入知识库名称', trigger: 'blur' },-->
<!--    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }-->
<!--  ],-->
<!--  category: [-->
<!--    { required: true, message: '请选择知识库分类', trigger: 'change' }-->
<!--  ],-->
<!--  visibility: [-->
<!--    { required: true, message: '请选择可见范围', trigger: 'change' }-->
<!--  ],-->
<!--  description: [-->
<!--    { required: true, message: '请输入知识库描述', trigger: 'blur' }-->
<!--  ]-->
<!--}-->

<!--// 搜索-->
<!--const handleSearch = () => {-->
<!--  currentPage.value = 1-->
<!--  loadData()-->
<!--}-->

<!--// 新增-->
<!--const handleAdd = () => {-->
<!--  dialogVisible.value = true-->
<!--  dialogTitle.value = '新建知识库'-->
<!--  formData.value = {-->
<!--    title: '',-->
<!--    category: '',-->
<!--    visibility: 'public',-->
<!--    description: ''-->
<!--  }-->
<!--}-->

<!--// 表单提交-->
<!--const handleSubmit = async () => {-->
<!--  if (!formRef.value) return-->

<!--  await formRef.value.validate(async (valid) => {-->
<!--    if (valid) {-->
<!--      submitLoading.value = true-->
<!--      try {-->
<!--        await createKnowledge(formData.value)-->
<!--        successMessage('创建成功')-->
<!--        dialogVisible.value = false-->
<!--        loadData()-->
<!--      } catch (error) {-->
<!--        console.error(error)-->
<!--      } finally {-->
<!--        submitLoading.value = false-->
<!--      }-->
<!--    }-->
<!--  })-->
<!--}-->

<!--// 编辑-->
<!--const handleEdit = (row) => {-->
<!--  // 这里需要实现编辑功能-->
<!--  console.log('编辑', row)-->
<!--}-->

<!--// 查看-->
<!--const handleView = (row) => {-->
<!--  // 这里需要实现查看功能-->
<!--  console.log('查看', row)-->
<!--}-->

<!--// 删除-->
<!--const handleDelete = async (row) => {-->
<!--  await ElMessageBox.confirm('确认删除该知识库?', '提示', {-->
<!--    type: 'warning'-->
<!--  })-->
<!--  await deleteKnowledge(row.id)-->
<!--  successMessage('删除成功')-->
<!--  loadData()-->
<!--}-->

<!--// 分页-->
<!--const handleSizeChange = (val: number) => {-->
<!--  pageSize.value = val-->
<!--  loadData()-->
<!--}-->

<!--const handleCurrentChange = (val: number) => {-->
<!--  currentPage.value = val-->
<!--  loadData()-->
<!--}-->

<!--onMounted(() => {-->
<!--  loadData()-->
<!--})-->
<!--</script>-->

<!--<style lang="scss" scoped>-->
<!--.knowledge-container {-->
<!--  padding: 20px;-->
<!--  background: #f5f7fa;-->
<!--  min-height: calc(100vh - 84px);-->

<!--  .header-actions {-->
<!--    display: flex;-->
<!--    justify-content: space-between;-->
<!--    align-items: center;-->
<!--    margin-bottom: 16px;-->

<!--    .left {-->
<!--      .search-input {-->
<!--        width: 300px;-->
<!--      }-->
<!--    }-->
<!--  }-->

<!--  .knowledge-list {-->
<!--    background: #fff;-->
<!--    padding: 20px;-->
<!--    border-radius: 4px;-->
<!--  }-->

<!--  .pagination {-->
<!--    margin-top: 16px;-->
<!--    display: flex;-->
<!--    justify-content: flex-end;-->
<!--  }-->
<!--}-->

<!--.visibility-options {-->
<!--  .visibility-option {-->
<!--    margin-bottom: 16px;-->
<!--    display: flex;-->
<!--    align-items: flex-start;-->

<!--    .visibility-radio {-->
<!--      margin-top: 2px;-->
<!--      margin-right: 12px;-->
<!--      flex-shrink: 0;-->

<!--      :deep(.el-radio__label) {-->
<!--        font-weight: 500;-->
<!--      }-->
<!--    }-->

<!--    .visibility-description {-->
<!--      font-size: 13px;-->
<!--      color: #606266;-->
<!--      line-height: 1.5;-->
<!--      padding-top: 2px;-->
<!--    }-->

<!--    &:last-child {-->
<!--      margin-bottom: 0;-->
<!--    }-->
<!--  }-->
<!--}-->
<!--</style>-->



<!--444-->
<template>
  <div class="knowledge-container">
    <!-- 顶部操作区域 -->
    <div class="header-actions">
      <div class="left">
        <el-input
          v-model="searchKeyword"
          placeholder="请输入知识库名称"
          class="search-input"
          @keyup.enter="handleSearch"
        >
          <template #suffix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
      <div class="right">
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>新增知识库
        </el-button>
      </div>
    </div>

    <!-- 知识库列表 -->
    <div class="knowledge-list">
      <el-table :data="tableData" style="width: 100%">
        <el-table-column prop="icon" label="" width="60">
          <template #default>
            <el-icon size="20" color="#409EFF"><Document /></el-icon>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="知识库名称" />
        <el-table-column prop="category" label="分类" width="120" />
        <el-table-column prop="visibility" label="可见范围" width="120">
          <template #default="scope">
            <span v-if="scope.row.visibility === 'public'">公共</span>
            <span v-else>私密</span>
          </template>
        </el-table-column>
        <el-table-column prop="creator" label="创建人" width="120" />
        <el-table-column prop="createTime" label="创建时间" width="180" />
        <el-table-column label="操作" width="180">
          <template #default="scope">
            <el-button text @click="handleEdit(scope.row)" v-auth="permission.edit">编辑</el-button>
            <el-button text @click="handleView(scope.row)">查看</el-button>
            <el-button text type="danger" @click="handleDelete(scope.row)" v-auth="permission.delete">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          layout="total, sizes, prev, pager, next"
        />
      </div>
    </div>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="700px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="知识库名称" prop="title">
          <el-input v-model="formData.title" placeholder="请输入知识库名称" />
        </el-form-item>
        <el-form-item label="知识库分类" prop="category">
          <el-select v-model="formData.category" placeholder="请选择知识库分类">
            <el-option label="技术文档" value="tech" />
            <el-option label="产品说明" value="product" />
            <el-option label="操作指南" value="guide" />
            <el-option label="常见问题" value="faq" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="可见范围" prop="visibility">
          <div class="visibility-container">
            <div
              class="visibility-option"
              :class="{ 'selected': formData.visibility === 'public' }"
              @click="formData.visibility = 'public'"
            >
              <div class="option-header">
                <div class="radio-circle">
                  <div class="inner-circle" v-if="formData.visibility === 'public'"></div>
                </div>
                <span class="option-title">公共</span>
              </div>
              <div class="option-description">
                公共知识库，初次创建后所有人员可查看，仅自己可编辑，其余人员可申请编辑权限。
              </div>
            </div>

            <div
              class="visibility-option"
              :class="{ 'selected': formData.visibility === 'private' }"
              @click="formData.visibility = 'private'"
            >
              <div class="option-header">
                <div class="radio-circle">
                  <div class="inner-circle" v-if="formData.visibility === 'private'"></div>
                </div>
                <span class="option-title">私密</span>
              </div>
              <div class="option-description">
                私密知识库，初次创建后仅自己可查看，仅自己可编辑，其余人员可申请查看权限。
              </div>
            </div>
          </div>
        </el-form-item>
        <el-form-item label="知识库描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入知识库描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup name="Knowledge">
import { ref, onMounted } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { Search, Plus, Document } from '@element-plus/icons-vue'
import { getKnowledgeList, createKnowledge, deleteKnowledge } from './api'
import { ElMessageBox, ElMessage } from 'element-plus'
import { successMessage } from '/@/utils/message'

// 权限定义
const permission = {
  add: 'knowledge:add',
  edit: 'knowledge:edit',
  delete: 'knowledge:delete'
}

const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const tableData = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('新建知识库')
const formRef = ref<FormInstance>()
const submitLoading = ref(false)

// 获取列表数据
const loadData = async () => {
  const params = {
    page: currentPage.value,
    limit: pageSize.value,
    keyword: searchKeyword.value
  }
  const res = await getKnowledgeList(params)
  tableData.value = res.data.list
  total.value = res.data.total
}

// 表单数据
const formData = ref({
  title: '',
  category: '',
  visibility: 'public',
  description: ''
})

// 表单校验规则
const formRules: FormRules = {
  title: [
    { required: true, message: '请输入知识库名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  category: [
    { required: true, message: '请选择知识库分类', trigger: 'change' }
  ],
  visibility: [
    { required: true, message: '请选择可见范围', trigger: 'change' }
  ],
  description: [
    { required: true, message: '请输入知识库描述', trigger: 'blur' }
  ]
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  loadData()
}

// 新增
const handleAdd = () => {
  dialogVisible.value = true
  dialogTitle.value = '新建知识库'
  formData.value = {
    title: '',
    category: '',
    visibility: 'public',
    description: ''
  }
}

// 表单提交
const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        await createKnowledge(formData.value)
        successMessage('创建成功')
        dialogVisible.value = false
        loadData()
      } catch (error) {
        console.error(error)
      } finally {
        submitLoading.value = false
      }
    }
  })
}

// 编辑
const handleEdit = (row) => {
  // 这里需要实现编辑功能
  console.log('编辑', row)
}

// 查看
const handleView = (row) => {
  // 这里需要实现查看功能
  console.log('查看', row)
}

// 删除
const handleDelete = async (row) => {
  await ElMessageBox.confirm('确认删除该知识库?', '提示', {
    type: 'warning'
  })
  await deleteKnowledge(row.id)
  successMessage('删除成功')
  loadData()
}

// 分页
const handleSizeChange = (val: number) => {
  pageSize.value = val
  loadData()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  loadData()
}

onMounted(() => {
  loadData()
})
</script>

<style lang="scss" scoped>
.knowledge-container {
  padding: 20px;
  background: #f5f7fa;
  min-height: calc(100vh - 84px);

  .header-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;

    .left {
      .search-input {
        width: 300px;
      }
    }
  }

  .knowledge-list {
    background: #fff;
    padding: 20px;
    border-radius: 4px;
  }

  .pagination {
    margin-top: 16px;
    display: flex;
    justify-content: flex-end;
  }
}

.visibility-container {
  display: flex;
  gap: 16px;

  .visibility-option {
    flex: 1;
    border: 1px solid #dcdfe6;
    border-radius: 4px;
    padding: 16px;
    cursor: pointer;
    transition: all 0.3s ease;

    &:hover {
      border-color: #409EFF;
    }

    &.selected {
      border-color: #409EFF;
      background-color: #f0f7ff;
    }

    .option-header {
      display: flex;
      align-items: center;
      margin-bottom: 8px;

      .radio-circle {
        width: 16px;
        height: 16px;
        border: 1px solid #dcdfe6;
        border-radius: 50%;
        margin-right: 8px;
        display: flex;
        align-items: center;
        justify-content: center;

        .inner-circle {
          width: 8px;
          height: 8px;
          background-color: #409EFF;
          border-radius: 50%;
        }
      }

      .option-title {
        font-weight: 500;
      }
    }

    .option-description {
      font-size: 13px;
      color: #606266;
      line-height: 1.5;
    }
  }
}
</style>













