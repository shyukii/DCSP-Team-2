# File structure

Please see below for the file structure. Read this please! Some of the code might take a while to run - please be patient.

## Virtual Environment Setup

Before running any of the code in this repository, you should set up a virtual environment to manage dependencies. Follow these steps:

### For Windows:
```

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

### For macOS/Linux:
```
# Navigate to the project directory
cd path/to/DCSP-Team-2

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

To deactivate the virtual environment when you're done, simply run:
```
deactivate
```

### Data

`dataextract.py` is a file used to connect to the Postgre server to create `dfs`. Run this **first**. See note below.

`datavisualiser.py` is a jupyter notebook to explore some of the data.

`credentials.json` DO NOT TOUCH THIS FILE. Credentials for minIO

`minIO.py` This retrieves the various images from the MinIO bucket. Modify this later for integration with computer vision tech

Note: `dfs` is a dictionary containing the various dataframes related to our assignment. The keys are the different types of data (e.g. devicedata, errors etc) and the values are the tables of data itself (you can run standard pandas/numpy/seaborn exploration on these tables to get a better feel)

### Image Segmentation

`extraction_timing.py` a model that predicts the optimal compost extraction timing based on the NPK levels

### Green and Browns

`feed_recommender.py` is the file that recommends what is the optimal browns and greens ratio to give the worms.

### CO2 Forecasting

`carbondioxide_predictor.py` is the file we'll use to predict the level of CO2. To determine if a compost feed is eco-friendly.
