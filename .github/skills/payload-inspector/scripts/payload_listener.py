import json
from urllib.parse import parse_qs

class PayloadSniffer:
    def __init__(self, target_keywords=None):
        """
        :param target_keywords: 用於過濾的敏感關鍵字清單，例如 ['pwd', 'password', 'rangpwd']
        """
        if target_keywords is None:
            self.target_keywords = ["pwd", "password", "rangpwd", "account", "user", "login"]
        else:
            self.target_keywords = [k.lower() for k in target_keywords]
            
        self.captured_records = []

    def attach_to_page(self, page):
        """將攔截監聽器附加至指定 Playwright page"""
        page.on("request", self._on_request)

    def _on_request(self, request):
        if request.method in ["POST", "PUT", "PATCH"]:
            post_data = request.post_data
            if not post_data:
                return

            post_data_lower = post_data.lower()
            # 檢查是否含有目標關鍵字
            matched_keywords = [kw for kw in self.target_keywords if kw in post_data_lower]
            if matched_keywords:
                parsed_content = None
                content_type = "unknown"

                # 1. 嘗試解析 JSON
                try:
                    parsed_content = request.post_data_json
                    content_type = "json"
                except Exception:
                    pass

                # 2. 嘗試解析 Form-urlencoded (如 a=1&b=2)
                if parsed_content is None and "=" in post_data:
                    try:
                        raw_dict = parse_qs(post_data)
                        # 將單值 list 壓平
                        parsed_content = {k: v[0] if len(v) == 1 else v for k, v in raw_dict.items()}
                        content_type = "form-data"
                    except Exception:
                        pass

                # 3. 若皆非標準格式則保留原始字串
                if parsed_content is None:
                    parsed_content = post_data
                    content_type = "raw-text"

                record = {
                    "url": request.url,
                    "method": request.method,
                    "content_type": content_type,
                    "matched_keywords": matched_keywords,
                    "payload": parsed_content,
                    "headers": dict(request.headers)
                }
                self.captured_records.append(record)

    def get_records(self):
        """取得所有攔截到的紀錄"""
        return self.captured_records

    def print_summary(self):
        """以好讀的方式輸出攔截摘要"""
        if not self.captured_records:
            print("⚠️ 未攔截到任何含有敏感關鍵字的網路請求。")
            return

        print(f"\n🎯 [攔截報告] 共擷取到 {len(self.captured_records)} 筆相關 Payload：")
        for i, rec in enumerate(self.captured_records, 1):
            print(f"\n--- [請求 #{i}] -------------------------------")
            print(f"🔗 目的 URL: {rec['url']}")
            print(f"📦 請求類型: {rec['method']} ({rec['content_type']})")
            print(f"🔑 命中關鍵字: {', '.join(rec['matched_keywords'])}")
            print(f"📄 Payload 內容:")
            if isinstance(rec['payload'], dict):
                for k, v in rec['payload'].items():
                    # 特別標註 rangpwd 或 password 欄位
                    is_sensitive = any(kw in k.lower() for kw in ["pwd", "password", "rangpwd"])
                    flag = " 🚨 [敏感欄位]" if is_sensitive else ""
                    print(f"   • {k}: {v}{flag}")
            else:
                print(f"   {rec['payload']}")
        print("--------------------------------------------------\n")
