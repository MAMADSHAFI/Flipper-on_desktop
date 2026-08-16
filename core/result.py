# core/result.py — جدید
@dataclass
class ModuleResult:
    success: bool
    data: Any
    log: list[str]
    artifacts: list[Path]  # فایل‌های خروجی (pcap, dump, report)
