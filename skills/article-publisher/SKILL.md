---
name: article-publisher
description: 文章自动发布技能。将本地 Markdown 文章发布到自建网站，自动上传封面图到 R2 对象存储并替换链接。当用户需要发布文章、上传封面、批量发布、管理发布状态时使用。支持：(1) 单篇/批量发布 MD 文章；(2) 自动上传封面图到 Cloudflare R2；(3) 自动替换 MD 里的本地图片链接为云端链接；(4) 发布状态跟踪，避免重复发布。触发词：发布文章、上传封面、发布到网站、批量发布、articles。
---

# 文章自动发布技能

## 核心功能

将本地 Markdown 文章自动发布到你的网站，流程：

1. 扫描指定目录下的 MD 文件
2. 上传同名封面图（.jpg）到 Cloudflare R2
3. 替换 MD 里的本地图片链接为 R2 云端链接
4. 调用网站发布 API 发布文章
5. 记录发布状态，避免重复发布

## 第一次使用：配置

**敏感信息不硬编码在技能里。** 第一次运行时，向用户收集以下配置，保存到本地配置文件 `~/.config/article-publisher/config.json`：

### 需要收集的配置项：

**网站发布配置：**
- `publish_api_url`：发布 API 地址（如 `http://your-site.com/articles/api/create/`）
- `publish_token`：发布接口的 Token（X-Internal-Token）

**R2 对象存储配置：**
- `r2_endpoint`：R2 S3 API 地址（如 `https://xxxx.r2.cloudflarestorage.com`）
- `r2_access_key`：Access Key ID
- `r2_secret_key`：Secret Access Key
- `r2_bucket`：Bucket 名称
- `r2_public_base`：公开访问 URL 前缀（如 `https://pub-xxxx.r2.dev`）
- `r2_key_prefix`：对象前缀（默认 `covers`）

**文章目录配置：**
- `articles_dir`：MD 文件所在目录

### 配置文件格式（config.json）：

```json
{
  "publish_api_url": "http://your-site.com/articles/api/create/",
  "publish_token": "your-token-here",
  "r2_endpoint": "https://xxxx.r2.cloudflarestorage.com",
  "r2_access_key": "your-access-key",
  "r2_secret_key": "your-secret-key",
  "r2_bucket": "your-bucket-name",
  "r2_public_base": "https://pub-xxxx.r2.dev",
  "r2_key_prefix": "covers",
  "articles_dir": "/path/to/your/articles"
}
```

## 工作流程

### 第一步：检查配置

运行前先检查配置文件是否存在且完整。如果缺失，向用户收集配置并保存。

### 第二步：扫描文章

扫描 `articles_dir` 下的所有 `.md` 文件。

### 第三步：检查发布状态

读取状态文件（`articles_status.json`），跳过已经发布过的文章。

状态文件格式：
```json
{
  "filename.md": {
    "status": "published",
    "article_id": 123,
    "article_title": "文章标题",
    "published_at": "2026-09-25T10:00:00"
  }
}
```

### 第四步：上传封面图

找到同名的 `.jpg` 文件，上传到 R2：
- 上传路径：`{r2_key_prefix}/{filename}.jpg`
- 返回公开 URL：`{r2_public_base}/{r2_key_prefix}/{filename}.jpg`

### 第五步：替换图片链接

把 MD 里第一处图片链接的本地路径，替换成 R2 云端 URL。

### 第六步：调用发布 API

POST 请求发布 API：
- Headers：`X-Internal-Token: {publish_token}`
- Body：`{"title": "文章标题", "content": "完整MD内容"}`

### 第七步：更新状态

发布成功后，更新状态文件。

## 关键原则

1. **敏感信息不硬编码**：所有密钥、Token 都通过配置文件读取，不写在代码里
2. **配置文件本地化**：保存在用户目录下，不跟着技能走
3. **幂等性**：已发布的文章不会重复发布
4. **失败可重试**：发布失败的文章下次会重新尝试

## 脚本位置

发布脚本：`scripts/publish.py`

运行方式：
```bash
python3 scripts/publish.py
```

## 输出

发布完成后，输出：
- 扫描到多少篇文章
- 新发布了多少篇
- 跳过了多少篇（已发布）
- 每篇的发布结果（成功/失败）
