# from django.db import models, connection
# from django.db.models import Q, F
# from django.contrib.auth.hashers import make_password, check_password
# from django_restql.fields import DynamicSerializerMethodField
# from rest_framework import serializers
# from rest_framework.decorators import action
# from rest_framework.permissions import IsAuthenticated
# from rest_framework import serializers
# from rest_framework.response import Response
# from django.contrib.auth import get_user_model
#
# # 从 dvadmin 导入
# from dvadmin.system.models import Users, Dept, KnowledgeBase
# from dvadmin.utils.git_dict_model import get_dict_options
# from dvadmin.utils.json_response import ErrorResponse, DetailResponse, SuccessResponse
# from dvadmin.utils.serializers import CustomModelSerializer
# from dvadmin.utils.validator import CustomUniqueValidator
# from dvadmin.utils.viewset import CustomModelViewSet
# from dvadmin.utils.export import ExportMixin
# from dvadmin.utils.import_export_mixin import ImportSerializerMixin
# from dvadmin.utils.permission import CustomPermission
#
# User = get_user_model()
#
#
# class MmRepositorySerializer(serializers.ModelSerializer):
#     type_name = serializers.SerializerMethodField()
#     master_name = serializers.SerializerMethodField()
#     archived_user_name = serializers.SerializerMethodField()
#     recycle_user_name = serializers.SerializerMethodField()
#
#     class Meta:
#         model = KnowledgeBase
#         fields = [
#             'id', 'name', 'type_id', 'type_name', 'master', 'master_name',
#             'limits', 'create_time', 'icon_url', 'status', 'archived_time',
#             'archived_user', 'archived_user_name', 'archived_desc', 'recycle',
#             'recycle_time', 'recycle_user', 'recycle_user_name', 'description'
#         ]
#         read_only_fields = [
#             'create_time', 'archived_time', 'archived_user',
#             'recycle_time', 'recycle_user'
#         ]
#
#     def get_type_name(self, obj):
#         """获取知识库类型名称"""
#         from dvadmin.utils.git_dict_model import get_dict_label
#         return get_dict_label('repository_type', obj.type_id)
#
#     def get_master_name(self, obj):
#         """获取负责人名称"""
#         return obj.master_name
#
#     def get_archived_user_name(self, obj):
#         """获取归档人名称"""
#         if obj.archived_user:
#             from dvadmin.utils.git_dict_model import get_user_name
#             return get_user_name(obj.archived_user.id)
#         return None
#
#     def get_recycle_user_name(self, obj):
#         """获取回收人名称"""
#         if obj.recycle_user:
#             from dvadmin.utils.git_dict_model import get_user_name
#             return get_user_name(obj.recycle_user.id)
#         return None
#
#     def validate_type_id(self, value):
#         """验证知识库类型ID是否有效"""
#         from dvadmin.utils.git_dict_model import validate_dict_value
#         if not validate_dict_value('repository_type', value):
#             raise serializers.ValidationError("无效的知识库类型")
#         return value
#
#
#
# # ======================== 2. 序列化器定义（完全对齐模型字段）=======================
# # class KnowledgeBaseCategorySerializer(CustomModelSerializer):
# #     """知识库分类序列化器（对齐KnowledgeBaseCategory模型）"""
# #
# #     class Meta:
# #         model = KnowledgeBaseCategory
# #         read_only_fields = ["id", "create_time", "update_time"]  # 模型存在的字段
# #         fields = "__all__"  # 模型字段：name/sort/status/create_time/update_time
# #         extra_kwargs = {
# #             "sort": {"required": False, "default": 0},
# #             "status": {"required": False, "default": True}
# #         }
#
#
# class KnowledgeBaseListSerializer(CustomModelSerializer):
#     """知识库列表序列化器（对齐KnowledgeBase模型，删除无效关联字段）"""
#
#     # 移除模型不存在的关联字段：category/creator/editor/dept/visibility
#     class Meta:
#         model = KnowledgeBase
#         # 仅保留模型存在的只读字段（无view_count/creator，新增archived_user_id等）
#         read_only_fields = ["id", "create_time", "archived_time", "recycle_time", "archived_user_id", "recycle_user_id"]
#         # 排除模型不存在的content字段，直接指定返回字段（更安全）
#         fields = [
#             "id", "name", "type_id", "master", "limits", "status",
#             "icon_url", "archived_desc", "recycle", "description",
#             "create_time", "archived_time", "recycle_time"
#         ]
#         # 移除无效的extra_kwargs（is_recommend/visibility模型不存在）
#         extra_kwargs = {}
#
#
# class KnowledgeBaseCreateSerializer(CustomModelSerializer):
#     """知识库新增序列化器（对齐KnowledgeBase模型，删除无效字段）"""
#     # 1. 模型无title字段，替换为实际的name字段，并添加唯一性验证
#     name = serializers.CharField(
#         max_length=255,
#         validators=[CustomUniqueValidator(
#             queryset=KnowledgeBase.objects.all(),
#             message="知识库名称已存在"
#         )]
#     )
#
#     # 2. 移除模型不存在的content字段
#     # 3. 移除模型不存在的visibility/dept字段相关配置
#
#     class Meta:
#         model = KnowledgeBase
#         # 只读字段：模型中自动生成/无需用户输入的字段
#         read_only_fields = ["id", "create_time", "archived_time", "recycle_time", "archived_user_id", "recycle_user_id"]
#         # 新增允许的字段：仅模型存在且需用户输入的字段
#         fields = [
#             "name", "type_id", "master", "limits", "status",
#             "icon_url", "archived_desc", "recycle", "description"
#         ]
#         # 移除无效的extra_kwargs（is_recommend/visibility/dept模型不存在）
#         extra_kwargs = {}
#
#     # 4. 移除无效的validate方法（visibility/dept模型不存在，无需验证）
#
#     def save(self, **kwargs):
#         """保留创建人逻辑（若模型后续需添加creator字段，当前可注释）"""
#         # 注意：当前KnowledgeBase模型无creator字段，若需添加需先更新模型
#         # user = self.context["request"].user
#         # instance = super().save(creator=user, **kwargs)
#         instance = super().save(**kwargs)
#         return instance
#
#
# class KnowledgeBaseUpdateSerializer(CustomModelSerializer):
#     """知识库修改序列化器（对齐KnowledgeBase模型）"""
#     # 1. 模型无title字段，替换为实际的name字段，并添加唯一性验证
#     # 1. 移除validator中的filter_func，仅保留基础验证（或直接去掉validators）
#     name = serializers.CharField(
#         max_length=255
#         # 若需要基础唯一性验证（不含排除自身），可保留此行；若需完整验证，建议删除并在下方方法中处理
#         # validators=[CustomUniqueValidator(queryset=KnowledgeBase.objects.all(), message="知识库名称已存在")]
#     )
#
#     # 2. 移除模型不存在的content字段
#
#     class Meta:
#         model = KnowledgeBase
#         read_only_fields = ["id", "create_time", "archived_time", "recycle_time", "archived_user_id", "recycle_user_id"]
#         # 修改允许的字段：同新增字段（模型存在的字段）
#         fields = [
#             "name", "type_id", "master", "limits", "status",
#             "icon_url", "archived_desc", "recycle", "description"
#         ]
#         # 移除无效的extra_kwargs（visibility/dept模型不存在）
#         extra_kwargs = {}
#
#
#     # 2. 手动实现更新时的唯一性验证（排除当前实例ID）
#     def validate_name(self, value):
#         # 排除当前编辑的实例，检查其他实例是否有重名
#         if KnowledgeBase.objects.exclude(id=self.instance.id).filter(name=value).exists():
#             raise serializers.ValidationError("知识库名称已存在")
#         return value
#     def save(self, **kwargs):
#         """保留编辑人逻辑（若模型后续需添加editor字段，当前可注释）"""
#         # 注意：当前KnowledgeBase模型无editor字段，若需添加需先更新模型
#         # user = self.context["request"].user
#         # instance = super().save(editor=user, **kwargs)
#         instance = super().save(**kwargs)
#         return instance
#
#
# class KnowledgeBaseDetailSerializer(CustomModelSerializer):
#     """知识库详情序列化器（返回模型所有字段）"""
#
#     # 移除模型不存在的关联字段：category_info/creator_info/editor_info/dept_info/visibility_display
#     class Meta:
#         model = KnowledgeBase
#         read_only_fields = ["id", "create_time", "archived_time", "recycle_time", "archived_user_id", "recycle_user_id"]
#         fields = "__all__"  # 模型所有字段：name/type_id/master/limits等
#
#
# class ExportKnowledgeBaseSerializer(CustomModelSerializer):
#     """知识库导出序列化器（对齐模型字段，删除无效配置）"""
#     # 时间字段格式化（保留）
#     create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
#     archived_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
#     recycle_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
#     # 移除模型不存在的字段：visibility/is_recommend/category/creator/editor/dept/content
#     # 新增模型存在的布尔字段格式化（如recycle：1=是，0=否）
#     recycle_display = serializers.SerializerMethodField(read_only=True)
#
#     def get_recycle_display(self, instance):
#         return "是" if instance.recycle == 1 else "否"
#
#     class Meta:
#         model = KnowledgeBase
#         # 导出字段：仅模型存在且有意义的字段
#         fields = [
#             "name", "type_id", "master", "limits", "status",
#             "icon_url", "archived_desc", "recycle", "recycle_display",
#             "description", "create_time", "archived_time", "recycle_time"
#         ]
#
#
# # ======================== 3. 视图集定义（完全对齐模型字段）=======================
# class KnowledgeBaseViewSet(CustomModelViewSet, ExportMixin, ImportSerializerMixin):
#     """
#     知识库接口
#     list:查询
#     create:新增
#     update:修改
#     retrieve:单例
#     destroy:删除
#     export_data:导出
#     import_data:导入
#     category_list:获取分类列表
#     """
#     # 基础配置（对齐模型）
#     queryset = KnowledgeBase.objects.all()
#     serializer_class = KnowledgeBaseListSerializer
#     create_serializer_class = KnowledgeBaseCreateSerializer
#     update_serializer_class = KnowledgeBaseUpdateSerializer
#     detail_serializer_class = KnowledgeBaseDetailSerializer
#     permission_classes = [IsAuthenticated]
#
#     # 筛选、搜索、排序配置（仅保留模型存在的字段）
#     filter_fields = ["status", "type_id", "master", "recycle", "create_time"]  # 模型均存在
#     search_fields = ["name", "description", "archived_desc"]  # 模型均存在（支持名称/描述搜索）
#     ordering_fields = ["create_time", "archived_time", "recycle_time"]  # 模型均存在
#     ordering = ["-create_time"]  # 按创建时间倒序
#
#     # 导出配置（对齐模型+导出序列化器）
#     export_field_label = {
#         "name": "知识库名称",
#         "type_id": "类型ID",
#         "master": "负责人ID",
#         "limits": "权限限制",
#         "status": "状态",
#         "icon_url": "图标URL",
#         "archived_desc": "归档描述",
#         "recycle": "是否回收（1=是/0=否）",
#         "recycle_display": "回收状态",
#         "description": "描述",
#         "create_time": "创建时间",
#         "archived_time": "归档时间",
#         "recycle_time": "回收时间"
#     }
#     export_serializer_class = ExportKnowledgeBaseSerializer
#
#     # 导入配置（对齐模型+导入序列化器）
#     import_serializer_class = KnowledgeBaseCreateSerializer
#     import_field_dict = {
#         "name": "知识库名称（必填，不可重复）",  # 模型必填+唯一
#         "type_id": {
#             "title": "类型ID（必填）",
#             "choices": {"data": {"类型1": 1, "类型2": 2, "类型3": 3}}  # 按实际业务类型调整
#         },
#         "master": {
#             "title": "负责人ID（必填）",
#             # 若关联用户表，建议用动态查询（示例：关联system.Users模型）
#             # "choices": {"queryset": Users.objects.filter(is_active=True), "values_name": "name"}
#             "choices": {"data": {"用户1": 1, "用户2": 2, "用户3": 3}}  # 临时固定值，后续可改动态
#         },
#         "limits": {
#             "title": "权限限制（必填）",
#             "choices": {"data": {"公开": 1, "私有": 2, "部门内": 3}}  # 按实际权限逻辑调整
#         },
#         "status": {
#             "title": "状态（必填）",
#             "choices": {"data": {"正常": "normal", "归档": "archived", "禁用": "disabled"}}  # 按实际状态值调整
#         },
#         "icon_url": {"title": "图标URL（选填）"},
#         "archived_desc": {"title": "归档描述（选填，仅归档状态时填写）"},
#         "recycle": {
#             "title": "是否回收（选填）",
#             "choices": {"data": {"是": 1, "否": 0}},
#             "default": 0
#         },
#         "description": {"title": "描述（选填）"}
#     }
#
#     # # ======================== 自定义接口（保留分类相关，删除无效逻辑）=======================
#     # @action(methods=["GET"], detail=False, permission_classes=[IsAuthenticated])
#     # def category_list(self, request):
#     #     """获取知识库分类列表（用于前端下拉选择）"""
#     #     queryset = KnowledgeBaseCategory.objects.filter(status=True).order_by("sort")
#     #     serializer = KnowledgeBaseCategorySerializer(queryset, many=True)
#     #     return SuccessResponse(data=serializer.data, msg="获取分类列表成功")
#     #
#     # @action(methods=["POST"], detail=False, permission_classes=[IsAuthenticated])
#     # def add_category(self, request):
#     #     """新增知识库分类（简化接口，无需单独视图集）"""
#     #     serializer = KnowledgeBaseCategorySerializer(data=request.data)
#     #     serializer.is_valid(raise_exception=True)
#     #     serializer.save()
#     #     return SuccessResponse(data=serializer.data, msg="新增分类成功")
#     #
#     # @action(methods=["PUT"], detail=False, permission_classes=[IsAuthenticated])
#     # def update_category(self, request):
#     #     """修改知识库分类"""
#     #     category_id = request.data.get("id")
#     #     if not category_id:
#     #         return ErrorResponse(msg="分类ID不能为空")
#     #     instance = KnowledgeBaseCategory.objects.filter(id=category_id).first()
#     #     if not instance:
#     #         return ErrorResponse(msg="分类不存在")
#     #     serializer = KnowledgeBaseCategorySerializer(instance, data=request.data, partial=True)
#     #     serializer.is_valid(raise_exception=True)
#     #     serializer.save()
#     #     return SuccessResponse(data=serializer.data, msg="修改分类成功")
#
#     @action(methods=["GET"], detail=True, permission_classes=[IsAuthenticated])
#     def increase_view_count(self, request, pk=None):
#         """查看知识库时，增加访问次数（注：当前模型无view_count字段，需先添加模型字段才能启用）"""
#         # 若需启用此功能，先在KnowledgeBase模型添加：view_count = models.IntegerField(default=0, verbose_name="访问次数")
#         instance = self.get_object()
#         # KnowledgeBase.objects.filter(id=instance.id).update(view_count=F("view_count") + 1)
#         # instance.refresh_from_db()
#         # return DetailResponse(data={"view_count": instance.view_count}, msg="访问次数更新成功")
#         return SuccessResponse(msg="访问次数功能待启用（需添加view_count模型字段）")
#
#     def get_queryset(self):
#         # 根据用户权限过滤数据
#         user = self.request.user
#         if user.is_superuser:
#             return KnowledgeBase.objects.filter(recycle=0)
#         else:
#             # 普通用户只能看到自己创建的知识库或公开的知识库
#             return KnowledgeBase.objects.filter(
#                 models.Q(recycle=0) & (
#                         models.Q(master=user) |
#                         models.Q(limits=0)
#                 )
#             )
#
#     def perform_create(self, serializer):
#         # 自动设置创建者和负责人
#         serializer.save(master=self.request.user)
#
#
#
#     @action(detail=False, methods=['get'])
#     def types(self, request):
#         """获取知识库类型选项"""
#         types = get_dict_options('repository_type')
#         return Response(types)
#
#
#
#
#     # ======================== 重写父类方法（删除无效权限逻辑）=======================
#     def get_queryset(self):
#         # 1. 首先检测是否为Swagger文档生成的伪请求
#         if getattr(self, 'swagger_fake_view', False):
#             return KnowledgeBase.objects.none()
#
#         user = self.request.user
#         # 2. 未认证用户返回空（保留基础权限）
#         if not user.is_authenticated:
#             return KnowledgeBase.objects.none()
#
#         # 3. 移除无效的权限过滤（visibility/dept/creator模型不存在，无法按此过滤）
#         # 超级管理员/普通用户均返回全量数据（后续可按实际业务添加模型字段后扩展权限）
#         return super().get_queryset()
#
#     def destroy(self, request, *args, **kwargs):
#         """重写删除：简化权限（后续可按实际业务扩展，如添加creator字段后限制删除）"""
#         instance = self.get_object()
#         # 若需限制“仅创建人删除”，先在模型添加creator字段，再启用以下逻辑：
#         # if not (request.user.is_superuser or request.user == instance.creator):
#         #     return ErrorResponse(msg="仅创建人或超级管理员可删除此知识库")
#         self.perform_destroy(instance)
#         return SuccessResponse(msg="删除知识库成功")
from time import timezone

# 2222222
# apps/system/serializers.py
from rest_framework import serializers
from dvadmin.system.models import Dictionary, KnowledgeBase


class DictRepoTypeSerializer(serializers.ModelSerializer):
    """字典表-知识库类型序列化器（用于前端下拉选择）"""
    class Meta:
        model = Dictionary
        fields = ["id", "label"]  # 仅返回id（关联知识库表type_id）和label（前端显示）


class KnowledgeListSerializer(serializers.ModelSerializer):
    # 自定义方法：获取知识库类型名称（type_id→字典表label）
    type_name = serializers.SerializerMethodField()

    class Meta:
        model = KnowledgeBase
        fields = [
            "id", "name", "type_id", "type_name", "master", "master_name",
            "limits", "create_time", "status", "description"
        ]

    def get_type_name(self, obj):
        try:
            # 匹配字典表中“知识库类型”子级（parent_id=1）且id=obj.type_id的记录
            dict_data = Dictionary.objects.get(
                parent_id=1,  # 父级=知识库类型枚举组id（假设为1）
                id=obj.type_id,
                status=True  # 仅启用的类型
            )
            return dict_data.label
        except Dictionary.DoesNotExist:
            return "未知类型"

    # 自定义方法：获取负责人名称
    def get_master_name(self, obj):
        return obj.master.username if obj.master else "未知用户"


class KnowledgeCreateUpdateSerializer(serializers.ModelSerializer):
    """知识库新增/编辑序列化器（验证type_id是否存在）"""
    class Meta:
        model = KnowledgeBase
        fields = [
            "name", "type_id", "limits", "description", "icon_url",
            "status"  # 编辑时可修改状态（如归档）
        ]
        extra_kwargs = {
            "name": {"required": True, "error_messages": {"required": "请输入知识库名称"}},
            "type_id": {"required": True, "error_messages": {"required": "请选择知识库类型"}},
            "limits": {"required": True, "error_messages": {"required": "请选择可见范围"}},
        }

    # 验证type_id：必须是字典表中“知识库类型”的有效子级id
    def validate_type_id(self, value):
        if not Dictionary.objects.filter(
            parent_id=1,  # 父级=知识库类型枚举组
            id=value,
            status=True,
            is_value=True  # 必须是具体业务值
        ).exists():
            raise serializers.ValidationError("选择的知识库类型不存在或已禁用")
        return value

    # 新增时自动填充负责人（当前登录用户）
    def create(self, validated_data):
        validated_data["master"] = self.context["request"].user
        return super().create(validated_data)





# apps/system/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
# from .models import DictData, KnowledgeRepository



class DictRepoTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """仅提供“获取知识库类型下拉选项”接口（无需修改字典数据）"""
    # 筛选条件：父级=知识库类型枚举组（parent_id=1）、启用、具体业务值
    queryset = Dictionary.objects.filter(
        parent_id=1,
        status=True,
        is_value=True
    ).order_by("sort")
    serializer_class = DictRepoTypeSerializer

    # 自定义接口：获取所有知识库类型（供前端下拉使用）
    @action(detail=False, methods=["get"], url_path="repo-types")
    def get_repo_types(self, request):
        data = self.get_serializer(self.queryset, many=True).data
        return Response(data)

# class DictRepoTypeViewSet(viewsets.ReadOnlyModelViewSet):
#     """仅提供"获取知识库类型下拉选项"接口"""
#     # 筛选条件：父级=知识库类型枚举组（parent_id=1）、启用、具体业务值
#     queryset = Dictionary.objects.filter(
#         parent_id=1,
#         status=True,
#         is_value=True
#     ).order_by("sort")
#     serializer_class = DictRepoTypeSerializer
#
#     # 自定义接口：获取所有知识库类型（供前端下拉使用）
#     @action(detail=False, methods=["get"], url_path="repo-types")
#     def get_repo_types(self, request):
#         data = self.get_serializer(self.queryset, many=True).data
#         return Response(data)



class KnowledgeBaseViewSet(viewsets.ModelViewSet):
    """知识库CRUD视图集"""
    queryset = KnowledgeBase.objects.filter(recycle=0).order_by("-create_time")
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["type_id", "status", "limits"]  # 支持按类型、状态、可见范围筛选

    # 动态选择序列化器
    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return KnowledgeCreateUpdateSerializer
        return KnowledgeListSerializer

    # 列表接口：返回分页数据（前端需要list+total）
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                "list": serializer.data,
                "total": self.paginator.page.paginator.count
            })
        serializer = self.get_serializer(queryset, many=True)
        return Response({"list": serializer.data, "total": queryset.count()})

    # 删除接口：逻辑删除（设置recycle=1）
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.recycle = 1
        instance.recycle_user_id = request.user
        instance.recycle_time = timezone.now()
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)