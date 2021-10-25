import pandas as pd
from joblib import load
from sklearn.preprocessing import LabelEncoder
from flask import Flask, render_template, request
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/box', methods=['POST'])
def box():
    message = [x for x in request.form.values()][0]

    model = load("model.joblib")
    encoder = LabelEncoder()
    
    url_to_covid = 'https://covid.ourworldindata.org/data/owid-covid-data.csv'
    df = pd.read_csv(url_to_covid)
    df_orig = df

    percent_missing = df.isnull().sum() * 100 / len(df)
    missing_value_df = pd.DataFrame({'column_name': df.columns,
                                     'percent_missing': percent_missing})
    cols_too_many_missing = missing_value_df[missing_value_df.percent_missing > 50].index.tolist()
    df = df.drop(columns=cols_too_many_missing)

    missing_iso_code = df[df.iso_code.isna()]
    df = df.drop(index=missing_iso_code.index)

    missing_continent = df[df.continent.isna()]
    df = df.drop(index=missing_continent.index)

    nominal = df.select_dtypes(include=['object']).copy()
    nominal_cols = nominal.columns.tolist()

    for col in nominal_cols:
        if df[col].isna().sum() > 0:
            df[col].fillna('MISSING', inplace=True)
        df[col] = encoder.fit_transform(df[col])

    numerical = df.select_dtypes(include=['float64']).copy()
    for col in numerical:
        df[col].fillna((df[col].mean()), inplace=True)

    X = df.drop(columns=['new_cases'])
    y = df.new_cases
    
    encoder.fit_transform(df_orig['location'])
    encode_ind = (encoder.classes_).tolist().index(message)
    to_pred = X[X.location == encode_ind].iloc[-1].values.reshape(1,-1)
    prediction = model.predict(to_pred)[0]

    return render_template("home.html", message=prediction)

if __name__ == '__main__':
    app.run(debug=True)
