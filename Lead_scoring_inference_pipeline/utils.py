'''
filename: utils.py
functions: encode_features, load_model
creator: shashank.gupta
version: 1
'''

###############################################################################
# Import necessary modules
# ##############################################################################

import mlflow
import mlflow.sklearn
import pandas as pd

import sqlite3

import os
import logging

from datetime import datetime
from Lead_scoring_inference_pipeline.constants import *
#from constants import *
import time



def check_if_table_has_value(cnx, table_name):
    # cnx = sqlite3.connect(db_path+db_file_name)
    check_table = pd.read_sql(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';", cnx).shape[0]
    if check_table == 1:
        return True
    else:
        return False

###############################################################################
# Define the function to train the model
# ##############################################################################


def encode_features():
    '''
    This function one hot encodes the categorical features present in our  
    training dataset. This encoding is needed for feeding categorical data 
    to many scikit-learn models.

    INPUTS
        db_file_name : Name of the database file 
        db_path : path where the db file should be
        ONE_HOT_ENCODED_FEATURES : list of the features that needs to be there in the final encoded dataframe
        FEATURES_TO_ENCODE: list of features  from cleaned data that need to be one-hot encoded
        **NOTE : You can modify the encode_featues function used in heart disease's inference
        pipeline for this.

    OUTPUT
        1. Save the encoded features in a table - features

    SAMPLE USAGE
        encode_features()
    '''
    try:
        cnx = sqlite3.connect(DB_PATH+DB_FILE_NAME)
        if not check_if_table_has_value(cnx,'features'):
                print("model_input Exists")
                df = pd.read_sql('select * from model_input', cnx)


                # Implement these steps to prevent dimension mismatch during inference
                encoded_df = pd.DataFrame(columns= ONE_HOT_ENCODED_FEATURES) # from constants.py
                placeholder_df = pd.DataFrame()

                # One-Hot Encoding using get_dummies for the specified categorical features
                for f in FEATURES_TO_ENCODE:
                    if(f in df.columns):
                        encoded = pd.get_dummies(df[f])
                        encoded = encoded.add_prefix(f + '_')
                        placeholder_df = pd.concat([placeholder_df, encoded], axis=1)
                    else:
                        print('Feature not found')
                        # return df

                # Implement these steps to prevent dimension mismatch during inference
                for feature in encoded_df.columns:
                    if feature in df.columns:
                        encoded_df[feature] = df[feature]
                    if feature in placeholder_df.columns:
                        encoded_df[feature] = placeholder_df[feature]

                encoded_df.fillna(0,inplace=True)


                encoded_df.to_sql(name='features', con=cnx,if_exists='replace',index=False)
                print('features created/replaced')
        else:
            print("features already exists")
    except Exception as e:
        print (f'Exception thrown in encode_features : {e}')
    finally:
        if cnx:        
            cnx.close()

###############################################################################
# Define the function to load the model from mlflow model registry
# ##############################################################################

def get_models_prediction():
    '''
    This function loads the model which is in production from mlflow registry and 
    uses it to do prediction on the input dataset. Please note this function will the load
    the latest version of the model present in the production stage. 

    INPUTS
        db_file_name : Name of the database file
        db_path : path where the db file should be
        model from mlflow model registry
        model name: name of the model to be loaded
        stage: stage from which the model needs to be loaded i.e. production


    OUTPUT
        Store the predicted values along with input data into a table

    SAMPLE USAGE
        load_model()
    '''
    try:
        mlflow.set_tracking_uri(TRACKING_URI)
        cnx = sqlite3.connect(DB_PATH + DB_FILE_NAME)
        
        
        # Load model as a PyFuncModel.
        print('Loading model from mlflow, using production model')
        model_uri = f"models:/{MODEL_NAME}/{STAGE}"
        print('Model url ' + model_uri)
        loaded_model = mlflow.sklearn.load_model(model_uri)
        
        
        # Predict on a Pandas DataFrame.
        print('Loading features  from table')
        X = pd.read_sql('select * from features', cnx)
        print('Making Prediction')
        predictions = loaded_model.predict(pd.DataFrame(X))
        pred_df = X.copy()

        pred_df['app_complete_flag'] = predictions
        pred_df.to_sql(name='predictions', con=cnx,if_exists='replace',index=False)
        print("Predictions are done and create/replaced Table")
    except Exception as e:
        print (f'Exception thrown in get_models_prediction : {e}')
    finally:
        if cnx:        
            cnx.close()

###############################################################################
# Define the function to check the distribution of output column
# ##############################################################################

def prediction_ratio_check():
    '''
    This function calculates the % of 1 and 0 predicted by the model and  
    and writes it to a file named 'prediction_distribution.txt'.This file 
    should be created in the ~/airflow/dags/Lead_scoring_inference_pipeline 
    folder. 
    This helps us to monitor if there is any drift observed in the predictions 
    from our model at an overall level. This would determine our decision on 
    when to retrain our model.
    

    INPUTS
        db_file_name : Name of the database file
        db_path : path where the db file should be

    OUTPUT
        Write the output of the monitoring check in prediction_distribution.txt with 
        timestamp.

    SAMPLE USAGE
        prediction_col_check()
    '''
    try:
        cnx = sqlite3.connect(DB_PATH + DB_FILE_NAME)
        print('Loading predictions table')
        pred = pd.read_sql('select * from predictions', cnx)
        pct_ones = round(pred['app_complete_flag'].sum() / pred['app_complete_flag'].count() * 100, 2) 
        pct_zeroes = 100 - pct_ones
        f = open(FILE_PATH, "a")
        f.write(f"Prediction ratio for the date {time.ctime()} for Ones % {pct_ones} and Zeroes % {pct_zeroes}\n")
        f.close()
        print(f"Prediction ratio for the date {time.ctime()} for Ones % {pct_ones} and Zeroes % {pct_zeroes}")
    except Exception as e:
        print (f'Exception thrown in prediction_ratio_check : {e}')
    finally:
        if cnx:        
            cnx.close()

###############################################################################
# Define the function to check the columns of input features
# ##############################################################################


def input_features_check():
    '''
    This function checks whether all the input columns are present in our new
    data. This ensures the prediction pipeline doesn't break because of change in
    columns in input data.

    INPUTS
        db_file_name : Name of the database file
        db_path : path where the db file should be
        ONE_HOT_ENCODED_FEATURES: List of all the features which need to be present
        in our input data.

    OUTPUT
        It writes the output in a log file based on whether all the columns are present
        or not.
        1. If all the input columns are present then it logs - 'All the models input are present'
        2. Else it logs 'Some of the models inputs are missing'

    SAMPLE USAGE
        input_col_check()
    '''
    try:

        # Creating an object
        logger = logging.getLogger()

        cnx = sqlite3.connect(DB_PATH + DB_FILE_NAME)
        print('Loading features table')
        features = pd.read_sql('select * from features', cnx)
        cnx.close()

        if list(features.columns) == ONE_HOT_ENCODED_FEATURES:
            logger.info('All the models input are present')
            print('All the models input are present')
        else:
            logger.error('Some of the models inputs are missing')
            priint('All the models input are present')

    except Exception as e:
        print (f'Exception thrown in input_col_check : {e}')
    finally:
        if cnx:        
            cnx.close()
    
    
