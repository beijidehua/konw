<!--<template>-->
<!--  <div class="app-container">-->
<!--    &lt;!&ndash; 顶栏（两个系统共享） &ndash;&gt;-->
<!--    <TopBar />-->

<!--    <div class="main-content">-->
<!--      &lt;!&ndash; 动态侧边栏：根据系统类型切换 &ndash;&gt;-->
<!--&lt;!&ndash;      <template v-if="systemType === 'main'">&ndash;&gt;-->
<!--&lt;!&ndash;        &lt;!&ndash; 原系统侧边栏 &ndash;&gt;&ndash;&gt;-->
<!--&lt;!&ndash;        <MainSidebar />&ndash;&gt;-->
<!--&lt;!&ndash;      </template>&ndash;&gt;-->
<!--&lt;!&ndash;      <template v-else-if="systemType === 'knowledge'">&ndash;&gt;-->
<!--&lt;!&ndash;        &lt;!&ndash; 知识库系统专属侧边栏 &ndash;&gt;&ndash;&gt;-->
<!--&lt;!&ndash;        <KnowledgeSidebar />&ndash;&gt;-->
<!--&lt;!&ndash;      </template>&ndash;&gt;-->
<!--      <template v-if="systemType === 'repository'">-->
<!--        &lt;!&ndash; 知识库系统专属侧边栏 &ndash;&gt;-->
<!--        <RepositorySidebar />-->
<!--      </template>-->
<!--      &lt;!&ndash; 内容区域（路由出口） &ndash;&gt;-->
<!--      <router-views class="page-content" />-->
<!--    </div>-->
<!--  </div>-->
<!--</template>-->

<!--<script setup>-->
<!--import { useRoute, useRouter } from 'vue-router';-->
<!--import { computed } from 'vue';-->

<!--// 导入组件-->
<!--import TopBar from './components/TopBar.vue'; // 共享顶栏-->
<!--import MainSidebar from './components/MainSidebar.vue'; // 原系统侧边栏-->
<!--import KnowledgeSidebar from '/@/components/sidebar/KnowledgeSidebar.vue'; // 知识库侧边栏-->

<!--// 获取当前路由信息-->
<!--const route = useRoute();-->

<!--// 根据路由元信息判断系统类型（优先取子路由，子路由没有则取父路由）-->
<!--const systemType = computed(() => {-->
<!--  // 子路由存在时，取子路由的meta-->
<!--  if (route.matched.length > 1) {-->
<!--    return route.matched[1].meta.systemType || 'main';-->
<!--  }-->
<!--  // 否则取顶级路由的meta-->
<!--  return route.matched[0].meta.systemType || 'main';-->
<!--});-->
<!--</script>-->

<!--<style scoped>-->
<!--.app-container {-->
<!--  display: flex;-->
<!--  flex-direction: column;-->
<!--  height: 100vh;-->
<!--  overflow: hidden;-->
<!--}-->

<!--.main-content {-->
<!--  display: flex;-->
<!--  flex: 1;-->
<!--  overflow: hidden;-->
<!--}-->

<!--.page-content {-->
<!--  flex: 1;-->
<!--  padding: 20px;-->
<!--  overflow-y: auto;-->
<!--  background: #f5f7fa;-->
<!--}-->
<!--</style>-->


<template>
  <div class="app-container">
    <!-- 顶栏（两个系统共享） -->
    <TopBar />

    <div class="main-content">
      <!-- 动态侧边栏：根据系统类型切换 -->
      <template v-if="systemType === 'repository'">
        <!-- 知识库系统专属侧边栏 -->
        <RepositorySidebar />
      </template>
      <template v-else>
        <!-- 默认使用主系统侧边栏 -->
        <MainSidebar />
      </template>
      <!-- 内容区域（路由出口） -->
      <router-view class="page-content" />
    </div>
  </div>
</template>

<script setup>import { useRoute } from 'vue-router';
import { computed } from 'vue';

// 导入组件
import TopBar from '@/layout/component/header.vue'; // 共享顶栏
import MainSidebar from '@/layout/component/aside.vue';   // 原系统侧边栏
import RepositorySidebar from './RepositorySidebar.vue'; // 仓库系统侧边栏

// 获取当前路由信息
const route = useRoute();

// 根据路由元信息判断系统类型（优先取子路由，子路由没有则取父路由）
const systemType = computed(() => {
  // 子路由存在时，取子路由的meta
  if (route.matched.length > 1) {
    return route.matched[1].meta.systemType;
  }
  // 否则取顶级路由的meta
  return route.matched[0].meta.systemType;
});
</script>

<style scoped>.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

.main-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.page-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background: #f5f7fa;
}
</style>