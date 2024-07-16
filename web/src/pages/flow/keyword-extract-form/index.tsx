import LLMSelect from '@/components/llm-select';
import TopNItem from '@/components/top-n-item';
import { useTranslate } from '@/hooks/commonHooks';
import { Form } from 'antd';
import { useSetLlmSetting } from '../hooks';
import { IOperatorForm } from '../interface';

const KeywordExtractForm = ({ onValuesChange, form }: IOperatorForm) => {
  const { t } = useTranslate('flow');

  useSetLlmSetting(form);

  return (
    <Form
      name="basic"
      labelCol={{ span: 6 }}
      wrapperCol={{ span: 18 }}
      autoComplete="off"
      form={form}
      onValuesChange={onValuesChange}
    >
      <Form.Item
        name={'llm_id'}
        label={t('model', { keyPrefix: 'chat' })}
        tooltip={t('modelTip', { keyPrefix: 'chat' })}
      >
        <LLMSelect></LLMSelect>
      </Form.Item>
      <TopNItem initialValue={1}></TopNItem>
    </Form>
  );
};

export default KeywordExtractForm;
