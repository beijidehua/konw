# -*- coding: utf-8 -*-

"""
@author: H0nGzA1
@contact: QQ:2505811377
@Remark: 目录管理
"""
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from dvadmin.system.models import Users, MmRepository  # 导入关联模型（用户表、知识库表）
from dvadmin.utils.filters import DataLevelPermissionsFilter
from dvadmin.utils.json_response import DetailResponse, SuccessResponse, ErrorResponse
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet
from django.utils import timezone

# 导入目录模型（需确保模型路径与项目实际结构一致）
from dvadmin.system.models import Category


class CategorySerializer(CustomModelSerializer):
    """
    目录-序列化器（用于列表查询、详情展示）
    """
    # 自定义序列化字段：父级目录名称（通过父级ID关联查询）
    parent_name = serializers.SerializerMethodField()
    # 自定义序列化字段：负责人姓名（关联Users表查询）
    master_name = serializers.SerializerMethodField()
    # 标记是否有子目录（用于前端树形组件展示）
    has_children = serializers.SerializerMethodField()
    hasChild = serializers.SerializerMethodField()
    # 目录深度文本说明（如“1级目录”“2级目录”）
    dimension_label = serializers.SerializerMethodField()
    # 所属知识库名称（关联MmRepository表查询）
    repository_name = serializers.SerializerMethodField()

    def get_parent_name(self, obj: Category):
        """获取父级目录名称，无父级则返回空字符串"""
        return obj.parent_category.name if obj.parent_category else ""

    def get_master_name(self, obj: Category):
        """获取负责人姓名，关联Users表查询，无对应用户则返回“未知”"""
        try:
            user = Users.objects.get(id=obj.master)
            return user.name or user.username  # 优先显示姓名，无姓名则显示用户名
        except Users.DoesNotExist:
            return "未知"

    def get_has_children(self, obj: Category):
        """判断当前目录是否有子目录（返回1/0，适配部分前端组件需求）"""
        return 1 if Category.objects.filter(parent_category=obj).exists() else 0

    def get_hasChild(self, obj: Category):
        """兼容前端树形组件的子目录判断（返回布尔值）"""
        return Category.objects.filter(parent_category=obj).exists()

    def get_dimension_label(self, obj: Category):
        """返回目录深度的文本描述（如“1级目录”）"""
        return f"{obj.dimension}级目录"

    def get_repository_name(self, obj: Category):
        """获取所属知识库名称，关联MmRepository表查询，无对应知识库则返回“未知”"""
        try:
            repo = MmRepository.objects.get(id=obj.repository_id)
            return repo.name
        except MmRepository.DoesNotExist:
            return "未知"

    class Meta:
        model = Category
        fields = "__all__"
        # 只读字段：由模型自动维护，禁止前端修改
        read_only_fields = ["id", "dimension", "tree_path", "update_time"]


class CategoryImportSerializer(CustomModelSerializer):
    """
    目录-导入-序列化器（用于Excel批量导入场景）
    """
    class Meta:
        model = Category
        # 导入时需手动传入的字段（排除自动维护字段）
        fields = ["name", "repository_id", "parent_category", "master", "icon_url", "sort"]
        read_only_fields = ["id", "dimension", "tree_path", "update_time"]


class CategoryCreateUpdateSerializer(CustomModelSerializer):
    """
    目录管理-创建/更新时的序列化器（单独定义，灵活控制字段权限）
    """
    class Meta:
        model = Category
        # 创建/更新时允许传入的字段（自动维护字段无需前端处理）
        fields = ["name", "repository_id", "parent_category", "master", "icon_url", "sort"]


class CategoryViewSet(CustomModelViewSet):
    """
    目录管理接口
    支持功能：
    - list: 目录列表查询（支持懒加载）
    - create: 新增目录
    - update: 修改目录
    - retrieve: 获取目录详情
    - destroy: 删除目录（含子目录校验）
    - 自定义接口：树形目录查询、排序调整、目录详情扩展等
    """
    # 基础查询集
    queryset = Category.objects.all()
    # 不同场景的序列化器映射
    serializer_class = CategorySerializer
    create_serializer_class = CategoryCreateUpdateSerializer
    update_serializer_class = CategoryCreateUpdateSerializer
    import_serializer_class = CategoryImportSerializer
    # 筛选字段（支持按多维度筛选）
    filter_fields = ["name", "id", "repository_id", "parent_category", "master", "dimension", "sort"]
    # 搜索字段（支持模糊搜索）
    search_fields = ["name", "repository_id"]
    # Excel导入字段映射（用于导入时的字段校验提示）
    import_field_dict = {
        "name": "目录名称",
        "repository_id": "所属知识库ID",
        "parent_category": "父级目录ID",
        "master": "负责人ID",
        "icon_url": "图标路径",
        "sort": "排序值"
    }

    def list(self, request, *args, **kwargs):
        """
        重写列表查询：支持懒加载（仅返回当前层级目录），适配前端树形组件
        请求参数：parent_category（可选，父级目录ID，0或空表示顶级目录）
        """
        # 允许修改查询参数（Django默认query_params不可变）
        request.query_params._mutable = True
        params = request.query_params

        # 移除分页参数（懒加载时前端无需分页，一次性返回当前层级数据）
        for param in ["page", "limit"]:
            if param in params:
                del params[param]

        # 筛选当前层级目录
        parent_id = params.get("parent_category")
        if parent_id in [None, "0"]:
            # 顶级目录：筛选父级为None的目录
            queryset = self.filter_queryset(self.get_queryset()).filter(parent_category__isnull=True)
        else:
            # 子目录：筛选指定父级ID的目录
            queryset = self.filter_queryset(self.get_queryset()).filter(parent_category_id=parent_id)

        # 按排序值升序排列（确保展示顺序正确）
        queryset = queryset.order_by("sort")
        # 序列化数据并返回
        serializer = self.get_serializer(queryset, many=True, request=request)
        return SuccessResponse(data=serializer.data, msg="获取目录列表成功")

    @action(methods=["GET"], detail=False, permission_classes=[IsAuthenticated])
    def tree_by_repo(self, request, *args, **kwargs):
        """
        按知识库ID获取完整树形目录（一次性返回所有层级）
        请求参数：repository_id（必传，指定所属知识库）
        返回格式：嵌套树形结构（含子目录）
        """
        # 获取并校验知识库ID参数
        repository_id = request.query_params.get("repository_id")
        if not repository_id:
            return ErrorResponse(msg="参数缺失：请提供 repository_id（所属知识库ID）")

        # 筛选指定知识库的所有目录
        queryset = self.filter_queryset(self.get_queryset()).filter(repository_id=repository_id)
        if not queryset.exists():
            return SuccessResponse(data=[], msg=f"知识库ID={repository_id}下无目录数据")

        # 递归构建树形结构
        def build_tree(cate_list, parent_id=None):
            tree = []
            for cate in cate_list:
                if cate.parent_category_id == parent_id:
                    # 序列化当前目录数据
                    cate_data = self.get_serializer(cate).data
                    # 递归查询当前目录的子目录
                    cate_data["children"] = build_tree(cate_list, parent_id=cate.id)
                    tree.append(cate_data)
            return tree

        # 转换为列表并按“父级ID+排序值”排序，确保构建顺序正确
        cate_list = list(queryset.order_by("parent_category", "sort"))
        tree_data = build_tree(cate_list)

        return SuccessResponse(data=tree_data, msg=f"获取知识库ID={repository_id}树形目录成功")

    @action(methods=["GET"], detail=False, permission_classes=[IsAuthenticated])
    def all_category(self, request, *args, **kwargs):
        """
        获取指定知识库下的所有目录（平级列表），用于下拉选择等场景
        请求参数：repository_id（必传，指定所属知识库）
        返回格式：平级列表（含ID、名称、父级ID、层级等关键字段）
        """
        repository_id = request.query_params.get("repository_id")
        if not repository_id:
            return ErrorResponse(msg="参数缺失：请提供 repository_id（所属知识库ID）")

        # 筛选指定知识库的目录，并按“层级+排序值”排序
        queryset = self.filter_queryset(self.get_queryset()).filter(
            repository_id=repository_id
        ).order_by("dimension", "sort")

        # 仅返回关键字段，减少数据传输量
        data = queryset.values("id", "name", "parent_category", "dimension", "master")
        return DetailResponse(data=data, msg="获取所有目录列表成功")

    @action(methods=["POST"], detail=True, permission_classes=[IsAuthenticated])
    def adjust_sort(self, request, pk=None):
        """
        调整目录排序值（单独接口，适配前端拖拽排序场景）
        请求体：{"sort": 整数}（新的排序值）
        """
        # 获取当前目录实例
        category = self.get_object()
        # 获取并校验排序值参数
        new_sort = request.data.get("sort")
        if new_sort is None or not isinstance(new_sort, int):
            return ErrorResponse(msg="参数错误：请提供有效的 sort 值（整数类型）")

        # 更新排序值（仅更新必要字段，提升性能）
        category.sort = new_sort
        category.save(update_fields=["sort", "update_time"])

        # 返回更新后的目录数据
        serializer = self.get_serializer(category)
        return SuccessResponse(data=serializer.data, msg="目录排序调整成功")

    def destroy(self, request, *args, **kwargs):
        """
        重写删除方法：先校验是否有子目录，有则禁止删除（避免子目录成为孤儿数据）
        """
        # 获取当前目录实例
        category = self.get_object()
        # 检查当前目录是否存在子目录
        if Category.objects.filter(parent_category=category).exists():
            return ErrorResponse(
                msg=f"当前目录「{category.name}」存在子目录，禁止删除，请先删除所有子目录"
            )

        # 执行物理删除（若需逻辑删除，可添加 is_deleted 字段并修改为更新操作）
        category.delete()
        return SuccessResponse(data=[], msg=f"目录「{category.name}」删除成功")

    @action(methods=["GET"], detail=False, permission_classes=[IsAuthenticated])
    def category_info(self, request):
        """
        获取单个目录的详细信息（含关联表扩展数据）
        请求参数：category_id（必传，指定目录ID）
        返回格式：含知识库名称、负责人姓名等关联信息
        """
        # 获取并校验目录ID参数
        category_id = request.query_params.get("category_id")
        if not category_id:
            return ErrorResponse(msg="参数缺失：请提供 category_id（目录ID）")

        # 查询目录信息（不存在则返回错误）
        try:
            category = self.get_queryset().get(id=category_id)
        except Category.DoesNotExist:
            return ErrorResponse(msg=f"目录ID={category_id}不存在")

        # 序列化目录基础数据
        serializer = self.get_serializer(category)
        data = serializer.data

        # 补充返回目录的完整路径（通过tree_path解析）
        if data.get("tree_path"):
            parent_ids = list(map(int, data["tree_path"].split(",")))
            parent_cates = Category.objects.filter(id__in=parent_ids).values("id", "name")
            data["full_path"] = " > ".join([cate["name"] for cate in parent_cates] + [data["name"]])
        else:
            data["full_path"] = data["name"]  # 顶级目录无父路径，直接显示名称

        return SuccessResponse(data=data, msg="获取目录详情成功")