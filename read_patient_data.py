import copy
import csv
import os
import re
import sys
from typing import List, Tuple, Iterable, Set


Visit = List[str]
Encounters = List[Visit]


LBS_PATTERN = re.compile(
    r"\d+\.?\d+\s*lbs"
)  # matches weight values in pounds (e.g., "150 lbs").
MED_PATTERN = re.compile(
    r"(?:ozempic|vyvanse|succenda)?"  # Match keywords (optional)
    r"\s+"  # Match one or more whitespace characters
    r"(?:at\s+)?"  # Match 'at' keyword followed by one or more whitespace characters (optional)
    r"(?:\d+\.)?"  # Match one or more digits followed by a decimal point (optional)
    r"\d+"  # Match one or more digits
    r"\s*mg\s"  # Match 'mg' keyword preceded by one or more whitespace characters
    r"(?:ozempic|vyvanse|succenda)?",  # Match keywords (optional)
    re.IGNORECASE,
)  # matches medication values in milligrams (e.g., "5mg OZEMPIC").

HEIGHT_PATTERN = re.compile(
    r"\d+(?:\.\d+)?\s*cm"
)  # matches height values in centimeters (e.g., "170cm").
SMOKE_PATTERN = re.compile(
    r"[sS]moker[:|\s*][-|\s*]"
)  # matches smoking-related keywords (e.g., "smoker:").
FLOAT_PATTERN = re.compile(
    r"\d+(?:\.\d+)?"
)  # matches floating point values (e.g., "3.14").
ALCOHOL_PATTERN = re.compile(
    r"(?:^|\. )([^.\n]*\balcohol\b[^.\n]*\.)\s*", re.IGNORECASE
)  # matches alcohol-related keywords (e.g., "alcohol").


def get_obesity_medications(encounters: Encounters) -> str:
    """searches for medications related to obesity in a patient's medical records and returns the
    medication name, amount, and unit of measurement."""
    drug = ""
    amount = ""
    unit = ""
    for row in _yield_from_rows(encounters):
        if "Obesity Medications:" in row:
            results = re.findall(MED_PATTERN, row)
            if results:
                for result in results:
                    info: List[str] = result.replace("at", "").strip().split()
                    if len(info) == 3:
                        for r in info:
                            if "." in r or r.isdigit():
                                amount = r
                            elif "mg" in r:
                                unit = r
                            else:
                                drug = r

                    return f"{drug.capitalize()} ({amount} {unit})"
    return ""


def get_comorbidity(encounters: Encounters) -> Set[str]:
    """
    Searches for comorbidities (other health conditions that a patient has in addition to the primary health
    condition) in a patient's medical records and returns a set of comorbidities.
    """
    start_recording = False
    interesting = set()
    for row in _yield_from_rows(encounters):
        if start_recording is True:
            stripped = row.strip()
            if stripped:
                interesting.add(stripped)
            if stripped == "":
                start_recording = False

        if "Comorbidities:" in row:
            start_recording = True
    return interesting


def _yield_from_rows(encounters: Encounters) -> Iterable[str]:
    """Yields each row from all encounters from recent to oldest."""
    for visit in encounters:
        for row in visit:
            yield row


def get_hemoglobin_a1c(encounters: Encounters) -> float:
    """searches for the latest Hemoglobin A1c (a blood test used to measure blood sugar levels over the
    last 2-3 months) reading in a record and returns the value as a float."""
    """Returns the latest A1c reading."""
    for row in _yield_from_rows(encounters):
        row = row.lower()
        if "a1c" in row:
            row = row.replace("a1c", "")
            floats = [
                float(f)
                for f in re.findall(FLOAT_PATTERN, row)
                if float(f) < 17 and not f.startswith("0")
            ]
            if floats:
                return round(sum(floats) / len(floats), 1)
    return 0.0


def has_insurance(encounters: Encounters) -> str:
    """Searches for insurance information in a patient's medical records and returns the information as a string."""
    for row in _yield_from_rows(encounters):
        if "Insurance:" in row:
            details = row.split("Insurance:")
            if len(details) > 1:
                return details[1].strip()


def get_alcohol(encounters: Encounters) -> str:
    """Searches for alcohol consumption information in a record and returns the information as a string."""
    items = []
    for row in _yield_from_rows(encounters):
        if row.startswith("Alcohol:"):
            items.append(row)
        else:
            results = re.findall(ALCOHOL_PATTERN, row)
            items += results
    if items:
        return items[0]  # only returns the most recent mention of alcohol
    return "0 Servings"


def get_fasting_glucose(encounters: Encounters) -> float:
    """Searches for the latest fasting glucose (a blood test used to measure glucose levels in the blood after
    fasting) reading in a record and returns the value as a float."""
    for row in _yield_from_rows(encounters):
        if "fasting glucose" in row.lower() or "glucose fasting" in row.lower():
            result = re.findall(FLOAT_PATTERN, row)
            if result:
                return float(result[0])
    return 0.0


def is_smoker(encounters: Encounters) -> str:
    """Searches for smoking related information in a record and returns the information as a string."""
    for row in _yield_from_rows(encounters):
        smoker = re.findall(SMOKE_PATTERN, row)
        if smoker:
            return row.replace(smoker[0], "").strip()
    return ""


def normalize_height(heights: List[str]) -> Tuple[int, int]:
    """normalizes height values (in centimeters) by converting any height values in feet and inches to
    centimeters and returns the normalized height as a tuple of integers (height, difference bw/low and high)."""
    INCHES_TO_CMS = 2.54
    new_heights = set()
    for height in heights:
        height = height.replace("cm", "").strip()
        height = height.replace('"', "")
        feet_inches = height.split("'")
        if len(feet_inches) == 2:
            feet, inches = feet_inches
            feet = float(feet.strip()) * 12
            inches = float(inches.strip())
            height = (feet + inches) * INCHES_TO_CMS

        else:
            height = float(height.strip())
        new_heights.add(round(height))
    low = min(new_heights) if new_heights else 0
    high = max(new_heights) if new_heights else 0
    return high, high - low


def _get_weights_for_visit(visit: Visit) -> Tuple[float, float, float]:
    # today, peak, intake
    a, b, c = 0.0, 0.0, 0.0
    for line in visit:
        if line.startswith(("Today's Weight:", "Current Weight:")):
            a = _get_float_from_weight_line(line)
        elif line.startswith("Peak Adult Weight:"):
            b = _get_float_from_weight_line(line)
        elif line.startswith("Intake Weight:"):
            c = _get_float_from_weight_line(line)

    return float(a), float(b), float(c)


def _get_float_from_weight_line(line: str) -> float:
    # weight line may or may not contain a range using a '-', such as 100-110
    # weight line may or may not contain a decimal, such as 100.5
    # weight line may or may not contain lbs at the end, such as 100.5 lbs

    MIN_WEIGHT = 100  # often descriptors are provided, such as 'down by 2 lbs'
    MAX_WEIGHT = 1000  # often the year is provided on this line.

    line = line.replace("lbs", "")
    # often contains a date on the same line
    line = line.lower().split("date:")[0]

    result = [
        float(r)
        for r in re.findall(FLOAT_PATTERN, line)
        if MIN_WEIGHT < float(r) < MAX_WEIGHT
    ]
    if result:
        return result[-1]  # always take the last number

    return 0.0


def split_into_encounters(lines: List[str]) -> Encounters:
    """Takes a list of strings and splits them into separate encounters, based on the
    presence of the "ID:" line. Each encounter is stored as a separate list of strings
    within the encounters list."""
    encounters = []
    visit = []
    for line in lines:
        visit.append(line)
        if line.startswith("ID:"):
            if len(visit) > 2:
                encounters.append(copy.deepcopy(visit))
                visit = visit[-2:]
    if visit:
        encounters.append(visit)
    return encounters


def find_height(encounters: Encounters) -> Tuple[int, int]:
    """Searches through the encounters for the patient's height and returns it along with the height discrepancy."""
    heights = []
    for row in _yield_from_rows(encounters):
        results = re.findall(HEIGHT_PATTERN, row)
        if results:
            heights += results

    height, discrepancy = normalize_height(heights)
    return height, discrepancy


def calculate_bmi(height_cm: int, weight_lbs: float) -> float:
    """calculates and returns the patient's BMI based on their height and weight.."""
    kilos = weight_lbs / 2.205
    meters = height_cm / 100
    result = round(kilos / meters**2, 1) if kilos > 0 and meters > 0 else 0.0
    return result


def get_recent_intake_dates(visit: Visit) -> Tuple[str, str]:
    """Extracts the most recent and the intake visit dates for a given encounter."""
    dates = [line.split()[2] for line in visit if line.startswith("Visit Date:")]
    DEFAULT = "0000-00-00"
    recent, intake = DEFAULT, DEFAULT
    if len(dates) >= 2:
        recent = dates[0]
        intake = dates[-1]
    return recent, intake


def get_intake_max_min_weights(encounters: Encounters) -> Tuple[float, float, float]:
    """Calculates the maximum, minimum, and intake weight for a patient across all their encounters."""
    max_weight = 0.0
    min_weight = sys.maxsize
    intake_weight = 0.0
    for visit in encounters:
        weights = _get_weights_for_visit(visit)
        if weights and max(weights) > max_weight:
            max_weight = max(weights)

        # min() relies on a non-empty container
        reduced_weights = [w for w in weights if w > 0]
        if reduced_weights:
            minimum_non_zero_weights = min(reduced_weights)
            if minimum_non_zero_weights < min_weight:
                min_weight = minimum_non_zero_weights

        if weights[2] != 0.0:
            intake_weight = max(intake_weight, weights[2])

    # if all defaults, min_weight will still be maxsize! Let's correct that.
    min_weight = min_weight if min_weight is not sys.maxsize else 0.0

    return intake_weight, max_weight, min_weight


def main():
    """reads text files in the current directory, processes the text data, and stores
    the extracted information for each patient in a dictionary. The dictionaries are
    stored in a list, which is then written to a CSV file."""
    datasheets = []

    for file in os.listdir("."):
        if file.endswith(".txt"):
            try:
                datasheet = {}
                with open(file) as handle:

                    lines = handle.read()
                    lines = lines.replace(
                        "\u200c", ""
                    )  # problem introduced in data collection
                    lines = lines.split("\n")
                    encounters = split_into_encounters(lines)
                    encounters_count = len(encounters)
                    # start collecting data across the encounters
                    intake_weight, max_weight, min_weight = get_intake_max_min_weights(
                        encounters
                    )
                    height, discrepancy = find_height(encounters)

                    recent_date, intake_date = get_recent_intake_dates(lines)
                    datasheet["MRN"] = os.path.splitext(file)[0]
                    datasheet["Encounters"] = encounters_count
                    datasheet["Recent Visit Date"] = recent_date
                    datasheet["Intake Visit Date"] = intake_date
                    datasheet["Intake WeightLBS"] = intake_weight
                    datasheet["Max WeightLBS"] = max_weight
                    datasheet["Min WeightLBS"] = min_weight
                    datasheet["HeightCM"] = height
                    datasheet["Height_Low_Err"] = discrepancy
                    datasheet["Intake BMI"] = calculate_bmi(height, intake_weight)
                    datasheet["Max BMI"] = calculate_bmi(height, max_weight)
                    datasheet["Min BMI"] = calculate_bmi(height, min_weight)
                    datasheet["Smoker"] = is_smoker(encounters)
                    datasheet["Insurance"] = has_insurance(encounters)
                    datasheet["Latest Fasting Glucose"] = get_fasting_glucose(
                        encounters
                    )
                    datasheet["Latest A1c%"] = get_hemoglobin_a1c(encounters)
                    datasheet["Comorbidity"] = ";".join(get_comorbidity(encounters))
                    datasheet["Obesity Medications"] = get_obesity_medications(
                        encounters
                    )
                    datasheet["Latest Alcohol"] = get_alcohol(encounters)

                datasheets.append(copy.deepcopy(datasheet))
            except Exception as e:
                tb = e.__traceback__
                while tb.tb_next:
                    tb = tb.tb_next
                lineno = tb.tb_lineno
                print(
                    f"Couldn't process {file}: {e} from ln.{e.__traceback__.tb_lineno} that came from: ln.{lineno}"
                )

    return datasheets


if __name__ == "__main__":
    datasheets = main()
    if datasheets:
        with open("patient_data.csv", "w") as handle:
            w = csv.DictWriter(handle, datasheets[0].keys())
            w.writeheader()
            for ds in datasheets:
                w.writerow(ds)
