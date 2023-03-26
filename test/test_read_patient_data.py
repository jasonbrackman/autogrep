import unittest
from read_patient_data import (
    get_intake_max_min_weights,
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
                    ["a1c: 5.5"],  # should be 5.5%
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

        group = [
            [
                "Today's Weight: 222lbs",
                "Peak Adult Weight: 444 lbs",
                "Intake Weight: 333       lbs",
            ]
        ]

        int_weight, max_weight, min_weight = get_intake_max_min_weights(group)
        assert int_weight == 333
        assert max_weight == 444
        assert min_weight == 222

    def test_get_intake_max_min_weights_with_dash(self):
        group = [
            [
                "Today's Weight: 200-222 lbs",
                "Peak Adult Weight: 200-444.0 lbs",
                "Intake Weight: 200-333.0lbs",
            ]
        ]

        int_weight, max_weight, min_weight = get_intake_max_min_weights(group)
        assert int_weight == 333
        assert max_weight == 444
        assert min_weight == 222

    def test_get_intake_max_min_weights_without_lbs(self):
        group = [
            [
                "Today's Weight: 222",
                "Peak Adult Weight: 444 ",
                "Intake Weight:333       lbs",
            ]
        ]

        int_weight, max_weight, min_weight = get_intake_max_min_weights(group)
        assert int_weight == 333.0
        assert max_weight == 444.0
        assert min_weight == 222.0

    def test_get_intake_max_min_weights_all_zeroes(self):
        group = [
            [
                "Today's Weight: 0",
                "Peak Adult Weight: 0 ",
                "Intake Weight:0       lbs",
            ]
        ]

        int_weight, max_weight, min_weight = get_intake_max_min_weights(group)
        assert int_weight == 0.0
        assert max_weight == 0.0
        assert min_weight == 0.0

    def test_get_intake_max_min_weights_missing_intake(self):
        group = [
            [
                "Today's Weight: 568lbs",
                "Peak Adult Weight: 345 lbs",
                "Intake Weight: ",  # no intake weight
            ],
            [
                "Today's Weight: 222lbs",
                "Peak Adult Weight: 444 lbs",
                "Intake Weight: ",  # no intake weight
            ],
        ]
        int_weight, max_weight, min_weight = get_intake_max_min_weights(group)

        assert int_weight == 0.0
        assert max_weight == 568.0
        assert min_weight == 222.0

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

    def test_get_hemoglobin_a1c_with_dashes(self):
        group = [["A1c:6-7"]]
        assert get_hemoglobin_a1c(group) == 6.5