# Zhi-Zip Web

> 🗜️ 在线压缩 / 解压工具 · Flask + FastAPI + Celery + Redis  


[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-3.0%2B-black.svg)](https://flask.palletsprojects.com/)
[![FastAPI](https://img.shields.io/badge/fastapi-0.110%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Celery](https://img.shields.io/badge/celery-5.3%2B-37814A.svg)](https://docs.celeryq.dev/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](./LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](./CONTRIBUTING.md)

---

## ✨ 特性

- 📦 **多文件 / 文件夹递归压缩**：保留相对目录结构，解压后层次不乱
- 🛡️ **防覆盖**：上传重名自动追加 `_1`、`_2`；zip 内条目名使用相对路径，天然隔离
- ⚡ **异步任务**：Celery + Redis，上传即返回 `task_id`，不阻塞页面
- 📊 **实时进度**：前端每 800ms 轮询 `/api/tasks/{id}`，任务进度一目了然
- 🔒 **安全解压**：`Path.relative_to()` 校验每个成员路径，杜绝 Zip Slip 穿越
- 🧩 **框架解耦**：压缩 / 解压核心逻辑集中在 `app/core/`，Flask 与 FastAPI 均不直接调用 `zipfile`
- 🪟 **Windows 友好**：Celery 使用 `--pool=solo`，无需 WSL 也能跑
- 📄 **自带 Swagger**：`http://localhost:8000/docs` 一键调试 API



---

## 🧱 技术栈

| 层 | 技术 | 端口 |
|---|---|---|
| 页面 | Flask + Jinja2 | `5000` |
| API | FastAPI + Uvicorn | `8000` |
| 任务 | Celery Worker（`--pool=solo`） | — |
| 队列 / 结果 | Redis | `6379` |

---

## 🚀 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/<your-name>/zhi-zip-web.git
cd zhi-zip-web
```

### 2. 创建虚拟环境并安装依赖

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. 启动 Redis（Windows 三选一）

| 方式 | 命令 | 说明 |
|---|---|---|
| **Memurai（推荐）** | 安装 MSI 后：`memurai-cli ping` | 原生 Windows 服务，返回 `PONG` 即成功 |
| WSL2 | `sudo service redis-server start` | Linux 子系统内跑官方 Redis |
| Docker | `docker run -d --name redis-zhi -p 6379:6379 redis:7-alpine` | 端口映射到本机 6379 |

### 4. 启动服务（需要 4 个终端）

```bash
# 终端 1 · Celery Worker
python run_worker.py

# 终端 2 · FastAPI
python run_fastapi.py

# 终端 3 · Flask 页面
python run_flask.py
```

打开：
- 页面：<http://localhost:5000>
- API 文档：<http://localhost:8000/docs>

Worker 日志出现 `celery@<host> ready.` 即表示一切就绪。

---

## 📁 目录结构

```
zhi-zip-web/
├── app/
│   ├── config.py                    # 路径、Redis、FastAPI 地址
│   ├── core/                        # 与框架无关的核心逻辑
│   │   ├── archiver.py              # zip 压缩（带进度回调）
│   │   └── safe_extract.py          # 防 Zip Slip 解压
│   ├── tasks/                       # Celery 任务
│   ├── fastapi_api/                 # REST API
│   └── flask_ui/                    # 页面 + 模板
├── storage/
│   ├── uploads/                     # 上传临时文件（按任务 UUID 分目录）
│   └── outputs/                     # 压缩 / 解压产物
├── run_flask.py
├── run_fastapi.py
├── run_worker.py
├── requirements.txt
└── README.md
```

---

## 🧪 API 概览

| 方法 | 路径 | 说明 |
|---|---|---|
| `POST` | `/api/compress/` | 创建压缩任务（`multipart/form-data`，字段 `files` 可多个） |
| `POST` | `/api/decompress/` | 创建解压任务（`file`，仅 `.zip`） |
| `GET` | `/api/tasks/{task_id}` | 查询状态 / 进度 / 结果 |
| `GET` | `/api/download/{name}` | 下载产物（限 `storage/outputs/`） |

示例：

```bash
# 压缩
curl -X POST http://localhost:8000/api/compress/ \
  -F "files=@a.txt" -F "files=@b.txt" -F "output_name=archive.zip"

# 查询
curl http://localhost:8000/api/tasks/<task_id>
```

```json
{ "task_id": "…", "status": "PROGRESS", "percent": 42, "current": "docs/a.txt" }
```

完整交互式文档见 Swagger：<http://localhost:8000/docs>。

---

## ⚙️ 配置项

均通过环境变量覆盖，集中在 `app/config.py`：

| 变量 | 默认值 | 说明 |
|---|---|---|
| `REDIS_URL` | `redis://localhost:6379/0` | Celery Broker + Result Backend |
| `FASTAPI_BASE_URL` | `http://localhost:8000` | Flask 页面调用 API 的地址 |



---

## ❓ 常见问题

<details>
<summary><b>Worker 报 <code>Error 10061 connecting to localhost:6379</code></b></summary>

Redis 未启动。按「快速开始」第 3 步启动后，在 Worker 终端 `Ctrl+C` 重启 `python run_worker.py`。
</details>

<details>
<summary><b>解压报「不安全的路径: xxx」</b></summary>

请确保 `app/core/safe_extract.py` 使用 `Path.relative_to()` 判断越界，而非字符串前缀比较——Windows 路径分隔符为 `\`，字符串比较会误判。
</details>

<details>
<summary><b>修改代码后 Celery 不生效</b></summary>

Celery Worker **不会热重载**，修改 `app/tasks/` 或 `app/core/` 后必须重启 `python run_worker.py`。FastAPI 已开启 `reload=True`。
</details>

<details>
<summary><b>Windows 下 Celery 卡死 / PermissionError</b></summary>

`run_worker.py` 已使用 `--pool=solo` + `FORKED_BY_MULTIPROCESSING=1`。若仍不稳定，建议 Worker 与 Redis 一并运行在 WSL2 或 Docker 中。
</details>

---

## ⚠️ 已知限制

- 解压目前**仅支持 `.zip`**
- 上传文件落盘 `storage/`，暂无容量上限与自动清理
- 任务状态在 Redis 中保留 1 小时（`result_expires=3600`）
- 单机部署，未做用户隔离与鉴权

---

## 📄 License

本项目基于 [MIT License](./LICENSE) 开源。

---

## 🙏 致谢

- 框架：[Flask](https://flask.palletsprojects.com/) · [FastAPI](https://fastapi.tiangolo.com/) · [Celery](https://docs.celeryq.dev/)
- 队列：[Redis](https://redis.io/) / [Memurai](https://www.memurai.com/)

---

<p align="center">
  <sub>如果这个项目对你有帮助，欢迎 ⭐ Star 支持一下！</sub>
</p>
