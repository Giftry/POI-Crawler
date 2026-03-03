import json
import csv
import os
from config import OUTPUT_CONFIG

class DataExporter:
    def __init__(self):
        self.output_format = OUTPUT_CONFIG["format"]
        self.output_dir = OUTPUT_CONFIG["output_dir"]
        self.file_prefix = OUTPUT_CONFIG["file_prefix"]
        
        # 确保输出目录存在
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def export(self, data):
        """
        导出数据
        :param data: 处理后的 POI 数据列表
        :return: 导出文件路径
        """
        if self.output_format == "json":
            return self._export_json(data)
        elif self.output_format == "csv":
            return self._export_csv(data)
        else:
            raise ValueError(f"不支持的输出格式: {self.output_format}")
    
    def _export_json(self, data):
        """
        导出为 JSON 文件
        :param data: 处理后的 POI 数据列表
        :return: 导出文件路径
        """
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(self.output_dir, f"{self.file_prefix}_{timestamp}.json")
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"数据已导出到: {file_path}")
        return file_path
    
    def _export_csv(self, data):
        """
        导出为 CSV 文件
        :param data: 处理后的 POI 数据列表
        :return: 导出文件路径
        """
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(self.output_dir, f"{self.file_prefix}_{timestamp}.csv")
        
        if not data:
            print("没有数据可导出")
            return None
        
        # 获取所有字段名
        fieldnames = list(data[0].keys())
        
        with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                # 处理列表类型的字段
                row_copy = row.copy()
                for key, value in row_copy.items():
                    if isinstance(value, list):
                        row_copy[key] = ",".join(str(item) for item in value)
                    elif isinstance(value, dict):
                        row_copy[key] = json.dumps(value, ensure_ascii=False)
                writer.writerow(row_copy)
        
        print(f"数据已导出到: {file_path}")
        return file_path
