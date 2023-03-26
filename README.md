# Autogrep

Parse and normalize 'data' from collected text files.

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Python package](https://github.com/jasonbrackman/autogrep/actions/workflows/python-test.yml/badge.svg?branch=master)](https://github.com/jasonbrackman/autogrep/actions/workflows/python-test.yml)

Autogrep's goal is to parse and normalize data from text files.  Each file consists of `Encounters`
that are made up of `Visits`. Each `Visit` contains lines of information, which may have 
spelling errors, variants for entries that should only be entered once, and non-standard units.

The focus is on cleaning up and standardizing the data so that it can be easily processed and 
analyzed. 

The information collected (and its type) includes the following:

- MRN: str
- Encounters: int
- Recent Visit Date: str 
- Intake Visit Date: str
- Intake WeightLBS: float
- Max WeightLBS: float
- Min WeightLBS: float
- HeightCM: int
- Height_Low_Err: int 
- Intake BMI: float
- Max BMI: float
- Min BMI: float
- Smoker: bool
- Insurance: str
- Latest Fasting Glucose: float 
- Latest A1c: float
- Comorbidities: str
- Obesity Medications: str

### Requirements
Python 3.8+

### To Use
The script should be placed in the same directory as the .txt files

MacOS - From a terminal window in the directory type: `python3 read_patient_data.py`

Windows - From a command window in the directory type: `py -3 read_patient_data.py`

When complete a patient_data.csv will be generated in the same folder.  If the file already 
exists it will be overwritten.

### Errors
Errors parsing a file will not stop the script.  Instead, it will skip the file and
try the next one.  If you want to cancel, use CTRL+C OR close the window.

NOTE: if errors ARE encountered, The file that the error occurred on, the error type, and 
some line numbers will be produced. They can be used to resolve the issue(s) later.
