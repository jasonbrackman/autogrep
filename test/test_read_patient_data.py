import unittest
from read_patient_data import get_weights, has_insurance


class TestReadPatientData(unittest.TestCase):
    def test_get_weights(self):
        groups01 = [
            [
                "Today's Weight: 200-222 lbs",
                "Peak Adult Weight: 200-444.0 lbs",
                "Intake Weight: 200-333.0lbs",
            ]
        ]

        groups02 = [
            [
                "Today's Weight: 222lbs",
                "Peak Adult Weight: 444 lbs",
                "Intake Weight: 333       lbs",
            ]
        ]

        for group in (groups01, groups02):
            int_weight, max_weight, min_weight = get_weights(group)
            assert int_weight == 333
            assert max_weight == 444
            assert min_weight == 222

    def test_has_insurance(self):
        empty = has_insurance([["Insurance:"]])
        space_before = has_insurance([["Insurance: space_before"]])
        space_after = has_insurance([["Insurance:space_after "]])
        assert empty == ''
        assert space_before == 'space_before'
        assert space_after == 'space_after'
