import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import static_ffmpeg
static_ffmpeg.add_paths()
import torch
from transformers import Qwen2_5OmniForConditionalGeneration, AutoProcessor, BitsAndBytesConfig
from qwen_omni_utils import process_mm_info
from config import MODEL_PATH

print("正在加载模型，请稍候...")

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
)

processor = AutoProcessor.from_pretrained(MODEL_PATH)
model = Qwen2_5OmniForConditionalGeneration.from_pretrained(
    MODEL_PATH,
    quantization_config=bnb_config,
    device_map="cuda",
    ignore_mismatched_sizes=True,
)
model.eval()
torch.cuda.empty_cache()

print("模型加载完成！")


def chat(messages: list, max_new_tokens: int = 512,
         temperature: float = 0.7, top_p: float = 0.9) -> str:
    text = processor.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    audios, images, videos = process_mm_info(
        messages,
        use_audio_in_video=True
    )
    inputs = processor(
        text=text,
        images=images if images else None,
        audio=audios if audios else None,
        videos=videos if videos else None,
        return_tensors="pt",
        padding=True,
    ).to("cuda")

    with torch.no_grad():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            do_sample=True,
            return_audio=False,  # 关闭语音输出，节省显存
        )

    # Qwen2.5-Omni generate 返回元组时取第一个元素
    if isinstance(output_ids, tuple):
        output_ids = output_ids[0]

    new_ids = output_ids[:, inputs["input_ids"].shape[1]:]
    response = processor.batch_decode(
        new_ids, skip_special_tokens=True
    )[0]
    torch.cuda.empty_cache()
    return response