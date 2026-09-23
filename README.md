# 🫘 小豆包 · 多模态聊天助手

> 制作人：汤礼泓 

---

## 硬件需求

- GPU：NVIDIA 独立显卡，显存 8GB 及以上（开发环境：RTX 5060 Laptop 8GB）
- 内存：16GB+
- 存储：25GB+（模型约 16GB + 环境约 5GB）
- 系统：Windows 11

---

## 环境配置

### 第一步：创建虚拟环境
```bash
conda create -n xiaodouobu python=3.10 -y
conda activate xiaodouobu
```

### 第二步：安装 PyTorch

先在终端运行以下命令查看你的 CUDA 版本：
```bash
nvidia-smi
```

看输出右上角的 `CUDA Version`，然后选择对应命令安装：
```bash
# CUDA 12.8（RTX 50系列）
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128

# CUDA 12.4
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# CUDA 12.1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# CUDA 11.8
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# 无显卡（仅 CPU，速度极慢不推荐）
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

### 第三步：安装其余依赖
```bash
pip install -r requirements.txt
```

### 第四步：下载模型（约 16GB，需要等待）

进入项目目录后执行：
```bash
cd 你的项目目录
modelscope download --model Qwen/Qwen2.5-Omni-7B --local_dir ./models/Qwen2.5-Omni-7B-FP16
```

> 💡 下载过程中如果中断，直接重新运行同一条命令即可，ModelScope 支持断点续传。

### 第五步：确认配置文件

本项目的 `config.py` 已使用**自动路径检测**，无需手动修改路径，模型只要放在项目目录下的 `models/Qwen2.5-Omni-7B-FP16` 即可自动识别。

如需修改 API 密钥，打开 `config.py` 修改：
```python
API_KEY = "rilab-xiaodouobu-2024"
```

---

## 启动方式

双击 `start.bat`，会自动检测 Conda 路径并依次启动后端、前端和公网隧道（如有 cloudflared.exe）。

或手动启动（推荐，便于查看报错）：
```bash
# 终端一：启动后端（设置显存优化环境变量）
conda activate xiaodouobu
cd 项目目录
set PYTORCH_ALLOC_CONF=expandable_segments:True
uvicorn backend.api:app --host 0.0.0.0 --port 8000
```

等待后端窗口出现以下内容后，再开新窗口启动前端：
```
模型加载完成！
Uvicorn running on http://0.0.0.0:xxxx
```
```bash
# 终端二：启动前端
conda activate xiaodouobu
cd 项目目录
python frontend/app.py
```

启动成功后浏览器访问：
```
http://localhost:xxxx
```

> ⚠️ 必须等后端窗口出现"模型加载完成"后再启动前端，否则前端无法连接后端。

> 💡 `PYTORCH_ALLOC_CONF=expandable_segments:True` 可减少显存碎片，在显存较小的设备上有助于避免 OOM 错误。

---

## 公网访问

如需公网访问，将 `cloudflared.exe` 放入项目根目录，启动后端和前端后执行：
```bash
cd 项目目录
.\cloudflared.exe tunnel --url http://localhost:7860
```

会输出类似：
```
Your quick Tunnel has been created! Visit it at:
https://xxxx-xxxx-xxxx.trycloudflare.com
```

将此链接分享给他人即可远程访问。双击 `start.bat` 会自动检测并启动隧道。

> ⚠️ 本机必须保持在线，关机或断网后链接立即失效。每次重启链接会变化。
如果想直接进行公网访问，可以联系我，我配置后会将临时链接给你。

---

## 在其他电脑上本地运行

### 我已经做的

将项目文件夹打包成 zip 发给对方（**不包含 models 文件夹**，模型太大了）。

### 使用者需要做的

**第一步：** 解压项目文件夹

**第二步：** 安装 Miniconda（若未安装）：https://docs.conda.io/en/latest/miniconda.html

**第三步：** 按照上方【环境配置】第一步到第三步依次执行

**第四步：** 按照上方【环境配置】第四步下载模型，放入项目目录下的 `models/Qwen2.5-Omni-7B-FP16`

**第五步：** 直接双击 `start.bat` 启动，无需修改任何配置文件

> ⚠️ 注意：所有终端命令必须在项目目录下执行，否则会报 `No module named 'backend'` 错误。

> ⚠️ `start.bat` 会自动检测 Miniconda 和 Anaconda 的默认安装路径。若安装在非默认路径（如 D 盘），需手动修改 `start.bat` 第一行的 `CONDA_PATH`。

---

## 支持的输入类型

- 文字
- 图片（jpg / png）
- 音频（wav / mp3）
- 视频（mp4）
- 多轮对话（上下文记忆）

---

## 可调节推理参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| max_new_tokens | 最大生成长度 | 512 |
| Temperature | 越高越有创造性 | 0.7 |
| Top-P | 越低越保守 | 0.9 |

---

## 资源占用

| 项目 | 数值 |
|------|------|
| 显存占用 | 约 7-8GB（bitsandbytes NF4 量化） |
| 内存占用 | 约 4-6GB |
| 单次推理延迟 | 约 5-15 秒 |
| 模型大小 | 约 16GB（FP16 原始权重） |
| 语音输出 | 已关闭（受显存限制） |

---

## 项目结构
```
xiaodouobu/
├── backend/
│   ├── __init__.py
│   ├── inference.py      # 模型推理核心
│   └── api.py            # FastAPI 接口、鉴权、限流
├── frontend/
│   └── app.py            # Gradio 可视化页面
├── monitor/
│   ├── __init__.py
│   └── logger.py         # 日志、QPS、显存监控
├── models/               # 模型文件（需自行下载，不含在压缩包内）
├── logs/                 # 运行日志自动生成
├── config.py             # 统一配置文件（自动检测路径）
├── requirements.txt      # 依赖列表
├── start.bat             # 一键启动脚本（自动检测 Conda 路径）
├── cloudflared.exe       # 公网隧道工具（可选，需自行下载）
└── README.md             # 本文件
```

---

## 已知限制

- bitsandbytes NF4 量化会略微影响回答质量
- 8GB 显存下处理高分辨率视频较慢
- 单 GPU 不支持并发请求，同时只能处理一个对话
- 首次启动模型加载约需 1-2 分钟
- 受显存限制已关闭语音输出（return_audio=False），仅支持文字回复
- 公网链接每次重启会变化，本机关机后立即失效，如需直接访问公网，可以联系我

## 满足的加分项
- 提供了一个可视化前端页面，并可在页面中调节部分推理参数
- 支持公网访问（仅为临时网址）与简单监控（日志、QPS、显存）
- 能够接受多类型的数据输入（文字、图片、音频和视频）
