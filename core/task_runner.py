# FlipperWin/core/task_runner.py
import threading
from typing import Callable, Any
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class TaskResult:
    """نتیجه استاندارد برای همه عملیات async"""
    success: bool
    data: Any = None
    logs: list[str] = field(default_factory=list)
    artifacts: list[str] = field(default_factory=list)  # فایل‌های خروجی
    error: str | None = None
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime | None = None

    def add_log(self, msg: str):
        self.logs.append(f"[{datetime.now():%H:%M:%S}] {msg}")

class TaskRunner:
    """اجرای task های سنگین در thread جدا با callback"""
    
    @staticmethod
    def run_async(
        task_fn: Callable,
        on_progress: Callable[[str], None] | None = None,
        on_complete: Callable[[TaskResult], None] | None = None,
        **task_kwargs
    ) -> threading.Thread:
        """
        اجرای یک تسک در پس‌زمینه
        
        Args:
            task_fn: تابعی که TaskResult برمی‌گرداند
            on_progress: callback برای گزارش پیشرفت (دریافت string)
            on_complete: callback نهایی با نتیجه
            **task_kwargs: پارامترهای تسک
        """
        def wrapper():
            result = TaskResult(success=False)
            try:
                # اجرای تسک و دریافت نتیجه
                result = task_fn(
                    progress_callback=on_progress,
                    **task_kwargs
                )
                result.success = True
            except Exception as e:
                result.success = False
                result.error = str(e)
                result.add_log(f"❌ خطا: {e}")
            finally:
                result.end_time = datetime.now()
                if on_complete:
                    on_complete(result)
        
        thread = threading.Thread(target=wrapper, daemon=True)
        thread.start()
        return thread
