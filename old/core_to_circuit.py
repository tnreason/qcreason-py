from qcreason.reasoning import generic_contraction as gc

from tnreason import engine as tnengine

import numpy as np

core1 = tnengine.get_core("NumpyCore")(
    values=np.random.rand(2, 2),
    colors=["red", "blue"]
)

core2 = tnengine.get_core("NumpyCore")(
    values=np.random.rand(2, 2),
    colors=["sledz", "blue"]
)

pandascore = gc.QCReasonParticleContractor(coreDict={"feature1": core1, "feature2": core2}, openColors=["red", "sledz"],
                                           specDict={"shots": 10000}).contract()
print(pandascore.values)
print(tnengine.convert(pandascore, "NumpyCore").values)