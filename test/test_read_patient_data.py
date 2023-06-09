import unittest
from read_patient_data import (
    get_intake_max_min_weights,
    has_insurance,
    get_fasting_glucose,
    get_hemoglobin_a1c,
    normalize_height,
    calculate_bmi,
    get_height_and_discrepancy,
)


class TestReadPatientData(unittest.TestCase):
    def test_get_hemoglobin_a1c_order(self):
        # only first non-empty answer is returned
        patterns = [
            [[["a1c:"], ["a1c 5.7"], ["a1c 6.2"]], 5.7],  # skip the first invalid num.
            [
                [["a1c: 5.5"], ["a1c 5.7"], ["a1c 6.2"]],
                5.5,
            ],  # take the first valid num.
            [[["a1c: "], ["a1c"], ["a1c  6.9"]], 6.9],  # take the last num
            [[["a1c:"], ["a1c"], ["a1c "]], 0.0],  # falls through for a default
        ]

        for group, expected in patterns:
            self.assertEquals(get_hemoglobin_a1c(group), expected)

    def test_get_hemoglobin_a1c_colon_and_without(self):
        patterns = [
            [[["Hemoglobin A1c 5.1"]], 5.1],  # without colon
            [[["Hemoglobin A1c: 5.2"]], 5.2],  # with colon
            [[["a1c:"]], 0.0],  # blank / data not entered
        ]

        for group, expected in patterns:
            self.assertEquals(get_hemoglobin_a1c(group), expected)

    def test_get_hemoglobin_a1c_with_dashes(self):
        group = [["A1c:6-7"]]
        assert get_hemoglobin_a1c(group) == 6.5

        group = [["a1c: 6.2-7"]]
        assert get_hemoglobin_a1c(group) == 6.6

    def test_get_hemoglobin_a1c_with_date(self):
        group = [["a1c:6.1 % 2023/feb/04"]]
        assert get_hemoglobin_a1c(group) == 6.1

    def test_get_hemoglobin_a1c_with_high_value(self):
        group = [["a1c: next measurement will be on the 17th"]]
        assert get_hemoglobin_a1c(group) == 0.0

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

    def test_get_intake_max_min_weights_extra_numbers(self):
        group = [
            [
                "Today's Weight: 568lbs down 2 lbs from last time",
                "Peak Adult Weight: 345 lbs  Date: 2021-12-08",
                "Intake Weight: 234  in dec 2021",
            ]
        ]
        int_weight, max_weight, min_weight = get_intake_max_min_weights(group)

        assert int_weight == 234.0
        assert max_weight == 568.0
        assert min_weight == 234.0

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

    def test_get_height_and_discrepancy(self):
        groups = [
            ([["Height: 4'5\"", "Height:135cm"]], 135, 0),
            ([["height:140 cm"]], 140, 0),
            ([["height: 136cm", "height: 134cm"]], 136, 2),
            ([["height 170cm and 5'10 and 160cm"]], 178, 18),
        ]
        for group, e_height, e_discrepancy in groups:
            height, discrepancy = get_height_and_discrepancy(group)
            assert height == e_height
            assert discrepancy == e_discrepancy

    def test_normalize_height(self):
        patterns = [
            [["4'11"], 150, 0],  # convert to cm, no diff obvs
            [["5'3", "5'3"], 160, 0],  # two of the same, no diff
            [["169 cm", "5'6"], 169, 1],  # mixed
            [["5'6", "169 cm"], 169, 1],  # mixed high / low
            [["5'0", "6'0"], 183, 31],  # Low / High in feet'inches"
            [["6'0", "5'0"], 183, 31],  # high/ low in feet'inches"
            [["165.1 cm", "165 cm", "165cm"], 165, 0],
        ]

        for heights, exp_total, exp_diff in patterns:
            i, j = normalize_height(heights)
            self.assertEquals(i, exp_total)
            self.assertEquals(j, exp_diff)

    def test_calculate_bmi_if_zero_files(self):
        height = 0
        weight = 0.0
        other = 10
        self.assertEquals(calculate_bmi(height, other), 0.0)  # odd to divide 0/10
        self.assertEquals(
            calculate_bmi(other, weight), 0.0
        )  # Any number divided by zero is zero.
        self.assertEquals(
            calculate_bmi(height, weight), 0.0
        )  # all zeros should result in zeros.
