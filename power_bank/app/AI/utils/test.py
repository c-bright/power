from sentence_transformers import SentenceTransformer

# 使用本地缓存路径
model = SentenceTransformer('E:/power_bank/power_bank/app/AI/my_model_cache/models--BAAI--bge-small-zh-v1.5/snapshots/7999e1d3359715c523056ef9478215996d62a620')
print(model.encode("你好").shape)