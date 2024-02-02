import { KnowledgeRouteKey } from '@/constants/knowledge';
import { useKnowledgeBaseId } from '@/hooks/knowledgeHook';
import { IKnowledgeFile } from '@/interfaces/database/knowledge';
import { getOneNamespaceEffectsLoading } from '@/utils/stroreUtil';
import { PlusOutlined, SearchOutlined } from '@ant-design/icons';
import type { MenuProps } from 'antd';
import {
  Button,
  Divider,
  Dropdown,
  Input,
  Space,
  Switch,
  Table,
  Tag,
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { debounce } from 'lodash';
import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { useDispatch, useNavigate, useSelector } from 'umi';
import CreateEPModal from './createEFileModal';
import styles from './index.less';
import ParsingActionCell from './parsing-action-cell';
import ParsingStatusCell from './parsing-status-cell';
import RenameModal from './rename-modal';
import SegmentSetModal from './segmentSetModal';
import UploadFile from './upload';

const KnowledgeFile = () => {
  const dispatch = useDispatch();
  const kFModel = useSelector((state: any) => state.kFModel);
  const effects = useSelector((state: any) => state.loading.effects);
  const { data } = kFModel;
  const knowledgeBaseId = useKnowledgeBaseId();

  const loading = getOneNamespaceEffectsLoading('kFModel', effects, [
    'getKfList',
    'updateDocumentStatus',
  ]);
  const [inputValue, setInputValue] = useState('');
  const [doc_id, setDocId] = useState('0');
  const [parser_id, setParserId] = useState('0');
  let navigate = useNavigate();

  const getKfList = (keywords?: string) => {
    const payload = {
      kb_id: knowledgeBaseId,
      keywords,
    };
    if (!keywords) {
      delete payload.keywords;
    }
    dispatch({
      type: 'kFModel/getKfList',
      payload,
    });
  };

  useEffect(() => {
    if (knowledgeBaseId) {
      getKfList();
    }
  }, [knowledgeBaseId]);

  const debounceChange = debounce(getKfList, 300);
  const debounceCallback = useCallback(
    (value: string) => debounceChange(value),
    [],
  );
  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
  ) => {
    const value = e.target.value;
    setInputValue(value);
    debounceCallback(e.target.value);
  };
  const onChangeStatus = (e: boolean, doc_id: string) => {
    dispatch({
      type: 'kFModel/updateDocumentStatus',
      payload: {
        doc_id,
        status: Number(e),
        kb_id: knowledgeBaseId,
      },
    });
  };
  const onRmDocument = () => {
    dispatch({
      type: 'kFModel/document_rm',
      payload: {
        doc_id,
        kb_id: knowledgeBaseId,
      },
    });
  };
  const showCEFModal = () => {
    dispatch({
      type: 'kFModel/updateState',
      payload: {
        isShowCEFwModal: true,
      },
    });
  };

  const showSegmentSetModal = () => {
    dispatch({
      type: 'kFModel/updateState',
      payload: {
        isShowSegmentSetModal: true,
      },
    });
  };

  const actionItems: MenuProps['items'] = useMemo(() => {
    return [
      {
        key: '1',
        label: (
          <div>
            <UploadFile kb_id={knowledgeBaseId} getKfList={getKfList} />
          </div>
        ),
      },
      {
        key: '2',
        label: (
          <div>
            <Button type="link" onClick={showCEFModal}>
              {' '}
              导入虚拟文件
            </Button>
          </div>
        ),
        // disabled: true,
      },
    ];
  }, [knowledgeBaseId]);
  const chunkItems: MenuProps['items'] = [
    {
      key: '1',
      label: (
        <div>
          <Button type="link" onClick={showSegmentSetModal}>
            {' '}
            分段设置
          </Button>
        </div>
      ),
    },
    {
      key: '2',
      label: (
        <div>
          <Button type="link" onClick={onRmDocument}>
            {' '}
            删除
          </Button>
        </div>
      ),
      // disabled: true,
    },
  ];

  const toChunk = (id: string) => {
    navigate(
      `/knowledge/${KnowledgeRouteKey.Dataset}/chunk?id=${knowledgeBaseId}&doc_id=${id}`,
    );
  };

  const setDocumentAndParserId = (record: IKnowledgeFile) => () => {
    setDocId(record.id);
    setParserId(record.parser_id);
  };

  const columns: ColumnsType<IKnowledgeFile> = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      render: (text: any, { id }) => (
        <div className={styles.tochunks} onClick={() => toChunk(id)}>
          <img
            className={styles.img}
            src="https://gw.alipayobjects.com/zos/antfincdn/efFD%24IOql2/weixintupian_20170331104822.jpg"
            alt=""
          />
          {text}
        </div>
      ),
    },
    {
      title: 'Chunk Number',
      dataIndex: 'chunk_num',
      key: 'chunk_num',
    },
    {
      title: 'Upload Date',
      dataIndex: 'create_date',
      key: 'create_date',
    },
    {
      title: 'Parsing Status',
      dataIndex: 'run',
      key: 'run',
      render: (text, record) => {
        return <ParsingStatusCell record={record}></ParsingStatusCell>;
      },
    },
    {
      title: 'Enabled',
      key: 'status',
      dataIndex: 'status',
      render: (_, { status, id }) => (
        <>
          <Switch
            defaultChecked={status === '1'}
            onChange={(e) => {
              onChangeStatus(e, id);
            }}
          />
        </>
      ),
    },
    {
      title: 'Action',
      key: 'action',
      render: (_, record) => (
        <ParsingActionCell
          documentId={doc_id}
          knowledgeBaseId={knowledgeBaseId}
          setDocumentAndParserId={setDocumentAndParserId(record)}
          record={record}
        ></ParsingActionCell>
      ),
    },
  ];

  const finalColumns = columns.map((x) => ({
    ...x,
    className: `${styles.column}`,
  }));

  return (
    <div className={styles.datasetWrapper}>
      <h3>Dataset</h3>
      <p>Hey, don't forget to adjust the chunk after adding the dataset! 😉</p>
      <Divider></Divider>
      <div className={styles.filter}>
        <Space>
          <h3>Total</h3>
          <Tag color="purple">100 files</Tag>
        </Space>
        <Space>
          <Input
            placeholder="Seach your files"
            value={inputValue}
            style={{ width: 220 }}
            allowClear
            onChange={handleInputChange}
            prefix={<SearchOutlined />}
          />

          <Dropdown menu={{ items: actionItems }} trigger={['click']}>
            <Button type="primary" icon={<PlusOutlined />}>
              Add file
            </Button>
          </Dropdown>
        </Space>
      </div>
      <Table
        rowKey="id"
        columns={finalColumns}
        dataSource={data}
        loading={loading}
        pagination={false}
        scroll={{ scrollToFirstRowOnChange: true, x: true, y: 'fill' }}
      />
      <CreateEPModal getKfList={getKfList} kb_id={knowledgeBaseId} />
      <SegmentSetModal
        getKfList={getKfList}
        parser_id={parser_id}
        doc_id={doc_id}
      />
      <RenameModal></RenameModal>
    </div>
  );
};

export default KnowledgeFile;
