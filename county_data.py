import pandas as pd


# A comma separated file (.csv) with AGI classes
county_data_agi = pd.read_csv('data/county2015/15incyallagi.csv')

# A comma separated file without AGI classes (The AGI_STUB variable has been set to zero for this file)
county_data_noagi = pd.read_csv('data/county2015/15incyallnoagi.csv')

# Merged dataset
frames = [county_data_agi, county_data_noagi]
county_data = pd.concat(frames, )

county_data.to_csv('test.csv')


# Rename things so we know what the heck we're doing
