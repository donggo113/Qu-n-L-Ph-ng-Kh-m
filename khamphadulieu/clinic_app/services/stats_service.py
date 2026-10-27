"""Thống kê cho biểu đồ Canvas: trả về dict {nhãn: giá trị} đã sắp xếp."""
from collections import defaultdict


def visits_by_day(visits) -> dict:
    out = defaultdict(int)
    for vs in visits:
        out[vs.date] += 1
    return dict(sorted(out.items()))


def revenue_by_month(visits) -> dict:
    out = defaultdict(float)
    for vs in visits:
        if vs.date:
            out[vs.date[:7]] += vs.total  # YYYY-MM
    return dict(sorted(out.items()))
