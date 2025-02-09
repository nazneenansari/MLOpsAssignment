##############################################################################
# Import necessary modules
# #############################################################################


from airflow import DAG
from airflow.operators.python import PythonOperator

from datetime import datetime, timedelta
from unit_test.utils import *
from unit_test.data_validation_checks import *

###############################################################################
# Define default arguments and DAG
# ##############################################################################

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2022,7,30),
    'retries' : 1, 
    'retry_delay' : timedelta(seconds=5)
}


ML_data_cleaning_dag = DAG(
                dag_id = 'Lead_Scoring_Data_Engineering_Pipeline',
                default_args = default_args,
                description = 'DAG to run data pipeline for lead scoring',
                schedule_interval = '@daily',
                catchup = False
)

###############################################################################
# Create a task for build_dbs() function with task_id 'building_db'
build_dbs_task = PythonOperator(
                            task_id = 'building_db',
                            python_callable = build_dbs,
                            dag = ML_data_cleaning_dag)
""

###############################################################################
# Create a task for raw_data_schema_check() function with task_id 'checking_raw_data_schema'
raw_data_schema_check_task = PythonOperator(
                            task_id = 'checking_raw_data_schema',
                            python_callable = raw_data_schema_check,
                            dag = ML_data_cleaning_dag)
""

###############################################################################
# Create a task for load_data_into_db() function with task_id 'loading_data'
load_data_into_db_task = PythonOperator(
                            task_id = 'loading_data',
                            python_callable = load_data_into_db,
                            dag = ML_data_cleaning_dag)
""

###############################################################################
# Create a task for map_city_tier() function with task_id 'mapping_city_tier'
map_city_tier_task = PythonOperator(
                            task_id = 'mapping_city_tier',
                            python_callable = map_city_tier,
                            dag = ML_data_cleaning_dag)
""

###############################################################################
# Create a task for map_categorical_vars() function with task_id 'mapping_categorical_vars'
map_categorical_vars_task = PythonOperator(
                            task_id = 'mapping_categorical_vars',
                            python_callable = map_categorical_vars,
                            dag = ML_data_cleaning_dag)
""

###############################################################################
# Create a task for interactions_mapping() function with task_id 'mapping_interactions'
interactions_mapping_task = PythonOperator(
                            task_id = 'mapping_interactions',
                            python_callable = interactions_mapping,
                            dag = ML_data_cleaning_dag)
""

###############################################################################
# Create a task for model_input_schema_check() function with task_id 'checking_model_inputs_schema'
model_input_schema_check_task = PythonOperator(
                            task_id = 'checking_model_inputs_schema',
                            python_callable = model_input_schema_check,
                            dag = ML_data_cleaning_dag)
""

###############################################################################
# Define the relation between the tasks

build_dbs_task >> raw_data_schema_check_task >> load_data_into_db_task >> map_city_tier_task >> map_categorical_vars_task >> interactions_mapping_task >> model_input_schema_check_task
""

