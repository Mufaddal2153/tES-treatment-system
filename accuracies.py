from sklearn.metrics import accuracy_score
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_validate, KFold
from sklearn.multioutput import MultiOutputClassifier
from sklearn.ensemble import RandomForestClassifier

data1 = pd.read_csv("Electrode Dataset.csv")
data2 = pd.read_csv("Prescription Data.csv")

data1['Disease'].replace(['Depression','schizophrenia','Parkinson disease','Stroke','Aphasia','Dystonia','ataxia','Dysphagia'], [0,1,2,3,4,5,6,7], inplace=True)
data2['Disease'].replace(['Depression','Schizophrenia','Parkinson\'s Disease','Stroke','Aphasia','Dystonia','Ataxia','Dysphagia'], [0,1,2,3,4,5,6,7], inplace=True)

data1.drop('Unnamed: 5',axis=1,inplace=True)
data2.drop('Unnamed: 4',axis=1,inplace=True)

data2 = data2.astype({'Voltage':str,'Time Duration':str,'No. of Sessions':str})

## Electrode
X1 = data1[['Disease']]
y1 = data1.drop('Disease', axis=1)

X1_train, X1_test, y1_train, y1_test = train_test_split(X1, y1, test_size=0.2)

DT = MultiOutputClassifier(RandomForestClassifier(random_state=42,class_weight="balanced"))
DT.fit(X1,y1)

k_fold = KFold(n_splits=5, shuffle=True, random_state=42)

scores = cross_validate(DT, X1_train, y1_train, cv=k_fold, scoring=['f1_weighted'])

# y_pred = DT.predict(X1_test)

# print(f"Accuracy of electrode data with Decision Tree is: {accuracy_score(y_test, y_pred)*100}")