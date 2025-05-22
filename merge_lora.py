import argparse
from pathlib import Path
import torch
from safetensors.torch import save_file
from midi_model import MIDIModel, MIDIModelConfig
from peft import PeftModel

def main():
    parser = argparse.ArgumentParser(description='Merge LoRA adapter with base model')
    parser.add_argument('--base_model', type=str, required=True, 
                       help='Path to base model directory containing config.json')
    parser.add_argument('--lora_path', type=str, required=True,
                       help='Path to LoRA adapter directory')
    parser.add_argument('--output_dir', type=str, required=True,
                       help='Output directory for merged model')
    parser.add_argument('--dtype', type=str, default='fp32',
                       choices=['fp32', 'fp16', 'bf16'],
                       help='Output data type')
    args = parser.parse_args()

    # 加载基础模型配置
    config = MIDIModelConfig.from_pretrained(args.base_model)
    
    # 创建基础模型实例
    base_model = MIDIModel(config)
    
    # 加载并合并LoRA适配器
    model = PeftModel.from_pretrained(base_model, args.lora_path)
    merged_model = model.merge_and_unload()

    # 创建输出目录
    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 保存合并后的模型
    state_dict = merged_model.state_dict()
    save_file(state_dict, output_path / "model.safetensors")
    
    # 保存配置文件
    config.save_pretrained(output_path)
    
    print(f"Merged model saved to {output_path}")

if __name__ == "__main__":
    main()