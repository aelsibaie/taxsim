**TaxSim**

[![Build Status](https://travis-ci.com/TaxFoundation/taxsim.svg?token=yexSBERtR4Ec1WprzQ72&branch=master)](https://travis-ci.com/TaxFoundation/taxsim)
[![codecov](https://codecov.io/gh/TaxFoundation/taxsim/branch/master/graph/badge.svg?token=VnErjAtppV)](https://codecov.io/gh/TaxFoundation/taxsim)


```
usage: taxsim [-h] [-i input_file.csv] [-g default_taxpayer.csv]
              [-p plot_type] [-c] [-mp]

optional arguments:
  -h, --help            show this help message and exit
  -i input_file.csv, --input input_file.csv
                        specify location of input taxpayer(s) CSV file
  -g default_taxpayer.csv, --gencsv default_taxpayer.csv
                        generate blank input CSV file using specified filename
  -p plot_type, --plot plot_type
                        render average or marginal rate plots
  -c, --county          estimate county level tax liability (INCOMPLETE)
  -mp, --marriagepenalty
                        generate marriage penalty dataset
```

Other usage notes:

 - For `filing_status` use `0` for single filers, `1` for married filers, and `2` for head of household filers
 
 - List of example taxpayers is in `taxpayers.csv`
 
 - Most policy parameters can be found in the `params` folder
