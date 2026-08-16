"""
NetScanner Module - Network Discovery & Port Scanner
اسکنر شبکه محلی: کشف هاست‌ها + اسکن پورت + تشخیص سرویس
کاملاً نرم‌افزاری، بدون نیاز به Flipper Zero
"""

import socket
import ipaddress
import json
import csv
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from modules.base_module import BaseModule
from core.task_runner import TaskRunner, TaskResult


# پورت‌های رایج و سرویس مربوطه
COMMON_PORTS = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    139: "NetBIOS",
    143: "IMAP",
    443: "HTTPS",
    445: "SMB",
    3306: "MySQL",
    3389: "RDP",
    5432: "PostgreSQL",
    5900: "VNC",
    8080: "HTTP-Proxy",
    8443: "HTTPS-Alt",
}


class NetworkScanner(BaseModule):
    name = "NetScanner"
    version = "1.0.0"
    description = "Network Discovery & Port Scanner"
    icon = "🌐"

    # ------------------------------------------------------------------ #
    # چرخه حیات
    # ------------------------------------------------------------------ #
    def on_load(self):
        self.current_task = None
        self._stop_flag = False
        self.last_results = self.state.get("last_results", {})
        self.output_dir = Path(self.state.get("output_dir", "data/netscanner"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.log("NetScanner loaded")

    def on_unload(self):
        self.cmd_stop({})
        self.state["last_results"] = self.last_results
        self.state["output_dir"] = str(self.output_dir)
        self.save_state()

    # ------------------------------------------------------------------ #
    # ابزارهای داخلی
    # ------------------------------------------------------------------ #
    @staticmethod
    def _local_subnet() -> str:
        """تشخیص خودکار سابنت /24 محلی."""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        except Exception:
            ip = "127.0.0.1"
        finally:
            s.close()
        net = ipaddress.ip_network(f"{ip}/24", strict=False)
        return str(net)

    @staticmethod
    def _ping_host(ip: str, timeout: float = 0.5) -> bool:
        """
        بررسی زنده بودن هاست از طریق تلاش برای اتصال TCP روی چند پورت رایج.
        (بدون نیاز به دسترسی ادمین برای ICMP)
        """
        for port in (80, 443, 22, 445):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(timeout)
                    if sock.connect_ex((ip, port)) == 0:
                        return True
            except OSError:
                continue
        return False

    @staticmethod
    def _resolve_hostname(ip: str) -> str:
        try:
            return socket.gethostbyaddr(ip)[0]
        except (socket.herror, socket.gaierror, OSError):
            return ""

    @staticmethod
    def _scan_single_port(ip: str, port: int, timeout: float = 0.5):
        """اسکن یک پورت؛ در صورت باز بودن (port, service) برمی‌گرداند."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout)
                if sock.connect_ex((ip, port)) == 0:
                    service = COMMON_PORTS.get(port, "unknown")
                    return port, service
        except OSError:
            pass
        return None

    # ------------------------------------------------------------------ #
    # فرمان: کشف هاست‌های شبکه
    # ------------------------------------------------------------------ #
    def cmd_scan(self, params: dict):
        """
        کشف هاست‌های زنده در یک سابنت.
        params:
            subnet: str  (اختیاری، پیش‌فرض سابنت محلی)
            workers: int (پیش‌فرض 100)
        """
        subnet = params.get("subnet") or self._local_subnet()
        workers = int(params.get("workers", 100))
        self._stop_flag = False

        def task(progress_callback=None):
            result = TaskResult()
            result.start_time = datetime.now()
            try:
                network = ipaddress.ip_network(subnet, strict=False)
                hosts = [str(h) for h in network.hosts()]
                total = len(hosts)
                alive = []

                result.add_log(f"Scanning {subnet} ({total} hosts)")

                with ThreadPoolExecutor(max_workers=workers) as pool:
                    futures = {pool.submit(self._ping_host, ip): ip for ip in hosts}
                    for i, fut in enumerate(as_completed(futures), 1):
                        if self._stop_flag:
                            result.add_log("Scan stopped by user")
                            break
                        ip = futures[fut]
                        if fut.result():
                            hostname = self._resolve_hostname(ip)
                            alive.append({"ip": ip, "hostname": hostname})
                            result.add_log(f"[+] {ip} {hostname}")
                        if progress_callback:
                            progress_callback(f"{i}/{total} scanned - {len(alive)} alive")

                result.data = {"subnet": subnet, "alive_hosts": alive}
                result.success = True
                self.last_results = result.data
                result.add_log(f"Done: {len(alive)} live hosts")
            except Exception as e:
                result.error = str(e)
                result.add_log(f"Error: {e}")
            finally:
                result.end_time = datetime.now()
            return result

        self.current_task = TaskRunner.run_async(
            task,
            on_progress=lambda msg: self.kernel.emit_event(
                "netscanner_progress", {"message": msg}
            ),
            on_complete=lambda res: self.kernel.emit_event(
                "netscanner_complete", res
            ),
        )
        return {"status": "started", "subnet": subnet}

    # ------------------------------------------------------------------ #
    # فرمان: اسکن پورت روی یک هاست
    # ------------------------------------------------------------------ #
    def cmd_port_scan(self, params: dict):
        """
        اسکن پورت‌های یک هاست مشخص.
        params:
            target: str  (الزامی) - IP یا hostname
            ports:  list (اختیاری) - پیش‌فرض COMMON_PORTS
            workers: int (پیش‌فرض 50)
        """
        target = params.get("target")
        if not target:
            return {"error": "target is required"}

        ports = params.get("ports") or list(COMMON_PORTS.keys())
        workers = int(params.get("workers", 50))
        self._stop_flag = False

        def task(progress_callback=None):
            result = TaskResult()
            result.start_time = datetime.now()
            try:
                ip = socket.gethostbyname(target)
                result.add_log(f"Port scan on {target} ({ip})")
                open_ports = []
                total = len(ports)

                with ThreadPoolExecutor(max_workers=workers) as pool:
                    futures = {
                        pool.submit(self._scan_single_port, ip, p): p
                        for p in ports
                    }
                    for i, fut in enumerate(as_completed(futures), 1):
                        if self._stop_flag:
                            result.add_log("Port scan stopped by user")
                            break
                        r = fut.result()
                        if r:
                            port, service = r
                            open_ports.append({"port": port, "service": service})
                            result.add_log(f"[+] {port}/tcp open - {service}")
                        if progress_callback:
                            progress_callback(
                                f"{i}/{total} ports - {len(open_ports)} open"
                            )

                open_ports.sort(key=lambda x: x["port"])
                result.data = {"target": target, "ip": ip, "open_ports": open_ports}
                result.success = True
                result.add_log(f"Done: {len(open_ports)} open ports")
            except socket.gaierror:
                result.error = f"Cannot resolve host: {target}"
                result.add_log(result.error)
            except Exception as e:
                result.error = str(e)
                result.add_log(f"Error: {e}")
            finally:
                result.end_time = datetime.now()
            return result

        self.current_task = TaskRunner.run_async(
            task,
            on_progress=lambda msg: self.kernel.emit_event(
                "netscanner_progress", {"message": msg}
            ),
            on_complete=lambda res: self.kernel.emit_event(
                "netscanner_complete", res
            ),
        )
        return {"status": "started", "target": target}

    # ------------------------------------------------------------------ #
    # فرمان: توقف اسکن جاری
    # ------------------------------------------------------------------ #
    def cmd_stop(self, params: dict):
        self._stop_flag = True
        if self.current_task and self.current_task.is_alive():
            self.current_task.join(timeout=2)
        self.current_task = None
        return {"status": "stopped"}

    # ------------------------------------------------------------------ #
    # فرمان: خروجی گرفتن از آخرین نتایج
    # ------------------------------------------------------------------ #
    def cmd_export(self, params: dict):
        """
        ذخیره آخرین نتایج به فایل.
        params:
            format: "json" | "csv"  (پیش‌فرض json)
        """
        if not self.last_results:
            return {"error": "no results to export"}

        fmt = params.get("format", "json").lower()
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = self.output_dir / f"scan_{ts}.{fmt}"

        try:
            if fmt == "json":
                path.write_text(
                    json.dumps(self.last_results, indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )
            elif fmt == "csv":
                hosts = self.last_results.get("alive_hosts", [])
                with open(path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=["ip", "hostname"])
                    writer.writeheader()
                    writer.writerows(hosts)
            else:
                return {"error": f"unsupported format: {fmt}"}
            return {"status": "exported", "path": str(path)}
        except Exception as e:
            return {"error": str(e)}

    # ------------------------------------------------------------------ #
    # فرمان: وضعیت ماژول
    # ------------------------------------------------------------------ #
    def cmd_status(self, params: dict):
        return {
            "running": bool(self.current_task and self.current_task.is_alive()),
            "last_scan": self.last_results,
            "output_dir": str(self.output_dir),
        }
