from rest_framework import serializers
from .models import KnowledgeBase

class KnowledgeBaseDetailSerializer(serializers.ModelSerializer):
    """知识库详情序列化器"""
    masterName = serializers.CharField(source='master.name', read_only=True)  # 负责人姓名
    stat     ccccccccccccccccccccccccccc usLabel = serializers.CharField(source='get_status_display', read_only=True)  # 状态中文显示

    class Meta:
        model = KnowledgeBase
        fields = [
            'id', 'name', 'description', 'create_datetime',
            'masterName', 'doc_count', 'view_count',
            'status', 'statusLabel'
        ]
        read_only_fields = fields  # 详情接口通常为只读


from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import KnowledgeBase



class KnowledgeBaseViewSet(viewsets.GenericViewSet):
    """知识库视图集"""
    queryset = KnowledgeBase.objects.all()
    serializer_class = KnowledgeBaseDetailSerializer

    @action(detail=True, methods=['get'], url_path='overview')
    def overview(self, request, pk=None):
        """获取知识库详情"""
        try:
            knowledge_base = self.get_object()
            # 增加访问量（可选功能）
            knowledge_base.view_count += 1
            knowledge_base.save(update_fields=['view_count'])

            serializer = self.get_serializer(knowledge_base)
            return Response({
                'code': 2000,
                'data': serializer.data,
                'msg': 'success'
            })
        except KnowledgeBase.DoesNotExist:
            return Response({
                'code': 4000,
                'msg': '知识库不存在'
            }, status=status.HTTP_404_NOT_FOUND)
