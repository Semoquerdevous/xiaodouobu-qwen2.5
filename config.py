import os

# 自动获取项目目录，换电脑无需修改路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "Qwen2.5-Omni-7B-FP16")

# API 密钥
API_KEY = "rilab-xiaodouobu-2024"

# 端口
API_PORT = 8000
FRONTEND_PORT = 7860