import { connect } from 'umi';
import i18n from 'i18next';
import { useTranslation, Trans } from 'react-i18next'
import { Modal, Table } from 'antd'
import styles from './index.less';
import type { ColumnsType } from 'antd/es/table';


interface DataType {
    key: React.Key;
    name: string;
    role: string;
    time: string;
}

const Index = ({ settingModel, dispatch }) => {
    const { isShowTntModal, tenantIfo, loading } = settingModel
    const { t } = useTranslation()
    const handleCancel = () => {
        dispatch({
            type: 'settingModel/updateState',
            payload: {
                isShowTntModal: false
            }
        });
    };
    console.log(tenantIfo)
    const handleOk = async () => {
        dispatch({
            type: 'settingModel/updateState',
            payload: {
                isShowTntModal: false
            }
        });
    };
    const columns: ColumnsType<DataType> = [
        { title: '姓名', dataIndex: 'name', key: 'name' },
        { title: '角色', dataIndex: 'role', key: 'age' },
        { title: '活动时间', dataIndex: 'time', key: 'time' },
    ];

    return (
        <Modal title="用户" open={isShowTntModal} onOk={handleOk} onCancel={handleCancel}>
            <div className={styles.tenantIfo}>
                {tenantIfo.name}
            </div>
            <Table rowKey='name' loading={loading} columns={columns} dataSource={[]} />
        </Modal >
    );
}
export default connect(({ settingModel, loading }) => ({ settingModel, loading }))(Index);
