# TaxSim

TaxSim is the backend to the Tax Foundation [2018 Tax Reform Calculator](https://taxfoundation.org/2018-tax-reform-calculator/) and the tool used to generate the marriage penalty dataset in the Tax Foundation [marriage penalty and bonus paper](https://taxfoundation.org/tax-cuts-and-jobs-act-marriage-penalty-marriage-bonus/). TaxSim is also able to plot graphs of average or marginal tax rates across varying income levels and can process any input comma separated value (CSV) file or dataset with custom taxpayer parameters.


## Usage:

TaxSim was designed and developed with Python 3, so please first ensure you have a compatible Python installation. [Anaconda](https://www.anaconda.com/download/) is a popular Python distribution that comes bundled with many data science related libraries and is recommended for beginners. TaxSim uses a command line interface (CLI), so adding Python to your Windows PATH is highly recommended.

After cloning the `master` branch to your workspace, `cd` into the root directory. Download all the required libraries by running this command:

`pip install -r requirements.txt`

_Note: The use of [Python virtual environments]( https://docs.python.org/3/library/venv.html) is recommended, but not required._

From then, you should have access to the TaxSim CLI. Enter `python taxsim -h` in your console and you should be presented with this help menu which should confirm that everything is properly setup:

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

### Example Usage

Running the simulator on the default input file (taxpayers.csv):
`python taxsim`

Generating a blank taxpayer input CSV file:
`python taxsim -g new_taxpayer.csv`

Running the simulator on an edited input CSV file:
`python taxsim -i new_taxpayer.csv`

Rendering average effective tax rate graphs:
`python taxsim -p average`


## Methodology:
This tax calculator was designed to simulate the effects of the Tax Cuts and Jobs Act on federal individual income tax liability. Development started in early November of 2017, thus naming conventions might seem a bit strange. For example, the function which calculations pre-TCJA taxes is named `calc_federal_taxes` and uses the `current_law_policy` policy object, whereas the function which calculates tax liability under the TCJA is named `calc_senate_2018_taxes` and uses the `senate_2018_policy` policy object. Additionally, there is an unused function named `calc_house_2018_taxes` which uses the `house_2018_policy` policy object, although it has been unmaintained ever since it became clear Congress was moving forward with the Senate version of the bill.

### Structure:
The main file which handles all IO and houses the main tax calculation functions is found in the `taxsim` folder and is named `taxsim.py` In it you will find some incidental, configurable global variables and the three main tax calculation functions which attempt to follow the flow of a traditional IRS form 1040.

Each tax calculation function takes an input taxpayer, policy object, and `mrate` Boolean which can toggle the calculation of marginal rates on and off. Since the calculation of marginal rates essentially requires running the calculator twice, it should be turned off when passing in large datasets where marginal rate calculations are not required.

The main tax functions in `taxsim.py` call functions from `tax_funcs.py` when calculating the line items of the form 1040.

Policy parameters used by the main tax calculation functions are found in the `params` folder. Policy parameters can be stored in four different ways inside the policy CSV files.
- Simple parameters can be stored by themselves as ordinary key-value pairs
- Parameters which have thresholds or brackets that vary between filing statuses are structured as arrays in the following format: `[single, married, head_of_household]`
- Parameters which have thresholds or brackets that depend on the amount of qualified children are structured as arrays in the following format: `[0_children, 1_children, 2_children, ...]`
- Tax brackets are stored as arrays which can vary in size 


## Continuous Integration and Deployment:
[![Build Status](https://travis-ci.com/TaxFoundation/taxsim.svg?token=yexSBERtR4Ec1WprzQ72&branch=master)](https://travis-ci.com/TaxFoundation/taxsim)

TaxSim is set up for continuous integration, testing, and deployment.

Travis CI is setup to watch the `master` branch for any new commits. Travis CI is configured in the ` .travis.yml` file and handles Slack notifications and GitHub PR integration.

AWS CodePipeline is responsible for testing and deploying the TaxSim API backend to AWS Elastic Beanstalk, where it is used by the 2018 and 2019 Tax Reform calculator. The CodePipeline is split up in to three steps. The first step, Source, simply watches the master branch for any new commits. Once a new commit is detected, it is cloned and sent to the second step, Testing. The testing environment is setup with AWS CodeBuild and is configurable via the ` buildspec.yml` file. If the tests run and finish without any errors, the pipeline moves on to step three, where the test-passing master branch is then deployed to AWS Elastic Beanstalk on a rolling deployment policy. For these reasons it is **pivotal** that the versions in the `web_tax_calculator_2019` and `web_tax_calculator_2018` branch remain production ready.
