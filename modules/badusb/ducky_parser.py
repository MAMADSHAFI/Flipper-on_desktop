# FlipperWin/modules/badusb/ducky_parser.py
from typing import List, Dict, Tuple
import re

class DuckyParser:
    """پارسر Ducky Script با پشتیبانی کامل از دستورات"""
    
    # نقشه کلیدهای ویژه
    SPECIAL_KEYS = {
        'ENTER': '\n',
        'TAB': '\t',
        'ESCAPE': 'esc',
        'BACKSPACE': 'backspace',
        'DELETE': 'delete',
        'SPACE': ' ',
        'UP': 'up',
        'DOWN': 'down',
        'LEFT': 'left',
        'RIGHT': 'right',
        'HOME': 'home',
        'END': 'end',
        'PAGEUP': 'page_up',
        'PAGEDOWN': 'page_down',
        'CAPSLOCK': 'caps_lock',
        'F1': 'f1', 'F2': 'f2', 'F3': 'f3', 'F4': 'f4',
        'F5': 'f5', 'F6': 'f6', 'F7': 'f7', 'F8': 'f8',
        'F9': 'f9', 'F10': 'f10', 'F11': 'f11', 'F12': 'f12',
    }
    
    # نقشه modifier keys
    MODIFIERS = {
        'GUI': 'cmd',      # Windows key یا Command
        'WINDOWS': 'cmd',
        'COMMAND': 'cmd',
        'CTRL': 'ctrl',
        'CONTROL': 'ctrl',
        'SHIFT': 'shift',
        'ALT': 'alt',
        'OPTION': 'alt',
    }
    
    def parse(self, script_content: str) -> List[Dict]:
        """تبدیل Ducky Script به لیست دستورات قابل اجرا"""
        commands = []
        lines = script_content.strip().split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('REM') or line.startswith('//'):
                continue
            
            # Parse command
            cmd = self._parse_line(line, line_num)
            if cmd:
                commands.append(cmd)
        
        return commands
    
    def _parse_line(self, line: str, line_num: int) -> Dict:
        """پردازش یک خط از اسکریپت"""
        parts = line.split(None, 1)
        if not parts:
            return None
        
        keyword = parts[0].upper()
        args = parts[1] if len(parts) > 1 else ''
        
        # DELAY command
        if keyword == 'DELAY':
            try:
                ms = int(args)
                return {'type': 'delay', 'ms': ms, 'line': line_num}
            except ValueError:
                return {'type': 'error', 'msg': f'Invalid DELAY value: {args}', 'line': line_num}
        
        # STRING command
        if keyword == 'STRING':
            return {'type': 'string', 'text': args, 'line': line_num}
        
        # Special keys (ENTER, TAB, etc.)
        if keyword in self.SPECIAL_KEYS:
            return {'type': 'key', 'key': self.SPECIAL_KEYS[keyword], 'line': line_num}
        
        # Modifier combinations (GUI r, CTRL ALT DELETE)
        if keyword in self.MODIFIERS or ' ' in line:
            return self._parse_combo(line, line_num)
        
        return {'type': 'error', 'msg': f'Unknown command: {keyword}', 'line': line_num}
    
    def _parse_combo(self, line: str, line_num: int) -> Dict:
        """پردازش کلیدهای ترکیبی مانند GUI r یا CTRL-ALT-DELETE"""
        parts = line.upper().split()
        modifiers = []
        key = None
        
        for part in parts:
            if part in self.MODIFIERS:
                modifiers.append(self.MODIFIERS[part])
            elif part in self.SPECIAL_KEYS:
                key = self.SPECIAL_KEYS[part]
            else:
                key = part.lower()
        
        if not key and modifiers:
            key = modifiers.pop()
               
        return {
            'type': 'combo',
            'modifiers': modifiers,
            'key': key,
            'line': line_num
        }
    
    def validate(self, commands: List[Dict]) -> Tuple[bool, List[str]]:
        """اعتبارسنجی لیست دستورات و برگرداندن خطاها"""
        errors = []
        for cmd in commands:
            if cmd.get('type') == 'error':
                errors.append(f"خط {cmd['line']}: {cmd['msg']}")
        
        return len(errors) == 0, errors
