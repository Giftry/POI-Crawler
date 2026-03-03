class DataProcessor:
    def __init__(self):
        pass
    
    def process_poi_data(self, raw_pois):
        """
        处理原始 POI 数据
        :param raw_pois: 原始 POI 数据列表
        :return: 处理后的 POI 数据列表
        """
        processed_pois = []
        
        for poi in raw_pois:
            processed_poi = self._extract_poi_fields(poi)
            if processed_poi:
                processed_pois.append(processed_poi)
        
        return processed_pois
    
    def _extract_poi_fields(self, poi):
        """
        提取 POI 字段
        :param poi: 原始 POI 数据
        :return: 提取后的 POI 数据
        """
        try:
            # 提取基本信息
            processed_poi = {
                "name": poi.get("name", ""),
                "location": poi.get("location", ""),
                "address": poi.get("address", ""),
                "tel": poi.get("tel", ""),
                "type": poi.get("type", ""),
                "typecode": poi.get("typecode", ""),
                "business_area": poi.get("business_area", ""),
                "cityname": poi.get("cityname", ""),
                "adname": poi.get("adname", ""),
                "pname": poi.get("pname", ""),
                "shopinfo": poi.get("shopinfo", ""),
            }
            
            # 处理经纬度
            if processed_poi["location"]:
                try:
                    lon, lat = processed_poi["location"].split(",")
                    processed_poi["longitude"] = float(lon)
                    processed_poi["latitude"] = float(lat)
                except Exception:
                    processed_poi["longitude"] = None
                    processed_poi["latitude"] = None
            else:
                processed_poi["longitude"] = None
                processed_poi["latitude"] = None
            
            return processed_poi
        except Exception as e:
            print(f"处理 POI 数据时出错: {e}")
            return None
