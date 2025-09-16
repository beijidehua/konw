# -*- coding: utf-8 -*-

"""
@author: H0nGzA1
@contact: QQ:2505811377
@Remark: 仓库管理
"""
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from dvadmin.system.models import Users
from dvadmin.utils.filters import DataLevelPermissionsFilter
from dvadmin.utils.json_response import DetailResponse, SuccessResponse, ErrorResponse
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet
from django.utils import timezone

from dvadmin.system.models import MmRepository


class MmRepositorySerializer(CustomModelSerializer):
    """
    仓库-序列化器
    """
    status_label = serializers.SerializerMethodField()
    limits_label = serializers.SerializerMethodField()
    recycle_label = serializers.SerializerMethodField()
    has_children = serializers.SerializerMethodField()
    hasChild = serializers.SerializerMethodField()

    def get_status_label(self, obj: MmRepository):
        return dict(MmRepository.STATUS_CHOICES).get(obj.status, '')

    def get_limits_label(self, obj: MmRepository):
        return dict(MmRepository.LIMITS_CHOICES).get(obj.limits, '')

    def get_recycle_label(self, obj: MmRepository):
        return dict(MmRepository.RECYCLE_CHOICES).get(obj.recycle, '')

    def get_hasChild(self, instance):
        # 这里可以根据需要实现，如果有子仓库的概念
        return False

    def get_has_children(self, obj: MmRepository):
        # 这里可以根据需要实现，如果有子仓库的概念
        return 0

    class Meta:
        model = MmRepository
        fields = '__all__'
        read_only_fields = ["id"]


class MmRepositoryImportSerializer(CustomModelSerializer):
    """
    仓库-导入-序列化器
    """

    class Meta:
        model = MmRepository
        fields = '__all__'
        read_only_fields = ["id"]


class MmRepositoryCreateUpdateSerializer(CustomModelSerializer):
    """
    仓库管理 创建/更新时的列化器
    """

    class Meta:
        model = MmRepository
        fields = '__all__'


class MmRepositoryViewSet(CustomModelViewSet):
    """
    仓库管理接口
    list:查询
    create:新增
    update:修改
    retrieve:单例
    destroy:删除
    """
    queryset = MmRepository.objects.all()
    serializer_class = MmRepositorySerializer
    create_serializer_class = MmRepositoryCreateUpdateSerializer
    update_serializer_class = MmRepositoryCreateUpdateSerializer
    filter_fields = ['name', 'id', 'type_id', 'master', 'status', 'recycle']
    search_fields = ['name', 'description']
    # extra_filter_class = []
    import_serializer_class = MmRepositoryImportSerializer
    import_field_dict = {
        "name": "仓库名称",
        "type_id": "类型ID",
        "master": "负责人",
    }

    def list(self, request, *args, **kwargs):
        # 如果懒加载，则只返回父级
        request.query_params._mutable = True
        params = request.query_params
        page = params.get('page', None)
        limit = params.get('limit', None)
        if page:
            del params['page']
        if limit:
            del params['limit']
        queryset = self.filter_queryset(self.get_queryset())
        serializer = MmRepositorySerializer(queryset, many=True, request=request)
        data = serializer.data
        return SuccessResponse(data=data)

    @action(methods=["GET"], detail=False, permission_classes=[IsAuthenticated])
    def all_repository(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        data = queryset.filter(status='normal', recycle=0).order_by('create_time').values('name', 'id')
        return DetailResponse(data=data, msg="获取成功")

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def archive(self, request, pk=None):
        """归档仓库"""
        repository = self.get_object()
        if repository.status == 'archived':
            return ErrorResponse(msg="仓库已经归档")

        repository.status = 'archived'
        repository.archived_time = timezone.now()
        repository.archived_user_id = request.user.id
        repository.archived_desc = request.data.get('archived_desc', '')
        repository.save()

        serializer = self.get_serializer(repository)
        return SuccessResponse(data=serializer.data, msg="归档成功")

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def restore(self, request, pk=None):
        """恢复已归档的仓库"""
        repository = self.get_object()
        if repository.status != 'archived':
            return ErrorResponse(msg="仓库未归档")

        repository.status = 'normal'
        repository.archived_time = None
        repository.archived_user_id = None
        repository.archived_desc = None
        repository.save()

        serializer = self.get_serializer(repository)
        return SuccessResponse(data=serializer.data, msg="恢复成功")

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def recycle(self, request, pk=None):
        """回收仓库"""
        repository = self.get_object()
        if repository.recycle == 1:
            return ErrorResponse(msg="仓库已经回收")

        repository.recycle = 1
        repository.recycle_time = timezone.now()
        repository.recycle_user_id = request.user.id
        repository.save()

        serializer = self.get_serializer(repository)
        return SuccessResponse(data=serializer.data, msg="回收成功")

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def restore_recycle(self, request, pk=None):
        """恢复回收的仓库"""
        repository = self.get_object()
        if repository.recycle != 1:
            return ErrorResponse(msg="仓库未回收")

        repository.recycle = 0
        repository.recycle_time = None
        repository.recycle_user_id = None
        repository.save()

        serializer = self.get_serializer(repository)
        return SuccessResponse(data=serializer.data, msg="恢复成功")

    def destroy(self, request, *args, **kwargs):
        """重写删除方法，改为回收操作"""
        instance = self.get_object()
        instance.recycle = 1
        instance.recycle_time = timezone.now()
        instance.recycle_user_id = request.user.id
        instance.save()
        return SuccessResponse(data=[], msg="删除成功")

    @action(methods=['GET'], detail=False, permission_classes=[])
    def repository_info(self, request):
        """仓库信息"""
        repository_id = request.query_params.get('repository_id')
        if repository_id is None:
            return ErrorResponse(msg="仓库不存在")

        try:
            repository = MmRepository.objects.get(id=repository_id)
        except MmRepository.DoesNotExist:
            return ErrorResponse(msg="仓库不存在")

        # 这里可以根据需要添加更多统计信息
        data = {
            'repository_name': repository.name,
            'type_id': repository.type_id,
            'master': repository.master,
            'status': repository.status,
            'status_label': dict(MmRepository.STATUS_CHOICES).get(repository.status, ''),
            'create_time': repository.create_time,
            'description': repository.description,
        }
        return SuccessResponse(data=data, msg="获取成功")