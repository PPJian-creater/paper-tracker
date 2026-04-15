# 📚 Research Atlas - 学术文献追踪系统

基于 GitHub Actions 自动爬取、GitHub Pages 免费托管的 SSCI 学术文献追踪平台。

🌐 **在线访问**: https://你的用户名.github.io/仓库名/

---

## ✨ 核心特性

| 特性 | 说明 |
|------|------|
| 🆓 **完全免费** | GitHub Actions + Pages 零成本部署，无服务器费用 |
| 🔄 **自动更新** | 每天北京时间 00:00 自动爬取最新文献 |
| 📚 **四大领域** | 公共行政(PA) + 公共政策(PP) + 政治学(POL) + 中国研究(CHINA) |
| 🗂️ **智能收藏** | 书签收藏 + 文件夹分类 + 拖拽管理 + 导入导出 |
| 🔍 **高级搜索** | 多字段组合检索（标题/摘要/作者/关键词） |
| 📊 **可视化** | 热词分析 + 发文趋势 + 词云 |
| 🎨 **现代UI** | 毛玻璃拟态设计 + 学术风格配色 |
| 📱 **响应式** | 完美适配手机/平板/电脑 |
| 🌐 **全球加速** | jsDelivr CDN 加速访问 |

---

## 📚 覆盖期刊（86本SSCI）

| 领域 | 数量 | 代表期刊 |
|------|------|----------|
| 公共行政 (PA) | 20本 | PAR, PA, JPART, Governance... |
| 公共政策 (PP) | 23本 | Policy Sciences, JPAM, JPP... |
| 政治学 (POL) | 36本 | APSR, AJPS, JOP, IO, ISQ... |
| 中国研究 (CHINA) | 7本 | The China Quarterly, JCC... |

---

## 🚀 快速开始

### 1. Fork 仓库

点击右上角 **Fork** 按钮，等待 Fork 完成。

### 2. 配置 Secrets

进入你 Fork 的仓库 → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

| Name | Value |
|------|-------|
| `EMAIL` | 你的邮箱（用于OpenAlex API标识） |

### 3. 启用 GitHub Pages

**Settings** → **Pages** → **Source** 选择 **GitHub Actions** → 保存

### 4. 首次爬取数据

**Actions** 标签 → 选择 **每日爬取SSCI文献** → **Run workflow** → 选择 `initial` 模式 → 等待10-20分钟

### 5. 访问网站

```
https://你的用户名.github.io/仓库名/
```

---

## 📁 项目结构

```
.
├── .github/workflows/
│   └── crawl.yml          # GitHub Actions 定时任务
├── data/
│   ├── papers.json        # 文献数据（自动生成）
│   └── data.json          # 前端数据（自动生成）
├── scripts/
│   ├── crawler.py         # 爬虫脚本（4大模块）
│   └── export.py          # 数据导出
├── index.html             # 前端页面
└── README.md              # 本文件
```

---

## 🎯 功能模块

### 1️⃣ 发现模块
- **最新更新** - 查看最新收录的文献，支持查看前一天数据
- **热词分析** - 近90天标题热词 + 摘要热词，支持分领域筛选
- **发文趋势** - 近30天文献发表趋势，支持分模块展示
- **精彩推荐** - 随机推荐优质文献

### 2️⃣ 四大领域 (PA/PP/POL/CHINA)
- 期刊筛选 + 时间范围筛选
- 文献卡片（分类/标题/作者/摘要/关键词）
- 书签收藏（点击选择文件夹）

### 3️⃣ 收藏模块
- **文件夹管理** - 新建/删除/重命名
- **书签收藏** - 点击书签选择目标文件夹
- **批量操作** - 多选删除
- **导入导出** - JSON格式，支持跨设备迁移

### 4️⃣ 期刊导航
- 86本期刊已验证官网链接
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

### 修改邮箱

编辑 `scripts/crawler.py`：

```python
EMAIL = "your-email@example.com"
```

### 修改期刊列表

编辑 `scripts/crawler.py` 中的 `JOURNALS_CONFIG`。

---

## 🔧 本地开发

```bash
# 克隆仓库
git clone https://github.com/你的用户名/仓库名.git
cd 仓库名

# 安装依赖
pip install requests

# 运行爬虫
python scripts/crawler.py --days 7

# 导出数据
python scripts/export.py

# 本地预览
python -m http.server 8000
# 访问 http://localhost:8000
```

---

## 📝 数据来源

- **OpenAlex API** (https://openalex.org/)
- 免费、开源、无API Key限制
- 支持 polite pool 提升速率限制

---

## 🔄 更新日志

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
