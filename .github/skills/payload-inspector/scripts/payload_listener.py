import re
import json
import ipaddress
from urllib.parse import parse_qs

class PayloadAuditor:
    """
    Playwright 網路傳輸稽核器：
    1. 攔截 POST/PUT 請求 Payload (包含 rangpwd, password, user 等)
    2. 自動比對密碼是否為明文
    3. 自動掃描是否洩漏內部 IPv4 位址
    4. 輸出符合資安查核報表格式之文字
    """
    def __init__(self, page, input_account=None, input_password=None, sensitive_keys=None):
        self.page = page
        self.input_account = input_account
        self.input_password = input_password
        self.sensitive_keys = sensitive_keys or ["rangpwd", "pwd", "password", "pass", "account", "user", "login"]
        
        # 匹配 IPv4 的正規表達式
        self.ip_pattern = re.compile(r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b')
        
        self.captured_records = []
        
        # 綁定監聽
        self.page.on("request", self._on_request)

    def _on_request(self, request):
        if request.method in ["POST", "PUT", "PATCH"]:
            post_data = request.post_data
            if not post_data:
                return

            post_data_lower = post_data.lower()
            # 檢查是否含有監聽關鍵字
            if any(k in post_data_lower for k in self.sensitive_keys):
                parsed_content = None
                content_type = "raw"

                # 1. 嘗試解析 JSON
                try:
                    parsed_content = request.post_data_json
                    content_type = "json"
                except Exception:
                    pass

                # 2. 嘗試解析 Form-urlencoded
                if parsed_content is None and "=" in post_data:
                    try:
                        raw_dict = parse_qs(post_data)
                        parsed_content = {k: v[0] if len(v) == 1 else v for k, v in raw_dict.items()}
                        content_type = "form-data"
                    except Exception:
                        pass

                if parsed_content is None:
                    parsed_content = post_data

                record = {
                    "url": request.url,
                    "method": request.method,
                    "content_type": content_type,
                    "payload": parsed_content,
                    "raw_text": post_data
                }
                self.captured_records.append(record)

    def get_records(self):
        return self.captured_records

    def get_audit_findings_text(self):
        """
        產出符合範例截圖樣式之查核報告文字
        """
        if not self.captured_records:
            return "未攔截到相關傳輸封包"

        findings = []

        # 合併所有攔截到封包的文字以進行掃描
        combined_text = "\n".join([r["raw_text"] for r in self.captured_records])

        # ---------------------------------------------
        # 1. 掃描內部 IPv4 位址洩漏
        # ---------------------------------------------
        raw_ips = set(self.ip_pattern.findall(combined_text))
        internal_ips = []
        for ip in raw_ips:
            try:
                ip_obj = ipaddress.ip_address(ip)
                if ip_obj.is_private and not ip.startswith("127."):
                    internal_ips.append(ip)
            except ValueError:
                pass

        if internal_ips:
            findings.append("發現IPv4 位址:")
            for ip in sorted(internal_ips):
                findings.append(f"{ip}")
            findings.append("") # 空行分隔

        # ---------------------------------------------
        # 2. 掃描明確明文密碼
        # ---------------------------------------------
        has_plaintext_pwd = False
        detected_pwd_lines = []

        # 檢查 A: 輸入的測試密碼是否直接以原始字串出現在 payload
        if self.input_password and self.input_password in combined_text:
            has_plaintext_pwd = True

        # 檢查 B: 提取具體參數欄位
        for rec in self.captured_records:
            data = rec["payload"]
            if isinstance(data, dict):
                for k, v in data.items():
                    k_lower = k.lower()
                    if any(kw in k_lower for kw in ["pwd", "password", "rangpwd"]):
                        # 檢查是否為明文
                        if self.input_password and str(v) == self.input_password:
                            detected_pwd_lines.append(f"{k} = {v}")
                            has_plaintext_pwd = True
                        elif "rangpwd" in k_lower:
                            # 記錄 rangpwd 欄位現身狀態
                            detected_pwd_lines.append(f"{k} = {str(v)[:30]}... (已加密)")

        if has_plaintext_pwd:
            findings.append("發現明確的明文密碼:")
            if detected_pwd_lines:
                findings.extend(detected_pwd_lines)
            elif self.input_password:
                findings.append(f"password = {self.input_password}")
        elif detected_pwd_lines:
            findings.append("發現密碼傳輸欄位:")
            findings.extend(detected_pwd_lines)

        # ---------------------------------------------
        # 3. 若無上述重大缺失，列出抓到的傳輸概要
        # ---------------------------------------------
        if not findings:
            findings.append("未發現明文密碼或內部 IP 洩漏 (傳輸安全檢測正常)")

        return "\n".join(findings).strip()
