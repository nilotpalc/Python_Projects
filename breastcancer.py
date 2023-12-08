# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# %%
# show me the list of datasets in seaborn
sns.get_dataset_names()

# %%
# load the dataset flights
flights = sns.load_dataset('flights')

# %%
flights.head()

# %% [markdown]
# You can use the `load_*` functions from the `sklearn.datasets` module to load the built-in datasets in scikit-learn. To show the list of available datasets, you can use the `datasets.load_*?` command in a Jupyter notebook cell. This will display a help message with the available datasets. Here's an example:
# 
# 

# %%
# show the list of names of datasets in scikit learn
import sklearn.datasets as datasets

# show the list of available functions and attributes in the sklearn.datasets module as a list
dir(datasets)
# print(dir(datasets))

# %%
# load the breast_cancer dataset as a pandas dataframe
breast_cancer = datasets.load_breast_cancer(as_frame=True)
breast_cancer_df = breast_cancer.frame
breast_cancer_df.head()

# %%
# change the name of the target column to 'diagnosis'
# change the column type of 'diagnosis' to string
breast_cancer_df.rename(columns={'target': 'diagnosis'}, inplace=True)
breast_cancer_df['diagnosis'] = breast_cancer_df['diagnosis'].astype(str)

# %%
# change all 0 values in the 'diagnosis' column to 'malignant' and the balance values to 'benign'
breast_cancer_df["diagnosis"] = breast_cancer_df["diagnosis"].replace(
    {"0": "malignant", "1": "benign"}
)
breast_cancer_df.head()

# %%
# create a scatter plot using plotly express to visualize the relationship between the mean radius and mean texture
import plotly.express as px

fig = px.scatter(breast_cancer_df, x="mean radius", y="mean texture", color="diagnosis")

# display the plotly visual in the jupyter notebook
fig.show()

# %%
# create a dependence plot using plotly library to visualize the relationship between the mean radius and mean texture and colored by mean perimeter
import plotly.graph_objects as go
import plotly.express as px

fig = go.Figure(
    data=go.Scatter(
        x=breast_cancer_df["mean radius"],
        y=breast_cancer_df["mean texture"],
        mode="markers",
        marker=dict(
            color=breast_cancer_df["mean perimeter"],
            colorscale="Viridis",
            showscale=True,
        ),
    )
)
# generate a square plot for the fig object
fig.update_layout(width=500, height=500)
#  add the axis titles to the x and y axis for the fig object
fig.update_layout(xaxis_title="mean radius", yaxis_title="mean texture")
fig.show()

# %%
# create a dependence plot using matplotlib library to visualize the relationship between the mean radius and mean texture and show the legend as a colorbar
import matplotlib.pyplot as plt

plt.scatter(
    x=breast_cancer_df["mean radius"],
    y=breast_cancer_df["mean texture"],
    c=breast_cancer_df["mean perimeter"],
    cmap="viridis",
)
# show gridlines in the scatter plot
plt.grid()
# set the x and y axis labels
plt.xlabel("mean radius")
plt.ylabel("mean texture")

# add a title to the color bar with the label text rotated by 180 degrees
plt.colorbar(orientation='vertical').set_label("mean perimeter", rotation=-90,labelpad=15)

# create a variable for the dataset name
dataset_name = "Breast Cancer Dataset"

# add a title to the chart combining the "Chart for" with the name of the dataset
plt.title("Chart for " + dataset_name, pad=10)

# display the chart
plt.show()

# %%
# show the data type of a single column in the dataframe and return the data type as a string
aaa = breast_cancer_df["mean radius"].dtype

# convert aaa into a string value
bbb = str(aaa)
bbb



# %%
# copy data from clipboard
newdf = pd.read_clipboard()


