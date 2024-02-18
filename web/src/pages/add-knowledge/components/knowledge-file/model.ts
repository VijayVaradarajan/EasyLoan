import { BaseState } from '@/interfaces/common';
import { IKnowledgeFile } from '@/interfaces/database/knowledge';
import kbService from '@/services/kbService';
import { message } from 'antd';
import omit from 'lodash/omit';
import pick from 'lodash/pick';
import { Nullable } from 'typings';
import { DvaModel } from 'umi';

export interface KFModelState extends BaseState {
  isShowCEFwModal: boolean;
  isShowTntModal: boolean;
  isShowSegmentSetModal: boolean;
  isShowRenameModal: boolean;
  tenantIfo: any;
  data: IKnowledgeFile[];
  total: number;
  currentRecord: Nullable<IKnowledgeFile>;
}

const model: DvaModel<KFModelState> = {
  namespace: 'kFModel',
  state: {
    isShowCEFwModal: false,
    isShowTntModal: false,
    isShowSegmentSetModal: false,
    isShowRenameModal: false,
    tenantIfo: {},
    data: [],
    total: 0,
    currentRecord: null,
    searchString: '',
    pagination: {
      current: 1,
      pageSize: 10,
    },
  },
  reducers: {
    updateState(state, { payload }) {
      return {
        ...state,
        ...payload,
      };
    },
    setIsShowRenameModal(state, { payload }) {
      return { ...state, isShowRenameModal: payload };
    },
    setCurrentRecord(state, { payload }) {
      return { ...state, currentRecord: payload };
    },
    setSearchString(state, { payload }) {
      return { ...state, searchString: payload };
    },
    setPagination(state, { payload }) {
      return { ...state, pagination: { ...state.pagination, ...payload } };
    },
  },
  effects: {
    *createKf({ payload = {} }, { call }) {
      const { data } = yield call(kbService.createKb, payload);
      const { retcode } = data;
      if (retcode === 0) {
        message.success('创建成功！');
      }
    },
    *updateKf({ payload = {} }, { call }) {
      const { data } = yield call(kbService.updateKb, payload);
      const { retcode } = data;
      if (retcode === 0) {
        message.success('修改成功！');
      }
    },
    *getKfDetail({ payload = {} }, { call }) {
      const { data } = yield call(kbService.get_kb_detail, payload);
    },
    *getKfList({ payload = {} }, { call, put, select }) {
      const state: KFModelState = yield select((state: any) => state.kFModel);
      const requestBody = {
        ...payload,
        page: state.pagination.current,
        page_size: state.pagination.pageSize,
      };
      if (state.searchString) {
        requestBody['keywords'] = state.searchString;
      }
      const { data } = yield call(kbService.get_document_list, requestBody);
      const { retcode, data: res } = data;

      if (retcode === 0) {
        yield put({
          type: 'updateState',
          payload: {
            data: res.docs,
            total: res.total,
          },
        });
      }
    },
    throttledGetDocumentList: [
      function* ({ payload }, { call, put }) {
        yield put({ type: 'getKfList', payload: { kb_id: payload } });
      },
      { type: 'throttle', ms: 1000 }, // TODO: Provide type support for this effect
    ],
    pollGetDocumentList: [
      function* ({ payload }, { call, put }) {
        yield put({ type: 'getKfList', payload: { kb_id: payload } });
      },
      { type: 'poll', delay: 5000 }, // TODO: Provide type support for this effect
    ],
    *updateDocumentStatus({ payload = {} }, { call, put }) {
      const { data } = yield call(
        kbService.document_change_status,
        pick(payload, ['doc_id', 'status']),
      );
      const { retcode } = data;
      if (retcode === 0) {
        message.success('修改成功！');
        put({
          type: 'getKfList',
          payload: { kb_id: payload.kb_id },
        });
      }
    },
    *document_rm({ payload = {} }, { call, put }) {
      const { data } = yield call(kbService.document_rm, {
        doc_id: payload.doc_id,
      });
      const { retcode } = data;
      if (retcode === 0) {
        message.success('删除成功！');
        yield put({
          type: 'getKfList',
          payload: { kb_id: payload.kb_id },
        });
      }
      return retcode;
    },
    *document_rename({ payload = {} }, { call, put }) {
      const { data } = yield call(
        kbService.document_rename,
        omit(payload, ['kb_id']),
      );
      const { retcode } = data;
      if (retcode === 0) {
        message.success('rename success！');
        yield put({
          type: 'setIsShowRenameModal',
          payload: false,
        });
        yield put({
          type: 'getKfList',
          payload: { kb_id: payload.kb_id },
        });
      }

      return retcode;
    },
    *document_create({ payload = {} }, { call, put }) {
      const { data } = yield call(kbService.document_create, payload);
      const { retcode } = data;
      if (retcode === 0) {
        put({
          type: 'kFModel/updateState',
          payload: {
            isShowCEFwModal: false,
          },
        });
        message.success('创建成功！');
      }
      return retcode;
    },
    *document_run({ payload = {} }, { call, put }) {
      const { data } = yield call(
        kbService.document_run,
        omit(payload, ['knowledgeBaseId']),
      );
      const { retcode } = data;
      if (retcode === 0) {
        if (payload.knowledgeBaseId) {
          yield put({
            type: 'getKfList',
            payload: { kb_id: payload.knowledgeBaseId },
          });
        }
        message.success('Operation successfully ！');
      }
      return retcode;
    },
    *document_change_parser({ payload = {} }, { call, put }) {
      const { data } = yield call(kbService.document_change_parser, payload);
      const { retcode } = data;
      if (retcode === 0) {
        put({
          type: 'updateState',
          payload: {
            isShowSegmentSetModal: false,
          },
        });
        message.success('修改成功！');
      }
      return retcode;
    },
  },
};
export default model;
