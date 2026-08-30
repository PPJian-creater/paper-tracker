#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
国内期刊RSS爬虫 - 知网期刊文献爬取
基于知网RSS接口，解析30本CSSCI期刊最新文献
输出到独立的 data/cn_papers.json，与SSCI数据隔离
"""

import json
import os
import re
import hashlib
import time
import random
from datetime import datetime, timedelta
from xml.etree import ElementTree as ET

# 使用urllib替代requests，避免额外依赖
try:
    import urllib.request as urllib_request
    import urllib.error as urllib_error
except ImportError:
    import urllib2 as urllib_request
    import urllib2 as urllib_error

# RSS基础URL
RSS_BASE = "https://rss.cnki.net/knavi/rss/{code}?pcode=CJFD,CCJD"

# 30本国内期刊配置
CN_JOURNALS = {
    "ZSHK": "中国社会科学",
    "JJYJ": "经济研究",
    "GLSJ": "管理世界",
    "POLI": "政治学研究",
    "SHXJ": "社会学研究",
    "ZXGL": "中国行政管理",
    "GGGL": "公共管理学报",
    "GGXZ": "公共行政评论",
    "GOGL": "公共管理评论",
    "GGZC": "公共管理与政策评论",
    "DZZW": "电子政务",
    "XZNT": "行政论坛",
    "GSXX": "甘肃行政学院学报",
    "ZSWD": "治理研究",
    "JJSH": "经济社会体制比较",
    "SHEH": "社会",
    "ZGXB": "中共中央党校(国家行政学院)学报",
    "XZXY": "北京行政学院学报",
    "SHXY": "上海行政学院学报",
    "JSXZ": "江苏行政学院学报",
    "XZGL": "行政管理改革",
    "QUAK": "求实",
    "SUTA": "探索",
    "XHAI": "学海",
    "ZNJJ": "中国农村经济",
    "ZNCG": "中国农村观察",
    "NJWT": "农业经济问题",
    "NCJJ": "农村经济",
    "NJNS": "南京农业大学学报(社会科学版)",
    "SHPL": "社会学评论",
}

# User-Agent池（轮换使用）
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
]

# 非学术条目过滤关键词（标题匹配，不区分大小写）
INVALID_TITLE_PATTERNS = [
    r"征稿", r"征订", r"通知", r"声明", r"广告", r"敬告", r"启事",
    r"延期", r"变更", r"招聘", r"会议", r"论坛", r"启事", r"公告",
    r"订阅", r"投稿", r"征引", r"目录", r"总目", r"索引", r"编委会",
]

# RSS XML命名空间
NAMESPACES = {
    'content': 'http://purl.org/rss/1.0/modules/content/',
    'dc': 'http://purl.org/dc/elements/1.1/',
}


def get_headers():
    """生成请求头，随机UA"""
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'application/rss+xml, application/xml, text/xml, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': 'https://rss.cnki.net/',
    }


def load_existing_papers():
    """加载已有国内期刊文献"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(script_dir, '..', 'data', 'cn_papers.json')
    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_papers(papers):
    """保存文献到文件"""
    os.makedirs('data', exist_ok=True)
    with open('data/cn_papers.json', 'w', encoding='utf-8') as f:
        json.dump(papers, f, ensure_ascii=False, indent=2)


def generate_paper_id(title, journal_name):
    """生成稳定的论文ID：cnki_ + MD5(标题|期刊名)"""
    key = f"{title}|{journal_name}"
    md5_hash = hashlib.md5(key.encode('utf-8')).hexdigest()[:16]
    return f"cnki_{md5_hash}"


def clean_title(title):
    """清洗标题：去除HTML标签、多余空白、知网后缀等"""
    if not title:
        return ''
    # 去除HTML标签
    title = re.sub(r'<[^>]+>', '', title)
    # 去除知网常见后缀 [J]、[N] 等
    title = re.sub(r'\s*\[[A-Z]\]\s*$', '', title)
    # 去除多余空白
    title = re.sub(r'\s+', ' ', title).strip()
    return title


def clean_abstract(text):
    """清洗摘要：去除HTML标签、多余空白、知网省略号后缀"""
    if not text:
        return ''
    # 去除HTML标签
    text = re.sub(r'<[^>]+>', '', text)
    # 去除多余空白
    text = re.sub(r'\s+', ' ', text).strip()
    # 去除末尾的省略号或截断标记
    text = re.sub(r'…$', '', text)
    text = re.sub(r'\.\.\.$', '', text)
    return text


def parse_authors(author_str):
    """解析作者字符串：知网格式为 作者1;作者2;"""
    if not author_str:
        return []
    # 按分号或逗号分割
    authors = re.split(r'[;,；，]', author_str)
    # 清洗每个作者名
    authors = [a.strip() for a in authors if a.strip()]
    return authors


def parse_pub_date(pub_date_str):
    """解析RSS日期为 YYYY-MM-DD 格式"""
    if not pub_date_str:
        return None
    pub_date_str = pub_date_str.strip()

    # 格式1: Mon, 03 Jun 2026 00:00:00 GMT
    try:
        dt = datetime.strptime(pub_date_str, '%a, %d %b %Y %H:%M:%S %Z')
        return dt.strftime('%Y-%m-%d')
    except ValueError:
        pass

    # 格式2: 2026-06-03
    try:
        dt = datetime.strptime(pub_date_str, '%Y-%m-%d')
        return dt.strftime('%Y-%m-%d')
    except ValueError:
        pass

    # 格式3: 2026-06-03T00:00:00
    try:
        dt = datetime.strptime(pub_date_str[:10], '%Y-%m-%d')
        return dt.strftime('%Y-%m-%d')
    except ValueError:
        pass

    return None


def is_invalid_title(title):
    """判断是否为非学术条目"""
    if not title:
        return True
    title_clean = title.strip()
    if len(title_clean) < 5:
        return True
    for pattern in INVALID_TITLE_PATTERNS:
        if re.search(pattern, title_clean, re.IGNORECASE):
            return True
    return False


def fetch_rss(journal_code, journal_name):
    """获取单个期刊的RSS并解析"""
    url = RSS_BASE.format(code=journal_code)
    headers = get_headers()

    max_retries = 2
    content = None
    for attempt in range(max_retries + 1):
        req = urllib_request.Request(url, headers=headers)
        try:
            with urllib_request.urlopen(req, timeout=15) as response:
                content = response.read()
            break
        except Exception as e:
            if attempt < max_retries:
                wait = 3 + random.uniform(0, 2)
                print(f"  [{journal_name}] 请求失败，{wait:.1f}秒后重试: {e}")
                time.sleep(wait)
            else:
                print(f"  [{journal_name}] 请求失败（已达最大重试）: {e}")
                return []

    if content is None:
        return []

    # 处理可能的编码问题
    # 尝试多种编码
    text = None
    for encoding in ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']:
        try:
            text = content.decode(encoding)
            break
        except (UnicodeDecodeError, LookupError):
            continue

    if text is None:
        print(f"  [{journal_name}] 无法解码RSS内容")
        return []

    # 解析XML
    try:
        root = ET.fromstring(text.encode('utf-8'))
    except ET.ParseError as e:
        print(f"  [{journal_name}] XML解析失败: {e}")
        return []

    papers = []
    channel = root.find('channel')
    if channel is None:
        print(f"  [{journal_name}] RSS格式异常：找不到channel")
        return []

    items = channel.findall('item')
    for item in items:
        title_elem = item.find('title')
        link_elem = item.find('link')
        pub_date_elem = item.find('pubDate')
        desc_elem = item.find('description')
        author_elem = item.find('author')

        raw_title = title_elem.text if title_elem is not None and title_elem.text else ''
        title = clean_title(raw_title)
        link = link_elem.text if link_elem is not None and link_elem.text else ''
        pub_date_str = pub_date_elem.text if pub_date_elem is not None and pub_date_elem.text else ''
        raw_desc = desc_elem.text if desc_elem is not None and desc_elem.text else ''
        raw_author = author_elem.text if author_elem is not None and author_elem.text else ''

        # 过滤非学术条目
        if is_invalid_title(title):
            continue

        # 解析日期
        published_date = parse_pub_date(pub_date_str)
        if not published_date:
            continue

        # 过滤未来日期
        try:
            pub_dt = datetime.strptime(published_date, '%Y-%m-%d').date()
            if pub_dt > datetime.now().date():
                continue
        except ValueError:
            continue

        paper_id = generate_paper_id(title, journal_name)

        paper = {
            "openalex_id": paper_id,
            "title": title,
            "abstract": clean_abstract(raw_desc),
            "journal_name": journal_name,
            "published_date": published_date,
            "url": link,
            "doi": "",
            "keywords": [],
            "authors": parse_authors(raw_author),
            "category": "CN"
        }
        papers.append(paper)

    return papers


def crawl_cn_journals():
    """主爬取函数"""
    print("=" * 60)
    print("国内期刊RSS爬虫")
    print("=" * 60)

    # 加载已有数据
    existing_papers = load_existing_papers()
    existing_ids = {p.get('openalex_id') for p in existing_papers}
    print(f"已有文献: {len(existing_papers)} 篇")

    all_new_papers = []
    total_fetched = 0
    total_skipped = 0

    journal_codes = list(CN_JOURNALS.keys())
    # 随机打乱顺序，降低反爬风险
    random.shuffle(journal_codes)

    for i, code in enumerate(journal_codes, 1):
        journal_name = CN_JOURNALS[code]
        print(f"\n[{i}/{len(journal_codes)}] 爬取: {journal_name}")

        papers = fetch_rss(code, journal_name)
        new_papers = []
        for p in papers:
            if p['openalex_id'] not in existing_ids:
                new_papers.append(p)
                existing_ids.add(p['openalex_id'])
            else:
                total_skipped += 1

        if new_papers:
            print(f"  获取 {len(papers)} 条，新增 {len(new_papers)} 篇")
            all_new_papers.extend(new_papers)
        else:
            print(f"  获取 {len(papers)} 条，无新增")
        total_fetched += len(papers)

        # 随机间隔，避免反爬（RSS接口轻量，间隔较短即可）
        if i < len(journal_codes):
            delay = random.uniform(0.3, 0.8)
            time.sleep(delay)

    # 合并并排序（按日期降序）
    all_papers = all_new_papers + existing_papers
    all_papers.sort(key=lambda p: p.get('published_date', ''), reverse=True)

    print("\n" + "=" * 60)
    print(f"爬取完成:")
    print(f"  本次获取条目: {total_fetched}")
    print(f"  重复跳过: {total_skipped}")
    print(f"  新增文献: {len(all_new_papers)}")
    print(f"  文献总数: {len(all_papers)}")
    print("=" * 60)

    save_papers(all_papers)
    return len(all_new_papers), len(all_papers)


if __name__ == '__main__':
    crawl_cn_journals()
