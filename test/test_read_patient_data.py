import unittest
from read_patient_data import (
    get_weights,
    has_insurance,
    get_fasting_glucose,
    get_hemoglobin_a1c,
)


class TestReadPatientData(unittest.TestCase):
    def test_get_hemoglobin(self):
        self.assertEquals(
            get_hemoglobin_a1c([["Hemoglobin A1c 5.1"]]), 5.1
        )  # without colon
        self.assertEquals(
            get_hemoglobin_a1c([["Hemoglobin A1c: 5.2"]]), 5.2
        )  # with colon
        self.assertEquals(get_hemoglobin_a1c([["a1c:"]]), 0.0)  # blank / not entered

        # only first non-empty answer is returned
        self.assertEquals(
            get_hemoglobin_a1c(
                # not valid  # expected  # ignored
                [["a1c:"], ["a1c 5.7"], ["a1c 6.2"]]
            ),
            5.7,
        )  # blank / not entered))

        self.assertEquals(
            get_hemoglobin_a1c(
                [
                    ["a1c: 5.5"], # should be 5.5%
                    ["a1c 5.7"],  # expected
                    ["a1c 6.2"],  # ignored
                ]
            ),
            5.5,
        )
        self.assertEquals(
            get_hemoglobin_a1c(
                [
                    ["a1c: "],  # should be 5.5%
                    ["a1c"],  # expected
                    ["a1c  "],  # ignored
                ]
            ),
            0.0,
        )

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
        patterns = [
            ["Insurance:", ""],
            ["Insurance: space_before", "space_before"],
            ["Insurance:space_after ", "space_after"],
            ["Insurance: before_after ", "before_after"],
        ]
        for line, expected in patterns:
            self.assertEquals(has_insurance([[line]]), expected)

    def test_get_fasting_glucose(self):
        patterns = [
            ["fasting glucose:", 0.0],
            ["Fasting Glucose: 5.2", 5.2],
            ["fasting glucose 5.4", 5.4],
            ["fasting glucose:4.7", 4.7],
            ["Fasting Glucose3.9", 3.9],
        ]
        for line, expected in patterns:
            self.assertEquals(get_fasting_glucose([[line]]), expected)
