# Autogrep

Parse and normalize 'data' from collected text files.

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