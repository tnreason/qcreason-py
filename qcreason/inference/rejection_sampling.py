def filter_results(results, ancillaColors=["samplingAncilla"], keepColors=None):
    ## Drop the samples where one sampling ancilla is 0
    filtered_results = results[results[ancillaColors].sum(axis=1) == len(ancillaColors)]
    if keepColors is not None:
        return filtered_results[keepColors]
    else:
        return filtered_results

def compute_satisfaction(resultDf, weightedFormulas):
    from tnreason import application as tnapp
    from tnreason import engine as tneng

    empDistribution = tnapp.get_empirical_distribution(sampleDf=resultDf)
    satDict = dict()
    for formulaKey in weightedFormulas:
        satDict[formulaKey] = tneng.contract(
            {**empDistribution.create_cores(),
             **tnapp.create_cores_to_expressionsDict({formulaKey: weightedFormulas[formulaKey][:-1]})},
            openColors=[])[:] / empDistribution.get_partition_function()
    return satDict
