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
import wikipedia
import pandas as pd
from graph.settings import DEBUG
from graph.component.base import ComponentBase, ComponentParamBase


class WikipediaParam(ComponentParamBase):
    """
    Define the Wikipedia component parameters.
    """

    def __init__(self):
        super().__init__()
        self.top_n = 10
        self.language = 'en'
        self.no = 'The content found on Wikipedia is empty'

    def check(self):
        self.check_positive_integer(self.top_n, "Top N")
        self.check_valid_value(self.language, "Wikipedia languages",
                               ['af', 'pl', 'ar', 'ast', 'az', 'bg', 'nan', 'bn', 'be', 'ca', 'cs', 'cy', 'da', 'de',
                                'et', 'el', 'en', 'es', 'eo', 'eu', 'fa', 'fr', 'gl', 'ko', 'hy', 'hi', 'hr', 'id',
                                'it', 'he', 'ka', 'lld', 'la', 'lv', 'lt', 'hu', 'mk', 'arz', 'ms', 'min', 'my', 'nl',
                                'ja', 'nb', 'nn', 'ce', 'uz', 'pt', 'kk', 'ro', 'ru', 'ceb', 'sk', 'sl', 'sr', 'sh',
                                'fi', 'sv', 'ta', 'tt', 'th', 'tg', 'azb', 'tr', 'uk', 'ur', 'vi', 'war', 'zh', 'yue'])


class Wikipedia(ComponentBase, ABC):
    component_name = "Wikipedia"

    def _run(self, history, **kwargs):
        ans = self.get_input()
        ans = " - ".join(ans["content"]) if "content" in ans else ""
        if not ans:
            return Wikipedia.be_output("")

        wiki_res = []
        wikipedia.set_lang(self._param.language)
        wiki_engine = wikipedia
        for wiki_key in wiki_engine.search(ans, results=self._param.top_n):
            try:
                page = wiki_engine.page(title=wiki_key, auto_suggest=False)
                wiki_res.append({"content": '<a href="' + page.url + '">' + page.title + '</a> ' + page.summary})
            except Exception as e:
                print(e)
                pass

        if not wiki_res:
            return Wikipedia.be_output(self._param.no)

        df = pd.DataFrame(wiki_res)
        if DEBUG: print(df, ":::::::::::::::::::::::::::::::::")
        return df
