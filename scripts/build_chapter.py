#!/usr/bin/env python3
"""从《伊利亚特-冰与火之歌.md》抽取指定章节，生成站点章节页。

用法:
  python3 scripts/build_chapter.py <md路径> <章节序号> <章节名> <对应原卷> [上一章名] [下一章名]

示例:
  python3 scripts/build_chapter.py ../伊利亚特-冰与火之歌.md 1 "阿喀琉斯 I" "一" "" "阿喀琉斯 II（待更）"

说明:
  - 章节在 md 中以 "## 第N章" 开头，到下一个 "---" 结束；
  - 以 * 开头的行（编辑注记）不进入正文；
  - 上一章名为空则上一章导航不输出；下一章名含"待更"则以纯文本呈现。
"""
import re
import sys
from pathlib import Path

TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>第 {num} 章 · {title} | 伊利亚特-小说版</title>
<meta name="description" content="{desc}">
<link rel="stylesheet" href="../assets/style.css">
</head>
<body>
<div class="wrap">

  <header class="chapter-head">
    <a class="back-link" href="../index.html">&larr; 返回目录</a>
    <p class="chapter-kicker">第 {num} 章</p>
    <h1 class="chapter-title">{title}</h1>
    <p class="chapter-vol">对应原卷：{vol}</p>
  </header>

  <article class="chapter-body">
{body}
  </article>

  <nav class="chapter-nav">
{nav}
  </nav>

  <p class="colophon">伊利亚特 · 小说版</p>

</div>
</html>
"""

CN_NUM = "零一二三四五六七八九"


def cn_num(n: int) -> str:
    if n <= 10:
        return "十" if n == 10 else CN_NUM[n]
    if n < 20:
        return "十" + CN_NUM[n % 10]
    return CN_NUM[n // 10] + "十" + (CN_NUM[n % 10] if n % 10 else "")


def extract_chapter(md_text: str, num: int):
    pat = re.compile(
        r"^## 第" + cn_num(num) + r"章[^\n]*\n(.*?)(?=^---$|\Z)", re.M | re.S
    )
    m = pat.search(md_text)
    if not m:
        sys.exit(f"未找到第 {num} 章（## 第{cn_num(num)}章）")
    paras = []
    for line in m.group(1).strip().splitlines():
        line = line.strip()
        if not line or line.startswith(("#", ">")):
            continue
        if line == "* * *":  # 场景分隔符，保留为场景间隔
            paras.append('<div class="scene-break">* * *</div>')
            continue
        if line.startswith("*"):  # 编辑注记不进入正文
            continue
        paras.append(f"<p>{line}</p>")
    return paras


def main():
    md_path, num, title, vol = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
    prev_name = sys.argv[5] if len(sys.argv) > 5 else ""
    next_name = sys.argv[6] if len(sys.argv) > 6 else ""

    paras = extract_chapter(Path(md_path).read_text(encoding="utf-8"), num)
    body = "\n".join(f"    {p}" for p in paras)

    nav = []
    if prev_name:
        nav.append(f'    <a class="prev" href="ch{num - 1:02d}.html">&larr; {prev_name}</a>')
    if next_name:
        if "待更" in next_name:
            nav.append(f'    <span class="next">下一章：{next_name}</span>')
        else:
            nav.append(f'    <a class="next" href="ch{num + 1:02d}.html">{next_name} &rarr;</a>')

    desc = re.sub(r"<[^>]+>", "", paras[0])[:60] + "……" if paras else ""
    html = TEMPLATE.format(num=num, title=title, vol=vol, desc=desc, body=body, nav="\n".join(nav))

    out = Path(__file__).resolve().parent.parent / "chapters" / f"ch{num:02d}.html"
    out.write_text(html, encoding="utf-8")
    print(f"OK {out}  段落数={len(paras)}  总字数={sum(len(p) for p in paras)}")


if __name__ == "__main__":
    main()
