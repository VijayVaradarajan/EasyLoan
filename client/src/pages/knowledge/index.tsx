import React, { useState, } from 'react';
import { useNavigate } from 'umi'
import { Card, List, Popconfirm, message, FloatButton } from 'antd';
import { MinusSquareOutlined, DeleteOutlined, PlusOutlined } from '@ant-design/icons';
import styles from './index.less'

const data = [
  {
    title: 'Title 1',
    text: '1',
    des: '111'
  },
  {
    title: 'Title 2',
    text: '2',
    des: '111'
  },
  {
    title: 'Title 3',
    text: '3',
    des: '111'
  },
  {
    title: 'Title 4',
    text: '4',
    des: '111'
  },
];
const dd = [{
  title: 'Title 4',
  text: '4',
  des: '111'
}]
const App: React.FC = () => {
  const navigate = useNavigate()
  const [datas, setDatas] = useState(data)
  const confirm = (index: number) => {
    console.log(index);
    setDatas(datas => datas.filter((item, i) => i !== index))
    message.success('Click on Yes');
  };
  const handleAddKnowledge = () => {
    // setDatas((datas) => [...datas, ...dd])
    navigate('add');
  }
  return (<><FloatButton onClick={handleAddKnowledge} icon={<PlusOutlined />} type="primary" style={{ right: 24, top: 100 }} />
    <List
      grid={{ gutter: 16, column: 4 }}
      dataSource={datas}
      renderItem={(item, index) => (
        <List.Item>
          <Card className={styles.card}>
            <div className={styles.container}>
              <div className={styles.content}>
                <span className={styles.context}>
                  content
                </span>
                <span className={styles.delete}>
                  <Popconfirm
                    title="Delete the task"
                    description="Are you sure to delete this task?"
                    onConfirm={() => { confirm(index) }}
                    okText="Yes"
                    cancelText="No"
                  >
                    <DeleteOutlined />
                  </Popconfirm>

                </span>
              </div>
              <div className={styles.footer}>
                <span className={styles.text}>
                  <MinusSquareOutlined />{item.text}
                </span>
                <span className={styles.text}>
                  <MinusSquareOutlined />{item.des}
                </span>
              </div>

            </div>
          </Card>
        </List.Item>
      )}
    /></>
  )
};

export default App;