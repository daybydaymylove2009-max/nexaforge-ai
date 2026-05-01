import json
import os
from typing import Dict, List, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DataAnalyzer")

class DataHealthChecker:
    """智能数据体检与修复专家"""
    
    def __init__(self, dataset_path: str):
        self.dataset_path = dataset_path
        self.stats = {
            "total_samples": 0,
            "corrupted_samples": 0,
            "fixed_samples": 0,
            "empty_fields": 0,
            "avg_instruction_len": 0,
            "avg_output_len": 0,
            "max_len": 0,
            "is_healthy": True
        }
        self.healthy_data = []

    def check_and_fix(self) -> Dict:
        """执行全方位数据体检"""
        logger.info(f"🔍 正在对数据集 {self.dataset_path} 进行智能分析...")
        
        if not os.path.exists(self.dataset_path):
            self.stats["is_healthy"] = False
            return self.stats

        try:
            with open(self.dataset_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            logger.warning("⚠️ 检测到编码问题，尝试使用 latin-1 强制读取并修复...")
            with open(self.dataset_path, 'r', encoding='latin-1') as f:
                lines = f.readlines()

        fixed_lines = []
        total_instr_len = 0
        total_out_len = 0

        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            self.stats["total_samples"] += 1
            
            try:
                # 尝试标准解析
                sample = json.loads(line)
            except json.JSONDecodeError:
                # 尝试简单自动修复逻辑
                self.stats["corrupted_samples"] += 1
                sample = self._attempt_fix_json(line)
                if sample:
                    self.stats["fixed_samples"] += 1
                    logger.info(f"   ✅ 已自动修复第 {i+1} 行的数据格式")
                else:
                    logger.warning(f"   ❌ 无法修复第 {i+1} 行数据，已跳过")
                    continue

            # 字段检查与补全
            if "instruction" not in sample:
                sample["instruction"] = "请根据上下文回答问题"
                self.stats["empty_fields"] += 1
            
            if "output" not in sample or not sample["output"]:
                logger.warning(f"   ⚠️ 第 {i+1} 行输出为空，已跳过")
                self.stats["empty_fields"] += 1
                continue

            # 统计指标
            instr_len = len(str(sample.get("instruction", "")))
            out_len = len(str(sample.get("output", "")))
            total_instr_len += instr_len
            total_out_len += out_len
            self.stats["max_len"] = max(self.stats["max_len"], instr_len + out_len)

            self.healthy_data.append(sample)

        # 计算平均值
        if self.stats["total_samples"] > 0:
            self.stats["avg_instruction_len"] = total_instr_len / self.stats["total_samples"]
            self.stats["avg_output_len"] = total_out_len / self.stats["total_samples"]

        # 健康评估
        if self.stats["corrupted_samples"] / max(1, self.stats["total_samples"]) > 0.3:
            self.stats["is_healthy"] = False
            logger.error("❌ 数据集质量过低，损坏样本超过 30%")

        return self.stats

    def _attempt_fix_json(self, line: str) -> Optional[Dict]:
        """尝试修复一些简单的 JSON 错误（如未闭合的括号）"""
        line = line.strip()
        if not line.startswith("{"): line = "{" + line
        if not line.endswith("}"): line = line + "}"
        
        try:
            return json.loads(line)
        except:
            return None

    def save_cleaned_data(self, output_path: str = None):
        """保存清洗后的数据集"""
        target = output_path or self.dataset_path.replace(".jsonl", "_cleaned.jsonl")
        with open(target, 'w', encoding='utf-8') as f:
            for item in self.healthy_data:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        logger.info(f"✨ 清洗后的数据集已保存至: {target}")
        return target

    def get_smart_advice(self) -> List[str]:
        """生成针对数据的智能建议"""
        advice = []
        if self.stats["max_len"] > 2048:
            advice.append("💡 数据预警: 检测到超长文本样本，系统将自动进行截断，建议手动检查数据分布。")
        if self.stats["total_samples"] < 10:
            advice.append("💡 训练建议: 数据量非常少，模型可能会产生严重的过拟合。")
        if self.stats["fixed_samples"] > 0:
            advice.append(f"✅ 系统已自动修复 {self.stats['fixed_samples']} 条格式错误的样本。")
        return advice
