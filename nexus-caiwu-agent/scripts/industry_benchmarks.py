#!/usr/bin/env python3
"""
行业财务基准数据
定义 A 股主要行业的财务指标基准和评分标准
"""

# 12个主要行业的财务基准数据
INDUSTRY_BENCHMARKS = {
    "technology": {
        "name": "高科技",
        "name_en": "Technology",
        "description": "软件、半导体、人工智能、云计算等",
        "keywords": ["软件", "半导体", "芯片", "人工智能", "云计算", "互联网", "电子", "计算机", "通信设备"],
        "stock_patterns": ["688"],  # 科创板
        "stock_examples": ["688981", "688256", "688008", "300750", "002415"],
        "metrics": {
            "gross_margin": {"min": 40, "max": 70, "ideal": 55, "weight": 0.15},
            "net_margin": {"min": 10, "max": 35, "ideal": 22, "weight": 0.15},
            "roe": {"min": 10, "max": 30, "ideal": 18, "weight": 0.25},
            "roa": {"min": 5, "max": 18, "ideal": 12, "weight": 0.10},
            "debt_ratio": {"min": 15, "max": 50, "ideal": 30, "weight": 0.10},
            "asset_turnover": {"min": 0.4, "max": 1.2, "ideal": 0.8, "weight": 0.10},
            "rd_ratio": {"min": 3, "max": 25, "ideal": 12, "weight": 0.15}  # 研发费用率
        },
        "special_rules": {
            "high_rd_bonus": True,      # 高研发投入奖励
            "growth_critical": True     # 成长性关键
        }
    },

    "manufacturing": {
        "name": "制造业",
        "name_en": "Manufacturing",
        "description": "机械、设备、汽车、家电、零部件等",
        "keywords": ["制造", "机械", "设备", "汽车", "家电", "零部件", "装备", "工业"],
        "stock_examples": ["600031", "000651", "000333", "601012", "002594"],
        "metrics": {
            "gross_margin": {"min": 12, "max": 35, "ideal": 22, "weight": 0.20},
            "net_margin": {"min": 4, "max": 15, "ideal": 8, "weight": 0.20},
            "roe": {"min": 6, "max": 20, "ideal": 12, "weight": 0.25},
            "roa": {"min": 3, "max": 12, "ideal": 7, "weight": 0.10},
            "debt_ratio": {"min": 30, "max": 65, "ideal": 45, "weight": 0.15},
            "asset_turnover": {"min": 0.5, "max": 1.8, "ideal": 1.0, "weight": 0.10}
        },
        "special_rules": {
            "capacity_utilization": True,  # 产能利用率重要
            "inventory_critical": True      # 存货管理关键
        }
    },

    "construction": {
        "name": "建筑",
        "name_en": "Construction",
        "description": "建筑、工程、基建、房建、装修等",
        "keywords": ["建筑", "工程", "基建", "房建", "装修", "园林", "装饰", "施工"],
        "stock_examples": ["601668", "601390", "601800", "601669", "601186"],
        "metrics": {
            "gross_margin": {"min": 6, "max": 15, "ideal": 10, "weight": 0.15},
            "net_margin": {"min": 1.5, "max": 5, "ideal": 3, "weight": 0.20},
            "roe": {"min": 6, "max": 18, "ideal": 12, "weight": 0.25},
            "roa": {"min": 1, "max": 5, "ideal": 2.5, "weight": 0.10},
            "debt_ratio": {"min": 65, "max": 85, "ideal": 75, "weight": 0.10},  # 高负债正常
            "asset_turnover": {"min": 0.25, "max": 0.7, "ideal": 0.45, "weight": 0.10},
            "ocf_to_np": {"min": 0.5, "max": 1.5, "ideal": 0.9, "weight": 0.10}  # 现金流/净利润
        },
        "special_rules": {
            "debt_tolerance": "high",      # 高负债容忍
            "cashflow_critical": True,     # 现金流关键
            "order_book_important": True   # 订单储备重要
        }
    },

    "retail": {
        "name": "零售",
        "name_en": "Retail",
        "description": "零售、商贸、百货、超市、电商、贸易等",
        "keywords": ["零售", "商贸", "百货", "超市", "电商", "贸易", "销售", "连锁"],
        "stock_examples": ["601933", "002024", "002714", "600694", "601888"],
        "metrics": {
            "gross_margin": {"min": 12, "max": 40, "ideal": 25, "weight": 0.15},
            "net_margin": {"min": 2, "max": 10, "ideal": 5, "weight": 0.20},
            "roe": {"min": 8, "max": 25, "ideal": 15, "weight": 0.25},
            "roa": {"min": 4, "max": 15, "ideal": 8, "weight": 0.10},
            "debt_ratio": {"min": 35, "max": 70, "ideal": 50, "weight": 0.10},
            "asset_turnover": {"min": 1.2, "max": 4.0, "ideal": 2.5, "weight": 0.20}  # 周转率关键
        },
        "special_rules": {
            "high_turnover": True,        # 高周转率行业
            "same_store_growth": True     # 同店增长重要
        }
    },

    "finance": {
        "name": "金融",
        "name_en": "Finance",
        "description": "银行、证券、保险、信托、租赁等",
        "keywords": ["银行", "证券", "保险", "信托", "租赁", "金融", "投资"],
        "stock_patterns": ["601", "60", "002"],
        "stock_examples": ["601398", "601318", "601166", "000001", "600030"],
        "metrics": {
            "roe": {"min": 8, "max": 22, "ideal": 14, "weight": 0.35},
            "roa": {"min": 0.5, "max": 1.5, "ideal": 1.0, "weight": 0.20},
            "debt_ratio": {"min": 85, "max": 96, "ideal": 91, "weight": 0.05},  # 特殊行业
            "net_margin": {"min": 20, "max": 50, "ideal": 35, "weight": 0.25},
            "cost_to_income": {"min": 25, "max": 45, "ideal": 32, "weight": 0.15}  # 成本收入比
        },
        "special_rules": {
            "use_custom_metrics": True,   # 使用自定义指标
            "capital_adequacy": True,     # 资本充足率重要
            "npl_ratio": True            # 不良贷款率关键
        }
    },

    "real_estate": {
        "name": "房地产",
        "name_en": "Real Estate",
        "description": "房地产开发、经营、物业、园区等",
        "keywords": ["房地产", "地产", "物业", "园区", "置业", "开发"],
        "stock_examples": ["000002", "600048", "001979", "600383", "000656"],
        "metrics": {
            "gross_margin": {"min": 18, "max": 45, "ideal": 30, "weight": 0.15},
            "net_margin": {"min": 6, "max": 18, "ideal": 11, "weight": 0.20},
            "roe": {"min": 6, "max": 22, "ideal": 13, "weight": 0.25},
            "roa": {"min": 2, "max": 8, "ideal": 4, "weight": 0.10},
            "debt_ratio": {"min": 55, "max": 88, "ideal": 72, "weight": 0.15},
            "asset_turnover": {"min": 0.15, "max": 0.5, "ideal": 0.3, "weight": 0.10},
            "ocf_to_np": {"min": 0.3, "max": 1.5, "ideal": 0.8, "weight": 0.05}
        },
        "special_rules": {
            "debt_tolerance": "high",      # 高负债容忍
            "cashflow_critical": True,     # 现金流关键
            "land_reserve": True          # 土地储备重要
        }
    },

    "consumer": {
        "name": "消费品",
        "name_en": "Consumer Goods",
        "description": "食品、饮料、白酒、医药、纺织、日化等",
        "keywords": ["食品", "饮料", "白酒", "医药", "纺织", "服装", "日化", "化妆品", "调味品"],
        "stock_examples": ["600519", "603288", "000858", "600887", "002304"],
        "metrics": {
            "gross_margin": {"min": 25, "max": 70, "ideal": 50, "weight": 0.20},
            "net_margin": {"min": 8, "max": 30, "ideal": 18, "weight": 0.20},
            "roe": {"min": 12, "max": 35, "ideal": 22, "weight": 0.30},
            "roa": {"min": 6, "max": 20, "ideal": 12, "weight": 0.10},
            "debt_ratio": {"min": 15, "max": 50, "ideal": 28, "weight": 0.10},
            "asset_turnover": {"min": 0.4, "max": 1.2, "ideal": 0.75, "weight": 0.10}
        },
        "special_rules": {
            "brand_value": True,          # 品牌价值重要
            "channel_coverage": True,     # 渠道覆盖关键
            "repetition_rate": True      # 复购率重要
        }
    },

    "energy": {
        "name": "能源",
        "name_en": "Energy",
        "description": "石油、天然气、煤炭、电力、新能源等",
        "keywords": ["石油", "天然气", "煤炭", "电力", "新能源", "光伏", "风电", "核电", "采掘"],
        "stock_examples": ["601857", "600900", "601899", "600021", "000400"],
        "metrics": {
            "gross_margin": {"min": 12, "max": 40, "ideal": 25, "weight": 0.15},
            "net_margin": {"min": 4, "max": 18, "ideal": 10, "weight": 0.20},
            "roe": {"min": 5, "max": 16, "ideal": 10, "weight": 0.25},
            "roa": {"min": 2, "max": 10, "ideal": 5, "weight": 0.10},
            "debt_ratio": {"min": 35, "max": 75, "ideal": 55, "weight": 0.15},
            "asset_turnover": {"min": 0.25, "max": 0.9, "ideal": 0.55, "weight": 0.15}
        },
        "special_rules": {
            "price_sensitive": True,      # 价格敏感
            "resource_reserves": True,    # 资源储备重要
            "policy_impact": True         # 政策影响大
        }
    },

    "utilities": {
        "name": "公用事业",
        "name_en": "Utilities",
        "description": "水务、燃气、供热、环保、污水处理等",
        "keywords": ["水务", "燃气", "供热", "环保", "污水", "固废", "环境"],
        "stock_examples": ["600011", "600323", "000685", "600874", "601199"],
        "metrics": {
            "gross_margin": {"min": 20, "max": 50, "ideal": 35, "weight": 0.15},
            "net_margin": {"min": 6, "max": 20, "ideal": 13, "weight": 0.20},
            "roe": {"min": 5, "max": 14, "ideal": 9, "weight": 0.30},
            "roa": {"min": 2, "max": 8, "ideal": 4, "weight": 0.10},
            "debt_ratio": {"min": 45, "max": 80, "ideal": 62, "weight": 0.15},
            "asset_turnover": {"min": 0.2, "max": 0.7, "ideal": 0.4, "weight": 0.10}
        },
        "special_rules": {
            "stable_cashflow": True,      # 现金流稳定
            "franchise_important": True,  # 特许经营权重要
            "regulated": True            # 受监管行业
        }
    },

    "telecom": {
        "name": "通信",
        "name_en": "Telecommunications",
        "description": "电信、移动、联通、通信设备等",
        "keywords": ["电信", "移动", "联通", "通信", "5G", "基站", "光纤"],
        "stock_examples": ["600941", "600050", "000063", "601728", "002468"],
        "metrics": {
            "gross_margin": {"min": 25, "max": 60, "ideal": 42, "weight": 0.15},
            "net_margin": {"min": 8, "max": 22, "ideal": 15, "weight": 0.20},
            "roe": {"min": 6, "max": 18, "ideal": 12, "weight": 0.30},
            "roa": {"min": 3, "max": 10, "ideal": 6, "weight": 0.10},
            "debt_ratio": {"min": 30, "max": 65, "ideal": 45, "weight": 0.15},
            "asset_turnover": {"min": 0.35, "max": 1.0, "ideal": 0.6, "weight": 0.10}
        },
        "special_rules": {
            "high_capex": True,           # 高资本开支
            "subscriber_base": True,      # 用户基础重要
            "arpu_important": True        # ARPU值重要
        }
    },

    "transportation": {
        "name": "交通运输",
        "name_en": "Transportation",
        "description": "航空、机场、港口、航运、物流、快递等",
        "keywords": ["航空", "机场", "港口", "航运", "物流", "快递", "铁路", "交通"],
        "stock_examples": ["601111", "002352", "600029", "601919", "601006"],
        "metrics": {
            "gross_margin": {"min": 12, "max": 40, "ideal": 25, "weight": 0.15},
            "net_margin": {"min": 4, "max": 16, "ideal": 10, "weight": 0.20},
            "roe": {"min": 5, "max": 16, "ideal": 10, "weight": 0.25},
            "roa": {"min": 2, "max": 10, "ideal": 5, "weight": 0.10},
            "debt_ratio": {"min": 35, "max": 75, "ideal": 55, "weight": 0.15},
            "asset_turnover": {"min": 0.25, "max": 0.9, "ideal": 0.55, "weight": 0.15}
        },
        "special_rules": {
            "heavy_assets": True,         # 重资产
            "fuel_cost_sensitive": True,  # 燃油成本敏感
            "capacity_utilization": True  # 运力利用率重要
        }
    },

    "materials": {
        "name": "原材料",
        "name_en": "Materials",
        "description": "钢铁、有色金属、化工、建材、造纸等",
        "keywords": ["钢铁", "有色金属", "化工", "建材", "造纸", "玻璃", "水泥", "金属"],
        "stock_examples": ["600019", "601600", "600585", "000895", "002601"],
        "metrics": {
            "gross_margin": {"min": 8, "max": 30, "ideal": 17, "weight": 0.15},
            "net_margin": {"min": 2, "max": 12, "ideal": 6, "weight": 0.20},
            "roe": {"min": 4, "max": 18, "ideal": 10, "weight": 0.25},
            "roa": {"min": 2, "max": 10, "ideal": 5, "weight": 0.10},
            "debt_ratio": {"min": 35, "max": 75, "ideal": 55, "weight": 0.15},
            "asset_turnover": {"min": 0.4, "max": 1.5, "ideal": 0.85, "weight": 0.15}
        },
        "special_rules": {
            "cyclical": True,              # 周期性
            "price_volatility": True,     # 价格波动大
            "inventory_important": True    # 库存重要
        }
    }
}

# 申万行业分类映射表（申万一级行业到自定义行业）
SW_INDUSTRY_MAPPING = {
    # 金融
    "银行": "finance",
    "非银金融": "finance",

    # 地产建筑
    "房地产": "real_estate",
    "建筑装饰": "construction",
    "建筑材料": "materials",

    # 原材料
    "钢铁": "materials",
    "有色金属": "materials",
    "化工": "materials",
    "基础化工": "materials",
    "石油石化": "energy",
    "煤炭": "materials",

    # 能源公用
    "电力设备": "energy",
    "公用事业": "utilities",

    # 交运
    "交通运输": "transportation",

    # 制造
    "汽车": "manufacturing",
    "机械设备": "manufacturing",
    "国防军工": "manufacturing",
    "电气设备": "manufacturing",

    # 科技
    "电子": "technology",
    "计算机": "technology",
    "通信": "telecom",
    "传媒": "technology",

    # 消费
    "食品饮料": "consumer",
    "家用电器": "consumer",
    "纺织服饰": "consumer",
    "轻工制造": "consumer",
    "医药生物": "consumer",
    "美容护理": "consumer",

    # 零售
    "商贸零售": "retail",
    "社会服务": "consumer",

    # 其他
    "农林牧渔": "consumer",
    "综合": "manufacturing"
}

# 获取所有行业列表
def get_all_industries():
    """获取所有行业列表"""
    return list(INDUSTRY_BENCHMARKS.keys())

# 获取行业信息
def get_industry_info(industry_id: str) -> dict:
    """获取指定行业的信息"""
    return INDUSTRY_BENCHMARKS.get(industry_id, INDUSTRY_BENCHMARKS["manufacturing"])

# 根据申万行业获取自定义行业
def get_industry_by_sw(sw_industry: str) -> str:
    """根据申万行业分类获取自定义行业ID"""
    return SW_INDUSTRY_MAPPING.get(sw_industry, "manufacturing")

# 获取行业基准指标
def get_industry_benchmarks(industry_id: str) -> dict:
    """获取指定行业的基准指标"""
    industry = get_industry_info(industry_id)
    return industry.get("metrics", {})

# 获取行业特殊规则
def get_industry_rules(industry_id: str) -> dict:
    """获取指定行业的特殊规则"""
    industry = get_industry_info(industry_id)
    return industry.get("special_rules", {})


if __name__ == "__main__":
    # 打印所有行业信息
    print("=" * 60)
    print("A股行业财务基准数据")
    print("=" * 60)

    for industry_id, info in INDUSTRY_BENCHMARKS.items():
        print(f"\n【{info['name']} ({info['name_en']})】")
        print(f"  描述: {info['description']}")
        print(f"  关键词: {', '.join(info['keywords'][:5])}...")
        print(f"  代表股票: {', '.join(info.get('stock_examples', [])[:3])}")

        metrics = info['metrics']
        print(f"  核心指标:")
        for metric, config in list(metrics.items())[:4]:
            print(f"    {metric}: 理想值 {config['ideal']}%, 范围 {config['min']}-{config['max']}%")
