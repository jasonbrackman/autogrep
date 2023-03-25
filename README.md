# autogrep
Parse data from collected text files.

[![Python package](https://github.com/jasonbrackman/autogrep/actions/workflows/python-test.yml/badge.svg?branch=master)](https://github.com/jasonbrackman/autogrep/actions/workflows/python-test.yml)

Data is defined as Encounters which are a collection of Visits.  Each Visit can involve the collection of information, sometimes, repeating the same information multiple times.
The purpose of this script is to normalize the data into tabular form.

Data processing collects:

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
- Fasting Glucose: float 
- A1c: float