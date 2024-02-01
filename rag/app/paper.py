import copy
import re
from collections import Counter
from rag.app import tokenize
from rag.nlp import huqie
from rag.parser.pdf_parser import HuParser
import numpy as np
from rag.utils import num_tokens_from_string


class Pdf(HuParser):
    def __call__(self, filename, binary=None, from_page=0,
                 to_page=100000, zoomin=3, callback=None):
        self.__images__(
            filename if not binary else binary,
            zoomin,
            from_page,
            to_page)
        callback(0.2, "OCR finished.")

        from timeit import default_timer as timer
        start = timer()
        self._layouts_paddle(zoomin)
        callback(0.47, "Layout analysis finished")
        print("paddle layouts:", timer() - start)
        self._table_transformer_job(zoomin)
        callback(0.68, "Table analysis finished")
        self._text_merge()
        column_width = np.median([b["x1"] - b["x0"] for b in self.boxes])
        self._concat_downward(concat_between_pages=False)
        self._filter_forpages()
        callback(0.75, "Text merging finished.")
        tbls = self._extract_table_figure(True, zoomin, False)

        # clean mess
        if column_width < self.page_images[0].size[0] / zoomin / 2:
            print("two_column...................", column_width,
                  self.page_images[0].size[0] / zoomin / 2)
            self.boxes = self.sort_X_by_page(self.boxes, column_width / 2)
        for b in self.boxes:
            b["text"] = re.sub(r"([\t 　]|\u3000){2,}", " ", b["text"].strip())
        freq = Counter([b["text"] for b in self.boxes])
        garbage = set([k for k, v in freq.items() if v > self.total_page * 0.6])
        i = 0
        while i < len(self.boxes):
            if self.boxes[i]["text"] in garbage \
                    or (re.match(r"[a-zA-Z0-9]+$", self.boxes[i]["text"]) and not self.boxes[i].get("layoutno")) \
                    or (i + 1 < len(self.boxes) and self.boxes[i]["text"] == self.boxes[i + 1]["text"]):
                self.boxes.pop(i)
            elif i + 1 < len(self.boxes) and self.boxes[i].get("layoutno", '0') == self.boxes[i + 1].get("layoutno",
                                                                                                         '1'):
                # merge within same layouts
                self.boxes[i + 1]["top"] = self.boxes[i]["top"]
                self.boxes[i + 1]["x0"] = min(self.boxes[i]["x0"], self.boxes[i + 1]["x0"])
                self.boxes[i + 1]["x1"] = max(self.boxes[i]["x1"], self.boxes[i + 1]["x1"])
                self.boxes[i + 1]["text"] = self.boxes[i]["text"] + " " + self.boxes[i + 1]["text"]
                self.boxes.pop(i)
            else:
                i += 1

        def _begin(txt):
            return re.match(
                "[0-9. 一、i]*(introduction|abstract|摘要|引言|keywords|key words|关键词|background|背景|目录|前言|contents)",
                txt.lower().strip())

        # get title and authors
        title = ""
        authors = []
        i = 0
        while i < min(32, len(self.boxes)):
            b = self.boxes[i]
            i += 1
            if b.get("layoutno", "").find("title") >= 0:
                title = b["text"]
                if _begin(title):
                    title = ""
                    break
                for j in range(3):
                    if _begin(self.boxes[i + j]["text"]): break
                    authors.append(self.boxes[i + j]["text"])
                    break
                break
        # get abstract
        abstr = ""
        i = 0
        while i + 1 < min(32, len(self.boxes)):
            b = self.boxes[i]
            i += 1
            txt = b["text"].lower().strip()
            if re.match("(abstract|摘要)", txt):
                if len(txt.split(" ")) > 32 or len(txt) > 64:
                    abstr = txt + self._line_tag(b, zoomin)
                    i += 1
                    break
                txt = self.boxes[i + 1]["text"].lower().strip()
                if len(txt.split(" ")) > 32 or len(txt) > 64:
                    abstr = txt + self._line_tag(self.boxes[i + 1], zoomin)
                i += 1
                break
        if not abstr: i = 0

        callback(0.8, "Page {}~{}: Text merging finished".format(from_page, min(to_page, self.total_page)))
        for b in self.boxes: print(b["text"], b.get("layoutno"))
        print(tbls)

        return {
            "title": title if title else filename,
            "authors": " ".join(authors),
            "abstract": abstr,
            "lines": [(b["text"] + self._line_tag(b, zoomin), b.get("layoutno", "")) for b in self.boxes[i:] if
                      re.match(r"(text|title)", b.get("layoutno", "text"))],
            "tables": tbls
        }


def chunk(filename, binary=None, from_page=0, to_page=100000, callback=None):
    pdf_parser = None
    paper = {}

    if re.search(r"\.pdf$", filename, re.IGNORECASE):
        pdf_parser = Pdf()
        paper = pdf_parser(filename if not binary else binary,
                           from_page=from_page, to_page=to_page, callback=callback)
    else: raise NotImplementedError("file type not supported yet(pdf supported)")
    doc = {
        "docnm_kwd": paper["title"] if paper["title"] else filename,
        "authors_tks": paper["authors"]
    }
    doc["title_tks"] = huqie.qie(re.sub(r"\.[a-zA-Z]+$", "", doc["docnm_kwd"]))
    doc["title_sm_tks"] = huqie.qieqie(doc["title_tks"])
    doc["authors_sm_tks"] = huqie.qieqie(doc["authors_tks"])
    # is it English
    eng = pdf_parser.is_english
    print("It's English.....", eng)

    res = []
    # add tables
    for img, rows in paper["tables"]:
        bs = 10
        de = ";" if eng else "；"
        for i in range(0, len(rows), bs):
            d = copy.deepcopy(doc)
            r = de.join(rows[i:i + bs])
            r = re.sub(r"\t——(来自| in ).*”%s" % de, "", r)
            tokenize(d, r)
            d["image"] = img
            res.append(d)

    if paper["abstract"]:
        d = copy.deepcopy(doc)
        txt = pdf_parser.remove_tag(paper["abstract"])
        d["important_kwd"] = ["abstract", "总结", "概括", "summary", "summarize"]
        d["important_tks"] = " ".join(d["important_kwd"])
        d["image"] = pdf_parser.crop(paper["abstract"])
        tokenize(d, txt, eng)
        res.append(d)

    readed = [0] * len(paper["lines"])
    # find colon firstly
    i = 0
    while i + 1 < len(paper["lines"]):
        txt = pdf_parser.remove_tag(paper["lines"][i][0])
        j = i
        if txt.strip("\n").strip()[-1] not in ":：":
            i += 1
            continue
        i += 1
        while i < len(paper["lines"]) and not paper["lines"][i][0]:
            i += 1
        if i >= len(paper["lines"]): break
        proj = [paper["lines"][i][0].strip()]
        i += 1
        while i < len(paper["lines"]) and paper["lines"][i][0].strip()[0] == proj[-1][0]:
            proj.append(paper["lines"][i])
            i += 1
        for k in range(j, i): readed[k] = True
        txt = txt[::-1]
        if eng:
            r = re.search(r"(.*?) ([\.;?!]|$)", txt)
            txt = r.group(1)[::-1] if r else txt[::-1]
        else:
            r = re.search(r"(.*?) ([。？；！]|$)", txt)
            txt = r.group(1)[::-1] if r else txt[::-1]
        for p in proj:
            d = copy.deepcopy(doc)
            txt += "\n" + pdf_parser.remove_tag(p)
            d["image"] = pdf_parser.crop(p)
            tokenize(d, txt)
            res.append(d)

    i = 0
    chunk = []
    tk_cnt = 0
    def add_chunk():
        nonlocal chunk, res, doc, pdf_parser, tk_cnt
        d = copy.deepcopy(doc)
        ck = "\n".join(chunk)
        tokenize(d, pdf_parser.remove_tag(ck), pdf_parser.is_english)
        d["image"] = pdf_parser.crop(ck)
        res.append(d)
        chunk = []
        tk_cnt = 0

    while i < len(paper["lines"]):
        if tk_cnt > 128:
            add_chunk()
        if readed[i]:
            i += 1
            continue
        readed[i] = True
        txt, layouts = paper["lines"][i]
        txt_ = pdf_parser.remove_tag(txt)
        i += 1
        cnt = num_tokens_from_string(txt_)
        if any([
            layouts.find("title") >= 0 and chunk,
            cnt + tk_cnt > 128 and tk_cnt > 32,
        ]):
            add_chunk()
            chunk = [txt]
            tk_cnt = cnt
        else:
            chunk.append(txt)
            tk_cnt += cnt

    if chunk: add_chunk()
    for i, d in enumerate(res):
        print(d)
        # d["image"].save(f"./logs/{i}.jpg")
    return res


if __name__ == "__main__":
    import sys

    chunk(sys.argv[1])
