from qcreason.preparation import m2bp_formulas as mf
from qcreason.preparation import computation_activation_circuit as cac
from qcreason.preparation import operations_transform as ot
import json

ops = cac.get_hln_ca_operations(
    weightedFormulaDict={
        #"f1": ["and", ["imp", "b", "c"], ["not", "a"], True],
        "f2": ["or", "a", "c", -0.5]
    }
)

ampOps = ot.amplify_ones_state(ops, amplificationColors=["ancilla_(or_a_c)"], amplificationNum=2)

print(ampOps)
print(ot.extract_qubit_colors(ampOps))

specDict = {
    "operations": ampOps,
    "qubitColors": ot.extract_qubit_colors(ampOps)}

with open("test_ca_amp_ops.json", "w") as f:
    json.dump(specDict, f, indent=4)

# print(mf.extract_atoms_from_dict({
#         #"f1": ["and", ["imp", "b", "c"], ["not", "a"], True],
#         "f2": ["or", "a", "c", -0.5]
#     }))
#
# pass

#print(mf.generate_formula_operations(["imp", "b", "c"]))
#print(mf.generate_formula_operations(["imp", "a", ["or", "b", "c"]]))