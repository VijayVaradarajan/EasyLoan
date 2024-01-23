#
#  Copyright 2024 The InfiniFlow Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
from abc import ABC
from openai import OpenAI
import os


class Base(ABC):
    def __init__(self, key, model_name):
        pass

    def chat(self, system, history, gen_conf):
        raise NotImplementedError("Please implement encode method!")


class GptTurbo(Base):
    def __init__(self, key, model_name="gpt-3.5-turbo"):
        self.client = OpenAI(api_key=key)
        self.model_name = model_name

    def chat(self, system, history, gen_conf):
        history.insert(0, {"role": "system", "content": system})
        res = self.client.chat.completions.create(
            model=self.model_name,
            messages=history,
            **gen_conf)
        return res.choices[0].message.content.strip(), res.usage.completion_tokens


from dashscope import Generation
class QWenChat(Base):
    def __init__(self, key, model_name=Generation.Models.qwen_turbo):
        import dashscope
        dashscope.api_key = key
        self.model_name = model_name

    def chat(self, system, history, gen_conf):
        from http import HTTPStatus
        history.insert(0, {"role": "system", "content": system})
        response = Generation.call(
            self.model_name,
            messages=history,
            result_format='message'
        )
        if response.status_code == HTTPStatus.OK:
            return response.output.choices[0]['message']['content'], response.usage.output_tokens
        return response.message, 0
