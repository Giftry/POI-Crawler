"""
POI类型定义

包含高德地图POI分类体系的大类编码和名称
"""

from typing import Dict, List, Optional, Tuple


# 高德地图 POI 大类编码（正确版本）
POI_TYPES: Dict[str, str] = {
    "010000": "汽车服务",
    "020000": "汽车销售",
    "030000": "汽车维修",
    "040000": "摩托车服务",
    "050000": "餐饮服务",
    "060000": "购物服务",
    "070000": "生活服务",
    "080000": "体育休闲服务",
    "090000": "医疗保健服务",
    "100000": "住宿服务",
    "110000": "风景名胜",
    "120000": "商务住宅",
    "130000": "政府机构及社会团体",
    "140000": "科教文化服务",
    "150000": "交通设施服务",
    "160000": "金融保险服务",
    "170000": "公司企业",
    "180000": "道路附属设施",
    "190000": "地名地址信息",
    "200000": "公共设施",
    "220000": "事件活动",
    "970000": "室内设施",
    "990000": "通行设施"
}


# POI 类型对应的颜色
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
    "200000": "#E8DAEF",
    "220000": "#FCF3CF",
    "970000": "#EBF5FB",
    "990000": "#EAFAF1"
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
    if len(code) >= 2:
        prefix = code[:2]
        # 查找匹配的大类
        for type_code in POI_TYPES.keys():
            if type_code.startswith(prefix):
                return type_code
    return code


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
