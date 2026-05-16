"""
POI类型定义

包含高德地图POI分类体系的大类编码和名称
"""

from typing import Dict, List, Optional, Tuple


POI_TYPES: Dict[str, str] = {
    "010000": "餐饮",
    "020000": "住宿",
    "030000": "交通设施",
    "040000": "金融",
    "050000": "旅游景点",
    "060000": "购物",
    "070000": "生活服务",
    "080000": "体育休闲",
    "090000": "医疗保健",
    "100000": "科教文化",
    "110000": "公司企业",
    "120000": "政府机构及社会团体",
    "130000": "道路附属设施",
    "140000": "地名地址信息",
    "150000": "建筑物",
    "160000": "通行设施",
    "170000": "公共设施",
    "180000": "事件活动",
    "190000": "其他"
}


POI_SUBTYPES: Dict[str, Dict[str, str]] = {
    "010000": {
        "010101": "中餐",
        "010102": "外国餐厅",
        "010103": "小吃快餐",
        "010104": "茶座",
        "010105": "咖啡厅",
        "010106": "酒吧",
        "010107": "糕饼店",
        "010108": "生日蛋糕",
        "010109": "水果店",
        "010110": "熟食",
        "010111": "外卖服务",
        "010199": "其他餐饮",
    },
    "060000": {
        "060101": "综合商场",
        "060102": "便利店",
        "060103": "超市",
        "060104": "菜市场",
        "060105": "服装鞋帽",
        "060106": "钟表眼镜",
        "060107": "化妆品",
        "060108": "珠宝首饰",
        "060109": "电器电子",
        "060110": "家居建材",
        "060111": "图书",
        "060112": "运动户外",
        "060113": "母婴用品",
        "060114": "汽车用品",
        "060199": "其他购物",
    },
}


POI_COLORS: Dict[str, str] = {
    "010000": "#FF6B6B",
    "020000": "#4ECDC4",
    "030000": "#45B7D1",
    "040000": "#96CEB4",
    "050000": "#FFEAA7",
    "060000": "#DDA0DD",
    "070000": "#98D8C8",
    "080000": "#F7DC6F",
    "090000": "#BB8FCE",
    "100000": "#85C1E9",
    "110000": "#F8B500",
    "120000": "#A9CCE3",
    "130000": "#CAD3C8",
    "140000": "#D5DBDB",
    "150000": "#ABB2B9",
    "160000": "#BDC3C7",
    "170000": "#C39BD3",
    "180000": "#FADBD8",
    "190000": "#D5D8DC",
}


def get_type_name(code: str) -> str:
    """
    获取POI类型名称

    Args:
        code: POI类型编码

    Returns:
        类型名称，如果未找到则返回原始编码
    """
    return POI_TYPES.get(code, code)


def get_type_code(name: str) -> Optional[str]:
    """
    通过名称获取POI类型编码

    Args:
        name: POI类型名称

    Returns:
        类型编码，如果未找到则返回None
    """
    for code, type_name in POI_TYPES.items():
        if type_name == name:
            return code
    return None


def get_all_type_codes() -> List[str]:
    """
    获取所有POI类型编码

    Returns:
        类型编码列表
    """
    return list(POI_TYPES.keys())


def get_type_color(code: str) -> str:
    """
    获取POI类型的默认显示颜色

    Args:
        code: POI类型编码

    Returns:
        颜色代码（十六进制）
    """
    return POI_COLORS.get(code, "#808080")


def get_type_by_prefix(prefix: str) -> List[Tuple[str, str]]:
    """
    通过前缀筛选POI类型

    Args:
        prefix: 类型编码前缀

    Returns:
        匹配的类型列表 [(编码, 名称), ...]
    """
    return [(code, name) for code, name in POI_TYPES.items()
            if code.startswith(prefix)]


def get_major_type(code: str) -> str:
    """
    获取POI的大类编码

    高德地图POI编码为6位，前两位代表大类

    Args:
        code: 完整POI类型编码

    Returns:
        大类编码
    """
    return code[:2] + "0000"


def get_major_type_name(code: str) -> str:
    """
    获取POI的大类名称

    Args:
        code: 完整POI类型编码

    Returns:
        大类名称
    """
    major_code = get_major_type(code)
    return get_type_name(major_code)


def format_poi_type(full_type: str) -> str:
    """
    格式化POI类型显示

    将 "餐饮服务;中餐厅;北京菜" 格式化为 "餐饮 > 中餐厅 > 北京菜"

    Args:
        full_type: 完整类型字符串

    Returns:
        格式化后的类型字符串
    """
    if not full_type:
        return ""

    parts = full_type.replace(";", ">").replace("|", ">").split(">")
    return " > ".join([p.strip() for p in parts if p.strip()])


class POITypeSelector:
    """POI类型选择器"""

    def __init__(self):
        self.selected_types: List[str] = []

    def select_all(self):
        """选择所有类型"""
        self.selected_types = get_all_type_codes()

    def select(self, *codes: str):
        """选择指定类型"""
        for code in codes:
            if code in POI_TYPES and code not in self.selected_types:
                self.selected_types.append(code)

    def deselect(self, *codes: str):
        """取消选择指定类型"""
        for code in codes:
            if code in self.selected_types:
                self.selected_types.remove(code)

    def deselect_all(self):
        """取消选择所有类型"""
        self.selected_types = []

    def get_selected(self) -> List[str]:
        """获取已选择的类型"""
        return self.selected_types.copy()

    def get_selected_with_names(self) -> List[Tuple[str, str]]:
        """获取已选择的类型及其名称"""
        return [(code, get_type_name(code)) for code in self.selected_types]

    def is_selected(self, code: str) -> bool:
        """检查类型是否被选中"""
        return code in self.selected_types
