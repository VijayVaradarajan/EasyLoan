import { IModalManagerChildrenProps } from '@/components/modal-manager';
import { useTranslate } from '@/hooks/common-hooks';
import { Form, Input, Modal } from 'antd';
import { useEffect } from 'react';
import { ApiKeyPostBody } from '../../interface';

interface IProps extends Omit<IModalManagerChildrenProps, 'showModal'> {
  loading: boolean;
  initialValue: string;
  llmFactory: string;
  onOk: (postBody: ApiKeyPostBody) => void;
  showModal?(): void;
}

type FieldType = {
  api_key?: string;
  base_url?: string;
  default_model?: string;
  api_version?: string;
  group_id?: string;
};

const modelsWithBaseUrl = ['OpenAI', 'Azure-OpenAI'];

const ApiKeyModal = ({
  visible,
  hideModal,
  llmFactory,
  loading,
  initialValue,
  onOk,
}: IProps) => {
  const [form] = Form.useForm();
  const { t } = useTranslate('setting');

  const handleOk = async () => {
    const ret = await form.validateFields();

    return onOk(ret);
  };

  useEffect(() => {
    if (visible) {
      form.setFieldValue('api_key', initialValue);
    }
  }, [initialValue, form, visible]);

  return (
    <Modal
      title={t('modify')}
      open={visible}
      onOk={handleOk}
      onCancel={hideModal}
      okButtonProps={{ loading }}
      confirmLoading={loading}
    >
      <Form
        name="basic"
        labelCol={{ span: 6 }}
        wrapperCol={{ span: 18 }}
        style={{ maxWidth: 600 }}
        autoComplete="off"
        form={form}
      >
        <Form.Item<FieldType>
          label={t('apiKey')}
          name="api_key"
          tooltip={t('apiKeyTip')}
          rules={[{ required: true, message: t('apiKeyMessage') }]}
        >
          <Input />
        </Form.Item>
        {modelsWithBaseUrl.some((x) => x === llmFactory) && (
          <>
            <Form.Item
              label={t('baseUrl')}
              name="base_url"
              tooltip={t('baseUrlTip')}
            >
              <Input placeholder="https://api.openai.com/v1" />
            </Form.Item>

            <Form.Item
              label={t('defaultModel')}
              name="default_model"
              tooltip={t('defaultModelNameTip')}
            >
              <Input placeholder="gpt-3.5-turbo" />
            </Form.Item>

            <Form.Item
              label={t('apiVersion')}
              name="api_version"
              tooltip={t('apiVersionTip')}
            >
              <Input placeholder="2024-02-01" defaultValue="2024-02-01" />
            </Form.Item>
          </>
        )}
        {llmFactory?.toLowerCase() === 'Minimax'.toLowerCase() && (
          <Form.Item<FieldType> label={'Group ID'} name="group_id">
            <Input />
          </Form.Item>
        )}
      </Form>
    </Modal>
  );
};

export default ApiKeyModal;
