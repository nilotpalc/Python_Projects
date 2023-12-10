# %%
import random
import math
import numpy as np
import pandas as pd

opg_stk_options = [50,100,150] # Opening Stock of N2 cylinders
lead_time_norm = [5,7,10] # No of Days between 2 PLTs
order_lot = [(50,4),(50,5)] # Order Lot Size and Replenishment Lead Time
ss = 5 # Safety Stock Levels for the Location

# Creating a combination of scenarios to run the simulation on PLT Lead Time and Pigging Opening Stock
scenario_list = []

for d in lead_time_norm:
    for k in opg_stk_options:
        for oo,tt in order_lot:
            scenario_list.append((d,k,oo,tt))

df_consol = pd.DataFrame(columns= ['Day Count','Opg_Stk', 'Cons_Qty', 'PLT Lead Time', 'On Order Qty', 'Receipt Qty',\
                                   'Supply Lead Time', 'Cls_Stk','Scenario','Max_Order_Limit','PLT_Lead_Time_Norm',\
                                   'Order_Lot','Order_Lead_Time_Norm','Stock_Out','SO_Delay_Count','SO_Category',\
                                   'SO_Days_Excess_SS'])

for d,k,oo,tt in scenario_list:

    # Simulating the Pigging Consumption, Ordering and Order Receipt days

    cons_day = 0 # Setting the start counter to zero

    z=700     # Defining the number of PLT and associated order-receipt cycles

    """
    Setting the initial parameters
    """
    cons_day_list = []
    order_day_list = []
    order_rec_list = []

    # Simulating the PLT Consumption and Order-Receipt Cycles
    n=0
        
    while n < z :
        plt_lead_time = random.randrange (d-1,d+2,1)
        cons_day += plt_lead_time
        if random.randrange (1,6) == 5:
            cons_qty = 100
        else:
            cons_qty = 50
        
        # Vendor places the order for replenishment the moment intimation is received for PLT
        order_day = cons_day - plt_lead_time 
        order_qty = cons_qty
        
        # adding integers to a list changes the type to string when used in a dataframe
        # creates a tuple (date of plt/order/receipt, qty, lead time)
        cons_day_list.append((cons_day,cons_qty,plt_lead_time))
        order_day_list.append((order_day,order_qty))
        
        # Receiving in multiples of lot sizes for bigger order sizes as per lead times advised by IMC
        order_rec_count = 0
        order_rec = order_day
        for i in range(math.ceil(order_qty/oo)):
                order_rec += random.randrange (tt-1,tt+2,1)
                order_bal = order_qty - oo*(order_rec_count)
                rec_qty = min (order_bal , oo)
                order_rec_list.append((order_rec,rec_qty,order_rec-order_day))
                order_rec_count +=1
        n += 1

    # Generating the data frame for N2 consumption
    df_cons = pd.DataFrame(cons_day_list,columns = ['Cons_Day','Cons_Qty','PLT Lead Time'])

    # Generating the data frame for N2 order placement
    df_ord_day = pd.DataFrame(order_day_list,columns = ['Order_Day','On Order Qty'])

    # Generating the data frame for N2 order receipts
    df_ord_rec = pd.DataFrame(order_rec_list,columns = ['Order_Rec_Day','Receipt Qty','Supply Lead Time'])
    # Aggregating for different orders being received on the same day
    df_ord_rec = df_ord_rec.groupby('Order_Rec_Day').agg({'Receipt Qty':'sum',"Supply Lead Time": 'max'})
    df_ord_rec.reset_index(inplace=True)

    """
    Combining multiple dataframes along with opening stock dataframe
    This is to link the day counter generated using the opening stock dataframe to \
    the other dataframes
    """
    # taking max of the days in cons_dataframe to create a total list of days to simulate
    df_op_stk = pd.DataFrame({"Opg_Stk":np.repeat(k,df_cons['Cons_Day'].max()+1)})
    df_op_stk.reset_index(inplace=True)
    df_op_stk.rename(columns={'index':"Day Count"},inplace=True)

    df_ops_cons = df_op_stk.merge(df_cons,left_on="Day Count",right_on="Cons_Day",how="left")
    df_ops_co_ord = df_ops_cons.merge(df_ord_day,left_on='Day Count',right_on='Order_Day',how='left')


    # Completing the final dataframe
    df_main = df_ops_co_ord.merge(df_ord_rec,left_on='Day Count',right_on='Order_Rec_Day',how='left')

    df_main.drop(['Cons_Day','Order_Day','Order_Rec_Day'],axis=1,inplace=True)

    df_main.fillna(0,inplace=True)
    df_main.set_index('Day Count',inplace=True)

    # Running a for loop to re-assign the opg_stock from the previous row except for the first row
    for i in range(len(df_main)):
        if i == 0:
            df_main.loc[i,"Opg_Stk"] = k
        else:
            df_main.loc[i,"Opg_Stk"] = df_main.loc[i-1,"Opg_Stk"] + df_main.loc[i-1,"Receipt Qty"]-df_main.loc[i-1,"Cons_Qty"]

    df_main['Cls_Stk'] = df_main['Opg_Stk']+df_main['Receipt Qty']-df_main['Cons_Qty']
    
    # Adding columns for Scenario Details
    df_main = df_main.assign(Scenario= lambda x: "Opg Stk of "+ str(k))
    df_main = df_main.assign(Max_Order_Limit = lambda x: k)
    df_main = df_main.assign(PLT_Lead_Time_Norm = lambda x: "PLT Lead Time of " + str(d))
    df_main = df_main.assign(Order_Lot = lambda x: "Order Lot of " + str(oo))
    df_main = df_main.assign(Order_Lead_Time_Norm = lambda x: "Order Lot Supply Time of " + str(tt))
    
    # Creating a column for indicating Stock Outs
    df_main = df_main.assign (Stock_Out = lambda x: 0)
    for i in range (len(df_main)):
        if df_main.loc[i,'Cons_Qty']>0:
            if df_main.loc [i,'Opg_Stk'] + df_main.loc [i,'Receipt Qty'] - df_main.loc[i,'Cons_Qty'] < 0:
                df_main.loc[i,"Stock_Out"] = 1
            else:
                df_main.loc[i,"Stock_Out"] = 0
        else:
            df_main.loc[i,"Stock_Out"] = 0
    
    # Creating a column for indicating the length of the Stock Outs
    df_main = df_main.assign (SO_Delay_Count = lambda x: 0)
    for i in range (len(df_main)):
        if df_main.loc[i,'Stock_Out'] == 1:
            z=0
            Qty_Recd = 0
            for a in range(i,len(df_main)):
                Qty_Recd += df_main.loc[a,"Receipt Qty"]
                if (df_main.loc[i,"Opg_Stk"] - df_main.loc[i,"Cons_Qty"] + Qty_Recd) < 0:
                    z+=1
                else:
                    break
                        
            df_main.loc[i,"SO_Delay_Count"] = z

        else:
            df_main.loc[i,"SO_Delay_Count"] = 0
    
    # Assigning Stock Out Category based on SS norms at location
    df_main = df_main.assign (SO_Category = lambda x: "No Stock Out")
    for i in range (len(df_main)):
        if df_main.loc[i,"SO_Delay_Count"] > 0:
            if df_main.loc[i,"SO_Delay_Count"] > 4:
                df_main.loc[i,"SO_Category"] = "Stock Out Days Greater Than or Equal to " + str(ss) + "D"
            else:
                df_main.loc[i,"SO_Category"] = "Stock Out Days Less Than " + str(ss) + "D"
        else:
            pass
    
    # Assigning Stock Out Category based on SS norms at location
    df_main = df_main.assign (SO_Days_Excess_SS = lambda x: 0)
    for i in range (len(df_main)):
        if df_main.loc[i,"Stock_Out"] == 1:
            df_main.loc[i,"SO_Days_Excess_SS"] = max(df_main.loc[i,"SO_Delay_Count"]-ss,0)
        else:
            pass
    
    df_consol = pd.concat([df_consol,df_main.reset_index()],ignore_index=True,join='inner')

df_consol.set_index('Day Count',inplace=True)

# %%
df_consol.reset_index().iloc[1000:1180]

# %%
df_consol.reset_index()[df_consol.reset_index()['SO_Delay_Count']>2].head()

# %%
df_consol.to_csv('Simulation_A_doc')

# %%
df_consol.columns

# %%
df_logreg = df_consol.loc[:,['Cons_Qty', 'PLT Lead Time', 'Order_Lead_Time_Norm','Stock_Out']].copy()
df_logreg['Order_Lead_Time_Norm'] = df_logreg['Order_Lead_Time_Norm'].apply(lambda x : int(x.split()[-1]))
df_logreg

# %%
df_logreg = df_logreg.reset_index()
df_logreg = df_logreg.drop('Day Count', axis = 1)

# %%
df_logreg['Stock_Out']

# %%
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(df_logreg.drop('Stock_Out',axis=1), 
                                                    df_logreg['Stock_Out'].astype('int'), test_size=0.30, 
                                                    random_state=101)

from sklearn.linear_model import LogisticRegression
logmodel = LogisticRegression()
logmodel.fit(X_train,y_train)

# %%
predictions = logmodel.predict(X_test)

# %%
from sklearn.metrics import classification_report
print(classification_report(y_test,predictions))

# %%
import statsmodels.api as sm
logit_model=sm.Logit(df_logreg['Stock_Out'].astype('int'),df_logreg.drop('Stock_Out',axis=1))
result=logit_model.fit()
print(result.summary())

# %%
print(np.exp(result.params))


