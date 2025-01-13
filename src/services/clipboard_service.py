from src.repository import ClipboardRepository
from src.core.metadata import OPPOSITE_USER
from src.schema import ClipboardItem

class ClipboardService():
    def __init__(self, clipboard_repository: ClipboardRepository):
        self.clipboard_repository = clipboard_repository
    
    def addClipboard(self, clipboard: str, username: str) -> bool:
        return self.clipboard_repository.addClipboardItem(clipboard, username)

    def getClipboards(self, username: str):

        # TODO: uncomment below line
        # other_user = OPPOSITE_USER[username]

        clipboardItems: list[ClipboardItem] = self.clipboard_repository.getAllClipboards(username=username);

        return [item.content for item in clipboardItems]
    
