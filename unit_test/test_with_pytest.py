##############################################################################
# Import the necessary modules
# #############################################################################

import pytest
from utils import *
from constants import *

###############################################################################
# Write test cases for load_data_into_db() function
# ##############################################################################

def test_load_data_into_db():
    """_summary_
    This function checks if the load_data_into_db function is working properly by
    comparing its output with test cases provided in the db in a table named
    'loaded_data_test_case'


    SAMPLE USAGE
        output=test_get_data()

    """
    build_dbs()
    load_data_into_db()
    cnx = sqlite3.connect(DB_PATH + DB_FILE_NAME)
    df = pd.read_sql('select * from loaded_data', cnx)          
    cnx.close()
    cnx = sqlite3.connect(DB_PATH + UNIT_TEST_DB_FILE_NAME)
    ref_df = pd.read_sql('select * from loaded_data_test_case', cnx)          
    cnx.close()
    assert sorted(df.columns) == sorted(ref_df.columns), "schema of loaded_data does not match" 
    
###############################################################################
# Write test cases for map_city_tier() function
# ##############################################################################
def test_map_city_tier():
    """_summary_
    This function checks if map_city_tier function is working properly by
    comparing its output with test cases provided in the db in a table named
    'city_tier_mapped_test_case'

    SAMPLE USAGE
        output=test_map_city_tier()
    """
    build_dbs()
    map_city_tier()
    cnx = sqlite3.connect(DB_PATH + DB_FILE_NAME)
    df = pd.read_sql('select * from city_tier_mapped', cnx)          
    cnx.close()
    cnx = sqlite3.connect(DB_PATH + UNIT_TEST_DB_FILE_NAME)
    ref_df = pd.read_sql('select * from city_tier_mapped_test_case', cnx)          
    cnx.close()
    assert sorted(df.columns) == sorted(ref_df.columns), "schema of city_tier_mapped does not match with schema of city_tier_mapped_test_case"
    
    
###############################################################################
# Write test cases for map_categorical_vars() function
# ##############################################################################    
def test_map_categorical_vars():
    """_summary_
    This function checks if map_cat_vars function is working properly by
    comparing its output with test cases provided in the db in a table named
    'categorical_variables_mapped_test_case'


    SAMPLE USAGE
        output=test_map_cat_vars()

    """   
    build_dbs()
    map_categorical_vars()
    cnx = sqlite3.connect(DB_PATH + DB_FILE_NAME)
    df = pd.read_sql('select * from categorical_variables_mapped', cnx)          
    cnx.close()
    cnx = sqlite3.connect(DB_PATH + UNIT_TEST_DB_FILE_NAME)
    ref_df = pd.read_sql('select * from categorical_variables_mapped_test_case', cnx)          
    cnx.close()
    assert sorted(df.columns) == sorted(ref_df.columns), "categorical_cariables_mapped does not match"
    #assert sorted(df.columns) == sorted(ref_df.columns), "categorical_variables_mapped does not match"
    

###############################################################################
# Write test cases for interactions_mapping() function
# ##############################################################################    
def test_interactions_mapping():
    """_summary_
    This function checks if test_column_mapping function is working properly by
    comparing its output with test cases provided in the db in a table named
    'interactions_mapped_test_case'


    SAMPLE USAGE
        output=test_column_mapping()

    """ 
   
    interactions_mapping()
    cnx = sqlite3.connect(DB_PATH + DB_FILE_NAME)
    df = pd.read_sql('select * from interactions_mapped', cnx)          
    cnx.close()
    cnx = sqlite3.connect(DB_PATH + UNIT_TEST_DB_FILE_NAME)
    ref_df = pd.read_sql('select * from interactions_mapped_test_case', cnx)          
    cnx.close()
    assert sorted(df.columns) == sorted(ref_df.columns), "interactions_mapped does not match interactions_mapped_test_case"