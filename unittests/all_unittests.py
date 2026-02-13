import unittest

from inference.test_rejection_forward import RejectionForwardTest
from inference.test_rejection_backward import RejectionBackwardTest
from inference.test_contraction import ContractionTest

from preparation.test_hln_augmentation import PreparationTest
from preparation.test_inversion import InversionTest
from preparation.test_deutsch_josza import DeutschJoszaTest
from preparation.test_phase_estimation import PhaseEstimationTest

unittest.main()


def suite():
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()

    test_classes = [
        RejectionForwardTest,
        RejectionBackwardTest,
        ContractionTest,
        PreparationTest,
        InversionTest,
        DeutschJoszaTest,
        PhaseEstimationTest
    ]

    for test_class in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(test_class))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())