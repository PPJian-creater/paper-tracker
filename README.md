# 📚 Literature Tracking - 学术文献追踪系统

基于 GitHub Actions 自动爬取、GitHub Pages 免费托管的 SSCI + 国内 CSSCI 学术文献追踪平台。

🌐 **在线访问**: https://你的用户名.github.io/仓库名/

---

## ✨ 核心特性

| 特性 | 说明 |
|------|------|
| 🆓 **完全免费** | GitHub Actions + Pages 零成本部署，无服务器费用 |
| 🔄 **自动更新** | 每日增量 + 每周日全量扫描（14天），北京时间 00:00 自动运行 |
| 📚 **六大领域** | 公共行政(PA) + 公共政策(PP) + 政治学(POL) + 经济学(ECON) + 中国研究(CHINA) + 国内期刊(CN) |
| 🇨🇳 **大陆作者筛选** | 自动识别作者机构，支持筛选含/不含大陆作者的文献 |
| 🇨🇳 **国内期刊** | 30 本 CSSCI 核心期刊，RSS 自动爬取（知网数据源） |
| 🗂️ **智能收藏** | 书签收藏 + 文件夹分类 + 拖拽管理 + 导入导出 |
| 🔍 **高级搜索** | 多字段组合检索（标题/摘要/作者/关键词） |
| 📊 **可视化** | 热词分析 + 发文趋势 |
| 🎨 **现代UI** | 毛玻璃拟态设计 + 学术风格配色 |
| 📱 **响应式** | 完美适配手机/平板/电脑 |
| 🌐 **全球加速** | jsDelivr CDN 加速访问 |

---

## 📚 覆盖期刊（112本SSCI + 30本国内CSSCI）

### 国际期刊（112本SSCI）

| 领域 | 数量 | 代表期刊 |
|------|------|----------|
| 公共行政 (PA) | 24本 | PAR, PA, JPART, Governance, PMR, CPA... |
| 公共政策 (PP) | 24本 | Policy Sciences, JPAM, JPP, CPP... |
| 政治学 (POL) | 36本 | APSR, AJPS, JOP, IO, ISQ... |
| 经济学 (ECON) | 20本 | AER, Econometrica, JPE, QJE, RESTUD... |
| 中国研究 (CHINA) | 8本 | The China Quarterly, JCC, China-An International Journal... |

### 国内期刊（30本CSSCI）

中国社会科学、经济研究、管理世界、政治学研究、社会学研究、中国行政管理、公共管理学报、公共行政评论、公共管理评论、公共管理与政策评论、电子政务、行政论坛、甘肃行政学院学报、治理研究、经济社会体制比较、社会、中共中央党校(国家行政学院)学报、北京行政学院学报、上海行政学院学报、江苏行政学院学报、行政管理改革、求实、探索、学海、中国农村经济、中国农村观察、农业经济问题、农村经济、南京农业大学学报(社会科学版)、社会学评论

> ⚠️ **注意**：国内期刊爬取依赖知网 RSS 接口，GitHub Actions 服务器可能因 IP 限制无法访问。建议本地手动运行 `cn_rss_crawler.py` 后上传数据。

---

## 🚀 快速开始

### 1. Fork 仓库

点击右上角 **Fork** 按钮，等待 Fork 完成。

### 2. 配置 Secrets

进入你 Fork 的仓库 → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

| Name | Value |
|------|-------|
| `EMAIL` | 你的邮箱（用于Crossref/OpenAlex API标识） |

### 3. 启用 GitHub Pages

**Settings** → **Pages** → **Source** 选择 **GitHub Actions** → 保存

### 4. 首次爬取数据

**Actions** 标签 → 选择 **每日爬取SSCI文献** → **Run workflow** → 选择 `initial` 模式 → 等待15-30分钟

### 5. 访问网站

```
https://你的用户名.github.io/仓库名/
```

---

## 📁 项目结构

```
.
├── .github/workflows/
│   └── crawl.yml              # GitHub Actions 定时任务
├── data/
│   ├── papers.json            # SSCI 文献数据（自动生成）
│   ├── cn_papers.json         # 国内期刊文献数据（自动生成）
│   ├── data.json              # 前端合并数据（自动生成）
│   └── ror_cn.json            # ROR 中国大陆机构库（5296个机构）
├── scripts/
│   ├── crawler.py             # 补充爬虫（OpenAlex，补充摘要/关键词）
│   ├── supplement.py          # 主爬虫（Crossref + ROR 作者机构判定 + S2）
│   ├── backfill_authors.py    # 存量/增量作者机构回填
│   ├── verify_mainland.py     # 作者机构针对性重核实
│   ├── cn_rss_crawler.py      # 国内期刊 RSS 爬虫（知网数据源）
│   ├── cleanup.py             # 数据清理（去重 + 未来日期过滤）
│   ├── update_dates.py        # 存量日期更新（Crossref，手动运行）
│   └── export.py              # 数据导出（合并 SSCI + 国内期刊）
├── index.html                 # 前端页面
└── README.md                  # 本文件
```

---

## 🎯 功能模块

### 1️⃣ 发现模块
- **统计卡片** - 六大领域近30天收录篇数，动态更新
- **最新更新** - 查看最新收录的文献，支持查看前一天数据
- **热词分析** - 近90天标题热词 + 摘要热词（国际期刊），支持分领域筛选
- **发文趋势** - 近30天文献发表趋势，支持分模块展示

### 2️⃣ 六大领域 (PA/PP/POL/ECON/CHINA/CN)
- 期刊筛选 + 时间范围筛选 + **大陆作者筛选**
- 文献卡片（分类/标题/作者/摘要/关键词 + 大陆作者标签）
- 书签收藏（点击选择文件夹）

### 3️⃣ 收藏模块
- **文件夹管理** - 新建/删除/重命名
- **书签收藏** - 点击书签选择目标文件夹
- **批量操作** - 多选删除
- **导入导出** - JSON格式，支持跨设备迁移

### 4️⃣ 期刊导航
- 111本期刊已验证官网链接
- 领域筛选 + 实时搜索
- 桌面端表格布局 / 移动端折叠列表（手风琴效果）

### 5️⃣ 搜索模块
- 多字段组合检索
- 领域/时间范围筛选
- 关键词高亮显示

---

## ⚙️ 自定义配置

### 修改定时规则

编辑 `.github/workflows/crawl.yml`：

```yaml
schedule:
  - cron: '0 16 * * *'  # 每天 UTC 16:00（北京时间 00:00）
```

### 配置 Secrets

进入仓库 → **Settings** → **Secrets and variables** → **Actions**

| Name | 必填 | 说明 |
|------|------|------|
| `EMAIL` | ✅ | 用于 OpenAlex / Crossref API 标识 |
| `S2_API_KEY` | ❌ | Semantic Scholar API Key（可选，提升限额） |

### 修改邮箱

编辑 `scripts/supplement.py` 和 `scripts/crawler.py`：

```python
EMAIL = "your-email@example.com"
```

### 修改期刊列表

编辑 `scripts/crawler.py` 和 `scripts/supplement.py` 中的 `JOURNALS_CONFIG`（两份配置需保持同步）。

---

## 🔧 本地开发

```bash
# 克隆仓库
git clone https://github.com/你的用户名/仓库名.git
cd 仓库名

# 安装依赖
pip install requests

# 运行主爬虫（Crossref + ROR 作者机构判定）
python scripts/supplement.py --days 7

# 补充爬虫（OpenAlex 补充摘要/关键词）
python scripts/crawler.py --days 30

# 爬取国内期刊（知网 RSS，需国内网络环境）
python scripts/cn_rss_crawler.py

# 清理重复和未来日期
python scripts/cleanup.py

# 导出数据（自动合并 SSCI + 国内期刊）
python scripts/export.py

# （可选）更新存量论文日期
python scripts/update_dates.py

# 本地预览
python -m http.server 8000
# 访问 http://localhost:8000
```

### 手动更新国内期刊流程

由于知网 RSS 对 GitHub Actions 服务器的 IP 有限制，建议本地手动更新国内期刊：

```bash
# 1. 确保在国内网络环境下运行
python scripts/cn_rss_crawler.py

# 2. 重新导出合并数据
python scripts/export.py

# 3. 提交到 GitHub
git add data/cn_papers.json data/data.json
git commit -m "update: 国内期刊文献 $(date +%Y-%m-%d)"
git push
```

---

## 📝 数据来源

| 数据源 | 用途 | 说明 |
|--------|------|------|
| **Crossref API** | 主数据源 + 作者机构判定 | 文献元数据、摘要、作者、affiliation（含 ROR 数据库交叉验证） |
| **OpenAlex API** | 补充摘要/关键词 | 补充 Crossref 可能缺失的摘要，DOI 自动去重 |
| **ROR 数据库** | 作者机构验证 | 5296 个中国大陆机构，用于判定作者是否来自大陆 |
| **Semantic Scholar** | 摘要补全 | 补充 OpenAlex / Crossref 缺失的摘要 |
| **知网 RSS** | 国内期刊数据源 | 30 本 CSSCI 核心期刊的 RSS 推送 |

### 作者大陆判定逻辑
- 双重判定：`"china"` 关键词 + ROR 5296 个大陆机构子串匹配
- 排除港澳台：`hong kong` / `macau` / `taiwan` / `taipei` 关键词过滤
- 三值输出：`true`（含大陆作者）/ `false`（不含）/ `null`（无法判断）

### Workflow 更新顺序
1. **Crossref 主爬** — 获取最新文献 + 作者机构
2. **OpenAlex 补充** — 补充缺失摘要，DOI 去重
3. **数据清理** — 去重 + 过滤
4. **数据导出** — 合并生成 data.json
5. **部署** — GitHub Pages 自动部署

---

## 🔄 更新日志

### 2026-06-25
- ✅ **大陆作者筛选** — 新增 `has_mainland_author` 字段，支持按作者机构筛选含/不含大陆作者的文献
- ✅ **ROR 数据库** — 下载 ROR v2.9 最新版，提取 5296 个中国大陆机构用于作者判定
- ✅ **判定升级** — `"china"` 关键词 + ROR 机构匹配双重验证，排除港澳台
- ✅ **Crossref 优先** — Workflow 调整为 Crossref 主爬 + OpenAlex 补充，机构信息以 Crossref 为准
- ✅ **去除 OpenAlex 国籍** — `crawler.py` 不再从 OpenAlex 提取作者国籍（误判率高达 44%）
- ✅ **存量回填** — `backfill_authors.py` 批量回填 4221 篇已有论文的机构信息
- ✅ **针对性重核实** — `verify_mainland.py` 对 ECON/CHINA/POL 模块反复核验，确保数据准确
- ✅ **前端增强** — 发现模块/领域模块新增红色「大陆作者」标签，筛选下拉框宽度统一

### 2026-06-17
- ✅ **新增经济学模块** - 20 本 SSCI 经济学期刊（16 本 Q1 + 1 本 Q2 + 3 本 Q3），涵盖 AER、Econometrica、JPE、QJE 等顶刊
- ✅ **六大领域扩展** - 新增「经济学(ECON)」模块，置于政治学和中国研究之间
- ✅ **统计卡片优化** - 调整为 3 列 × 2 行布局，避免新增领域后卡片过窄

### 2026-06-03
- ✅ **新增国内期刊模块** - 30 本 CSSCI 核心期刊 RSS 自动爬取，独立存储 `data/cn_papers.json`
- ✅ **五大领域扩展** - 新增「国内期刊(CN)」模块，与 PA/PP/POL/CHINA 并列
- ✅ **摘要+作者提取** - 知网 RSS 返回完整摘要和作者信息，数据质量提升
- ✅ **数据隔离设计** - 国内期刊与 SSCI 数据分开存储，互不影响
- ✅ **本地手动更新支持** - 因知网 IP 限制，提供本地手动更新国内期刊的完整流程
- ✅ **热词分析优化** - 排除中文文献，避免分词问题
- ✅ **UI 精简** - 移除导航栏图标、删除精彩推荐卡片

### 2026-05-19
- ✅ **新增5本期刊** - PA 新增 4 本（CPA, PPMG, PPM, ROPPA），PP 新增 1 本（CPP），覆盖达 91 本
- ✅ **统计卡片重构** - 发现模块卡片改为显示各领域"近30天篇数"，动态计算而非静态总数
- ✅ **期刊筛选修复** - 筛选下拉框直接读取期刊配置，确保无数据的新期刊也能正常显示
- ✅ **爬虫日期修复** - `crawler.py` / `supplement.py` 中 `--days` 参数曾因数据存在而被忽略，现通过 `min(now-days, latest-3天)` 确保 weekly（14天）和 initial（120天）模式按预期执行
- ✅ **ISSN 校正** - 5 本新增期刊统一使用在线版 ISSN，确保 OpenAlex / Crossref 正确索引

### 2026-05-13
- ✅ **双日期显示** - 支持 "在线发表 / 纸质刊出" 双日期展示
- ✅ **Crossref 日期优先** - `published_online` 优先使用 Crossref 的 `published-online` 日期
- ✅ **漏爬补充机制** - Crossref 按 ISSN 发现 OpenAlex 漏爬文献，S2 补全摘要
- ✅ **摘要自动补充** - OpenAlex 上线后自动补充存量无摘要文献
- ✅ **数据清理流程** - 全局 DOI 去重 + 未来日期过滤
- ✅ **期刊名称修复** - 解决 HTML 实体编码显示问题（如 `&amp;`）

### 2026-04-13
- ✅ 导航栏毛玻璃拟态设计升级
- ✅ 统计卡片样式优化（统一纯白透明风格）
- ✅ 搜索模块界面调整

### 2026-04-12
- ✅ 新增收藏导入导出功能（JSON格式）
- ✅ 用户数据隔离（多用户独立收藏）

### 2026-04-11
- ✅ 重构收藏系统（书签+文件夹管理）
- ✅ 新增政治学(POL)和中国研究(CHINA)模块
- ✅ 期刊导航表格布局优化
- ✅ 搜索支持多字段组合检索
- ✅ 新增热词分析功能（标题热词+摘要热词）
- ✅ UI全面升级（学术风格）

---

## 📄 许可证

MIT License

---

Made with ❤️ for Scholars
