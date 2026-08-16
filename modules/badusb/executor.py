# FlipperWin/modules/badusb/executor.py
from pynput.keyboard import Controller, Key
import time
from typing import Callable, Dict, List
from core.task_runner import TaskResult

class DuckyExecutor:
    """اجراکننده واقعی دستورات DuckyScript"""
    
    def __init__(self):
        self.keyboard = Controller()
        self.running = False
    
    def execute(self, commands: List[Dict], progress_callback: Callable[[str], None] = None) -> TaskResult:
        """اجرای لیست دستورات با بازخورد پیشرفت"""
        result = TaskResult(success=False, data={
            'total_commands': len(commands),
            'executed': 0,
            'failed': []
        })
        
        self.running = True
        result.add_log(f"🚀 شروع اجرای {len(commands)} دستور...")
        
        try:
            for idx, cmd in enumerate(commands):
                if not self.running:
                    result.add_log("⏸️ اجرا توسط کاربر متوقف شد")
                    break
                
                # گزارش پیشرفت
                progress_percent = int((idx / len(commands)) * 100)
                progress_msg = f"[{progress_percent}%] اجرای دستور {idx+1}/{len(commands)}"
                
                if progress_callback:
                    progress_callback(progress_msg)
                
                result.add_log(f"➤ خط {cmd.get('line', '?')}: {cmd.get('type')}")
                
                # اجرای دستور
                try:
                    self._execute_command(cmd)
                    result.data['executed'] += 1
                except Exception as e:
                    error_msg = f"خطا در خط {cmd.get('line')}: {str(e)}"
                    result.data['failed'].append(error_msg)
                    result.add_log(f"❌ {error_msg}")
            
            result.success = True
            result.add_log(f"✅ اجرا کامل شد: {result.data['executed']}/{len(commands)} موفق")
            
        except Exception as e:
            result.error = str(e)
            result.add_log(f"❌ خطای کلی: {e}")
        
        finally:
            self.running = False
        
        return result
    
    def _execute_command(self, cmd: Dict):
        """اجرای یک دستور منفرد"""
        cmd_type = cmd.get('type')
        
        if cmd_type == 'delay':
            time.sleep(cmd['ms'] / 1000.0)
        
        elif cmd_type == 'string':
            self.keyboard.type(cmd['text'])
        
        elif cmd_type == 'key':
            key_str = cmd['key']
            if hasattr(Key, key_str):
                self.keyboard.press(getattr(Key, key_str))
                self.keyboard.release(getattr(Key, key_str))
            else:
                self.keyboard.press(key_str)
                self.keyboard.release(key_str)
        
        elif cmd_type == 'combo':
            modifiers = [getattr(Key, m) for m in cmd['modifiers']]
            key = cmd['key']
            
            # فشار modifier ها
            for mod in modifiers:
                self.keyboard.press(mod)
            
            # فشار کلید اصلی
            if hasattr(Key, key):
                self.keyboard.press(getattr(Key, key))
                self.keyboard.release(getattr(Key, key))
            else:
                self.keyboard.press(key)
                # FlipperWin/modules/badusb/executor.py (ادامه)
                self.keyboard.release(key)
            
            # رها کردن modifier ها به ترتیب معکوس
            for mod in reversed(modifiers):
                self.keyboard.release(mod)
            
            time.sleep(0.05)  # تاخیر کوچک بین کلیدها
