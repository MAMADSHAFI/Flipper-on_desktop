"""
FlipperWin/modules/badusb/module.py
ماژول BadUSB با قابلیت اجرای واقعی DuckyScript به صورت async
"""
import os
from pathlib import Path
from typing import Optional, Callable
from modules.base_module import BaseModule
from core.task_runner import TaskRunner, TaskResult
from .ducky_parser import DuckyParser
from .executor import DuckyExecutor

class BadUSBModule(BaseModule):
    """ماژول BadUSB با پشتیبانی کامل از اجرای async"""
    
    def __init__(self, kernel):
        super().__init__(kernel)
        self.name = "BadUSB"
        self.version = "0.2.0"
        self.description = "USB HID keyboard injection (Ducky Script) - Async Support"
        self.icon = "⌨️"
        
        self.scripts_dir = Path(__file__).parent / "scripts"
        self.parser = DuckyParser()
        self.executor = DuckyExecutor()
        self.scripts = {}
        self.loaded = None
    
    def on_load(self):
        """بارگذاری اولیه ماژول"""
        self.scripts_dir.mkdir(exist_ok=True)
        
        # بارگذاری اسکریپت‌های ذخیره شده
        self.scripts = self.load("scripts", {})
        
        # ایجاد اسکریپت‌های نمونه
        samples = {
            "hello.txt": "REM Hello World Sample\nDELAY 500\nGUI r\nDELAY 200\nSTRING notepad\nENTER\nDELAY 500\nSTRING Hello from FlipperWin!\nENTER",
            "info.txt": "REM System Info\nGUI r\nDELAY 200\nSTRING cmd\nENTER\nDELAY 300\nSTRING systeminfo\nENTER",
            "test.txt": "REM Simple Test\nSTRING Testing BadUSB Module\nENTER\nDELAY 100\nSTRING Line 2\nENTER\nDELAY 100\nSTRING Line 3\nENTER"
        }
        
        for name, content in samples.items():
            script_path = self.scripts_dir / name
            if not script_path.exists():
                script_path.write_text(content, encoding='utf-8')
                # افزودن به دیکشنری scripts
                self.scripts[name.replace('.txt', '')] = content
        
        self.save("scripts", self.scripts)
        return {"status": "loaded", "scripts_dir": str(self.scripts_dir), "count": len(self.scripts)}
    
    def on_unload(self):
        """توقف اجرای فعال هنگام unload"""
        if self.executor.running:
            self.executor.running = False
        self.save("scripts", self.scripts)
        return {"status": "unloaded"}
    
    def cmd_list(self) -> dict:
        """لیست اسکریپت‌های موجود"""
        script_list = []
        
        # لیست از دیکشنری
        for name, content in self.scripts.items():
            script_list.append({
                "name": name,
                "lines": len(content.splitlines()),
                "size": len(content)
            })
        
        # لیست از فایل‌های موجود
        if self.scripts_dir.exists():
            for file in self.scripts_dir.glob("*.txt"):
                name = file.stem
                if name not in self.scripts:
                    content = file.read_text(encoding='utf-8')
                    script_list.append({
                        "name": name,
                        "lines": len(content.splitlines()),
                        "size": file.stat().st_size
                    })
        
        return {
            "success": True,
            "scripts": script_list,
            "count": len(script_list)
        }
    
    def cmd_load_script(self, name: str, content: str) -> dict:
        """ذخیره/بارگذاری اسکریپت جدید"""
        try:
            # ذخیره در دیکشنری
            self.scripts[name] = content
            self.loaded = name
            self.save("scripts", self.scripts)
            
            # ذخیره در فایل
            if not name.endswith('.txt'):
                name += '.txt'
            script_path = self.scripts_dir / name
            script_path.write_text(content, encoding='utf-8')
            
            return {
                "success": True,
                "message": f"اسکریپت '{name}' ذخیره شد",
                "lines": len(content.splitlines()),
                "path": str(script_path)
            }
        except Exception as e:
                    return {
                "success": False,
                "error": f"خطا در ذخیره اسکریپت: {str(e)}"
            }
    
    def cmd_get(self, name: str) -> dict:
        """دریافت محتوای یک اسکریپت"""
        if name in self.scripts:
            return {
                "success": True,
                "name": name,
                "content": self.scripts[name],
                "lines": len(self.scripts[name].splitlines())
            }
        
        # بررسی در فایل‌ها
        script_path = self.scripts_dir / f"{name}.txt"
        if script_path.exists():
            content = script_path.read_text(encoding='utf-8')
            self.scripts[name] = content
            return {
                "success": True,
                "name": name,
                "content": content,
                "lines": len(content.splitlines())
            }
        
        return {
            "success": False,
            "error": f"اسکریپت '{name}' یافت نشد"
        }
    
    def cmd_delete(self, name: str) -> dict:
        """حذف اسکریپت"""
        try:
            if name in self.scripts:
                del self.scripts[name]
                self.save("scripts", self.scripts)
            
            script_path = self.scripts_dir / f"{name}.txt"
            if script_path.exists():
                script_path.unlink()
            
            if self.loaded == name:
                self.loaded = None
            
            return {
                "success": True,
                "message": f"اسکریپت '{name}' حذف شد"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"خطا در حذف: {str(e)}"
            }
    
    def cmd_run(self, name: str) -> dict:
        """اجرای اسکریپت به صورت async"""
        if self.is_running:
            return {
                "success": False,
                "error": "اسکریپت دیگری در حال اجراست. ابتدا آن را متوقف کنید."
            }
        
        # دریافت محتوای اسکریپت
        script_result = self.cmd_get(name)
        if not script_result["success"]:
            return script_result
        
        content = script_result["content"]
        
        # Parse و اعتبارسنجی
        try:
            commands = self.parser.parse(content)
            validation = self.parser.validate(commands)
            
            if not validation["valid"]:
                return {
                    "success": False,
                    "error": "اسکریپت نامعتبر است",
                    "details": validation
                }
        except Exception as e:
            return {
        "success": False,
        "error": f"خطا در ذخیره اسکریپت: {str(e)}"
    }
        # تعریف callback برای گزارش پیشرفت
        def progress_callback(current: int, total: int, message: str = ""):
            """callback برای گزارش پیشرفت به UI"""
            progress = int((current / total) * 100) if total > 0 else 0
            self.kernel.emit_event("badusb_progress", {
                "script": name,
                "current": current,
                "total": total,
                "progress": progress,
                "message": message
            })
        
        # تعریف callback برای تکمیل
        def on_complete(result):
            """callback برای تکمیل اجرا"""
            self.is_running = False
            self.current_task = None
            
            self.kernel.emit_event("badusb_complete", {
                "script": name,
                "success": result.success,
                "message": result.message,
                "executed": result.data.get("executed", 0) if result.data else 0,
                "total": result.data.get("total", 0) if result.data else 0,
                "errors": result.errors
            })
        
        # اجرای async با TaskRunner
                # اجرای async با TaskRunner
        try:
            from ..core.task_runner import TaskRunner
            
            self.is_running = True
            self.current_task = TaskRunner.run_async(
                func=self.executor.execute,
                args=(commands,),
                kwargs={"progress_callback": progress_callback},
                on_complete=on_complete
            )
            
            return {
                "success": True,
                "message": f"اجرای اسکریپت '{name}' آغاز شد",
                "total_commands": len(commands),
                "async": True
            }
            
        except Exception as e:
            self.is_running = False
            return {
                "success": False,
                "error": f"خطا در اجرای async: {str(e)}"
            }
    
    def cmd_stop(self) -> dict:
        """توقف اجرای فعلی"""
        if not self.is_running:
            return {
                "success": False,
                "error": "هیچ اسکریپتی در حال اجرا نیست"
            }
        
        # سیگنال توقف به executor
        self.executor.running = False
        
        # انتظار برای اتمام task
        if self.current_task:
            self.current_task.join(timeout=2.0)
        
        self.is_running = False
        self.current_task = None
        
        return {
            "success": True,
            "message": "اجرا متوقف شد"
        }
    
    def cmd_status(self) -> dict:
        """وضعیت فعلی executor"""
        return {
            "success": True,
            "is_running": self.is_running,
            "loaded_script": self.loaded,
            "total_scripts": len(self.scripts)
        }