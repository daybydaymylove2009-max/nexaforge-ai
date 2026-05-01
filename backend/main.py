import json
import asyncio
import sys
import os
import multiprocessing

# 强制设置 UTF-8
os.environ["PYTHONIOENCODING"] = "utf-8"

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# 尝试导入本地模块
try:
    from .train_executor import run_fine_tune
except ImportError:
    from train_executor import run_fine_tune

try:
    from smart_trainer import SmartTrainer
except ImportError:
    # 兼容性导入
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from smart_trainer import SmartTrainer

app = FastAPI(title="智核万炼 NexaForge API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class TrainingManager:
    def __init__(self):
        self.process = None
        self.queue = multiprocessing.Queue()
        self.is_running = False

    def start_training(self, config):
        if self.is_running: return False
        self.queue = multiprocessing.Queue()
        self.process = multiprocessing.Process(target=run_fine_tune, args=(config, self.queue))
        self.process.start()
        self.is_running = True
        return True

    def stop_training(self):
        if self.process and self.process.is_alive():
            self.process.terminate()
        self.is_running = False

manager = TrainingManager()

# --- 企业级 API 路由实现 ---

@app.get("/api/health")
async def health():
    return {"status": "ok", "message": "NexaForge Engine Running"}

@app.get("/api/env/scan")
async def scan_env():
    """
    [核心逻辑实现]
    物理扫描系统硬件并生成企业级评估报告
    """
    try:
        trainer = SmartTrainer(auto_mode=True)
        # 获取最底层的 GPU 信息
        gpu_info = trainer.analyzer.get_gpu_info()
        # 获取智核推荐参数
        optimal_args, notes = trainer.adaptive_config.precompute_optimal_args()
        
        vram = gpu_info["vram_total_gb"] if gpu_info else 0
        if vram >= 80: level = "大师级 (Master-H100)"
        elif vram >= 40: level = "旗舰级 (A100)"
        elif vram >= 24: level = "专家级 (Workstation)"
        elif vram >= 12: level = "专业级 (High-End)"
        elif vram > 0: level = "入门级 (Entry)"
        else: level = "学习级 (CPU)"
        
        return {
            "gpu": gpu_info["name"] if gpu_info else "CPU Cluster",
            "vram": f"{gpu_info['vram_total_gb']}GB" if gpu_info else "N/A",
            "cap": gpu_info["compute_capability"] if gpu_info else "N/A",
            "count": gpu_info["count"] if gpu_info else 0,
            "level": level,
            "notes": notes
        }
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return {"error": str(e)}, 500

class TrainConfig(BaseModel):
    dataset_path: str = "dataset.jsonl"
    epochs: int = 3
    learning_rate: float = 2e-4
    use_cpu: bool = False
    batch_size: int = 2
    is_smart: bool = True
    lora_r: int = 16

@app.post("/api/train/start")
async def start_train(config: TrainConfig):
    success = manager.start_training(config.dict())
    return {"message": "启动成功"} if success else ({"message": "已有任务运行"}, 400)

@app.post("/api/train/stop")
async def stop_train():
    manager.stop_training()
    return {"message": "已停止"}

@app.get("/api/train/stream")
async def stream_progress():
    async def event_generator():
        while True:
            try:
                if not manager.queue.empty():
                    data = manager.queue.get_nowait()
                    yield f"data: {json.dumps(data)}\n\n"
                    if data.get("status") in ["completed", "error"]:
                        manager.is_running = False
                        break
                else:
                    await asyncio.sleep(0.5)
                    if not manager.is_running: break
            except: break
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/api/data/upload")
async def upload_data(file: UploadFile = File(...)):
    file_path = f"./{file.filename}"
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    return {"filename": file.filename, "path": file_path}

if __name__ == "__main__":
    import uvicorn
    # 强制在 8000 端口启动
    uvicorn.run(app, host="0.0.0.0", port=8000)
