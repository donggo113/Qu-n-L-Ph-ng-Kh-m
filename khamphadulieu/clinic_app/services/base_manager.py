"""Lớp quản lý chung: add / get / update / delete / search."""


class BaseManager:
    PREFIX = "X"
    MODEL = None

    def __init__(self, storage):
        self.storage = storage
        self.items = [self.MODEL.from_dict(d) for d in storage.load()]

    # ---- nội bộ ----
    def _next_id(self) -> str:
        nums = []
        for it in self.items:
            tail = str(it.id)[len(self.PREFIX):]
            if tail.isdigit():
                nums.append(int(tail))
        return f"{self.PREFIX}{(max(nums) + 1) if nums else 1:03d}"

    def _save(self) -> None:
        self.storage.save([it.to_dict() for it in self.items])

    def validate(self, item) -> None:
        """Lớp con ghi đè; ném ValueError nếu dữ liệu sai."""

    # ---- CRUD ----
    def get_all(self):
        return list(self.items)

    def get(self, id):
        return next((it for it in self.items if it.id == id), None)

    def add(self, item):
        item.id = self._next_id()
        self.validate(item)
        self.items.append(item)
        self._save()
        return item

    def update(self, item):
        idx = next((i for i, it in enumerate(self.items) if it.id == item.id), None)
        if idx is None:
            raise ValueError("Không tìm thấy bản ghi để cập nhật")
        self.validate(item)
        self.items[idx] = item
        self._save()
        return item

    def delete(self, id) -> bool:
        before = len(self.items)
        self.items = [it for it in self.items if it.id != id]
        if len(self.items) == before:
            return False
        self._save()
        return True

    def search(self, keyword: str):
        kw = (keyword or "").strip().lower()
        if not kw:
            return self.get_all()
        return [it for it in self.items
                if any(kw in str(v).lower() for v in it.to_dict().values())]
