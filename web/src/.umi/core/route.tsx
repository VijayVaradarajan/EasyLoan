// @ts-nocheck
// This file is generated by Umi automatically
// DO NOT CHANGE IT MANUALLY!
import React from 'react';

export async function getRoutes() {
  const routes = {"1":{"path":"/login","layout":false,"id":"1"},"2":{"path":"/","redirect":"/knowledge","parentId":"@@/global-layout","id":"2"},"3":{"id":"3","name":"知识库","icon":"home","auth":[3,4,100],"path":"/knowledge","pathname":"knowledge","parentId":"@@/global-layout"},"4":{"id":"4","name":"知识库","icon":"home","auth":[3,4,100],"path":"/knowledge/add/*","pathname":"knowledge","parentId":"@@/global-layout"},"5":{"id":"5","name":"聊天","icon":"home","auth":[3,4,100],"path":"/chat","pathname":"chat","parentId":"@@/global-layout"},"6":{"id":"6","name":"设置","icon":"home","auth":[3,4,100],"path":"/setting","pathname":"setting","parentId":"@@/global-layout"},"7":{"id":"7","name":"文件","icon":"file","auth":[3,4,100],"path":"/file","pathname":"file","parentId":"@@/global-layout"},"8":{"path":"/*","layout":false,"id":"8"},"@@/global-layout":{"id":"@@/global-layout","path":"/","isLayout":true}} as const;
  return {
    routes,
    routeComponents: {
'1': React.lazy(() => import(/* webpackChunkName: "p__login__index" */'@/pages/login/index.tsx')),
'2': React.lazy(() => import(/* webpackChunkName: "layouts__index" */'@/layouts/index.tsx')),
'3': React.lazy(() => import(/* webpackChunkName: "p__knowledge__index" */'@/pages/knowledge/index.tsx')),
'4': React.lazy(() => import(/* webpackChunkName: "p__add-knowledge__index" */'@/pages/add-knowledge/index.tsx')),
'5': React.lazy(() => import(/* webpackChunkName: "p__chat__index" */'@/pages/chat/index.tsx')),
'6': React.lazy(() => import(/* webpackChunkName: "p__setting__index" */'@/pages/setting/index.tsx')),
'7': React.lazy(() => import(/* webpackChunkName: "p__file__index" */'@/pages/file/index.tsx')),
'8': React.lazy(() => import(/* webpackChunkName: "p__404" */'@/pages/404.jsx')),
'@@/global-layout': React.lazy(() => import(/* webpackChunkName: "layouts__index" */'C:/Users/zfc/Desktop/docgpt/client/src/layouts/index.tsx')),
},
  };
}
