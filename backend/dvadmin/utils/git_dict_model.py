from django.core.cache import cache
from dvadmin.system.models import Dictionary, Users


def get_dict_label(dict_type, dict_value):
    """
    根据字典类型和值获取标签
    """
    cache_key = f"dict_{dict_type}_{dict_value}"
    cached_value = cache.get(cache_key)

    if cached_value is not None:
        return cached_value

    try:
        # 首先尝试通过父级查找字典类型
        parent_dict = Dictionary.objects.get(
            label=dict_type,
            is_value=False
        )

        # 然后查找具体的字典项
        dict_item = Dictionary.objects.get(
            parent=parent_dict,
            value=str(dict_value),
            status=True
        )

        label = dict_item.label
        # 缓存结果，有效期1小时
        cache.set(cache_key, label, 3600)
        return label

    except Dictionary.DoesNotExist:
        # 如果找不到，尝试直接查找（适用于没有父级的情况）
        try:
            dict_item = Dictionary.objects.get(
                label=dict_type,
                value=str(dict_value),
                status=True
            )

            label = dict_item.label
            cache.set(cache_key, label, 3600)
            return label

        except Dictionary.DoesNotExist:
            # 如果还是找不到，返回原始值
            return str(dict_value)


def validate_dict_value(dict_type, dict_value):
    """
    验证字典值是否有效
    """
    cache_key = f"dict_validate_{dict_type}_{dict_value}"
    cached_value = cache.get(cache_key)

    if cached_value is not None:
        return cached_value

    try:
        # 首先尝试通过父级查找字典类型
        parent_dict = Dictionary.objects.get(
            label=dict_type,
            is_value=False
        )

        # 然后验证具体的字典项是否存在
        exists = Dictionary.objects.filter(
            parent=parent_dict,
            value=str(dict_value),
            status=True
        ).exists()

        cache.set(cache_key, exists, 3600)
        return exists

    except Dictionary.DoesNotExist:
        # 如果找不到父级，尝试直接查找
        exists = Dictionary.objects.filter(
            label=dict_type,
            value=str(dict_value),
            status=True
        ).exists()

        cache.set(cache_key, exists, 3600)
        return exists


def get_dict_options(dict_type):
    """
    获取字典选项列表
    """
    cache_key = f"dict_options_{dict_type}"
    cached_value = cache.get(cache_key)

    if cached_value is not None:
        return cached_value

    try:
        # 首先尝试通过父级查找字典类型
        parent_dict = Dictionary.objects.get(
            label=dict_type,
            is_value=False
        )

        # 然后获取所有子项
        items = Dictionary.objects.filter(
            parent=parent_dict,
            status=True
        ).order_by('sort')

        options = [{'value': item.value, 'label': item.label} for item in items]

        cache.set(cache_key, options, 3600)
        return options

    except Dictionary.DoesNotExist:
        # 如果找不到父级，尝试直接查找
        items = Dictionary.objects.filter(
            label=dict_type,
            status=True
        ).order_by('sort')

        options = [{'value': item.value, 'label': item.label} for item in items]

        cache.set(cache_key, options, 3600)
        return options


def get_user_name(user_id):
    """
    根据用户ID获取用户名称
    """
    cache_key = f"user_name_{user_id}"
    cached_value = cache.get(cache_key)

    if cached_value is not None:
        return cached_value

    try:
        user = Users.objects.get(id=user_id)
        username = user.name
        cache.set(cache_key, username, 3600)
        return username
    except Users.DoesNotExist:
        return f"未知用户 ({user_id})"