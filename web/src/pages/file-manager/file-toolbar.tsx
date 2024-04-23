import { ReactComponent as DeleteIcon } from '@/assets/svg/delete.svg';
import { useShowDeleteConfirm, useTranslate } from '@/hooks/commonHooks';
import {
  DownOutlined,
  FileOutlined,
  FileTextOutlined,
  PlusOutlined,
  SearchOutlined,
} from '@ant-design/icons';
import {
  Breadcrumb,
  Button,
  Dropdown,
  Flex,
  Input,
  MenuProps,
  Space,
} from 'antd';
import { useCallback, useMemo } from 'react';
import {
  useFetchDocumentListOnMount,
  useGetPagination,
  useHandleSearchChange,
} from './hooks';

import { useRemoveFile } from '@/hooks/fileManagerHooks';
import styles from './index.less';

interface IProps {
  selectedRowKeys: string[];
}

const FileToolbar = ({ selectedRowKeys }: IProps) => {
  const { t } = useTranslate('knowledgeDetails');
  const { fetchDocumentList } = useFetchDocumentListOnMount();
  const { setPagination, searchString } = useGetPagination(fetchDocumentList);
  const { handleInputChange } = useHandleSearchChange(setPagination);
  const removeDocument = useRemoveFile();
  const showDeleteConfirm = useShowDeleteConfirm();

  const actionItems: MenuProps['items'] = useMemo(() => {
    return [
      {
        key: '1',
        label: (
          <div>
            <Button type="link">
              <Space>
                <FileTextOutlined />
                {t('localFiles')}
              </Space>
            </Button>
          </div>
        ),
      },
      { type: 'divider' },
      {
        key: '2',
        label: (
          <div>
            <Button type="link">
              <FileOutlined />
              {t('emptyFiles')}
            </Button>
          </div>
        ),
        // disabled: true,
      },
    ];
  }, [t]);

  const handleDelete = useCallback(() => {
    showDeleteConfirm({
      onOk: () => {
        return removeDocument(selectedRowKeys);
      },
    });
  }, [removeDocument, showDeleteConfirm, selectedRowKeys]);

  const disabled = selectedRowKeys.length === 0;

  const items: MenuProps['items'] = useMemo(() => {
    return [
      {
        key: '4',
        onClick: handleDelete,
        label: (
          <Flex gap={10}>
            <span className={styles.deleteIconWrapper}>
              <DeleteIcon width={18} />
            </span>
            <b>{t('delete', { keyPrefix: 'common' })}</b>
          </Flex>
        ),
      },
    ];
  }, [handleDelete, t]);

  return (
    <div className={styles.filter}>
      <Breadcrumb
        items={[
          {
            title: 'Home',
          },
          {
            title: <a href="">Application Center</a>,
          },
          {
            title: <a href="">Application List</a>,
          },
          {
            title: 'An Application',
          },
        ]}
      />
      <Space>
        <Dropdown
          menu={{ items }}
          placement="bottom"
          arrow={false}
          disabled={disabled}
        >
          <Button>
            <Space>
              <b> {t('bulk')}</b>
              <DownOutlined />
            </Space>
          </Button>
        </Dropdown>
        <Input
          placeholder={t('searchFiles')}
          value={searchString}
          style={{ width: 220 }}
          allowClear
          onChange={handleInputChange}
          prefix={<SearchOutlined />}
        />

        <Dropdown menu={{ items: actionItems }} trigger={['click']}>
          <Button type="primary" icon={<PlusOutlined />}>
            {t('addFile')}
          </Button>
        </Dropdown>
      </Space>
    </div>
  );
};

export default FileToolbar;
