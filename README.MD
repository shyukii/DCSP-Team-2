# File structure

Please see below for the file structure. Read this please!

### Data

`dataextract.py` is a file used to connect to the Postgre server to create `dfs`. See note below.

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

