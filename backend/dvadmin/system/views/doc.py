# -*- coding: utf-8 -*-

"""
@author: H0nGzA1
@contact: QQ:2505811377
@Remark: 文档管理
"""
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from dvadmin.system.models import Users, Category  # 导入关联模型（用户表、目录表）
from dvadmin.utils.filters import DataLevelPermissionsFilter
from dvadmin.utils.json_response import DetailResponse, SuccessResponse, ErrorResponse
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet
from django.utils import timezone

# 导入文档模型（需确保模型路径与项目实际结构一致）
from dvadmin.system.models import MmDocument


class MmDocumentSerializer(CustomModelSerializer):
    """
    文档-序列化器（用于列表查询、详情展示）
    """
    # 自定义序列化字段：关联表数据转义（提升前端展示友好性）
    category_name = serializers.SerializerMethodField()  # 所属目录名称
    master_name = serializers.SerializerMethodField()  # 负责人姓名
    type_label = serializers.SerializerMethodField()  # 文档类型文本（需关联字典表）
    category_path = serializers.SerializerMethodField()  # 所属目录完整路径（冗余字段解析）

    def get_category_name(self, obj: MmDocument):
        """获取所属目录名称（从关联目录表获取）"""
        return obj.category.name if obj.category else "未知目录"

    def get_master_name(self, obj: MmDocument):
        """获取负责人姓名（关联Users表，无对应用户返回“未知”）"""
        try:
            user = Users.objects.get(id=obj.master)
            return user.name or user.username  # 优先显示姓名，无姓名则显示用户名
        except Users.DoesNotExist:
            return "未知"

    def get_type_label(self, obj: MmDocument):
        """获取文档类型文本（需关联项目字典表，此处为示例逻辑，需根据实际字典表调整）"""
        # 假设项目中存在文档类型字典表（如SysDictData，dict_type="document_type"）
        try:
            from dvadmin.system.models import SysDictData
            dict_data = SysDictData.objects.get(dict_type="document_type", dict_value=str(obj.type_id))
            return dict_data.dict_label
        except (ImportError, SysDictData.DoesNotExist):
            return f"类型ID:{obj.type_id}"  # 无字典表时返回原始ID

    def get_category_path(self, obj: MmDocument):
        """解析目录路径冗余字段，返回完整目录路径（如“顶级目录 > 子目录1 > 子目录2”）"""
        if not obj.tree_path:
            return obj.category.name  # 无路径时直接返回当前目录名

        # 按路径ID查询所有父目录，拼接完整路径
        parent_ids = list(map(int, obj.tree_path.split(",")))
        parent_categories = Category.objects.filter(id__in=parent_ids).values("name")
        parent_names = [cate["name"] for cate in parent_categories]
        return " > ".join(parent_names + [obj.category.name])

    class Meta:
        model = MmDocument
        fields = "__all__"
        # 只读字段：由模型自动维护（冗余字段、更新时间等），禁止前端修改
        read_only_fields = ["id", "dimension", "tree_path", "update_time"]


class MmDocumentImportSerializer(CustomModelSerializer):
    """
    文档-导入-序列化器（用于Excel批量导入场景）
    """

    class Meta:
        model = MmDocument
        # 导入时需手动传入的字段（排除自动维护字段）
        fields = ["name", "type_id", "category", "master", "details", "detail_text", "sort"]
        read_only_fields = ["id", "dimension", "tree_path", "update_time"]

    def validate(self, data):
        """导入数据校验：确保同目录下无同名文档（符合模型unique_together约束）"""
        category = data.get("category")
        name = data.get("name")
        if MmDocument.objects.filter(category=category, name=name).exists():
            raise serializers.ValidationError(f"所属目录「{category.name}」下已存在同名文档「{name}」")
        return data


class MmDocumentCreateUpdateSerializer(CustomModelSerializer):
    """
    文档管理-创建/更新时的序列化器（单独定义，灵活控制字段权限）
    """

    class Meta:
        model = MmDocument
        # 创建/更新时允许传入的字段（自动维护字段无需前端处理）
        fields = ["name", "type_id", "category", "master", "details", "detail_text", "sort"]

    def validate(self, data):
        """数据校验：确保同目录下无同名文档（符合模型unique_together约束）"""
        instance = self.instance  # 更新时存在instance，创建时为None
        category = data.get("category", getattr(instance, "category", None))
        name = data.get("name", getattr(instance, "name", None))

        # 构建查询条件：排除当前实例（更新场景），避免自我冲突
        queryset = MmDocument.objects.filter(category=category, name=name)
        if instance:
            queryset = queryset.exclude(id=instance.id)

        if queryset.exists():
            raise serializers.ValidationError(f"所属目录「{category.name}」下已存在同名文档「{name}」")
        return data


class MmDocumentViewSet(CustomModelViewSet):
    """
    文档管理接口
    支持功能：
    - list: 文档列表查询（支持按目录、类型、负责人筛选）
    - create: 新增文档
    - update: 修改文档
    - retrieve: 获取文档详情
    - destroy: 删除文档（受目录保护约束）
    - 自定义接口：按目录路径筛选文档、文档文本预览、批量调整排序等
    """
    # 基础查询集
    queryset = MmDocument.objects.all()
    # 不同场景的序列化器映射
    serializer_class = MmDocumentSerializer
    create_serializer_class = MmDocumentCreateUpdateSerializer
    update_serializer_class = MmDocumentCreateUpdateSerializer
    import_serializer_class = MmDocumentImportSerializer
    # 筛选字段（支持按多维度快速筛选）
    filter_fields = ["name", "id", "type_id", "category", "master", "dimension", "sort"]
    # 搜索字段（支持按文档名、目录名模糊搜索）
    search_fields = ["name", "category__name", "detail_text"]  # 支持跨表搜索目录名
    # Excel导入字段映射（用于导入时的字段校验提示）
    import_field_dict = {
        "name": "文档名称",
        "type_id": "文档类型ID",
        "category": "所属目录ID",
        "master": "负责人ID",
        "details": "文档内容路径",
        "detail_text": "文档文本内容",
        "sort": "排序值"
    }

    def list(self, request, *args, **kwargs):
        """
        重写列表查询：支持按目录路径筛选（利用冗余字段tree_path），优化查询性能
        请求参数扩展：tree_path（可选，如“1,2”，筛选该目录及其子目录下的文档）
        """
        request.query_params._mutable = True
        params = request.query_params
        tree_path = params.get("tree_path")

        # 按目录路径筛选（模糊匹配tree_path，实现“目录及其子目录”文档查询）
        queryset = self.filter_queryset(self.get_queryset())
        if tree_path:
            # 筛选条件：tree_path为空（顶级目录）或包含目标路径（子目录）
            queryset = queryset.filter(
                models.Q(tree_path__isnull=True, category_id=int(tree_path)) |
                models.Q(tree_path__icontains=tree_path)
            )

        # 按“目录+排序值+更新时间”排序（同目录下先按sort升序，再按更新时间降序）
        queryset = queryset.order_by("category", "sort", "-update_time")

        # 分页处理（文档列表数据可能较多，默认开启分页）
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, request=request)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True, request=request)
        return SuccessResponse(data=serializer.data, msg="获取文档列表成功")

    @action(methods=["GET"], detail=False, permission_classes=[IsAuthenticated])
    def by_category(self, request, *args, **kwargs):
        """
        按目录ID获取该目录下的所有文档（含排序），用于目录详情页文档展示
        请求参数：category_id（必传，指定目录）
        """
        category_id = request.query_params.get("category_id")
        if not category_id:
            return ErrorResponse(msg="参数缺失：请提供 category_id（所属目录ID）")

        # 校验目录是否存在
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return ErrorResponse(msg=f"目录ID={category_id}不存在")

        # 筛选该目录下的文档，按排序值升序、更新时间降序排列
        queryset = self.filter_queryset(self.get_queryset()).filter(
            category=category
        ).order_by("sort", "-update_time")

        serializer = self.get_serializer(queryset, many=True, request=request)
        return SuccessResponse(data=serializer.data, msg=f"获取目录「{category.name}」下文档成功")

    @action(methods=["GET"], detail=True, permission_classes=[IsAuthenticated])
    def text_preview(self, request, pk=None):
        """
        文档文本预览接口（仅返回文本内容，用于前端快速预览，避免返回完整文档数据）
        """
        document = self.get_object()
        # 截取前500字符作为预览（可根据业务调整长度）
        preview_text = document.detail_text[:500] if document.detail_text else ""
        # 标记是否有更多文本（超过500字符时显示“...”）
        has_more = len(document.detail_text) > 500 if document.detail_text else False

        data = {
            "id": document.id,
            "name": document.name,
            "preview_text": preview_text + ("..." if has_more else ""),
            "has_more": has_more,
            "full_length": len(document.detail_text) if document.detail_text else 0
        }
        return SuccessResponse(data=data, msg="获取文档文本预览成功")

    @action(methods=["POST"], detail=False, permission_classes=[IsAuthenticated])
    def batch_adjust_sort(self, request, *args, **kwargs):
        """
        批量调整文档排序值（适配前端批量拖拽排序场景）
        请求体：[{"id": 1, "sort": 10}, {"id": 2, "sort": 20}, ...]
        """
        sort_list = request.data.get("sort_list", [])
        if not isinstance(sort_list, list) or len(sort_list) == 0:
            return ErrorResponse(msg="参数错误：请提供 sort_list（文档ID与排序值的列表）")

        # 批量更新排序值（使用bulk_update提升性能）
        document_ids = [item["id"] for item in sort_list]
        documents = MmDocument.objects.filter(id__in=document_ids)
        if len(documents) != len(document_ids):
            return ErrorResponse(msg="部分文档ID不存在，请检查参数")

        # 匹配文档与新排序值
        id_to_sort = {item["id"]: item["sort"] for item in sort_list}
        update_list = []
        for doc in documents:
            new_sort = id_to_sort[doc.id]
            if doc.sort != new_sort:
                doc.sort = new_sort
                update_list.append(doc)

        # 批量更新（仅更新sort和update_time字段）
        if update_list:
            MmDocument.objects.bulk_update(update_list, fields=["sort", "update_time"])

        return SuccessResponse(data=[], msg=f"成功调整 {len(update_list)} 个文档的排序值")

    def destroy(self, request, *args, **kwargs):
        """
        重写删除方法：适配模型PROTECT约束（若关联目录被保护，删除时返回友好提示）
        """
        try:
            document = self.get_object()
            document_name = document.name
            document.delete()
            return SuccessResponse(data=[], msg=f"文档「{document_name}」删除成功")
        except models.ProtectedError:
            return ErrorResponse(msg="当前文档关联的目录受保护，无法删除（或先删除目录关联约束）")
        except MmDocument.DoesNotExist:
            return ErrorResponse(msg="文档不存在或已被删除")

    @action(methods=["GET"], detail=False, permission_classes=[IsAuthenticated])
    def document_stats(self, request, *args, **kwargs):
        """
        文档统计接口（按类型、目录维度统计文档数量，用于数据看板）
        请求参数：repository_id（可选，按知识库筛选，需结合目录表关联）
        """
        repository_id = request.query_params.get("repository_id")
        queryset = self.filter_queryset(self.get_queryset())

        # 按知识库筛选（通过目录表关联，目录属于指定知识库）
        if repository_id:
            queryset = queryset.filter(category__repository_id=repository_id)

        # 1. 按文档类型统计数量
        type_stats = queryset.values("type_id").annotate(
            count=models.Count("id")
        ).order_by("-count")
        # 补充类型文本标签
        for stat in type_stats:
            try:
                from dvadmin.system.models import SysDictData
                dict_label = SysDictData.objects.get(
                    dict_type="document_type", dict_value=str(stat["type_id"])
                ).dict_label
            except (ImportError, SysDictData.DoesNotExist):
                dict_label = f"类型ID:{stat['type_id']}"
            stat["type_label"] = dict_label

        # 2. 按目录统计数量（前10个目录）
        category_stats = queryset.values("category__id", "category__name").annotate(
            count=models.Count("id")
        ).order_by("-count")[:10]

        # 3. 总数量统计
        total_count = queryset.count()
        latest_update = queryset.aggregate(max_time=models.Max("update_time"))["max_time"] or "无更新记录"

        data = {
            "total_count": total_count,
            "latest_update": latest_update,
            "type_stats": type_stats,
            "category_stats": category_stats
        }
        return SuccessResponse(data=data, msg="获取文档统计数据成功")