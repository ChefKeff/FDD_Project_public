# How to update the ML models

## Follow this step-by-step instructions in order to update the machine learning models used in Solveig. ☀️

### Getting the formatted and pre-processed data

1. Navigate to ```../data_collection_preprocessing/collect_and_preprocess.py```.
2. Set the from- and to-dates to be used in the functions. These are the date in between which the data will be collected from the APIs.
   1. For the collection from the STRÅNG API the ```frm_strang``` & ```to_strang``` parameters need be set formatted as ```yyyy-mm-dd```.
   2. For the Metry API the ```frm_metry``` and ```to_metry``` parameters are to be set formatted as ```yyyymmdd```.
   3. The format and parameters are visible in the end of the ```.py```-file.
   4. Please select a from-date that is quite early (like 2019-05-01) in order to get better models!
3. After setting the desired interval - please run the functions in order and wait for the functions to finish running fully before running the next. The order is:
   1. ```get_solar_data_STRANG(frm,to)```
   2. ```get_metry_data(frm,to)```
   3. ```generate_csv_for_ml()```
4. Running these functions in order should yield a bunch of new files in the ```./meter_obs_and_irr```-folder, entiteled ```{metry_id}_irr_and_energy_data.csv```.

When this is done and the ```.csv```-files are in the correct folder, and they look something like this <br>
|FIELD1|date_time                |irradiance|generated_energy|city     |metry_meter_id          |
|------|-------------------------|----------|----------------|---------|------------------------|
|0     |2019-05-01 00:00:00+00:00|0.0       |0.0             |stockholm|5a2804c997c17600591d9418|
|1     |2019-05-01 01:00:00+00:00|0.0       |0.0             |stockholm|5a2804c997c17600591d9418|
|2     |2019-05-01 02:00:00+00:00|0.0       |0.0             |stockholm|5a2804c997c17600591d9418|
|3     |2019-05-01 03:00:00+00:00|0.0       |1.57            |stockholm|5a2804c997c17600591d9418|
|4     |2019-05-01 04:00:00+00:00|18.6      |7.58            |stockholm|5a2804c997c17600591d9418|

Then the first step is done! Good job!

### Using the collected and formatted data to create the machine learning models

1. Navigate to ```../machine_learning/ml_notebook.ipynb```
2. Run the cells (except those listed under "unused code").
3. The files in the ```../per_meter_models_energy``` should get updated - this means that the model has been retrained.

## Done

Any problems? <a href="mailto:norinderniklas@gmail.com">Contact me!</a>
