def title_filter(ws):
    ws.auto_filter.ref = ws.dimensions

def title_freeze_panes(ws, cell_point):
    ws.freeze_panes = cell_point