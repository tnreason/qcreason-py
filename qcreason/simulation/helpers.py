def extract_qubit_colors(operationsList):
    colors = set()
    for op in operationsList:
        colors.update(op.get("target", []))
        colors.update(op.get("control", {}).keys())
    return list(colors)