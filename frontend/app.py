import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gradio as gr
import requests
import pynvml
from config import API_KEY, API_PORT, FRONTEND_PORT

API_URL = f"http://localhost:{API_PORT}/chat"
MONITOR_URL = f"http://localhost:{API_PORT}/monitor"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

def build_message(text, image, audio, video):
    content = []
    if image:
        content.append({"type": "image", "image": image})
    if audio:
        content.append({"type": "audio", "audio": audio})
    if video:
        content.append({"type": "video", "video": video})
    if text:
        content.append({"type": "text", "text": text})
    return content


def respond(text, image, audio, video, history, state,
            max_tokens, temperature, top_p):
    if not text and not image and not audio and not video:
        return history, state, ""

    content = build_message(text, image, audio, video)
    state.append({"role": "user", "content": content})

    try:
        resp = requests.post(API_URL, headers=HEADERS, json={
            "messages": state,
            "max_new_tokens": int(max_tokens),
            "temperature": float(temperature),
            "top_p": float(top_p),
        }, timeout=120)
        reply = resp.json().get("response", "（无响应）")
        latency = resp.json().get("latency", "?")
    except Exception as e:
        reply = f"请求失败：{str(e)}"
        latency = "?"

    state.append({"role": "assistant", "content": reply})

    # 构建 Gradio messages 格式
    display = []
    for msg in state:
        role = msg["role"]
        content = msg["content"]
        if isinstance(content, list):
            text_parts = [c["text"] for c in content if c.get("type") == "text"]
            display_text = " ".join(text_parts) if text_parts else "[多媒体输入]"
        else:
            display_text = content
        display.append({"role": role, "content": display_text})

    return display, state, f"⏱ 本次推理耗时：{latency} 秒"


def get_monitor():
    try:
        resp = requests.get(MONITOR_URL, headers=HEADERS, timeout=5)
        data = resp.json()
        gpu_used = data.get("gpu_used_gb", "?")
        gpu_total = data.get("gpu_total_gb", "?")
        qps = data.get("qps", "?")
        pct = round(gpu_used / gpu_total * 100, 1) if isinstance(gpu_used, float) else "?"
        return (f"🖥 显存：{gpu_used} GB / {gpu_total} GB（{pct}%）\n"
                f"📊 QPS（近1分钟）：{qps} 次/秒")
    except Exception as e:
        return f"监控获取失败：{str(e)}"


def clear_history():
    return [], [], ""


with gr.Blocks(title="🫘 小豆包") as demo:

    gr.HTML("""
    <div style="background:#eef2ff;border-left:5px solid #4f6ef7;
                padding:12px 18px;border-radius:8px;margin-bottom:4px;">
        <h2 style="margin:0;color:#2d3a8c;">🫘 小豆包 · 多模态助手</h2>
        <p style="margin:4px 0 0 0;color:#555;">
            <b>制作人：</b>汤礼泓 &nbsp;｜&nbsp;
            <b>用途声明：</b>本项目仅用于 RI-LAB 招新任务，请勿用于其他用途。
        </p>
    </div>
    """)

    with gr.Row():
        with gr.Column(scale=3):
            chatbot = gr.Chatbot(height=480, label="对话窗口")  # 移除 type="messages"
            latency_info = gr.Textbox(
                label="推理信息", interactive=False, lines=1
            )
            txt = gr.Textbox(
                placeholder="输入文字消息，或上传图片/音频/视频后发送...",
                label="文字输入",
                lines=2
            )
            with gr.Row():
                img_input = gr.Image(
                    type="filepath", label="📷 图片"
                )
                audio_input = gr.Audio(
                    type="filepath", label="🎤 音频"
                )
                video_input = gr.Video(label="🎬 视频")
            with gr.Row():
                send_btn = gr.Button("发送 ✉", variant="primary", scale=3)
                clear_btn = gr.Button("清空对话 🗑", scale=1)

        with gr.Column(scale=1):
            gr.Markdown("### ⚙️ 推理参数")
            max_tokens = gr.Slider(
                64, 1024, value=512, step=64,
                label="最大生成长度 (max_new_tokens)"
            )
            temperature = gr.Slider(
                0.1, 2.0, value=0.7, step=0.1,
                label="Temperature（越高越有创造性）"
            )
            top_p = gr.Slider(
                0.1, 1.0, value=0.9, step=0.05,
                label="Top-P（越低越保守）"
            )

            gr.Markdown("### 📊 系统监控")
            monitor_out = gr.Textbox(
                label="显存 & QPS", lines=3, interactive=False
            )
            monitor_btn = gr.Button("🔄 刷新监控")

    state = gr.State([])

    send_btn.click(
        respond,
        inputs=[txt, img_input, audio_input, video_input,
                chatbot, state, max_tokens, temperature, top_p],
        outputs=[chatbot, state, latency_info]
    )
    txt.submit(
        respond,
        inputs=[txt, img_input, audio_input, video_input,
                chatbot, state, max_tokens, temperature, top_p],
        outputs=[chatbot, state, latency_info]
    )
    clear_btn.click(
        clear_history,
        outputs=[chatbot, state, latency_info]
    )
    monitor_btn.click(get_monitor, outputs=monitor_out)


if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=FRONTEND_PORT,
        share=False,
        theme=gr.themes.Soft(),
        allowed_paths=["C:/"],
    )