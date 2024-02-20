import {
  LlmModelType,
  ModelVariableType,
  settledModelVariableMap,
} from '@/constants/knowledge';
import { Divider, Flex, Form, InputNumber, Select, Slider, Switch } from 'antd';
import classNames from 'classnames';
import { useEffect } from 'react';
import { ISegmentedContentProps } from './interface';

import { useFetchLlmList, useSelectLlmOptions } from '@/hooks/llmHooks';
import { variableEnabledFieldMap } from './constants';
import styles from './index.less';

const ModelSetting = ({ show, form }: ISegmentedContentProps) => {
  const parameterOptions = Object.values(ModelVariableType).map((x) => ({
    label: x,
    value: x,
  }));

  const parameters: ModelVariableType = Form.useWatch('parameters', form);

  const modelOptions = useSelectLlmOptions();

  const handleParametersChange = (value: ModelVariableType) => {
    console.info(value);
  };

  useEffect(() => {
    const variable = settledModelVariableMap[parameters];
    form.setFieldsValue({ llm_setting: variable });
  }, [parameters, form]);

  useEffect(() => {
    const values = Object.keys(variableEnabledFieldMap).reduce<
      Record<string, boolean>
    >((pre, field) => {
      pre[field] = true;
      return pre;
    }, {});
    form.setFieldsValue(values);
  }, [form]);

  useFetchLlmList(LlmModelType.Chat);

  return (
    <section
      className={classNames({
        [styles.segmentedHidden]: !show,
      })}
    >
      <Form.Item
        label="Model"
        name="llm_id"
        rules={[{ required: true, message: 'Please select!' }]}
      >
        <Select options={modelOptions} />
      </Form.Item>
      <Divider></Divider>
      <Form.Item
        label="Parameters"
        name="parameters"
        initialValue={ModelVariableType.Precise}
        // rules={[{ required: true, message: 'Please input!' }]}
      >
        <Select<ModelVariableType>
          options={parameterOptions}
          onChange={handleParametersChange}
        />
      </Form.Item>
      <Form.Item label="Temperature" tooltip={'xx'}>
        <Flex gap={20} align="center">
          <Form.Item
            name={'temperatureEnabled'}
            valuePropName="checked"
            noStyle
          >
            <Switch size="small" />
          </Form.Item>
          <Flex flex={1}>
            <Form.Item
              name={['llm_setting', 'temperature']}
              noStyle
              rules={[{ required: true, message: 'Province is required' }]}
            >
              <Slider className={styles.variableSlider} max={1} step={0.01} />
            </Form.Item>
          </Flex>
          <Form.Item
            name={['llm_setting', 'temperature']}
            noStyle
            rules={[{ required: true, message: 'Street is required' }]}
          >
            <InputNumber
              className={styles.sliderInputNumber}
              max={1}
              min={0}
              step={0.01}
            />
          </Form.Item>
        </Flex>
      </Form.Item>
      <Form.Item label="Top P" tooltip={'xx'}>
        <Flex gap={20} align="center">
          <Form.Item name={'topPEnabled'} valuePropName="checked" noStyle>
            <Switch size="small" />
          </Form.Item>
          <Flex flex={1}>
            <Form.Item
              name={['llm_setting', 'top_p']}
              noStyle
              rules={[{ required: true, message: 'Province is required' }]}
            >
              <Slider className={styles.variableSlider} max={1} step={0.01} />
            </Form.Item>
          </Flex>
          <Form.Item
            name={['llm_setting', 'top_p']}
            noStyle
            rules={[{ required: true, message: 'Street is required' }]}
          >
            <InputNumber
              className={styles.sliderInputNumber}
              max={1}
              min={0}
              step={0.01}
            />
          </Form.Item>
        </Flex>
      </Form.Item>
      <Form.Item label="Presence Penalty" tooltip={'xx'}>
        <Flex gap={20} align="center">
          <Form.Item
            name={'presencePenaltyEnabled'}
            valuePropName="checked"
            noStyle
          >
            <Switch size="small" />
          </Form.Item>
          <Flex flex={1}>
            <Form.Item
              name={['llm_setting', 'presence_penalty']}
              noStyle
              rules={[{ required: true, message: 'Province is required' }]}
            >
              <Slider className={styles.variableSlider} max={1} step={0.01} />
            </Form.Item>
          </Flex>
          <Form.Item
            name={['llm_setting', 'presence_penalty']}
            noStyle
            rules={[{ required: true, message: 'Street is required' }]}
          >
            <InputNumber
              className={styles.sliderInputNumber}
              max={1}
              min={0}
              step={0.01}
            />
          </Form.Item>
        </Flex>
      </Form.Item>
      <Form.Item label="Frequency Penalty" tooltip={'xx'}>
        <Flex gap={20} align="center">
          <Form.Item
            name={'frequencyPenaltyEnabled'}
            valuePropName="checked"
            noStyle
          >
            <Switch size="small" />
          </Form.Item>
          <Flex flex={1}>
            <Form.Item
              name={['llm_setting', 'frequency_penalty']}
              noStyle
              rules={[{ required: true, message: 'Province is required' }]}
            >
              <Slider className={styles.variableSlider} max={1} step={0.01} />
            </Form.Item>
          </Flex>
          <Form.Item
            name={['llm_setting', 'frequency_penalty']}
            noStyle
            rules={[{ required: true, message: 'Street is required' }]}
          >
            <InputNumber
              className={styles.sliderInputNumber}
              max={1}
              min={0}
              step={0.01}
            />
          </Form.Item>
        </Flex>
      </Form.Item>
      <Form.Item label="Max Tokens" tooltip={'xx'}>
        <Flex gap={20} align="center">
          <Form.Item name={'maxTokensEnabled'} valuePropName="checked" noStyle>
            <Switch size="small" />
          </Form.Item>
          <Flex flex={1}>
            <Form.Item
              name={['llm_setting', 'max_tokens']}
              noStyle
              rules={[{ required: true, message: 'Province is required' }]}
            >
              <Slider className={styles.variableSlider} max={2048} />
            </Form.Item>
          </Flex>
          <Form.Item
            name={['llm_setting', 'max_tokens']}
            noStyle
            rules={[{ required: true, message: 'Street is required' }]}
          >
            <InputNumber
              className={styles.sliderInputNumber}
              max={2048}
              min={0}
            />
          </Form.Item>
        </Flex>
      </Form.Item>
    </section>
  );
};

export default ModelSetting;
