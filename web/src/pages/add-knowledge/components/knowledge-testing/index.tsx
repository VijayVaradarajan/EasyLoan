import { Flex } from 'antd';
import TestingControl from './testing-control';
import TestingResult from './testing-result';

import styles from './index.less';

const KnowledgeTesting = () => {
  return (
    <Flex className={styles.testingWrapper} gap={16}>
      <TestingControl></TestingControl>
      <TestingResult></TestingResult>
    </Flex>
  );
};

export default KnowledgeTesting;
