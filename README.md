# 📚 公管SSCI期刊文献追踪 - GitHub Pages版

基于 GitHub Actions 自动爬取、GitHub Pages 免费部署的文献追踪系统。

## ✨ 特性

- 🆓 **完全免费** - GitHub Actions + Pages 零成本
- 🔄 **自动更新** - 每天自动爬取新文献
- 🌐 **全球访问** - jsDelivr CDN 加速
- 📱 **响应式设计** - 支持手机/平板/电脑
- 💾 **本地收藏** - 使用浏览器 localStorage
- 🔍 **全文搜索** - 支持标题/摘要/关键词搜索
- 📊 **数据可视化** - 趋势图、词云

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
4. 选择 `initial` 模式（爬取最近30天）
5. 等待完成（约 5-10 分钟）

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
│   ├── crawler.py          # 爬虫脚本
│   └── export.py           # 数据导出脚本
├── index.html              # 前端页面
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
    ]
}
```

### 修改定时规则

编辑 `.github/workflows/crawl.yml`：

```yaml
schedule:
  - cron: '0 0 * * *'  # 每天 UTC 00:00（北京时间 08:00）
```

Cron 表达式参考：
- `0 0 * * *` - 每天 00:00
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

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 许可证

MIT License

---

Made with ❤️ for Public Administration & Public Policy Scholars
