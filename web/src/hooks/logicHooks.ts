import { IKnowledgeFile } from '@/interfaces/database/knowledge';
import { IChangeParserConfigRequestBody } from '@/interfaces/request/document';
import { useCallback, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useSetModalState } from './commonHooks';
import { useSetDocumentParser } from './documentHooks';
import { useOneNamespaceEffectsLoading } from './storeHooks';
import { useSaveSetting } from './userSettingHook';

export const useChangeDocumentParser = (documentId: string) => {
  const setDocumentParser = useSetDocumentParser();

  const {
    visible: changeParserVisible,
    hideModal: hideChangeParserModal,
    showModal: showChangeParserModal,
  } = useSetModalState();
  const loading = useOneNamespaceEffectsLoading('kFModel', [
    'document_change_parser',
  ]);

  const onChangeParserOk = useCallback(
    async (parserId: string, parserConfig: IChangeParserConfigRequestBody) => {
      const ret = await setDocumentParser(parserId, documentId, parserConfig);
      if (ret === 0) {
        hideChangeParserModal();
      }
    },
    [hideChangeParserModal, setDocumentParser, documentId],
  );

  return {
    changeParserLoading: loading,
    onChangeParserOk,
    changeParserVisible,
    hideChangeParserModal,
    showChangeParserModal,
  };
};

export const useSetSelectedRecord = <T = IKnowledgeFile>() => {
  const [currentRecord, setCurrentRecord] = useState<T>({} as T);

  const setRecord = (record: T) => {
    setCurrentRecord(record);
  };

  return { currentRecord, setRecord };
};

export const useChangeLanguage = () => {
  const { i18n } = useTranslation();
  const saveSetting = useSaveSetting();

  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng === 'Chinese' ? 'zh' : 'en');
    saveSetting({ language: lng });
  };

  return changeLanguage;
};
