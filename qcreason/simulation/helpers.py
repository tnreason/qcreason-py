# def extract_qubit_colors(operationsList):
#     colors = set()
#     for op in operationsList:
#         if "target" in op:
#             for color in op["target"]:
#                 colors.add(color)
#         if "control" in op:
#             for color in op["control"].keys():
#                 colors.add(color)
#     return list(colors)

def extract_qubit_colors(operationsList):
    colors = set()
    for op in operationsList:
        colors.update(op.get("target", []))
        colors.update(op.get("control", {}).keys())
    return list(colors)