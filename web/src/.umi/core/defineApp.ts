// @ts-nocheck
// This file is generated by Umi automatically
// DO NOT CHANGE IT MANUALLY!
import type { IRuntimeConfig as Plugin0 } from 'C:/Users/zfc/Desktop/doc/ragflow/web/src/.umi/plugin-dva/runtimeConfig.d'
interface IDefaultRuntimeConfig {
  onRouteChange?: (props: { routes: any, clientRoutes: any, location: any, action: any, isFirst: boolean }) => void;
  patchRoutes?: (props: { routes: any }) => void;
  patchClientRoutes?: (props: { routes: any }) => void;
  render?: (oldRender: () => void) => void;
  rootContainer?: (lastRootContainer: JSX.Element, args?: any) => void;
  [key: string]: any;
}
export type RuntimeConfig = IDefaultRuntimeConfig & Plugin0

export function defineApp(config: RuntimeConfig): RuntimeConfig {
  return config;
}
