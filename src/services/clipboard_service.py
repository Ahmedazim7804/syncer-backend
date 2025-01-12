from src.repository import ClipboardRepository

class ClipboardService():
    def __init__(self, clipboard_repository: ClipboardRepository):
        self.clipboard_repository = clipboard_repository
    
    def addClipboard(self, clipboard: str, username: str) -> bool:
        return self.clipboard_repository.addClipboardItem(clipboard, username)

    
