import numpy as np
import pandas as pd
from typing import Union, List
from ..computation.spatial import correct_transect_intervals
from ..computation.operations import group_merge

def filter_species( dataframe_list: Union[List[pd.DataFrame], pd.DataFrame] , 
                    species_id: np.float64 ):
    """
    Filter species in one or multiple biological datasets

    Parameters
    ----------
    dataframe_list: Union[List[pd.DataFrame], pd.DataFrame]
        A list of dataframes or a single dataframe containing biological data/measurements
    species_id: np.float64
        Numeric code representing a particular species of interest
    """   
    
    ### If a single dataframe, convert to a list 
    if isinstance( dataframe_list , pd.DataFrame ):
        dataframe_list = [ dataframe_list ]

    ### Filter out the species-of-interest
    filtered_dataframes = tuple( df[ df.species_id == species_id ] for df in dataframe_list )

    ### Return output
    return filtered_dataframes

def index_sex_weight_proportions( biology_dict: dict ):
    """
    Generate dataframe containing sex-stratified weight proportions    

    Parameters
    ----------
    biology_dict: dict
        Biology data attribute dictionary 
    """     
    
    # Age-stratified weight proportions
    age_stratified_proportions = biology_dict[ 'weight' ][ 'proportions' ][ 'age_weight_proportions_df' ]

    # Age-stratified & sex-indexed weight proportions
    age_sex_stratified_proportions = biology_dict[ 'weight' ][ 'proportions' ][ 'sex_age_weight_proportions_df' ]

    # Concatenate the two to add a 'total' category
    return (
        pd.concat(
            [ ( age_sex_stratified_proportions
                .rename( columns = { 'weight_sex_stratum_proportion': 'weight_proportion' } ) ) ,
              ( age_stratified_proportions.assign( sex = 'total' )
                .rename( columns = { 'weight_stratum_proportion': 'weight_proportion' } ) ) ]
        )
    )

def index_transect_age_sex_proportions( acoustics_dict: dict ,
                                        biology_dict: dict ,
                                        info_strata: pd.DataFrame ):
    """
    Prepares the age- and sex-stratified dataframe for biomass calculation    

    Parameters
    ----------
    acoustics_dict: dict
        Acoustic data attribute dictionary 
    biology_dict: dict
        Biology data attribute dictionary 
    infra_strata: pd.DataFrame
        Dataframe containing strata definitions
    """     
    
    ### Prepare initial dataframes used for calculation population statistics
    # Construct georeferenced dataframe containing NASC data
    nasc_interval_df = correct_transect_intervals( acoustics_dict[ 'nasc' ][ 'nasc_df' ] )

    ### Call additional dataframes needed to merge with the NASC data and subsequently calculate
    ### population-level metrics (and later statistics)
    # Sex-stratum-indexed proportions and average weight
    weight_sex_strata = biology_dict[ 'weight' ][ 'weight_strata_df' ]

    # Stratum-averaged sigma_bs
    sigma_bs_strata = acoustics_dict[ 'sigma_bs' ][ 'strata_mean' ]

    # Adult NASC proportions for each stratum (number)
    # !!! TODO: Currently only uses 'age_1_excluded' -- this should become an argument that toggles
    ## This is not a major issue since both 'NASC_*' columns can be pivoted to create a single 
    ## NASC column so the column name does not have to be hard-coded. This could then correspond to
    ## the configuration settings in some way, or this may be where the argument comes into play where
    ## the dataframe can be simply filtered based on the input/selection.
    # between excluding and including age-1 fish
    nasc_number_proportions = (
        biology_dict[ 'weight' ][ 'proportions' ][ 'age_proportions_df' ]
    )

    # Adult NASC proportions for each stratum (weight)
    nasc_weight_proportions = (
        biology_dict[ 'weight' ][ 'proportions' ][ 'age_weight_proportions_df' ]
    )

    ### Consolidate dataframes that will be added into a list
    dataframes_to_add = [ nasc_interval_df , sigma_bs_strata , weight_sex_strata , nasc_number_proportions , 
                          nasc_weight_proportions ]
    

    ## Merge the relevant dataframes
    return (
        nasc_interval_df
        # Merge stratum information ( join = 'outer' since missing values will be filled later on)
        .merge( info_strata , on = [ 'stratum_num' , 'haul_num' ] , how = 'outer' )
        # Drop unused hauls
        .dropna( subset = 'transect_num' )
        # Fill NaN w/ 0's for 'fraction_hake'
        .assign( fraction_hake = lambda x: x[ 'fraction_hake' ].fillna( 0 ) )
        # Group merge
        .group_merge( dataframes_to_add = dataframes_to_add , inner_on = 'age' , outer_on = 'stratum_num' )
        )

def sum_strata_weight( haul_data: pd.DataFrame ,
                       specimen_data: pd.DataFrame ):
    """
    Sum haul weights from different datasets    

    Parameters
    ----------
    haul_data: pd.DataFrame
        Dataframe containing haul catch weight data
    specimen_data: pd.DataFrame
        Dataframe containing specimen weights
    """ 

    ### Process biological datasets
    # ---- Process haul data ( Station 2 - unsexed - unaged )
    haul_strata_weight = (
        haul_data
        .groupby( 'stratum_num' )[ 'haul_weight' ]
        .sum( )
        .to_frame( 'stratum_weight' )
        .reset_index( )
        .assign( group = 'unaged' )
    ) 

    # ---- Process specimen data ( Station 1 - sexed - aged )
    specimen_strata_weight = (
        specimen_data
        .groupby( 'stratum_num' )[ 'weight' ]
        .sum( )
        .to_frame( 'stratum_weight' )
        .reset_index( )
        .assign( group = 'aged' )
    )

    ### Merge the two dataframes
    # Yields the summed weights per stratum and station (or aged/unaged designation)
    weight_strata_aged_unaged = pd.concat( [ haul_strata_weight , specimen_strata_weight ] )
 
    ### Sum weights for each stratum
    weight_strata = (
        weight_strata_aged_unaged
        .groupby( "stratum_num" )[ "stratum_weight" ]
        .sum( )
        .to_frame( 'weight_stratum_all' )
        .reset_index( )
    )
    
    ### Carriage return
    return weight_strata_aged_unaged , weight_strata

def compute_aged_unaged_proportions( specimen_data: pd.DataFrame ,
                                     weight_strata: pd.DataFrame ):
    """
   Compute the overall weight proportions for aged and uanged fish within each stratum 

    Parameters
    ----------
    specimen_data: pd.DataFrame
        Dataframe containing specimen weights
    weight_strata: pd.DataFrame
        Dataframe contained summed weights of both aged and unaged fish
    """   
    ### Calculate adult:all age ratio for each stratum
    # ---- Drop unaged fish
    specimen_data_filtered = specimen_data[ specimen_data.sex != 'unsexed' ].dropna( how = 'any' , subset = 'age' ) 

    # ---- Sum the weight of adult fish
    specimen_adult = specimen_data_filtered[ specimen_data_filtered.age > 1 ].groupby( [ 'stratum_num' ] )[ 'weight' ].sum( )

    # ---- Sum the weight of all fish
    specimen_all = specimen_data_filtered.groupby( [ 'stratum_num' ] )[ 'weight' ].sum( ).to_frame( )

    # ---- Calculate the ratio between the two groups
    specimen_all[ 'weight_ratio' ] = ( specimen_adult / specimen_all.weight ).fillna( 0 )

    ### Calculate the aged proportions of all fish
    # ---- Merge with `weight_strata`
    aged_proportions = specimen_all.reset_index( ).merge( weight_strata , on = [ 'stratum_num' ] )

    # ---- Calculate the aged proportion of all fish
    aged_proportions[ 'proportion_aged_weight_all' ] = (
        aged_proportions.weight / aged_proportions.weight_stratum_all
    )

    # ---- Calculate the aged proportion of adult fish
    aged_proportions[ 'proportion_aged_weight_adult' ] = (
        aged_proportions.proportion_aged_weight_all * aged_proportions.weight_ratio
    )

    ### Calculate the unaged weight proportions
    # ---- All fish
    aged_proportions[ 'proportion_unaged_weight_all' ] = (
        1.0 - aged_proportions.proportion_aged_weight_all
    )

    # ---- Adult fish
    aged_proportions[ 'proportion_unaged_weight_adult' ] = (
        1.0 - aged_proportions.proportion_aged_weight_adult
    )

    return aged_proportions.drop( [ 'weight_ratio' ] , axis = 1 )

def compute_aged_weight_proportions( specimen_data: pd.DataFrame ,
                                     length_intervals: np.ndarray ,
                                     age_intervals: np.ndarray ):
    """
    Calculate length-age binned weight proportions    

    Parameters
    ----------
    specimen_data: pd.DataFrame
        Dataframe containing specimen weights
    length_intervals: np.ndarray
        Array containing length bins/intervals
    age_intervals: np.ndarray
        Array containing age bins/intervals
    """ 

    ### Process the specimen data 
    # ---- Drop unaged fish
    # ==== !!! TODO: pending what FEAT says, weights associated with 
    # ==== missing ages should be added into the 'unaged' category. 
    # ==== This would further mean apportioning these into `weight_strata_aged_uanged`
    specimen_data_filtered = specimen_data[ specimen_data.sex != 'unsexed' ].dropna( how = 'any' , subset = 'age' )
    
    # ---- Bin length and age measurements
    specimen_data_filtered = (
        specimen_data_filtered
        # ---- Bin length
        .bin_variable( length_intervals , 'length' )
        # ---- Age bin
        .bin_variable( age_intervals , 'age' )
    )

    ### Sum weights within each length and age bin for each sex within each stratum
    # ---- Create separate 'weight_adult' column
    specimen_data_filtered[ 'weight_adult' ] = (
        np.where( specimen_data_filtered.age > 1 , specimen_data_filtered.weight , 0.0 )
    )
    
    # ---- Calculate aggregate sums of fish weights
    specimen_binned_weight = (
        specimen_data_filtered
        # ---- Group weight summations across stratum/species/sex/length/age
        .groupby( [ 'stratum_num' , 'species_id' , 'sex' , 'length_bin' , 'age_bin' ] )
        # ---- Sum the weights 
        .agg( weight_all =( 'weight' , 'sum' )  , weight_adult =( 'weight_adult' , 'sum' ) ) 
        # ---- Fill empty/non-existent values with 0's
        .fillna( 0 )
        .reset_index( )
    )
    
    ### Calculate the relative weight proportions of each length-age bin for each sex within each stratum
    proportions_weight_length_age_sex = (
        specimen_binned_weight
        # ---- Calculate total sex-specific weights for each stratum
        .assign( total_weight_sex_all = lambda df: df.groupby( [ 'stratum_num' , 'species_id' , 'sex'  ] )[ 'weight_all' ].transform( sum ) ,
                 total_weight_sex_adult = lambda df: df.groupby( [ 'stratum_num' , 'species_id' , 'sex' ] )[ 'weight_adult' ].transform( sum ) )
        # ---- Calculate the weight proportions within each sex: from Matlab --> Len_age_key_wgt_*n
        .assign( proportion_weight_sex_all = lambda df: df.weight_all / df.total_weight_sex_all ,
                 proportion_weight_sex_adult = lambda df: df.weight_adult / df.total_weight_sex_adult )
    )

    ### Fill empty/non-existent values with 0's
    proportions_weight_length_age_sex[ 'proportion_weight_sex_all' ] = (
        proportions_weight_length_age_sex[ 'proportion_weight_sex_all' ].fillna( 0 )
    )

    proportions_weight_length_age_sex[ 'proportion_weight_sex_adult' ] = (
        proportions_weight_length_age_sex[ 'proportion_weight_sex_adult' ].fillna( 0 )
    )

    ### Return output
    return proportions_weight_length_age_sex.reset_index( drop = True )

def compute_aged_sex_weight_proportions( proportions_weight_length_age_sex: pd.DataFrame ,
                                         aged_proportions: pd.DataFrame ):
    """
    Compute the aged proportions across all fish and specific sexes for each
    length and age bin  

    Parameters
    ----------
    proportions_weight_length_age_sex: pd.DataFrame
        Dataframe containing sexed weight proportions distributed across
        each age and length bin
    aged_proportions: pd.DataFrame
        Dataframe containing the weight proportions of aged fish within each stratum
    """   

    ### Caclulate the summed weights for all and adult fish 
    # ---- Group by `stratum_num` and `sex` and sum
    # ---- Also initializes the correct shape for the output dataframe
    aged_sex_weights = (
        proportions_weight_length_age_sex
        .groupby( [ 'stratum_num' , 'sex' ] )
        .agg(
            weight_aged_sex_all = ( 'weight_all' , 'sum' ) ,
            weight_aged_sex_adult = ( 'weight_adult' , 'sum' )
        )
        .reset_index( )
    )

    ### Calculate the weight proportions
    # ---- Merge `aged_sex_weights` with `weight_strata` to get strata weights
    aged_sex_proportions = aged_sex_weights.merge( aged_proportions ,
                                                   on = [ 'stratum_num' ] ,
                                                   how = 'left' )

    # ---- Proportions for all fish
    aged_sex_proportions[ 'proportion_weight_all' ] = (
        aged_sex_proportions.weight_aged_sex_all / aged_sex_proportions.weight_stratum_all
    )

    # ---- Proportions for adult fish
    aged_sex_proportions[ 'proportion_weight_adult' ] = (
        aged_sex_proportions.weight_aged_sex_adult / aged_sex_proportions.weight_stratum_all
    )

    # ---- Fill empty/NaN values with 0's and drop unused columns
    aged_sex_proportions = aged_sex_proportions.fillna( 0 ).filter( regex = "^(?=.*aged|stratum_num|sex)(?!.*unaged|weight_)" )
  
    ### Return output 
    return aged_sex_proportions

def distribute_aged_weight_proportions( proportions_weight_length_age_sex: pd.DataFrame ,
                                        aged_sex_proportions: pd.DataFrame ):
    """
    Distribute overall weight proportions across each sex and age/length bins   

    Parameters
    ----------
    proportions_weight_length_age_sex: pd.DataFrame
        Dataframe containing sexed weight proportions distributed across
        each age and length bin
    aged_sex_proportions: pd.DataFrame
        Dataframe contained weight proportions of sexed fish for aged fish
    """     

    ### Calculate the normalized age-length-sex aged fish weight proportions
    # ---- Merge `proportions_weight_length_age_sex` with `aged_sex_proportions`
    distributed_aged_weight_proportions = proportions_weight_length_age_sex.merge( aged_sex_proportions ,
                                                                                   on = [ 'stratum_num' , 'sex' ] , 
                                                                                   how = 'left' )
    
    # ---- Normalized weight proportions for all fish
    distributed_aged_weight_proportions[ 'normalized_proportion_weight_all' ] = (
        distributed_aged_weight_proportions.proportion_weight_sex_all * distributed_aged_weight_proportions.proportion_aged_weight_all
    )

    # ---- Normalized weight proportions for jus adult fish
    distributed_aged_weight_proportions[ 'normalized_proportion_weight_adult' ] = (
        distributed_aged_weight_proportions.proportion_weight_sex_adult * distributed_aged_weight_proportions.proportion_aged_weight_adult
    )   

    # ---- Remove unnecessary columns and return the dataframe
    return distributed_aged_weight_proportions.filter( regex = '^(?!weight_|total_weight_|proportion_).*' )

def calculate_aged_biomass( kriging_biomass_df: pd.DataFrame ,
                            specimen_data: pd.DataFrame ,
                            length_distribution: pd.DataFrame ,
                            age_distribution: pd.DataFrame ,
                            aged_proportions: pd.DataFrame ):
    """
    Calculate the kriged biomass distributed over length and age for each sex and among
    all fish (sexed)

    Parameters
    ----------
    kriging_biomass_df: pd.DataFrame
        Dataframe containing kriged biomass estimates
    specimen_data: pd.DataFrame
        Dataframe containing specimen weights
    length_distribution: np.ndarray
        Array containing length bins/intervals
    age_distribution: np.ndarray
        Array containing age bins/intervals
    aged_proportions: pd.DataFrame
        Dataframe containing the weight proportions of aged fish within each stratum
    """

    ### Sum aged fish weights across age and length bins, then calculate weight proportions
    proportions_weight_length_age_sex = compute_aged_weight_proportions( specimen_data ,
                                                                         length_distribution ,
                                                                         age_distribution )

    ### Calculate the summed aged proportions for all aged fish, and for aged fish 
    # ---- belonging to each sex
    aged_sex_proportions = compute_aged_sex_weight_proportions( proportions_weight_length_age_sex ,
                                                                aged_proportions )
    
    ### Calculate weight proportions of aged fish distributed over age-length bins
    # ---- for each sex within each stratum relative to the summed weights of each
    # ---- stratum (i.e. aged + unaged weights)
    distributed_sex_proportions = distribute_aged_weight_proportions( proportions_weight_length_age_sex ,
                                                                      aged_sex_proportions )
    
    ### Sum 'kriging_biomass_df' across each stratum for appropriate stratum-specific apportionment
    kriged_stratum_biomass = kriging_biomass_df.groupby( [ 'stratum_num' ] )[ 'B_adult_kriged' ].sum( )

    ### Apportion sexed biomass across age-length
    # ---- Initialize dataframe
    stratum_sexed_kriged_biomass = distributed_sex_proportions.set_index( 'stratum_num' )
    stratum_sexed_kriged_biomass[ 'biomass_kriged' ] = kriged_stratum_biomass

    # ---- Apportioned biomass for all fish
    stratum_sexed_kriged_biomass[ 'biomass_sexed_aged_all' ] = (  
        stratum_sexed_kriged_biomass.biomass_kriged
        * stratum_sexed_kriged_biomass.normalized_proportion_weight_all
    ).fillna( 0 )

    # ---- Apportioned biomass for adult fish
    stratum_sexed_kriged_biomass[ 'biomass_sexed_aged_adult' ] = (  
        stratum_sexed_kriged_biomass.biomass_kriged
        * stratum_sexed_kriged_biomass.normalized_proportion_weight_adult
    ).fillna( 0 )

    # ---- Sum across strata to produce 'grand totals' for each sex
    apportioned_sexed_kriged_biomass = (
        stratum_sexed_kriged_biomass
        .groupby( [ 'species_id' , 'sex' , 'length_bin' , 'age_bin' ] )
        .agg( { 'biomass_sexed_aged_all': 'sum' ,
                'biomass_sexed_aged_adult': 'sum' } )
        .reset_index( )
    )

    ### Calculate biomass proportions across age-length
    # ---- Sum weights within each length-age bin for each stratum
    proportions_weight_length_age = (
        proportions_weight_length_age_sex
        .groupby( [ 'stratum_num' , 'species_id' , 'length_bin' , 'age_bin' ] )
        .agg( { 'weight_all': 'sum' ,
                'weight_adult': 'sum' } )
        .reset_index( )
    )

    # ---- Sum stratum weights
    # ---- All fish
    proportions_weight_length_age[ 'total_weight_all' ] = (
        proportions_weight_length_age.groupby( [ 'stratum_num' , 'species_id' ] )[ 'weight_all' ].transform( sum )
    )

    # ---- Adult fish
    proportions_weight_length_age[ 'total_weight_adult' ] = (
        proportions_weight_length_age.groupby( [ 'stratum_num' , 'species_id' ] )[ 'weight_adult' ].transform( sum )
    )

    # ---- Calculate proportions
    # ---- All fish
    proportions_weight_length_age[ 'proportion_weight_length_all' ] = (
        proportions_weight_length_age.weight_all / proportions_weight_length_age.total_weight_all
    ).fillna( 0 )

    # ---- Adult fish
    proportions_weight_length_age[ 'proportion_weight_length_adult' ] = (
        proportions_weight_length_age.weight_adult / proportions_weight_length_age.total_weight_adult
    ).fillna( 0 )

    # ---- Index `aged_proportions`
    index_aged_proportions = aged_proportions.filter( regex = "^(?=.*aged|stratum_num)(?!.*unaged)" ).set_index( 'stratum_num' )

    # ---- Initialize dataframe
    stratum_kriged_biomass = proportions_weight_length_age.set_index( 'stratum_num' )
    stratum_kriged_biomass[ 'proportion_aged_weight_all' ] =  index_aged_proportions.proportion_aged_weight_all
    stratum_kriged_biomass[ 'proportion_aged_weight_adult' ] = index_aged_proportions.proportion_aged_weight_adult
    stratum_kriged_biomass[ 'biomass_kriged' ] = kriged_stratum_biomass

    # ---- Apportioned biomass for all fish
    stratum_kriged_biomass[ 'biomass_aged_all' ] = (  
        stratum_kriged_biomass.biomass_kriged
        * stratum_kriged_biomass.proportion_weight_length_all 
        * stratum_kriged_biomass.proportion_aged_weight_all
    ).fillna( 0 )

    # ---- Apportioned biomass for adult fish
    stratum_kriged_biomass[ 'biomass_aged_adult' ] = (  
        stratum_kriged_biomass.biomass_kriged
        * stratum_kriged_biomass.proportion_weight_length_adult
        * stratum_kriged_biomass.proportion_aged_weight_adult
    ).fillna( 0 )

    # ---- Sum across strata to produce 'grand totals' for all fish
    apportioned_total_kriged_biomass = (
        stratum_kriged_biomass
        .groupby( [ 'species_id' , 'length_bin' , 'age_bin' ] )
        .agg( { 'biomass_aged_all': 'sum' ,
                'biomass_aged_adult': 'sum' } )
        .reset_index( )
    )

    ### Return output (tuple)
    return apportioned_sexed_kriged_biomass , apportioned_total_kriged_biomass


def compute_unaged_number_proportions( length_data: pd.DataFrame ,
                                       length_intervals: np.ndarray ):
    """
    Calculate length binned weight proportions among unaged fish  

    Parameters
    ----------
    length_data: pd.DataFrame
        Dataframe containing length data measured from unaged fish
    length_intervals: np.ndarray
        Array containing length bins/intervals
    """ 

    ### Calculate number proportion
    # ---- Bin length measurements
    length_data_binned = (
        length_data
        # ---- Bin length
        .bin_variable( length_intervals , 'length' ) 
    )

    # ---- Sum the number of individuals within each bin 
    proportions_unaged_length = (
        length_data_binned
        # ---- Group number summations across stratum/species/sex/length
        .groupby( [ 'stratum_num' , 'species_id' , 'length_bin' ] )
        # ---- Sum count
        .agg( number_all = ( 'length_count' , 'sum' ) )
        # ---- Fill empty/non-existent values with 0's
        .fillna( 0 )
        .reset_index( )
    )

    ### Calculate the number proportions
    # --- Stratum total counts
    proportions_unaged_length[ 'stratum_number_all' ] = (
        proportions_unaged_length.groupby( [ 'stratum_num' ] )[ 'number_all' ].transform( sum )
    )

    # ---- Proportions of each sex-length bin pair relative to `stratum_number_all`
    proportions_unaged_length[ 'proportion_number_all' ] = (
        proportions_unaged_length.number_all / proportions_unaged_length.stratum_number_all
    ).fillna( 0 )

    ### Filter out unnecessary columns and return output
    return proportions_unaged_length.filter( regex = '^(?!number_|stratum_number_).*' )

def compute_unaged_weight_proportions( proportions_unaged_length: pd.DataFrame ,
                                       length_weight_df: pd.DataFrame ):
    """
   Compute the unaged weight proportions across all fish and specific sexes for each
   length bin  

    Parameters
    ----------
    proportions_unaged_length: pd.DataFrame
        Dataframe containing the total number proportions distributed across
        each length bin
    length_weight_df: pd.DataFrame
        Dataframe containing the modeled weights for each sex and length bin
        fit from the length-weight regression (fit for all animals)
    """   

    ### Extract length-weight regression results calculated for all animals
    length_weight_all = length_weight_df[ length_weight_df.sex == 'all' ][ [ 'length_bin' , 'weight_modeled' ] ]

    ### Calculate the weight proportion of each length bin that is 'weighted' by the number proportions
    # ---- Merge `proportions_unaged_length_sex` and `length_weight_all`
    proportions_unaged_weight_length = pd.merge( proportions_unaged_length ,
                                                 length_weight_all ,
                                                 on = [ 'length_bin' ] ,
                                                 how = 'left' )
    
    # ---- Calculate the weight proportion (`w_ln_all_array` in the original Matlab code)
    proportions_unaged_weight_length[ 'weight_proportion_all' ] = (
        proportions_unaged_weight_length.weight_modeled * proportions_unaged_weight_length.proportion_number_all
    )

    ### Sum weight proportions for each strata to get the weight per length bin
    # ---- Calculate the summed weights per stratum (`w_ln_array_sum` in the original Matlab code)
    proportions_unaged_weight_length[ 'weight_stratum_proportion' ] = (
       proportions_unaged_weight_length.groupby( [ 'stratum_num' ] )[ 'weight_proportion_all' ].transform( sum )
    )
    
    # ---- Calculate the weight per length distribution bin (`w_ln_all_N` in the original Matlab code)
    proportions_unaged_weight_length[ 'proportion_weight_length' ] = (
        proportions_unaged_weight_length.weight_proportion_all / proportions_unaged_weight_length.weight_stratum_proportion
    )

    ### Drop unnecessary columns and return output
    return proportions_unaged_weight_length.filter( regex = '^(?!weight_|proportion_number_).*' )

def compute_unaged_sex_proportions( length_data: pd.DataFrame ,
                                    length_intervals: pd.DataFrame ,
                                    length_weight_df: pd.DataFrame ,
                                    aged_proportions: pd.DataFrame ):
    """
    Calculate the normalized weight proportions for unaged sexed fish

    Parameters
    ----------
    length_data: pd.DataFrame
        Dataframe containing length data measured from unaged fish
    length_intervals: np.ndarray
        Array containing length bins/intervals
    length_weight_df: pd.DataFrame
        Dataframe containing the modeled weights for each sex and length bin
        fit from the length-weight regression (fit for all animals)
    aged_proportions: pd.DataFrame
        Dataframe containing the weight proportions of unaged fish within each stratum
    """ 

    ### Calculate sexed weights within each stratum
    # ---- Extract sexed length-weight regression fits
    length_weight_sex = length_weight_df[ length_weight_df.sex != 'all' ][ [ 'length_bin' , 'sex' , 'weight_modeled' ] ]

    # ---- Bin length measurements
    length_data_binned = (
        length_data
        # ---- Bin length
        .bin_variable( length_intervals , 'length' ) 
    )

    # ---- Extract bin length values (i.e. mid)
    length_data_binned[ 'length_bin_value' ] = (
        length_data_binned[ 'length_bin' ].apply( lambda x: x.mid )
    )

    # ---- Merge `length_data_filtered ` and `length_weight_sex`
    sexed_unaged_model_weights = length_data_binned.merge( length_weight_sex ,
                                                           on = [ 'length_bin' , 'sex' ] ,
                                                           how = 'left' )
    
    # ---- Interpolate weights over length values for each sex (weighted by `length_count`)
    interpolated_weights = (
        sexed_unaged_model_weights
        .groupby( [ 'stratum_num' , 'sex' ] ) 
        .apply( lambda df: pd.Series( {
                'weight_interp': ( np.interp( df.length ,
                                              df.length_bin_value ,
                                              df.weight_modeled ) * df.length_count ).sum( )
            } ) )
        .reset_index( )
    )

    ### Calculate the unaged weight proportion relative to the haul catches
    # ---- Merge the unaged weight strata with the interpolated weights
    proportions_unaged_weight_sex = pd.merge( interpolated_weights ,
                                              aged_proportions ,
                                              on = [ 'stratum_num' ] ,
                                              how = 'left' )
    
    # ---- Sum `weight_interp` over each stratum
    proportions_unaged_weight_sex[ 'stratum_sex_weight_interp' ] = (
        proportions_unaged_weight_sex.groupby( ['stratum_num' ] )[ 'weight_interp' ].transform( sum ) 
    )

    # ---- Calculate the normalized weights for each sex
    proportions_unaged_weight_sex[ 'stratum_sex_weight_normalized' ] = (
        proportions_unaged_weight_sex[ 'weight' ] *
        proportions_unaged_weight_sex.weight_interp / proportions_unaged_weight_sex.stratum_sex_weight_interp
    )

    # ---- Sum the normalized stratum sex weight across each stratum
    proportions_unaged_weight_sex[ 'proportions_weight_sex' ] = (
        proportions_unaged_weight_sex.stratum_sex_weight_normalized /
        proportions_unaged_weight_sex.weight_stratum_all
    )

    # ---- Sum 'proportions_weight_sex'
    proportions_unaged_weight_sex[ 'proportions_weight_sex_total' ] = (
        proportions_unaged_weight_sex.groupby( [ 'stratum_num' ] )[ 'proportions_weight_sex' ].transform( sum )
    )

    # ---- Calculate the final sex proportion
    proportions_unaged_weight_sex[ 'proportion_weight_sex' ] = (
        proportions_unaged_weight_sex.proportions_weight_sex / proportions_unaged_weight_sex.proportions_weight_sex_total
    )

    ### Remove unnecessary columns and return output
    return proportions_unaged_weight_sex[ [ 'stratum_num' , 'sex' , 'proportion_weight_sex' ] ]

def compute_unaged_biomass( kriging_biomass_df: pd.DataFrame ,
                            length_data: pd.DataFrame ,
                            length_distribution: np.ndarray ,
                            length_weight_df: pd.DataFrame ,
                            aged_proportions: pd.DataFrame ):
    """
    Calculate the kriged biomass distributed over length and age for each sex and among
    all fish (sexed)

    Parameters
    ----------
    kriging_biomass_df: pd.DataFrame
        Dataframe containing kriged biomass estimates
    length_data: np.ndarray
        Dataframe containing length data measured from unaged fish
    length_distribution: pd.DataFrame
        Dataframe containing the weight proportions for each length and age bin computed for all fish
    length_weight_df: pd.DataFrame
        Dataframe containing the modeled weights for each sex and length bin
        fit from the length-weight regression (fit for all animals)
    aged_proportions: pd.DataFrame
        Dataframe containing the weight proportions of unaged fish within each stratum
    """

    ### Calculate number proportion
    proportions_unaged_length = compute_unaged_number_proportions( length_data , length_distribution )

    ### Calculate the normalized weight per unit length distribution (W_Ln_ALL in the original Matlab code)
    proportions_unaged_weight_length = compute_unaged_weight_proportions( proportions_unaged_length ,
                                                                          length_weight_df )

    ### Calculate sex-specific weight proportions for unaged fish (within unaged fish)
    proportions_unaged_weight_sex = compute_unaged_sex_proportions( length_data ,
                                                                    length_distribution ,
                                                                    length_weight_df ,
                                                                    aged_proportions )

    ### Sum 'kriging_biomass_df' across each stratum for appropriate stratum-specific apportionment
    kriged_stratum_biomass = kriging_biomass_df.groupby( [ 'stratum_num' ] )[ 'B_adult_kriged' ].sum( )

    ### Calculate sex-specific biomass apportionment
    # ---- Index `unaged_proportions`
    indexed_unaged_proportions = aged_proportions.filter( regex = "^(?=.*stratum_num|.*unaged).*(?!.*aged)" ).set_index( 'stratum_num' )

    # ---- Index `proportions_unaged_weight_length`
    indexed_proportions_unaged_weight_length = proportions_unaged_weight_length.set_index( 'stratum_num' )

    # ---- Initialize dataframe
    stratum_sexed_kriged_biomass = proportions_unaged_weight_sex.merge( indexed_proportions_unaged_weight_length ,
                                                                        on = [ 'stratum_num' ] ,
                                                                        how = 'left' ).set_index( 'stratum_num' )
    stratum_sexed_kriged_biomass[ 'proportion_unaged_weight_all' ] = indexed_unaged_proportions.proportion_unaged_weight_all
    stratum_sexed_kriged_biomass[ 'proportion_unaged_weight_adult' ] = indexed_unaged_proportions.proportion_unaged_weight_adult
    stratum_sexed_kriged_biomass[ 'biomass_kriged' ] = kriged_stratum_biomass

    # ---- Calculate the overall sexed proportions taking into account aged and unaged fish (all age class)
    stratum_sexed_kriged_biomass[ 'proportion_sexed_weight_all' ] = (
        stratum_sexed_kriged_biomass.proportion_weight_sex *
        stratum_sexed_kriged_biomass.proportion_unaged_weight_all
    )

    # ---- Calculate the overall sexed proportions taking into account aged and unaged fish (adults)
    stratum_sexed_kriged_biomass[ 'proportion_sexed_weight_adult' ] = (
        stratum_sexed_kriged_biomass.proportion_weight_sex *
        stratum_sexed_kriged_biomass.proportion_unaged_weight_adult
    )

    # ---- Apportioned biomass for all fish
    stratum_sexed_kriged_biomass[ 'biomass_sexed_unaged_all' ] = (
        stratum_sexed_kriged_biomass.biomass_kriged
        * stratum_sexed_kriged_biomass.proportion_sexed_weight_all
        * stratum_sexed_kriged_biomass.proportion_weight_length
    )

    # ---- Apportioned biomass for adult fish
    stratum_sexed_kriged_biomass[ 'biomass_sexed_unaged_adult' ] = (
        stratum_sexed_kriged_biomass.biomass_kriged
        * stratum_sexed_kriged_biomass.proportion_sexed_weight_adult
        * stratum_sexed_kriged_biomass.proportion_weight_length
    )

    # ---- ' Grand total ' for all sexed unaged fish
    apportioned_sexed_kriged_biomass = (
            stratum_sexed_kriged_biomass
            .groupby( [ 'species_id' , 'sex' , 'length_bin'  ] )
            .agg( { 'biomass_sexed_unaged_all': 'sum' ,
                    'biomass_sexed_unaged_adult': 'sum' } )
            .reset_index( )
        )
    
    ### Calculate biomass proportions across length
    # ---- Initialize dataframe
    stratum_kriged_biomass = indexed_proportions_unaged_weight_length
    stratum_kriged_biomass[ 'proportion_unaged_weight_all' ] = indexed_unaged_proportions.proportion_unaged_weight_all
    stratum_kriged_biomass[ 'proportion_unaged_weight_adult' ] = indexed_unaged_proportions.proportion_unaged_weight_adult
    stratum_kriged_biomass[ 'biomass_kriged' ] = kriged_stratum_biomass

    # ---- Apportioned biomass for all fish
    stratum_kriged_biomass[ 'biomass_unaged_all' ] = (
        stratum_kriged_biomass.biomass_kriged
        * stratum_kriged_biomass. proportion_unaged_weight_all
        * stratum_kriged_biomass.proportion_weight_length
    )

    # ---- Apportioned biomass for adult fish
    stratum_kriged_biomass[ 'biomass_unaged_adult' ] = (
        stratum_kriged_biomass.biomass_kriged
        * stratum_kriged_biomass.proportion_unaged_weight_adult
        * stratum_kriged_biomass.proportion_weight_length
    )

    # ---- ' Grand total ' for all sexed unaged fish
    apportioned_kriged_biomass = (
            stratum_kriged_biomass
            .groupby( [ 'species_id' , 'length_bin'  ] )
            .agg( { 'biomass_unaged_all': 'sum' ,
                    'biomass_unaged_adult': 'sum' } )
            .reset_index( )
        )
    
    ### Return output (tuple)
    return apportioned_sexed_kriged_biomass , apportioned_kriged_biomass
    
def apply_age_bins( aged_biomass_sexed_df: pd.DataFrame ,
                    unaged_biomass_sexed_df: pd.DataFrame ):
    """
    Redistribute unaged biomass over the defined age distribution

    Parameters
    ----------
    aged_biomass_sexed_df: pd.DataFrame
        Dataframe containing biomass data of sexed aged fish
    unaged_biomass_sexed_df: pd.DataFrame
        Dataframe containing biomass data of sexed unaged fish
    aged_biomass_total_df: pd.DataFrame
        Dataframe containing biomass data of all aged fish
    aged_biomass_total_df: pd.DataFrame
        Dataframe containing biomass data of all unaged fish
    """ 
    
    ### Merge unaged biomass length bins with aged bioamss length-age bins
    aged_unaged_sexed_biomass = pd.merge( aged_biomass_sexed_df , 
                                          unaged_biomass_sexed_df ,
                                          on = [ 'length_bin' , 'sex' ] ,
                                          how = 'left' )

    ### Calculate the total biomass for each sexed length bin (i.e. sum across age bins)
    # ---- Adult fish
    aged_unaged_sexed_biomass[ 'sum_length_bin_biomass_sexed_adult' ] = (
        aged_unaged_sexed_biomass.groupby( [ 'sex' , 'length_bin' ] )[ 'total_sexed_aged_biomass_adult' ].transform( sum ) + 
        aged_unaged_sexed_biomass.total_sexed_unaged_biomass_adult
    )

    ### Redistribute unaged biomass over the length-age bins for each sex
    # ---- Adult fish
    aged_unaged_sexed_biomass[ 'total_sexed_unaged_biomass_adult' ] = (
        aged_unaged_sexed_biomass.total_sexed_unaged_biomass_adult * 
        aged_unaged_sexed_biomass.total_sexed_aged_biomass_adult /
        aged_unaged_sexed_biomass.sum_length_bin_biomass_sexed_adult
    ).fillna( 0 )

    ### Remove unnecessary columns 
    aged_unaged_sexed_biomass.drop( [ 'total_sexed_aged_biomass_adult' , 
                                      'sum_length_bin_biomass_sexed_adult' ] ,
                                    axis = 1 ,
                                    inplace = True )
    
    ### Sum sexes together to retrieve the total biomass 
    aged_unaged_biomass = (
        aged_unaged_sexed_biomass
        .groupby( [ 'length_bin' , 'age_bin' ] )
        .agg( total_unaged_biomass_adult = ( 'total_sexed_unaged_biomass_adult' , 'sum' ) )
        .reset_index( )
    )
    

    ### Return output (tuple)
    return aged_unaged_sexed_biomass , aged_unaged_biomass