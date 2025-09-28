import hashlib
import os
from time import time
from pathlib import PurePosixPath

from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from application import dispatch
from dvadmin.utils.models import CoreModel, table_prefix, get_custom_app_models


class Role(CoreModel):
    name = models.CharField(max_length=64, verbose_name="角色名称", help_text="角色名称")
    key = models.CharField(max_length=64, unique=True, verbose_name="权限字符", help_text="权限字符")
    sort = models.IntegerField(default=1, verbose_name="角色顺序", help_text="角色顺序")
    status = models.BooleanField(default=True, verbose_name="角色状态", help_text="角色状态")

    class Meta:
        db_table = table_prefix + "system_role"
        verbose_name = "角色表"
        verbose_name_plural = verbose_name
        ordering = ("sort",)


class CustomUserManager(UserManager):

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        user = super(CustomUserManager, self).create_superuser(username, email, password, **extra_fields)
        user.set_password(password)
        try:
            user.role.add(Role.objects.get(name="管理员"))
            user.save(using=self._db)
            return user
        except ObjectDoesNotExist:
            user.delete()
            raise ValidationError("角色`管理员`不存在, 创建失败, 请先执行python manage.py init")


class Users(CoreModel, AbstractUser):
    username = models.CharField(max_length=150, unique=True, db_index=True, verbose_name="用户账号",
                                help_text="用户账号")
    email = models.EmailField(max_length=255, verbose_name="邮箱", null=True, blank=True, help_text="邮箱")
    mobile = models.CharField(max_length=255, verbose_name="电话", null=True, blank=True, help_text="电话")
    avatar = models.CharField(max_length=255, verbose_name="头像", null=True, blank=True, help_text="头像")
    name = models.CharField(max_length=40, verbose_name="姓名", help_text="姓名")
    GENDER_CHOICES = (
        (0, "未知"),
        (1, "男"),
        (2, "女"),
    )
    gender = models.IntegerField(
        choices=GENDER_CHOICES, default=0, verbose_name="性别", null=True, blank=True, help_text="性别"
    )
    USER_TYPE = (
        (0, "后台用户"),
        (1, "前台用户"),
    )
    user_type = models.IntegerField(
        choices=USER_TYPE, default=0, verbose_name="用户类型", null=True, blank=True, help_text="用户类型"
    )
    post = models.ManyToManyField(to="Post", blank=True, verbose_name="关联岗位", db_constraint=False,
                                  help_text="关联岗位")
    role = models.ManyToManyField(to="Role", blank=True, verbose_name="关联角色", db_constraint=False,
                                  help_text="关联角色")
    dept = models.ForeignKey(
        to="Dept",
        verbose_name="所属部门",
        on_delete=models.PROTECT,
        db_constraint=False,
        null=True,
        blank=True,
        help_text="关联部门",
    )
    login_error_count = models.IntegerField(default=0, verbose_name="登录错误次数", help_text="登录错误次数")
    pwd_change_count = models.IntegerField(default=0,blank=True, verbose_name="密码修改次数", help_text="密码修改次数")
    objects = CustomUserManager()

    def set_password(self, raw_password):
        if raw_password:
            super().set_password(hashlib.md5(raw_password.encode(encoding="UTF-8")).hexdigest())

    def save(self, *args, **kwargs):
        if self.name == "":
            self.name = self.username
        super().save(*args, **kwargs)

    class Meta:
        db_table = table_prefix + "system_users"
        verbose_name = "用户表"
        verbose_name_plural = verbose_name
        ordering = ("-create_datetime",)


class Post(CoreModel):
    name = models.CharField(null=False, max_length=64, verbose_name="岗位名称", help_text="岗位名称")
    code = models.CharField(max_length=32, verbose_name="岗位编码", help_text="岗位编码")
    sort = models.IntegerField(default=1, verbose_name="岗位顺序", help_text="岗位顺序")
    STATUS_CHOICES = (
        (0, "离职"),
        (1, "在职"),
    )
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="岗位状态", help_text="岗位状态")

    class Meta:
        db_table = table_prefix + "system_post"
        verbose_name = "岗位表"
        verbose_name_plural = verbose_name
        ordering = ("sort",)


class Dept(CoreModel):
    name = models.CharField(max_length=64, verbose_name="部门名称", help_text="部门名称")
    key = models.CharField(max_length=64, unique=True, null=True, blank=True, verbose_name="关联字符", help_text="关联字符")
    sort = models.IntegerField(default=1, verbose_name="显示排序", help_text="显示排序")
    owner = models.CharField(max_length=32, verbose_name="负责人", null=True, blank=True, help_text="负责人")
    phone = models.CharField(max_length=32, verbose_name="联系电话", null=True, blank=True, help_text="联系电话")
    email = models.EmailField(max_length=32, verbose_name="邮箱", null=True, blank=True, help_text="邮箱")
    status = models.BooleanField(default=True, verbose_name="部门状态", null=True, blank=True, help_text="部门状态")
    parent = models.ForeignKey(
        to="Dept",
        on_delete=models.CASCADE,
        default=None,
        verbose_name="上级部门",
        db_constraint=False,
        null=True,
        blank=True,
        help_text="上级部门",
    )

    @classmethod
    def _recursion(cls, instance, parent, result):
        new_instance = getattr(instance, parent, None)
        res = []
        data = getattr(instance, result, None)
        if data:
            res.append(data)
        if new_instance:
            array = cls._recursion(new_instance, parent, result)
            res += array
        return res

    @classmethod
    def get_region_name(cls, obj):
        """
        获取某个用户的递归所有部门名称
        """
        dept_name_all = cls._recursion(obj, "parent", "name")
        dept_name_all.reverse()
        return "/".join(dept_name_all)

    @classmethod
    def recursion_all_dept(cls, dept_id: int, dept_all_list=None, dept_list=None):
        """
        递归获取部门的所有下级部门
        :param dept_id: 需要获取的id
        :param dept_all_list: 所有列表
        :param dept_list: 递归list
        :return:
        """
        if not dept_all_list:
            dept_all_list = Dept.objects.values("id", "parent")
        if dept_list is None:
            dept_list = [dept_id]
        for ele in dept_all_list:
            if ele.get("parent") == dept_id:
                dept_list.append(ele.get("id"))
                cls.recursion_all_dept(ele.get("id"), dept_all_list, dept_list)
        return list(set(dept_list))

    class Meta:
        db_table = table_prefix + "system_dept"
        verbose_name = "部门表"
        verbose_name_plural = verbose_name
        ordering = ("sort",)


class Menu(CoreModel):
    parent = models.ForeignKey(
        to="Menu",
        on_delete=models.CASCADE,
        verbose_name="上级菜单",
        null=True,
        blank=True,
        db_constraint=False,
        help_text="上级菜单",
    )
    icon = models.CharField(max_length=64, verbose_name="菜单图标", null=True, blank=True, help_text="菜单图标")
    name = models.CharField(max_length=64, verbose_name="菜单名称", help_text="菜单名称")
    sort = models.IntegerField(default=1, verbose_name="显示排序", null=True, blank=True, help_text="显示排序")
    ISLINK_CHOICES = (
        (0, "否"),
        (1, "是"),
    )
    is_link = models.BooleanField(default=False, verbose_name="是否外链", help_text="是否外链")
    link_url = models.CharField(max_length=255, verbose_name="链接地址", null=True, blank=True, help_text="链接地址")
    is_catalog = models.BooleanField(default=False, verbose_name="是否目录", help_text="是否目录")
    web_path = models.CharField(max_length=128, verbose_name="路由地址", null=True, blank=True, help_text="路由地址")
    component = models.CharField(max_length=128, verbose_name="组件地址", null=True, blank=True, help_text="组件地址")
    component_name = models.CharField(max_length=50, verbose_name="组件名称", null=True, blank=True,
                                      help_text="组件名称")
    status = models.BooleanField(default=True, blank=True, verbose_name="菜单状态", help_text="菜单状态")
    cache = models.BooleanField(default=False, blank=True, verbose_name="是否页面缓存", help_text="是否页面缓存")
    visible = models.BooleanField(default=True, blank=True, verbose_name="侧边栏中是否显示",
                                  help_text="侧边栏中是否显示")
    is_iframe = models.BooleanField(default=False, blank=True, verbose_name="框架外显示", help_text="框架外显示")
    is_affix = models.BooleanField(default=False, blank=True, verbose_name="是否固定", help_text="是否固定")

    @classmethod
    def get_all_parent(cls, id: int, all_list=None, nodes=None):
        """
        递归获取给定ID的所有层级
        :param id: 参数ID
        :param all_list: 所有列表
        :param nodes: 递归列表
        :return: nodes
        """
        if not all_list:
            all_list = Menu.objects.values("id", "name", "parent")
        if nodes is None:
            nodes = []
        for ele in all_list:
            if ele.get("id") == id:
                parent_id = ele.get("parent")
                if parent_id is not None:
                    cls.get_all_parent(parent_id, all_list, nodes)
                nodes.append(ele)
        return nodes
    class Meta:
        db_table = table_prefix + "system_menu"
        verbose_name = "菜单表"
        verbose_name_plural = verbose_name
        ordering = ("sort",)

class MenuField(CoreModel):
    model = models.CharField(max_length=64, verbose_name='表名')
    menu = models.ForeignKey(to='Menu', on_delete=models.CASCADE, verbose_name='菜单', db_constraint=False)
    field_name = models.CharField(max_length=64, verbose_name='模型表字段名')
    title = models.CharField(max_length=64, verbose_name='字段显示名')
    class Meta:
        db_table = table_prefix + "system_menu_field"
        verbose_name = "菜单字段表"
        verbose_name_plural = verbose_name
        ordering = ("id",)

class FieldPermission(CoreModel):
    role = models.ForeignKey(to='Role', on_delete=models.CASCADE, verbose_name='角色', db_constraint=False)
    field = models.ForeignKey(to='MenuField', on_delete=models.CASCADE,related_name='menu_field', verbose_name='字段', db_constraint=False)
    is_query = models.BooleanField(default=1, verbose_name='是否可查询')
    is_create = models.BooleanField(default=1, verbose_name='是否可创建')
    is_update = models.BooleanField(default=1, verbose_name='是否可更新')

    class Meta:
        db_table = table_prefix + "system_field_permission"
        verbose_name = "字段权限表"
        verbose_name_plural = verbose_name
        ordering = ("id",)


class MenuButton(CoreModel):
    menu = models.ForeignKey(
        to="Menu",
        db_constraint=False,
        related_name="menuPermission",
        on_delete=models.CASCADE,
        verbose_name="关联菜单",
        help_text="关联菜单",
    )
    name = models.CharField(max_length=64, verbose_name="名称", help_text="名称")
    value = models.CharField(unique=True, max_length=64, verbose_name="权限值", help_text="权限值")
    api = models.CharField(max_length=200, verbose_name="接口地址", help_text="接口地址")
    METHOD_CHOICES = (
        (0, "GET"),
        (1, "POST"),
        (2, "PUT"),
        (3, "DELETE"),
    )
    method = models.IntegerField(default=0, verbose_name="接口请求方法", null=True, blank=True,
                                 help_text="接口请求方法")

    class Meta:
        db_table = table_prefix + "system_menu_button"
        verbose_name = "菜单权限表"
        verbose_name_plural = verbose_name
        ordering = ("-name",)


class RoleMenuPermission(CoreModel):
    role = models.ForeignKey(
        to="Role",
        db_constraint=False,
        related_name="role_menu",
        on_delete=models.CASCADE,
        verbose_name="关联角色",
        help_text="关联角色",
    )
    menu = models.ForeignKey(
        to="Menu",
        db_constraint=False,
        related_name="role_menu",
        on_delete=models.CASCADE,
        verbose_name="关联菜单",
        help_text="关联菜单",
    )

    class Meta:
        db_table = table_prefix + "role_menu_permission"
        verbose_name = "角色菜单权限表"
        verbose_name_plural = verbose_name
        # ordering = ("-create_datetime",)


class RoleMenuButtonPermission(CoreModel):
    role = models.ForeignKey(
        to="Role",
        db_constraint=False,
        related_name="role_menu_button",
        on_delete=models.CASCADE,
        verbose_name="关联角色",
        help_text="关联角色",
    )
    menu_button = models.ForeignKey(
        to="MenuButton",
        db_constraint=False,
        related_name="menu_button_permission",
        on_delete=models.CASCADE,
        verbose_name="关联菜单按钮",
        help_text="关联菜单按钮",
        null=True,
        blank=True
    )
    DATASCOPE_CHOICES = (
        (0, "仅本人数据权限"),
        (1, "本部门及以下数据权限"),
        (2, "本部门数据权限"),
        (3, "全部数据权限"),
        (4, "自定数据权限"),
    )
    data_range = models.IntegerField(default=0, choices=DATASCOPE_CHOICES, verbose_name="数据权限范围",
                                     help_text="数据权限范围")
    dept = models.ManyToManyField(to="Dept", blank=True, verbose_name="数据权限-关联部门", db_constraint=False,
                                  help_text="数据权限-关联部门")

    class Meta:
        db_table = table_prefix + "role_menu_button_permission"
        verbose_name = "角色按钮权限表"
        verbose_name_plural = verbose_name
        ordering = ("-create_datetime",)


class Dictionary(CoreModel):
    TYPE_LIST = (
        (0, "text"),
        (1, "number"),
        (2, "date"),
        (3, "datetime"),
        (4, "time"),
        (5, "files"),
        (6, "boolean"),
        (7, "images"),
    )
    label = models.CharField(max_length=100, blank=True, null=True, verbose_name="字典名称", help_text="字典名称")
    value = models.CharField(max_length=200, blank=True, null=True, verbose_name="字典编号", help_text="字典编号/实际值")
    parent = models.ForeignKey(
        to="self",
        related_name="sublist",
        db_constraint=False,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name="父级",
        help_text="父级",
    )
    type = models.IntegerField(choices=TYPE_LIST, default=0, verbose_name="数据值类型", help_text="数据值类型")
    color = models.CharField(max_length=20, blank=True, null=True, verbose_name="颜色", help_text="颜色")
    is_value = models.BooleanField(default=False, verbose_name="是否为value值",
                                   help_text="是否为value值,用来做具体值存放")
    status = models.BooleanField(default=True, verbose_name="状态", help_text="状态")
    sort = models.IntegerField(default=1, verbose_name="显示排序", null=True, blank=True, help_text="显示排序")
    remark = models.CharField(max_length=2000, blank=True, null=True, verbose_name="备注", help_text="备注")

    class Meta:
        db_table = table_prefix + "system_dictionary"
        verbose_name = "字典表"
        verbose_name_plural = verbose_name
        ordering = ("sort",)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert, force_update, using, update_fields)
        dispatch.refresh_dictionary()  # 有更新则刷新字典配置

    def delete(self, using=None, keep_parents=False):
        res = super().delete(using, keep_parents)
        dispatch.refresh_dictionary()
        return res


class OperationLog(CoreModel):
    request_modular = models.CharField(max_length=64, verbose_name="请求模块", null=True, blank=True,
                                       help_text="请求模块")
    request_path = models.CharField(max_length=400, verbose_name="请求地址", null=True, blank=True,
                                    help_text="请求地址")
    request_body = models.TextField(verbose_name="请求参数", null=True, blank=True, help_text="请求参数")
    request_method = models.CharField(max_length=8, verbose_name="请求方式", null=True, blank=True,
                                      help_text="请求方式")
    request_msg = models.TextField(verbose_name="操作说明", null=True, blank=True, help_text="操作说明")
    request_ip = models.CharField(max_length=32, verbose_name="请求ip地址", null=True, blank=True,
                                  help_text="请求ip地址")
    request_browser = models.CharField(max_length=64, verbose_name="请求浏览器", null=True, blank=True,
                                       help_text="请求浏览器")
    response_code = models.CharField(max_length=32, verbose_name="响应状态码", null=True, blank=True,
                                     help_text="响应状态码")
    request_os = models.CharField(max_length=64, verbose_name="操作系统", null=True, blank=True, help_text="操作系统")
    json_result = models.TextField(verbose_name="返回信息", null=True, blank=True, help_text="返回信息")
    status = models.BooleanField(default=False, verbose_name="响应状态", help_text="响应状态")

    class Meta:
        db_table = table_prefix + "system_operation_log"
        verbose_name = "操作日志"
        verbose_name_plural = verbose_name
        ordering = ("-create_datetime",)


def media_file_name(instance, filename):
    h = instance.md5sum
    basename, ext = os.path.splitext(filename)
    return os.path.join("files", h[:1], h[1:2], h + ext.lower())


class FileList(CoreModel):
    name = models.CharField(max_length=200, null=True, blank=True, verbose_name="名称", help_text="名称")
    url = models.FileField(upload_to=media_file_name, null=True, blank=True,)
    file_url = models.CharField(max_length=255, blank=True, verbose_name="文件地址", help_text="文件地址")
    engine = models.CharField(max_length=100, default='local', blank=True, verbose_name="引擎", help_text="引擎")
    mime_type = models.CharField(max_length=100, blank=True, verbose_name="Mime类型", help_text="Mime类型")
    size = models.CharField(max_length=36, blank=True, verbose_name="文件大小", help_text="文件大小")
    md5sum = models.CharField(max_length=36, blank=True, verbose_name="文件md5", help_text="文件md5")
    UPLOAD_METHOD_CHOIDES = (
        (0, '默认上传'),
        (1, '文件选择器上传'),
    )
    upload_method = models.SmallIntegerField(default=0, blank=True, null=True, choices=UPLOAD_METHOD_CHOIDES, verbose_name='上传方式', help_text='上传方式')
    FILE_TYPE_CHOIDES = (
        (0, '图片'),
        (1, '视频'),
        (2, '音频'),
        (3, '其他'),
    )
    file_type = models.SmallIntegerField(default=3, choices=FILE_TYPE_CHOIDES, blank=True, null=True, verbose_name='文件类型', help_text='文件类型')

    def save(self, *args, **kwargs):
        if not self.md5sum:  # file is new
            md5 = hashlib.md5()
            for chunk in self.url.chunks():
                md5.update(chunk)
            self.md5sum = md5.hexdigest()
        if not self.size:
            self.size = self.url.size
        if not self.file_url:
            url = media_file_name(self, self.name)
            self.file_url = f'media/{url}'
        super(FileList, self).save(*args, **kwargs)

    class Meta:
        db_table = table_prefix + "system_file_list"
        verbose_name = "文件管理"
        verbose_name_plural = verbose_name
        ordering = ("-create_datetime",)


class Area(CoreModel):
    name = models.CharField(max_length=100, verbose_name="名称", help_text="名称")
    code = models.CharField(max_length=20, verbose_name="地区编码", help_text="地区编码", unique=True, db_index=True)
    level = models.BigIntegerField(verbose_name="地区层级(1省份 2城市 3区县 4乡级)",
                                   help_text="地区层级(1省份 2城市 3区县 4乡级)")
    pinyin = models.CharField(max_length=255, verbose_name="拼音", help_text="拼音")
    initials = models.CharField(max_length=20, verbose_name="首字母", help_text="首字母")
    enable = models.BooleanField(default=True, verbose_name="是否启用", help_text="是否启用")
    pcode = models.ForeignKey(
        to="self",
        verbose_name="父地区编码",
        to_field="code",
        on_delete=models.CASCADE,
        db_constraint=False,
        null=True,
        blank=True,
        help_text="父地区编码",
    )

    class Meta:
        db_table = table_prefix + "system_area"
        verbose_name = "地区表"
        verbose_name_plural = verbose_name
        ordering = ("code",)

    def __str__(self):
        return f"{self.name}"


class ApiWhiteList(CoreModel):
    url = models.CharField(max_length=200, help_text="url地址", verbose_name="url")
    METHOD_CHOICES = (
        (0, "GET"),
        (1, "POST"),
        (2, "PUT"),
        (3, "DELETE"),
    )
    method = models.IntegerField(default=0, verbose_name="接口请求方法", null=True, blank=True,
                                 help_text="接口请求方法")
    enable_datasource = models.BooleanField(default=True, verbose_name="激活数据权限", help_text="激活数据权限",
                                            blank=True)

    class Meta:
        db_table = table_prefix + "api_white_list"
        verbose_name = "接口白名单"
        verbose_name_plural = verbose_name
        ordering = ("-create_datetime",)


class SystemConfig(CoreModel):
    parent = models.ForeignKey(
        to="self",
        verbose_name="父级",
        on_delete=models.CASCADE,
        db_constraint=False,
        null=True,
        blank=True,
        help_text="父级",
    )
    title = models.CharField(max_length=50, verbose_name="标题", help_text="标题")
    key = models.CharField(max_length=100, verbose_name="键", help_text="键", db_index=True)
    value = models.JSONField(max_length=100, verbose_name="值", help_text="值", null=True, blank=True)
    sort = models.IntegerField(default=0, verbose_name="排序", help_text="排序", blank=True)
    status = models.BooleanField(default=True, verbose_name="启用状态", help_text="启用状态")
    data_options = models.JSONField(verbose_name="数据options", help_text="数据options", null=True, blank=True)
    FORM_ITEM_TYPE_LIST = (
        (0, "text"),
        (1, "datetime"),
        (2, "date"),
        (3, "textarea"),
        (4, "select"),
        (5, "checkbox"),
        (6, "radio"),
        (7, "img"),
        (8, "file"),
        (9, "switch"),
        (10, "number"),
        (11, "array"),
        (12, "imgs"),
        (13, "foreignkey"),
        (14, "manytomany"),
        (15, "time"),
    )
    form_item_type = models.IntegerField(
        choices=FORM_ITEM_TYPE_LIST, verbose_name="表单类型", help_text="表单类型", default=0, blank=True
    )
    rule = models.JSONField(null=True, blank=True, verbose_name="校验规则", help_text="校验规则")
    placeholder = models.CharField(max_length=50, null=True, blank=True, verbose_name="提示信息", help_text="提示信息")
    setting = models.JSONField(null=True, blank=True, verbose_name="配置", help_text="配置")

    class Meta:
        db_table = table_prefix + "system_config"
        verbose_name = "系统配置表"
        verbose_name_plural = verbose_name
        ordering = ("sort",)
        unique_together = (("key", "parent_id"),)

    def __str__(self):
        return f"{self.title}"

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert, force_update, using, update_fields)
        dispatch.refresh_system_config()  # 有更新则刷新系统配置

    def delete(self, using=None, keep_parents=False):
        res = super().delete(using, keep_parents)
        dispatch.refresh_system_config()
        return res


class LoginLog(CoreModel):
    LOGIN_TYPE_CHOICES = ((1, "普通登录"), (2, "微信扫码登录"),)
    username = models.CharField(max_length=32, verbose_name="登录用户名", null=True, blank=True, help_text="登录用户名")
    ip = models.CharField(max_length=32, verbose_name="登录ip", null=True, blank=True, help_text="登录ip")
    agent = models.TextField(verbose_name="agent信息", null=True, blank=True, help_text="agent信息")
    browser = models.CharField(max_length=200, verbose_name="浏览器名", null=True, blank=True, help_text="浏览器名")
    os = models.CharField(max_length=200, verbose_name="操作系统", null=True, blank=True, help_text="操作系统")
    continent = models.CharField(max_length=50, verbose_name="州", null=True, blank=True, help_text="州")
    country = models.CharField(max_length=50, verbose_name="国家", null=True, blank=True, help_text="国家")
    province = models.CharField(max_length=50, verbose_name="省份", null=True, blank=True, help_text="省份")
    city = models.CharField(max_length=50, verbose_name="城市", null=True, blank=True, help_text="城市")
    district = models.CharField(max_length=50, verbose_name="县区", null=True, blank=True, help_text="县区")
    isp = models.CharField(max_length=50, verbose_name="运营商", null=True, blank=True, help_text="运营商")
    area_code = models.CharField(max_length=50, verbose_name="区域代码", null=True, blank=True, help_text="区域代码")
    country_english = models.CharField(max_length=50, verbose_name="英文全称", null=True, blank=True,
                                       help_text="英文全称")
    country_code = models.CharField(max_length=50, verbose_name="简称", null=True, blank=True, help_text="简称")
    longitude = models.CharField(max_length=50, verbose_name="经度", null=True, blank=True, help_text="经度")
    latitude = models.CharField(max_length=50, verbose_name="纬度", null=True, blank=True, help_text="纬度")
    login_type = models.IntegerField(default=1, choices=LOGIN_TYPE_CHOICES, verbose_name="登录类型",
                                     help_text="登录类型")

    class Meta:
        db_table = table_prefix + "system_login_log"
        verbose_name = "登录日志"
        verbose_name_plural = verbose_name
        ordering = ("-create_datetime",)


class MessageCenter(CoreModel):
    title = models.CharField(max_length=100, verbose_name="标题", help_text="标题")
    content = models.TextField(verbose_name="内容", help_text="内容")
    target_type = models.IntegerField(default=0, verbose_name="目标类型", help_text="目标类型")
    target_user = models.ManyToManyField(to=Users, related_name='user', through='MessageCenterTargetUser',
                                         through_fields=('messagecenter', 'users'), blank=True, verbose_name="目标用户",
                                         help_text="目标用户")
    target_dept = models.ManyToManyField(to=Dept, blank=True, db_constraint=False,
                                         verbose_name="目标部门", help_text="目标部门")
    target_role = models.ManyToManyField(to=Role, blank=True, db_constraint=False,
                                         verbose_name="目标角色", help_text="目标角色")

    class Meta:
        db_table = table_prefix + "message_center"
        verbose_name = "消息中心"
        verbose_name_plural = verbose_name
        ordering = ("-create_datetime",)


class MessageCenterTargetUser(CoreModel):
    users = models.ForeignKey(Users, related_name="target_user", on_delete=models.CASCADE, db_constraint=False,
                              verbose_name="关联用户表", help_text="关联用户表")
    messagecenter = models.ForeignKey(MessageCenter, on_delete=models.CASCADE, db_constraint=False,
                                      verbose_name="关联消息中心表", help_text="关联消息中心表")
    is_read = models.BooleanField(default=False, blank=True, null=True, verbose_name="是否已读", help_text="是否已读")

    class Meta:
        db_table = table_prefix + "message_center_target_user"
        verbose_name = "消息中心目标用户表"
        verbose_name_plural = verbose_name


def media_file_name_downloadcenter(instance:'DownloadCenter', filename):
    h = instance.md5sum
    basename, ext = os.path.splitext(filename)
    return PurePosixPath("files", "dlct", h[:1], h[1:2], basename + '-' + str(time()).replace('.', '') + ext.lower())


class DownloadCenter(CoreModel):
    TASK_STATUS_CHOICES = [
        (0, '任务已创建'),
        (1, '任务进行中'),
        (2, '任务完成'),
        (3, '任务失败'),
    ]
    task_name = models.CharField(max_length=255, verbose_name="任务名称", help_text="任务名称")
    task_status = models.SmallIntegerField(default=0, choices=TASK_STATUS_CHOICES, verbose_name='是否可下载', help_text='是否可下载')
    file_name = models.CharField(max_length=255, null=True, blank=True, verbose_name="文件名", help_text="文件名")
    url = models.FileField(upload_to=media_file_name_downloadcenter, null=True, blank=True)
    size = models.BigIntegerField(default=0, verbose_name="文件大小", help_text="文件大小")
    md5sum = models.CharField(max_length=36, null=True, blank=True, verbose_name="文件md5", help_text="文件md5")

    def save(self, *args, **kwargs):
        if self.url:
            if not self.md5sum:  # file is new
                md5 = hashlib.md5()
                for chunk in self.url.chunks():
                    md5.update(chunk)
                self.md5sum = md5.hexdigest()
            if not self.size:
                self.size = self.url.size
        super(DownloadCenter, self).save(*args, **kwargs)

    class Meta:
        db_table = table_prefix + "download_center"
        verbose_name = "下载中心"
        verbose_name_plural = verbose_name
        ordering = ("-create_datetime",)


# class KnowledgeBaseCategory(CoreModel):
#     """知识库分类模型"""
#     name = models.CharField(max_length=100, verbose_name="分类名称")
#     sort = models.IntegerField(default=0, verbose_name="排序号")
#     status = models.BooleanField(default=True, verbose_name="状态")
#     create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
#     update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
#
#     class Meta:
#         verbose_name = "知识库分类"
#         verbose_name_plural = verbose_name
#         ordering = ["sort"]
#         db_table = "system_knowledge_base_category"
#
#     def __str__(self):
#         return self.name


# class KnowledgeBase(CoreModel):
#     name = models.CharField(max_length=255)
#     type_id = models.IntegerField()
#     master = models.IntegerField()
#     limits = models.IntegerField()
#     create_time = models.DateTimeField()
#     icon_url = models.CharField(max_length=255, blank=True, null=True)
#     status = models.CharField(max_length=20)
#     archived_time = models.DateTimeField(blank=True, null=True)
#     archived_user_id = models.IntegerField(blank=True, null=True)
#     archived_desc = models.TextField(blank=True, null=True)
#     recycle = models.IntegerField()
#     recycle_time = models.DateTimeField(blank=True, null=True)
#     recycle_user_id = models.IntegerField(blank=True, null=True)
#     description = models.TextField(blank=True, null=True)
#
#     class Meta:
#         managed = False
#         db_table = 'mm_repository'


from django.db import models
from django.contrib.auth import get_user_model
# class DvadminSystemDictionary(models.Model):
#     TYPE_CHOICES = (
#         (0, 'text'),
#         (1, 'number'),
#         (2, 'date'),
#         (3, 'datetime'),
#         (4, 'time'),
#         (5, 'files'),
#         (6, 'boolean'),
#         (7, 'images'),
#     )
#
#     description = models.CharField(max_length=255, blank=True, null=True, verbose_name="描述信息")
#     modifier = models.CharField(max_length=255, blank=True, null=True, verbose_name="修改人")
#     dept_belong_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="所属部门ID")
#     update_datetime = models.DateTimeField(blank=True, null=True, verbose_name="更新时间")
#     create_datetime = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
#     label = models.CharField(max_length=100, blank=True, null=True, verbose_name="字典名称")
#     value = models.CharField(max_length=200, blank=True, null=True, verbose_name="字典编号/实际值")
#     type = models.IntegerField(choices=TYPE_CHOICES, default=0, verbose_name="数据值类型")
#     color = models.CharField(max_length=20, blank=True, null=True, verbose_name="颜色")
#     is_value = models.BooleanField(default=False, verbose_name="是否为value值")
#     status = models.BooleanField(default=True, verbose_name="状态")
#     sort = models.IntegerField(default=1, verbose_name="显示排序")
#     remark = models.TextField(blank=True, null=True, verbose_name="备注")
#     creator = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True,
#                                 related_name='created_dictionaries', verbose_name="创建人")
#     parent = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True,
#                                related_name='children', verbose_name="父级")
#
#     class Meta:
#         db_table = 'dvadmin_system_dictionary'
#         verbose_name = "系统字典"
#         verbose_name_plural = verbose_name
#         ordering = ['sort', 'create_datetime']
#
#     def __str__(self):
#         return f"{self.label} ({self.value})" if self.label else str(self.id)




User = get_user_model()


# class KnowledgeBase(models.Model):
#     LIMITS_CHOICES = (
#         (0, '所有人可编辑（公开）'),
#         (1, '仅知识库成员可编辑（私有）'),
#     )
#
#     STATUS_CHOICES = (
#         ('normal', '正常'),
#         ('archived', '归档'),
#     )
#
#     RECYCLE_CHOICES = (
#         (0, '未放入回收站'),
#         (1, '已放入回收站'),
#     )
#
#     name = models.CharField(max_length=200, verbose_name="知识库名称")
#     type_id = models.IntegerField(verbose_name="知识库类型ID")
#     master = models.ForeignKey(User, on_delete=models.CASCADE, related_name='repositories', verbose_name="负责人")
#     limits = models.IntegerField(choices=LIMITS_CHOICES, default=0, verbose_name="可见范围")
#     create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
#     icon_url = models.CharField(max_length=500, blank=True, null=True, verbose_name="图标访问路径")
#     status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='normal', verbose_name="知识库状态")
#     archived_time = models.DateTimeField(blank=True, null=True, verbose_name="归档时间")
#     archived_user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True,
#                                       related_name='archived_repositories', verbose_name="归档人")
#     archived_desc = models.TextField(blank=True, null=True, verbose_name="归档原因")
#     recycle = models.IntegerField(choices=RECYCLE_CHOICES, default=0, verbose_name="是否回收")
#     recycle_time = models.DateTimeField(blank=True, null=True, verbose_name="回收时间")
#     recycle_user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True,
#                                      related_name='recycled_repositories', verbose_name="回收人")
#     description = models.TextField(blank=True, null=True, verbose_name="知识库描述")
#
#     class Meta:
#         verbose_name = "知识库"
#         verbose_name_plural = verbose_name
#         ordering = ['-create_time']
#
#     def __str__(self):
#         return self.name
#
#     @property
#     def type_name(self):
#         """从字典表获取知识库类型名称"""
#         from dvadmin.utils.git_dict_model import get_dict_label
#         return get_dict_label('repository_type', self.type_id)
#
#     @property
#     def master_name(self):
#         """获取负责人名称"""
#         return self.master.username if self.master else ''

from django.db import models
from django.utils import timezone


class MmRepository(models.Model):
    STATUS_CHOICES = (
        ('normal', '正常'),
        ('archived', '归档'),
    )

    LIMITS_CHOICES = (
        (0, '无限制'),
        (1, '有限制'),
    )

    RECYCLE_CHOICES = (
        (0, '未回收'),
        (1, '已回收'),
    )

    name = models.TextField(verbose_name='仓库名称')
    type_id = models.IntegerField(verbose_name='类型ID')
    master = models.IntegerField(verbose_name='负责人')
    limits = models.IntegerField(choices=LIMITS_CHOICES, verbose_name='限制')
    create_time = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    icon_url = models.TextField(blank=True, null=True, verbose_name='图标URL')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='normal', verbose_name='状态')
    archived_time = models.DateTimeField(blank=True, null=True, verbose_name='归档时间')
    archived_user_id = models.IntegerField(blank=True, null=True, verbose_name='归档用户ID')
    archived_desc = models.TextField(blank=True, null=True, verbose_name='归档描述')
    recycle = models.IntegerField(choices=RECYCLE_CHOICES, default=0, verbose_name='回收状态')
    recycle_time = models.DateTimeField(blank=True, null=True, verbose_name='回收时间')
    recycle_user_id = models.IntegerField(blank=True, null=True, verbose_name='回收用户ID')
    description = models.TextField(blank=True, null=True, verbose_name='描述')

    class Meta:
        db_table = 'mm_repository'
        verbose_name = '仓库'
        verbose_name_plural = '仓库'

    def __str__(self):
        return self.name

    # 目录表
class Category(models.Model):
    """
    目录表 Model，对应数据库中的 category 表
    用于存储知识库的目录结构，支持多级目录（自关联）
    """
    # 1. 目录唯一ID：对应表中 id（Django 主键默认自增，无需额外指定 AUTOINCREMENT）
    id = models.IntegerField(primary_key=True, verbose_name="目录ID")

    # 2. 目录名称：对应表中 name（非空约束，最大长度建议根据业务定义，此处设为100）
    name = models.CharField(
        max_length=100,
        null=False,
        blank=False,  # blank=False 控制表单层面不允许空值，与 null=False 配合确保数据完整性
        verbose_name="目录名称"
    )

    # 3. 所属知识库ID：对应表中 repository_id（非空，关联知识库表，此处用 IntegerField 存ID）
    # 注：若后续需建立强关联，可改为 ForeignKey(Repository, on_delete=models.CASCADE)
    repository_id = models.IntegerField(
        null=False,
        blank=False,
        verbose_name="所属知识库ID"
    )

    # 4. 父级目录ID：对应表中 parent_category_id（自关联，允许为空，顶级目录存 None）
    # related_name="children" 便于通过父目录查询子目录（如 parent.children.all()）
    parent_category = models.ForeignKey(
        "self",  # 关联自身表
        on_delete=models.SET_NULL,  # 若父目录被删除，子目录的父ID设为 None（避免数据丢失）
        null=True,
        blank=True,
        related_name="children",
        verbose_name="父级目录"
    )

    # 5. 目录负责人ID：对应表中 master（非空，关联用户表，此处用 IntegerField 存ID）
    # 注：若需强关联用户表，可改为 ForeignKey(User, on_delete=models.PROTECT)
    master = models.IntegerField(
        null=False,
        blank=False,
        verbose_name="负责人ID"
    )

    # 6. 更新时间：对应表中 update_time（默认当前时间，更新时自动刷新）
    # auto_now=True 表示每次 save() 时自动更新为当前时间，无需手动维护
    update_time = models.DateTimeField(
        null=False,
        blank=False,
        default=timezone.now,
        verbose_name="更新时间"
    )

    # 7. 目录图标路径：对应表中 icon_url（允许为空，存储图标文件路径或URL）
    icon_url = models.CharField(
        max_length=255,  # 足够存储文件路径或网络URL
        null=True,
        blank=True,
        verbose_name="图标路径"
    )

    # 8. 排序值：对应表中 sort（非空，同层级按此值升序排列）
    sort = models.IntegerField(
        null=False,
        blank=False,
        default=0,  # 默认排序值设为0，便于新目录默认排在后面
        verbose_name="排序值"
    )

    # 9. 目录深度：对应表中 dimension（非空，最小值1，顶级目录为1，子目录=父目录深度+1）
    # 注：建议通过信号（signals）自动维护深度，避免手动输入错误
    dimension = models.IntegerField(
        null=False,
        blank=False,
        default=1,
        validators=[MinValueValidator(1)],  # 强制最小值为1，对应表中 CHECK 约束
        verbose_name="目录深度"
    )

    # 10. 上级目录路径：对应表中 tree_path（格式如“101,102,103”，顶级目录留空）
    # 注：建议通过信号自动维护路径，例如父目录路径 + 当前ID，避免手动拼接错误
    tree_path = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="上级目录路径"
    )

    class Meta:
        """
        Model 元数据配置，控制数据库表名、排序方式、索引等
        """
        # 数据库表名：强制指定为 "category"，与原始表结构一致（避免 Django 自动加后缀）
        db_table = "category"
        # 默认排序：同知识库、同父目录下，按 sort 升序排列（符合业务逻辑）
        ordering = ["repository_id", "parent_category", "sort"]
        # 索引：为高频查询字段添加索引，提升查询效率
        indexes = [
            # 按“知识库ID+父目录ID”查询子目录（最常用场景）
            models.Index(fields=["repository_id", "parent_category"]),
            # 按“负责人ID”查询目录
            models.Index(fields=["master"]),
            # 按“目录深度”查询（如筛选所有顶级目录：dimension=1）
            models.Index(fields=["dimension"]),
        ]
        # 后台管理界面显示的模型名称（中文友好）
        verbose_name = "目录"
        verbose_name_plural = "目录列表"

    def __str__(self):
        """
        定义模型实例的字符串表示（如在后台管理界面显示目录名称，便于识别）
        """
        return self.name

    def save(self, *args, **kwargs):
        """
        重写保存方法，自动维护 `dimension`（目录深度）和 `tree_path`（上级路径）
        避免手动计算错误，确保数据一致性
        """
        # 1. 处理目录深度：顶级目录（无父目录）深度为1，子目录=父目录深度+1
        if not self.parent_category:
            self.dimension = 1
            self.tree_path = ""  # 顶级目录路径为空
        else:
            self.dimension = self.parent_category.dimension + 1
            # 拼接路径：父目录路径 + 父目录ID + 逗号（如父路径“101”，则当前路径“101,102”）
            parent_path = self.parent_category.tree_path or ""
            self.tree_path = f"{parent_path},{self.parent_category.id}" if parent_path else str(
                self.parent_category.id)

        # 2. 调用父类 save 方法，完成数据入库
        super().save(*args, **kwargs)


#文档
class MmDocument(models.Model):
    """
    文档表 Model，对应数据库中的 mm_document 表
    用于存储各类文档信息，关联目录表，支持文本/非文本类型文档，包含冗余字段优化查询
    """
    # 1. 文档唯一ID：对应表中 id（Django 主键默认自增，无需额外指定 AUTOINCREMENT）
    id = models.IntegerField(primary_key=True, verbose_name="文档ID")

    # 2. 文档名称：对应表中 name（非空约束，最大长度设为255以满足大部分业务场景）
    name = models.CharField(
        max_length=255,
        null=False,
        blank=False,  # 表单层面不允许空值，与数据库约束一致
        verbose_name="文档名称"
    )

    # 3. 文档类型ID：对应表中 type_id（非空，关联字典表sys_dict_data，暂存ID）
    # 注：若项目中存在字典表Model（如SysDictData），建议改为 ForeignKey 强关联
    type_id = models.IntegerField(
        null=False,
        blank=False,
        verbose_name="文档类型ID"
    )

    # 4. 所属目录ID：对应表中 category_id（非空，关联mm_category表，存ID）
    # 此处用 ForeignKey 强关联目录表，确保目录存在性（避免无效目录ID）
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,  # 若关联目录被删除，禁止删除文档（保护数据完整性）
        null=False,
        blank=False,
        related_name="documents",  # 便于通过目录查询文档（如 category.documents.all()）
        verbose_name="所属目录"
    )

    # 5. 文档负责人ID：对应表中 master（非空，关联sys_user表，暂存ID）
    # 注：若项目中存在用户表Model（如Users），建议改为 ForeignKey 强关联
    master = models.IntegerField(
        null=False,
        blank=False,
        verbose_name="负责人ID"
    )

    # 6. 更新时间：对应表中 update_time（默认当前时间，更新时自动刷新）
    # auto_now=True 表示每次 save() 时自动更新为当前时间，无需手动维护
    update_time = models.DateTimeField(
        null=False,
        blank=False,
        auto_now=True,
        verbose_name="更新时间"
    )

    # 7. 文档内容路径：对应表中 details（允许为空，存储MinIO等文件存储的路径）
    # 最大长度设为512，满足长路径需求（如包含Bucket、文件夹层级的路径）
    details = models.CharField(
        max_length=512,
        null=True,
        blank=True,
        verbose_name="文档内容路径（MinIO）"
    )

    # 8. 文档文本内容：对应表中 detail_text（允许为空，仅存储文本类文档内容）
    # 用 TextField 存储大文本（无长度限制，满足长文档需求）
    detail_text = models.TextField(
        null=True,
        blank=True,
        verbose_name="文档文本内容"
    )

    # 9. 排序值：对应表中 sort（非空，默认0，同目录下按此值升序排列）
    sort = models.IntegerField(
        null=False,
        blank=False,
        default=0,
        verbose_name="排序值"
    )

    # 10. 所属目录深度：对应表中 dimension（非空，最小值1，冗余字段，与目录表一致）
    # 冗余存储目的：减少查询时关联目录表的开销，通过信号/重写save自动维护
    dimension = models.IntegerField(
        null=False,
        blank=False,
        validators=[MinValueValidator(1)],  # 强制最小值为1，对应表中 CHECK 约束
        verbose_name="所属目录深度（冗余）"
    )

    # 11. 所属目录路径：对应表中 tree_path（允许为空，冗余字段，与目录表一致）
    # 冗余存储目的：快速筛选某目录及其子目录下的所有文档，无需递归查询
    tree_path = models.CharField(
        max_length=512,
        null=True,
        blank=True,
        verbose_name="所属目录路径（冗余）"
    )

    class Meta:
        """
        Model 元数据配置，控制数据库表名、排序、索引等
        """
        # 强制指定表名为 "mm_document"，与原始表结构完全一致
        db_table = "mm_document"
        # 默认排序：同目录下按 sort 升序，更新时间降序（新文档优先）
        ordering = ["category", "sort", "-update_time"]
        # 索引优化：针对高频查询场景添加索引，提升性能
        indexes = [
            # 按“目录ID+排序值”查询（同目录下文档排序）
            models.Index(fields=["category", "sort"]),
            # 按“负责人ID”查询（筛选指定负责人的文档）
            models.Index(fields=["master"]),
            # 按“文档类型ID”查询（筛选指定类型的文档）
            models.Index(fields=["type_id"]),
            # 按“目录路径”查询（模糊匹配某目录及其子目录下的文档，如 tree_path LIKE "1,2%"）
            models.Index(fields=["tree_path"]),
        ]
        # 后台管理界面显示名称（中文友好）
        verbose_name = "文档"
        verbose_name_plural = "文档列表"
        # 唯一约束：同目录下不允许存在同名文档（避免重复）
        unique_together = ["category", "name"]

    def __str__(self):
        """
        模型实例的字符串表示（后台管理界面显示“目录名-文档名”，便于识别）
        """
        return f"{self.category.name} - {self.name}"

    def save(self, *args, **kwargs):
        """
        重写保存方法：自动维护冗余字段（dimension、tree_path）
        确保与关联目录的字段完全一致，避免手动维护错误
        """
        # 从关联的目录表中同步“目录深度”和“目录路径”
        self.dimension = self.category.dimension
        self.tree_path = self.category.tree_path

        # 调用父类 save 方法，完成数据入库
        super().save(*args, **kwargs)