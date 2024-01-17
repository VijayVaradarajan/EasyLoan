# -*- coding: utf-8 -*-

import json
import re
import logging
import copy
import math
from elasticsearch_dsl import Q, Search
from rag.nlp import huqie, term_weight, synonym


class EsQueryer:
    def __init__(self, es):
        self.tw = term_weight.Dealer()
        self.es = es
        self.syn = synonym.Dealer(None)
        self.flds = ["ask_tks^10", "ask_small_tks"]

    @staticmethod
    def subSpecialChar(line):
        return re.sub(r"([:\{\}/\[\]\-\*\"\(\)\|~\^])", r"\\\1", line).strip()

    @staticmethod
    def isChinese(line):
        arr = re.split(r"[ \t]+", line)
        if len(arr) <= 3:
            return True
        e = 0
        for t in arr:
            if not re.match(r"[a-zA-Z]+$", t):
                e += 1
        return e * 1. / len(arr) >= 0.8

    @staticmethod
    def rmWWW(txt):
        txt = re.sub(
            r"是*(什么样的|哪家|那家|啥样|咋样了|什么时候|何时|何地|何人|是否|是不是|多少|哪里|怎么|哪儿|怎么样|如何|哪些|是啥|啥是|啊|吗|呢|吧|咋|什么|有没有|呀)是*",
            "",
            txt)
        return re.sub(
            r"(what|who|how|which|where|why|(is|are|were|was) there) (is|are|were|was)*", "", txt, re.IGNORECASE)

    def question(self, txt, tbl="qa", min_match="60%"):
        txt = re.sub(
            r"[ \t,，。？?/`!！&]+",
            " ",
            huqie.tradi2simp(
                huqie.strQ2B(
                    txt.lower()))).strip()
        txt = EsQueryer.rmWWW(txt)

        if not self.isChinese(txt):
            tks = txt.split(" ")
            q = []
            for i in range(1, len(tks)):
                q.append("\"%s %s\"~2" % (tks[i - 1], tks[i]))
            if not q:
                q.append(txt)
            return Q("bool",
                     must=Q("query_string", fields=self.flds,
                            type="best_fields", query=" OR ".join(q),
                            boost=1, minimum_should_match="60%")
                     ), txt.split(" ")

        def needQieqie(tk):
            if len(tk) < 4:
                return False
            if re.match(r"[0-9a-z\.\+#_\*-]+$", tk):
                return False
            return True

        qs, keywords = [], []
        for tt in self.tw.split(txt):  # .split(" "):
            if not tt:
                continue
            twts = self.tw.weights([tt])
            syns = self.syn.lookup(tt)
            logging.info(json.dumps(twts, ensure_ascii=False))
            tms = []
            for tk, w in sorted(twts, key=lambda x: x[1] * -1):
                sm = huqie.qieqie(tk).split(" ") if needQieqie(tk) else []
                sm = [
                    re.sub(
                        r"[ ,\./;'\[\]\\`~!@#$%\^&\*\(\)=\+_<>\?:\"\{\}\|，。；‘’【】、！￥……（）——《》？：“”-]+",
                        "",
                        m) for m in sm]
                sm = [EsQueryer.subSpecialChar(m) for m in sm if len(m) > 1]
                sm = [m for m in sm if len(m) > 1]
                if len(sm) < 2:
                    sm = []

                keywords.append(re.sub(r"[ \\\"']+", "", tk))

                tk_syns = self.syn.lookup(tk)
                tk = EsQueryer.subSpecialChar(tk)
                if tk.find(" ") > 0:
                    tk = "\"%s\"" % tk
                if tk_syns:
                    tk = f"({tk} %s)" % " ".join(tk_syns)
                if sm:
                    tk = f"{tk} OR \"%s\" OR (\"%s\"~2)^0.5" % (
                        " ".join(sm), " ".join(sm))
                tms.append((tk, w))

            tms = " ".join([f"({t})^{w}" for t, w in tms])

            if len(twts) > 1:
                tms += f" (\"%s\"~4)^1.5" % (" ".join([t for t, _ in twts]))
            if re.match(r"[0-9a-z ]+$", tt):
                tms = f"(\"{tt}\" OR \"%s\")" % huqie.qie(tt)

            syns = " OR ".join(
                ["\"%s\"^0.7" % EsQueryer.subSpecialChar(huqie.qie(s)) for s in syns])
            if syns:
                tms = f"({tms})^5 OR ({syns})^0.7"

            qs.append(tms)

        flds = copy.deepcopy(self.flds)
        mst = []
        if qs:
            mst.append(
                Q("query_string", fields=flds, type="best_fields",
                  query=" OR ".join([f"({t})" for t in qs if t]), boost=1, minimum_should_match=min_match)
            )

        return Q("bool",
                 must=mst,
                 ), keywords

    def hybrid_similarity(self, avec, bvecs, atks, btkss, tkweight=0.3,
                          vtweight=0.7):
        from sklearn.metrics.pairwise import cosine_similarity as CosineSimilarity
        import numpy as np
        sims = CosineSimilarity([avec], bvecs)

        def toDict(tks):
            d = {}
            if isinstance(tks, type("")):
                tks = tks.split(" ")
            for t, c in self.tw.weights(tks):
                if t not in d:
                    d[t] = 0
                d[t] += c
            return d

        atks = toDict(atks)
        btkss = [toDict(tks) for tks in btkss]
        tksim = [self.similarity(atks, btks) for btks in btkss]
        return np.array(sims[0]) * vtweight + np.array(tksim) * tkweight, sims[0], tksim

    def similarity(self, qtwt, dtwt):
        if isinstance(dtwt, type("")):
            dtwt = {t: w for t, w in self.tw.weights(self.tw.split(dtwt))}
        if isinstance(qtwt, type("")):
            qtwt = {t: w for t, w in self.tw.weights(self.tw.split(qtwt))}
        s = 1e-9
        for k, v in qtwt.items():
            if k in dtwt:
                s += v * dtwt[k]
        q = 1e-9
        for k, v in qtwt.items():
            q += v * v
        d = 1e-9
        for k, v in dtwt.items():
            d += v * v
        return s / math.sqrt(q) / math.sqrt(d)
