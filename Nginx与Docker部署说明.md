# Nginx 与 Docker 部署说明

## 1. 部署结构
本项目采用前后端分离部署：

- Windows：运行 MySQL、WeBASE、FISCO-BCOS 节点、Nginx
- Linux：使用 Docker 运行 Flask 后端
- 前端：由 Windows 上的 Nginx 托管 `power/dist`

## 2. Nginx 作用
Nginx 部署在 Windows，负责：

- 托管前端静态资源
- 处理 Vue Router history 刷新
- 将后端接口请求代理到 Linux Docker 中的 Flask 服务

### 建议代理路径
- `/api/` -> `http://<LINUX_BACKEND_IP>:5000`
- `/login` -> `http://<LINUX_BACKEND_IP>:5000`
- `/register` -> `http://<LINUX_BACKEND_IP>:5000`
- `/user/` -> `http://<LINUX_BACKEND_IP>:5000`

### 前端静态资源目录
- `<FRONTEND_DIST_PATH>`

### 关键配置点
- `root <FRONTEND_DIST_PATH>;`
- `try_files $uri $uri/ /index.html;`
- `proxy_pass http://<LINUX_BACKEND_IP>:5000;`

## 3. Docker 作用
Docker 部署在 Linux，仅负责运行后端 Flask 服务。

### 当前设计
- 容器内运行 Python 后端
- 后端通过环境变量连接 Windows 上的 MySQL
- 容器内关闭链同步线程，避免依赖 Windows 上的 WeBASE、Selenium、SDK 路径

### 关键环境变量
- `FLASK_RUN_HOST=0.0.0.0`
- `FLASK_RUN_PORT=5000`
- `DISABLE_SYNC_WORKER=1`
- `MYSQL_HOST=<Windows 局域网 IP>`
- `MYSQL_PORT=3306`
- `MYSQL_USER=<MySQL 用户名>`
- `MYSQL_PASSWORD=<MySQL 密码>`
- `MYSQL_DATABASE=power`

## 4. Docker 文件位置
后端目录建议保留：

- `power_bank/Dockerfile`
- `power_bank/docker-compose.backend.yml`
- `power_bank/.dockerignore`

Nginx 配置文件维护在 Windows 安装目录：

- `<NGINX_CONF_PATH>`

## 5. 启动顺序
### Windows
1. 启动 MySQL
2. 启动 FISCO-BCOS 节点
3. 启动 WeBASE
4. 在 `power` 目录执行 `npm run build`
5. 启动或重载 Nginx

### Linux
1. 上传 `power_bank` 后端目录
2. 编辑 `docker-compose.backend.yml`
3. 执行 `docker compose -f docker-compose.backend.yml up -d --build`

## 6. 访问链路
浏览器统一访问 Windows Nginx：

- `http://<WINDOWS_HOST>:80/`

链路如下：

- 浏览器 -> Windows Nginx
- Windows Nginx -> Linux Docker Flask
- Linux Docker Flask -> Windows MySQL

## 7. 说明
该方案的核心是将区块链相关组件保留在 Windows 环境，将业务后端服务独立运行在 Linux Docker 中，便于后续部署与扩展。

