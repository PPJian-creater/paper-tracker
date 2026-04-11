# 📚 文献追踪（Research Atlas）- GitHub Pages版

基于 GitHub Actions 自动爬取、GitHub Pages 免费部署的学术文献追踪系统。

🌐 **在线访问**: https://你的用户名.github.io/仓库名/

---

## ✨ 核心特性

- 🆓 **完全免费** - GitHub Actions + Pages 零成本部署
- 🔄 **自动更新** - 每天北京时间 00:00 自动爬取新文献
- 📚 **四大领域** - 公共行政(PA) + 公共政策(PP) + 政治学(POL) + 中国研究(CHINA)
- 🗂️ **智能收藏** - 书签收藏 + 拖拽管理 + 文件夹分类
- 🔍 **高级搜索** - 多字段组合检索（标题/摘要/作者/关键词）
- 📊 **数据可视化** - 研究主题河流图 + 发文趋势图 + 词云
- 📱 **响应式设计** - 完美适配手机/平板/电脑
- 🌐 **全球访问** - jsDelivr CDN 加速

---

## 📚 覆盖期刊

| 分类 | 数量 | 代表期刊 |
|------|------|----------|
| 公共行政 (PA) | 20本 | PAR, PA, JPART, Governance 等 |
| 公共政策 (PP) | 23本 | Policy Sciences, JPAM, JPP 等 |
| 政治学 (POL) | 36本 | APSR, AJPS, JOP, IO 等 |
| 中国研究 (CHINA) | 7本 | The China Quarterly, JCC 等 |
| **总计** | **86本** | SSCI顶级期刊 |

---

## 🖼️ 功能预览

### 1️⃣ 发现模块
- **研究主题河流图** - ECharts ThemeRiver展示各领域关键词热度演变
- **发文趋势图** - 近30天文献发表趋势
- **随机推荐** - 精选优质文献推荐
- **实时统计** - 文献总数、今日更新、各领域分布

### 2️⃣ 四大领域模块 (PA/PP/POL/CHINA)
- **期刊筛选** - 按期刊名称筛选文献
- **时间筛选** - 7天/30天/90天/1年时间范围
- **文献卡片** - 清晰展示标题、作者、摘要、关键词
- **快速收藏** - 点击书签图标选择收藏文件夹
- **拖拽收藏** - 支持拖拽文献到收藏夹侧边栏

### 3️⃣ 收藏模块
- **文件夹管理** - 新建、删除、重命名收藏文件夹
- **书签收藏** - 点击书签图标选择目标文件夹
- **拖拽移动** - 拖拽文献卡片到收藏夹快速移动
- **本地存储** - 使用浏览器 localStorage，数据持久化

### 4️⃣ 期刊导航
- **86本期刊** - 已验证官网链接
- **领域筛选** - 快速查看特定领域期刊
- **实时搜索** - 输入期刊名称即时过滤
- **紧凑布局** - 表格形式高效浏览

### 5️⃣ 搜索模块
- **多字段组合** - 可同时选择标题+摘要+作者+关键词
- **高级筛选** - 按领域、时间范围筛选
- **结果高亮** - 关键词在结果中高亮显示

---

## 🚀 快速开始

### 1. Fork 本仓库

1. 点击右上角的 **Fork** 按钮
2. 等待 Fork 完成

### 2. 配置 GitHub Actions

1. 进入你 Fork 的仓库
2. 点击 **Settings** → **Secrets and variables** → **Actions**
3. 点击 **New repository secret**
4. 添加：
   - **Name**: `EMAIL`
   - **Value**: 你的邮箱地址（用于OpenAlex API标识）

### 3. 启用 GitHub Pages

1. **Settings** → **Pages**
2. **Source**: 选择 "GitHub Actions"
3. 保存

### 4. 手动触发首次爬取

1. 进入 **Actions** 标签
2. 选择 "每日爬取SSCI文献"
3. 点击 "Run workflow"
4. 选择 `initial` 模式（爬取从2026年1月1日至今的文献）
5. 等待完成（约 10-20 分钟）

### 5. 访问网站

爬取完成后，访问：
```
https://你的用户名.github.io/仓库名/
```

---

## 📁 项目结构

```
.
├── .github/
│   └── workflows/
│       └── crawl.yml       # GitHub Actions 工作流
├── data/
│   ├── papers.json         # 文献数据（自动更新）
│   └── data.json           # 导出数据（自动更新）
├── scripts/
│   ├── crawler.py          # 爬虫脚本（支持4个模块）
│   └── export.py           # 数据导出脚本
├── index.html              # 前端页面（含全部新功能）
└── README.md               # 本文件
```

---

## ⚙️ 自定义配置

### 修改爬取邮箱

编辑 `scripts/crawler.py`：
```python
EMAIL = "your-email@example.com"  # 改成你的邮箱
```

### 修改期刊列表

编辑 `scripts/crawler.py` 中的 `JOURNALS_CONFIG`：

```python
JOURNALS_CONFIG = {
    "public_administration": [
        {"name": "期刊名称", "issn": "ISSN号"},
        # ...
    ],
    "public_policy": [
        {"name": "期刊名称", "issn": "ISSN号"},
        # ...
    ],
    "political_science": [
        {"name": "期刊名称", "issn": "ISSN号"},
        # ...
    ],
    "china_studies": [
        {"name": "期刊名称", "issn": "ISSN号"},
        # ...
    ]
}
```

### 修改定时规则

编辑 `.github/workflows/crawl.yml`：

```yaml
schedule:
  - cron: '0 16 * * *'  # 每天 UTC 16:00（北京时间 00:00）
```

Cron 表达式参考：
- `0 16 * * *` - 每天 UTC 16:00（北京时间 00:00）
- `0 0 * * *` - 每天 UTC 00:00（北京时间 08:00）
- `0 */6 * * *` - 每6小时
- `0 0 * * 1` - 每周一 00:00

---

## 🔧 本地开发

```bash
# 1. 克隆仓库
git clone https://github.com/你的用户名/仓库名.git
cd 仓库名

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install requests

# 4. 运行爬虫
python scripts/crawler.py --days 7

# 5. 导出数据
python scripts/export.py

# 6. 本地预览
python -m http.server 8000
# 访问 http://localhost:8000
```

---

## 📝 数据来源

- **OpenAlex API** (https://openalex.org/)
- 免费、开源、无API Key限制
- 支持polite pool（通过邮箱标识提升速率限制）

---

## 🔄 更新日志

### 2025-04-11 全面升级
- ✅ 重构收藏系统：删除红心，改为书签+拖拽文件夹管理
- ✅ 新增政治学(POL)和中国研究(CHINA)两大模块
- ✅ 期刊导航优化：表格布局+领域筛选+实时搜索
- ✅ 搜索增强：支持多字段组合检索
- ✅ 新增研究主题河流图（ECharts ThemeRiver）
- ✅ UI全面升级：对标Nature/Science学术风格

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 许可证

MIT License

---

Made with ❤️ for Research Atlas Scholars
