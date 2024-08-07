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
import random
from abc import ABC
from functools import partial
import pandas as pd
import requests
import re
from graph.settings import DEBUG
from graph.component.base import ComponentBase, ComponentParamBase
import deepl

class DeepLParam(ComponentParamBase):
    """
    Define the DeepL component parameters.
    """

    def __init__(self):
        super().__init__()
        self.prompt = ""
        self.auth_key = "xxx"
        self.parameters = []
        self.source_lang = 'ZH'
        self.target_lang = 'EN-GB'
    def check(self):
        self.check_positive_integer(self.top_n, "Top N")
        self.check_valid_value(self.source_lang, "Source language", ['AR', 'BG', 'CS', 'DA', 'DE', 'EL', 'EN', 'ES', 'ET', 'FI', 'FR', 'HU', 'ID', 'IT', 'JA', 'KO', 'LT', 'LV', 'NB', 'NL', 'PL', 'PT', 'RO', 'RU', 'SK', 'SL', 'SV', 'TR', 'UK', 'ZH'])
        self.check_valid_value(self.target_lang, "Target language",['AR', 'BG', 'CS', 'DA', 'DE', 'EL', 'EN-GB', 'EN-US', 'ES', 'ET', 'FI', 'FR', 'HU', 'ID', 'IT', 'JA', 'KO', 'LT', 'LV', 'NB', 'NL', 'PL', 'PT-BR', 'PT-PT', 'RO', 'RU', 'SK', 'SL', 'SV', 'TR', 'UK', 'ZH'])


class DeepL(ComponentBase, ABC):
    component_name = "GitHub"

    def _run(self, history, **kwargs):
        prompt = self._param.prompt


        ans = self.get_input()
        ans = " - ".join(ans["content"]) if "content" in ans else ""
        if not ans:
            return DeepL.be_output("")


        for para in self._param.parameters:
            cpn = self._canvas.get_component(para["component_id"])["obj"]
            _, out = cpn.output(allow_partial=False)
            if "content" not in out.columns:
                kwargs[para["key"]] = "Nothing"
            else:
                kwargs[para["key"]] = "  - " + "\n  - ".join(out["content"])

        kwargs["input"] = ans
        for n, v in kwargs.items():
            prompt = re.sub(r"\{%s\}" % n, str(v), prompt)

        try:
            translator = deepl.Translator(self._param.auth_key)
            result = translator.translate_text(prompt,source_lang=self._param.source_lang, target_lang=self._param.target_lang)

            return DeepL.be_output(result.text)
        except Exception as e:
            DeepL.be_output("**Error**:"+str(e))
