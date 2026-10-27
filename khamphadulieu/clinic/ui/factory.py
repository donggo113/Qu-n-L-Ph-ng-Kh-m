from .components import DataView


def make_view(title_add, data, cols, optional=()):
    """cols: (key, nhãn, độ rộng, kiểu[, danh sách chọn])"""
    keys = tuple(c[0] for c in cols)
    fields = [(c[1], c[0], c[3], *( [c[4]] if len(c) > 4 else [] )) for c in cols]
    labels = {c[0]: c[1] for c in cols}
    widths = {c[0]: c[2] for c in cols}

    class View(DataView):
        def __init__(self, parent):
            super().__init__(parent, list(data), keys, title_add, column_widths=widths,
                             form_fields=fields, detail_fields=fields, column_labels=labels,
                             optional_fields=optional)
    return View
