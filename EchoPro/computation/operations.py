import numpy as np
import pandas as pd
from ..utils.monkey_patch_dataframe import patch_method_to_DataFrame
from typing import Union , List
from typing import Callable
    
@patch_method_to_DataFrame( pd.DataFrame )
def discretize_variable( dataframe: pd.DataFrame , 
                         bin_values: np.ndarray ,
                         bin_variable: str ):
    """
    Discretizes the target variable into user-defined bins

    Parameters
    ----------
    dataframe: pd.DataFrame
        A DataFrame object containing length and age variables required
        for analyses handling binned variables
    bin_values: np.ndarray
        An array of discrete bin values used to construct the intervals for 
        the variable of interest
    bin_variable: str
        The variable that will be binned into discrete intervals
    Notes
    -----
    This will add a column to defined dataframes that groups length and age values
    into each bin that is explicitly defined in the function arguments
    """
    return (
        dataframe # input dataframe
        .assign( **{f'{bin_variable}_bin': lambda x: pd.cut(x[bin_variable], bin_values)} ) # assign bin
    )
    
@patch_method_to_DataFrame( pd.DataFrame )
def quantize_variables( dataframe: pd.DataFrame ,
                        bin_variable: str ,
                        bin_values: np.ndarray,
                        contrasts: Union[str, List[str]] = [] ,
                        variables: Union[str, List[str]] = ['length', 'weight'] ,
                        functions: Union[str, List[str]] = ['mean', 'size'] ):
    """
    Quantizes dataset given user-defined intervals/bins

    Parameters
    ----------
    dataframe: pd.DataFrame
        A DataFrame object containing length and age variables required
        for analyses handling binned variables
    bin_values: np.ndarray
        An array of discrete bin values used to construct the intervals for 
        the variable of interest
    bin_variable: str
        The variable that will be binned into discrete intervals 
    contrasts: str or List[str]
        Additional variables to group data by, such as sex or species
    variables: str or List[str]
        Data columns to quantize
    functions: str or List[str] or List[Callable]
        Summary statistics or other functions applied to quantized variables
    """
    # Ensure that the contrasts, if there are any, are a list in case input is just a str
    con_lst = [contrasts] if isinstance(contrasts, str) else contrasts
    
    # Ensure variables are a list in case input is just a str
    var_lst = [variables] if isinstance(variables, str) else variables
    
    # Ensure functions are contained within a list
    fun_lst = [functions] if isinstance(functions, (str, Callable)) else functions
    
    # Rename functions as needed and if they exist
    FUNCTION_ALIASES = {
        'mean': 'mean' ,
        'size': 'n' ,        
    }
    
    # Check against an allowed list 
    invalid_functions = set( functions ) - FUNCTION_ALIASES.keys()
    
    if invalid_functions:
        raise ValueError(f'Invalid aggregation functions provided: {invalid_functions}. Only {FUNCTION_ALIASES.keys()} are allowed.')

    # Construction the aggregation dictionary to apply the summary statistics toward
    aggregation_dict = {
        variable: [
            (f"{FUNCTION_ALIASES.get(agg, agg)}_{variable}", agg)
            for agg in fun_lst
        ]
        for variable in var_lst
    }
       
    return (
        dataframe # input dataframe 
        .discretize_variable( bin_values , bin_variable ) # discretize variable into bins )
        .groupby( [f'{bin_variable}_bin'] + con_lst ) # group by these variables/contrasts
        .agg( aggregation_dict ) # apply specified functions
        .replace( np.nan , 0 ) # replace NaN w/ 0's
        .droplevel( level = 0 , axis = 1 ) # drop the column indices 
        .reset_index( ) # reset the row indices
    )
    
@patch_method_to_DataFrame( pd.DataFrame )
def count_variable( dataframe: pd.DataFrame ,
                    contrasts: Union[str, List[str]] ,
                    variable: str ,
                    fun: str):
    """
    Quantizes dataset given user-defined intervals/bins

    Parameters
    ----------
    dataframe: pd.DataFrame
        A DataFrame object containing length and age variables required
        for analyses handling binned variables
    contrasts: str or List[str]
        Additional variables to group data by, such as sex or species
    variable: str
        Data column to bin and count
    """
    return (
        dataframe # input dataframe
        .reset_index( drop=True )
        .groupby( contrasts ) 
        .agg({variable: [('count' , fun)]})
        .replace(np.nan, 0 )
        .droplevel( level = 0 , axis = 1 )
        .reset_index()
        .sort_values(contrasts)
    ) 
    
@patch_method_to_DataFrame( pd.DataFrame )
def meld( specimen_dataframe: pd.DataFrame ,
          length_dataframe: pd.DataFrame ):
    """
    Concatenates the specimen and length dataframes using a shared format

    Parameters
    ----------
    specimen_dataframe: pd.DataFrame
        A DataFrame object containing data from the specimen dataset
    length_dataframe: pd.DataFrame
        A DataFrame object containing data from the length dataset
    """
    # Reorganize the specimen dataframe so it matches the format
    # of the length dataframe w/ length counts
    specimen_stacked = (
        specimen_dataframe 
        .copy()
        .groupby(['stratum_num' , 'species_id' , 'sex' , 'group' , 'station' , 'length' , 'length_bin' ])
        .apply(lambda x: len(x['length']))
        .reset_index(name='length_count')
    )
    
    # Concatenate the data frames and return
    return pd.concat( [ specimen_stacked ,
                        length_dataframe ] ,
                        join = 'inner' )
    