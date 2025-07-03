# app/services/genconvit_loader.py

import os
from app.genconvit.model.config import load_config
from app.genconvit.model.pred_func import load_genconvit

# Cấu hình model
config = load_config()
net = "genconvit"
fp16 = False  # hoặc True nếu bạn dùng float16
ed_weight = "genconvit_ed_inference"
vae_weight = "genconvit_vae_inference"

# Load model 1 lần
print("🔄 Loading GenConViT model once...")
model = load_genconvit(config, net, ed_weight, vae_weight, fp16)
print("✅ GenConViT model loaded.")
