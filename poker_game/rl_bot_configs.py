#!/usr/bin/env python3
"""
强化学习机器人配置集合
通过调整不同参数创建各种类型的机器人

这个文件展示了如何使用抽象基类和配置系统来创建不同风格的机器人：
- 通过调整学习参数来改变学习速度和探索策略
- 通过调整策略参数来改变游戏风格
- 通过开关高级功能来优化性能
"""

from .base_rl_bot import RLBotConfig

# ===== 预定义配置 =====

def get_original_config() -> RLBotConfig:
    """原版机器人配置 - 保守学习，基础功能"""
    return RLBotConfig(
        # 学习参数 (保守设置)
        epsilon=0.3,
        epsilon_decay=0.9995,
        epsilon_min=0.05,
        learning_rate=0.01,
        gamma=0.9,
        
        # 策略参数 (保守风格)
        aggression_threshold=0.7,
        max_bet_ratio=0.4,
        min_hand_strength_call=0.3,
        min_hand_strength_raise=0.65,
        all_in_threshold=0.9,
        
        # 高级功能 (基础功能)
        use_double_q_learning=False,
        use_experience_replay=False,
        use_enhanced_state=False,
        use_dynamic_actions=False,
        use_conservative_mode=False,
        
        memory_size=5000,
        replay_batch_size=16,
        snapshot_interval=50,
        model_name="rl_bot"
    )

def get_improved_config() -> RLBotConfig:
    """改进版机器人配置 - 激进学习，全部功能"""
    return RLBotConfig(
        # 学习参数 (激进设置)
        epsilon=0.35,
        epsilon_decay=0.9997,
        epsilon_min=0.08,
        learning_rate=0.015,
        gamma=0.95,
        
        # 策略参数 (激进风格)
        aggression_threshold=0.55,
        max_bet_ratio=0.6,
        min_hand_strength_call=0.2,
        min_hand_strength_raise=0.5,
        all_in_threshold=0.8,
        
        # 高级功能 (全部启用)
        use_double_q_learning=True,
        use_experience_replay=True,
        use_enhanced_state=True,
        use_dynamic_actions=True,
        use_conservative_mode=False,
        
        memory_size=10000,
        replay_batch_size=32,
        snapshot_interval=50,
        model_name="improved_rl_bot"
    )

def get_conservative_config() -> RLBotConfig:
    """保守版机器人配置 - 稳健学习，保守策略"""
    return RLBotConfig(
        # 学习参数 (平衡设置)
        epsilon=0.15,
        epsilon_decay=0.9998,
        epsilon_min=0.03,
        learning_rate=0.008,
        gamma=0.92,
        
        # 策略参数 (保守风格)
        aggression_threshold=0.6,
        max_bet_ratio=0.3,
        min_hand_strength_call=0.2,
        min_hand_strength_raise=0.65,
        all_in_threshold=0.85,
        
        # 高级功能 (选择性启用)
        use_double_q_learning=True,
        use_experience_replay=True,
        use_enhanced_state=True,
        use_dynamic_actions=True,
        use_conservative_mode=True,
        
        memory_size=8000,
        replay_batch_size=24,
        snapshot_interval=50,
        model_name="conservative_rl_bot"
    )

# ===== 特殊风格配置 =====

def get_aggressive_config() -> RLBotConfig:
    """超激进机器人配置 - 极度激进，高风险高回报"""
    return RLBotConfig(
        epsilon=0.4,           # 高探索率
        epsilon_decay=0.9995,
        epsilon_min=0.1,       # 保持较高探索
        learning_rate=0.02,    # 快速学习
        gamma=0.95,
        
        aggression_threshold=0.3,  # 很低的激进阈值
        max_bet_ratio=0.8,         # 允许大额下注
        min_hand_strength_call=0.1,
        min_hand_strength_raise=0.3,
        all_in_threshold=0.6,      # 容易全押
        
        use_double_q_learning=True,
        use_experience_replay=True,
        use_enhanced_state=True,
        use_dynamic_actions=True,
        
        memory_size=15000,
        replay_batch_size=64,
        model_name="aggressive_rl_bot"
    )

def get_tight_config() -> RLBotConfig:
    """超保守机器人配置 - 极度保守，只玩强牌"""
    return RLBotConfig(
        epsilon=0.1,           # 低探索率
        epsilon_decay=0.999,
        epsilon_min=0.01,      # 极低探索
        learning_rate=0.005,   # 缓慢学习
        gamma=0.9,
        
        aggression_threshold=0.8,  # 很高的激进阈值
        max_bet_ratio=0.2,         # 只允许小额下注
        min_hand_strength_call=0.4,
        min_hand_strength_raise=0.8,
        all_in_threshold=0.95,     # 几乎从不全押
        
        use_double_q_learning=True,
        use_experience_replay=True,
        use_enhanced_state=True,
        use_dynamic_actions=True,
        use_conservative_mode=True,
        
        memory_size=5000,
        replay_batch_size=16,
        model_name="tight_rl_bot"
    )

def get_bluff_config() -> RLBotConfig:
    """诈唬型机器人配置 - 善于诈唬和心理战"""
    return RLBotConfig(
        epsilon=0.25,
        epsilon_decay=0.9996,
        epsilon_min=0.05,
        learning_rate=0.012,
        gamma=0.93,
        
        aggression_threshold=0.4,  # 中等激进阈值
        max_bet_ratio=0.7,         # 允许较大下注
        min_hand_strength_call=0.15,
        min_hand_strength_raise=0.25,  # 低要求加注(诈唬)
        all_in_threshold=0.7,
        
        use_double_q_learning=True,
        use_experience_replay=True,
        use_enhanced_state=True,
        use_dynamic_actions=True,
        
        memory_size=12000,
        replay_batch_size=40,
        model_name="bluff_rl_bot"
    )

def get_adaptive_config() -> RLBotConfig:
    """适应型机器人配置 - 善于适应对手"""
    return RLBotConfig(
        epsilon=0.3,
        epsilon_decay=0.9999,      # 很慢的衰减，保持适应性
        epsilon_min=0.08,
        learning_rate=0.018,       # 较快学习以适应
        gamma=0.96,                # 重视长期回报
        
        aggression_threshold=0.6,
        max_bet_ratio=0.5,
        min_hand_strength_call=0.25,
        min_hand_strength_raise=0.55,
        all_in_threshold=0.85,
        
        use_double_q_learning=True,
        use_experience_replay=True,
        use_enhanced_state=True,
        use_dynamic_actions=True,
        
        memory_size=20000,         # 大容量记忆
        replay_batch_size=48,
        model_name="adaptive_rl_bot"
    )

# ===== 实验性配置 =====

def get_experimental_config() -> RLBotConfig:
    """实验性配置 - 用于测试新功能"""
    return RLBotConfig(
        epsilon=0.5,               # 高探索率
        epsilon_decay=0.999,
        epsilon_min=0.15,
        learning_rate=0.025,       # 高学习率
        gamma=0.98,                # 高折扣因子
        
        aggression_threshold=0.5,
        max_bet_ratio=0.6,
        min_hand_strength_call=0.2,
        min_hand_strength_raise=0.4,
        all_in_threshold=0.75,
        
        use_double_q_learning=True,
        use_experience_replay=True,
        use_enhanced_state=True,
        use_dynamic_actions=True,
        
        memory_size=25000,
        replay_batch_size=64,
        snapshot_interval=25,      # 更频繁的快照
        model_name="experimental_rl_bot"
    )

# ===== 配置字典 =====

PREDEFINED_CONFIGS = {
    'original': get_original_config,
    'improved': get_improved_config,
    'conservative': get_conservative_config,
    'aggressive': get_aggressive_config,
    'tight': get_tight_config,
    'bluff': get_bluff_config,
    'adaptive': get_adaptive_config,
    'experimental': get_experimental_config,
}

def get_config_by_name(name: str) -> RLBotConfig:
    """根据名称获取预定义配置"""
    if name in PREDEFINED_CONFIGS:
        return PREDEFINED_CONFIGS[name]()
    else:
        raise ValueError(f"未知配置名称: {name}. 可用配置: {list(PREDEFINED_CONFIGS.keys())}")

def create_custom_config(**kwargs) -> RLBotConfig:
    """创建自定义配置
    
    参数:
        **kwargs: 任何RLBotConfig支持的参数
    
    示例:
        config = create_custom_config(
            epsilon=0.2,
            learning_rate=0.01,
            aggression_threshold=0.5,
            model_name="my_custom_bot"
        )
    """
    return RLBotConfig(**kwargs)

# ===== 配置比较工具 =====

def compare_configs(*configs: RLBotConfig) -> dict:
    """比较多个配置的差异"""
    if not configs:
        return {}
    
    comparison = {}
    
    # 获取所有参数名
    all_params = set()
    for config in configs:
        all_params.update(config.__dict__.keys())
    
    # 比较每个参数
    for param in sorted(all_params):
        values = []
        for i, config in enumerate(configs):
            value = getattr(config, param, "N/A")
            values.append(f"Config{i+1}: {value}")
        comparison[param] = values
    
    return comparison

def print_config_summary(config: RLBotConfig):
    """打印配置摘要"""
    print(f"\n📋 {config.model_name} 配置摘要:")
    print("─" * 50)
    
    print("🎯 学习参数:")
    print(f"   探索率: {config.epsilon} → {config.epsilon_min} (衰减: {config.epsilon_decay})")
    print(f"   学习率: {config.learning_rate}")
    print(f"   折扣因子: {config.gamma}")
    
    print("\n🎮 策略参数:")
    print(f"   激进阈值: {config.aggression_threshold}")
    print(f"   最大下注比例: {config.max_bet_ratio*100:.0f}%")
    print(f"   跟注门槛: {config.min_hand_strength_call}")
    print(f"   加注门槛: {config.min_hand_strength_raise}")
    print(f"   全押门槛: {config.all_in_threshold}")
    
    print("\n⚙️ 高级功能:")
    features = []
    if config.use_double_q_learning:
        features.append("双Q学习")
    if config.use_experience_replay:
        features.append("经验回放")
    if config.use_enhanced_state:
        features.append("增强状态")
    if config.use_dynamic_actions:
        features.append("动态动作")
    if config.use_conservative_mode:
        features.append("保守模式")
    
    print(f"   启用: {', '.join(features) if features else '基础功能'}")
    print(f"   记忆容量: {config.memory_size}")
    print(f"   回放批次: {config.replay_batch_size}")

# ===== 使用示例 =====

if __name__ == "__main__":
    # 展示不同配置
    print("🤖 强化学习机器人配置系统")
    print("=" * 60)
    
    # 展示预定义配置
    for name in ['original', 'improved', 'conservative', 'aggressive']:
        config = get_config_by_name(name)
        print_config_summary(config)
    
    # 展示自定义配置
    print("\n🔧 自定义配置示例:")
    custom_config = create_custom_config(
        epsilon=0.25,
        learning_rate=0.015,
        aggression_threshold=0.45,
        max_bet_ratio=0.6,
        model_name="custom_balanced_bot"
    )
    print_config_summary(custom_config) 