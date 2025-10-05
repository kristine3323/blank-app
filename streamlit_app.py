import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime,date
import matplotlib.pyplot as plt

'''
# This is a rough check for your payroll 
_(China version) deducting pt @5,000_
'''

x = st.slider('牛马费',0.0,100000.0,18000.0,1000.0)
st.write('Okay so confirmed that your monthly wage is:',x)

tax_disc = st.number_input('个税减免',0,10000,0,1)
st.write("Okay so confirmed that your monthly tax discount is:",tax_disc)

house_disc = st.number_input('社保公积金')
st.write("Okay so confirmed that your monthly house fund is:",house_disc)

tax_rates = [
    (0,36000,0.03,0),
    (36000, 144000, 0.10, 2520),
    (144000, 300000, 0.20, 16920),
    (300000, 420000, 0.25, 31920),
    (420000, 660000, 0.30, 52920),
    (660000, 960000, 0.35, 85920),
    (960000, np.inf, 0.45, 181920)
]

year = datetime.now().year
df = pd.DataFrame({
    'Month': [date(year,i,1) for i in range(1,13)],
    'Monthly Payroll': x,
    'Taxable income': x - 5000.0 - tax_disc - house_disc,}
)
df.set_index("Month",inplace=True)

df['Accumulated Taxable income'] = df['Taxable income'].cumsum()

def calculate_tax(row):
    # 累计预扣法计算公式
    cumulative_income = row['Accumulated Taxable income']
    tax = 0
    for rate in tax_rates:
        if cumulative_income > rate[0]:
            tax += (min(cumulative_income, rate[1]) - rate[0]) * rate[2] - rate[3]*0
    return tax

df['Acc tax amount']=df.apply(calculate_tax,axis=1)

#添加税率区间
def get_tax_rate(row):
    cumulative_income = row['Accumulated Taxable income']
    tax_rate = f"免税区间"
    for rate in tax_rates:
        if cumulative_income > rate[0]:
            tax_rate = f"{rate[0]}-{rate[1]}元 ({rate[2]*100}%)"
    return tax_rate


df['Monthly tax'] = df['Acc tax amount'].diff().fillna(0)
df['Monthly tax'][0]=df['Acc tax amount'][0]

df['Monthly income'] = df['Monthly Payroll'] - df['Monthly tax'] - house_disc

result_df = df[['Accumulated Taxable income','Acc tax amount','Monthly income']]
result_df['Rate Range']=df.apply(get_tax_rate, axis=1)

config={
    "_index":st.column_config.DateColumn("Month",format = "MMM")
}

st.dataframe(result_df,column_config=config)
