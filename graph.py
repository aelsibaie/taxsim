import taxsim
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from collections import OrderedDict
from tqdm import tqdm
import logging

plt.style.use('ggplot')


def make_graph(main_income_type,
               file_name,
               filing_status,
               child_dep,
               income_ratios,
               payroll,
               step,
               top_range=10000,
               position=0):

    current_law_result_list = []
    house_2018_result_list = []
    senate_2018_result_list = []

    for i in tqdm(
            range(1, top_range),
            desc=file_name,
            unit='taxpayer',
            leave=True,
            ascii=True,
            position=position):
        income = i * step
        default_taxpayer = OrderedDict(
            [('filing_status', filing_status),
             ('child_dep', child_dep),
             ('nonchild_dep', 0),
             ('ordinary_income1', income * income_ratios["ordinary"]),
             ('ordinary_income2', 0),
             ('business_income', income * income_ratios["business"]),
             ('ss_income', income * income_ratios["ss"]),
             ('qualified_income', income * income_ratios["qualified"]),
             ('401k_contributions', 0),
             ('medical_expenses', 0),
             ('sl_income_tax', 0),
             ('sl_property_tax', 0),
             ('interest_paid', 0),
             ('charity_contributions', 0),
             ('other_itemized', 0)])
        current_law_result = taxsim.calc_federal_taxes(
            default_taxpayer, taxsim.current_law_policy)
        current_law_result_list.append(current_law_result)
        house_2018_result = taxsim.calc_house_2018_taxes(
            default_taxpayer, taxsim.house_2018_policy)
        house_2018_result_list.append(house_2018_result)
        senate_2018_result = taxsim.calc_senate_2018_taxes(
            default_taxpayer, taxsim.senate_2018_policy)
        senate_2018_result_list.append(senate_2018_result)

    current_law_df = pd.DataFrame(current_law_result_list)
    house_2018_df = pd.DataFrame(house_2018_result_list)
    senate_2018_df = pd.DataFrame(senate_2018_result_list)

    # Save CSVs
    current_law_df.to_csv(
        taxsim.GRAPH_DATA_RESULTS_DIR +
        file_name +
        '-current_law_graph_data.csv')
    house_2018_df.to_csv(
        taxsim.GRAPH_DATA_RESULTS_DIR +
        file_name +
        '-house_2018_graph_data.csv')
    senate_2018_df.to_csv(
        taxsim.GRAPH_DATA_RESULTS_DIR +
        file_name +
        '-senate_2018_graph_data.csv')

    filing_status_string = "Single"
    if filing_status == 1:
        filing_status_string = "Married"
    elif filing_status == 2:
        filing_status_string = "Head of Household"

    if payroll == 0:
        rate_type = "avg_effective_tax_rate_wo_payroll"
        payroll_string = "without payroll taxes"
    else:
        rate_type = "avg_effective_tax_rate"
        payroll_string = "with employee-side payroll taxes"

    if child_dep == 0:
        child_string = "No children"
    elif child_dep == 1:
        child_string = "1 child"
    else:
        child_string = str(child_dep) + " children"

    # Plot figure(s)
    fig = plt.figure()
    ax = plt.axes()
    ax.yaxis.set_major_formatter(FuncFormatter('{0:.0%}'.format))
    ax.xaxis.set_major_formatter(FuncFormatter('${:,.0f}'.format))
    ax.plot(
        current_law_df["gross_income"],
        current_law_df[rate_type],
        drawstyle='steps-pre',
        label='Current Law')
    ax.plot(
        house_2018_df["gross_income"],
        house_2018_df[rate_type],
        drawstyle='steps-pre',
        label='House 2018 Proposal')
    ax.plot(
        senate_2018_df["gross_income"],
        senate_2018_df[rate_type],
        drawstyle='steps-pre',
        label='Senate 2018 Proposal')
    ax.legend(loc='upper left')
    ax.set_title(
        'Average Federal Income Tax Rate by Gross Income, ' +
        filing_status_string +
        " Filer, " +
        child_string +
        ", " +
        main_income_type)
    ax.set_xlabel('Gross Income')
    ax.set_ylabel('Average Tax Rate (' + payroll_string + ')')
    fig.set_size_inches(12, 6)
    fig.savefig(taxsim.RESULTS_DIR + file_name + ".png", dpi=100)


graphs = [
    {
        "main_income_type": "Ordinary Income",
        "file_name": "single_0_ordinary",
        "filing_status": 0,
        "child_dep": 0,
        "income_ratios": {
            "ordinary": 1.0,
            "business": 0.0,
            "ss": 0.0,
            "qualified": 0.0},
        "payroll": 0,
        "step": 25
    },
    {
        "main_income_type": "Business Income",
        "file_name": "single_0_business",
        "filing_status": 0,
        "child_dep": 0,
        "income_ratios": {
            "ordinary": 0.0,
            "business": 1.0,
            "ss": 0.0,
            "qualified": 0.0},
        "payroll": 0,
        "step": 100
    },
    {
        "main_income_type": "Qualified Income",
        "file_name": "single_0_qualified",
        "filing_status": 0,
        "child_dep": 0,
        "income_ratios": {
            "ordinary": 0.0,
            "business": 0.0,
            "ss": 0.0,
            "qualified": 1.0},
        "payroll": 0,
        "step": 100
    },
    {
        "main_income_type": "50% Business & 50% Qualified Income",
        "file_name": "single_0_bus_and_qual",
        "filing_status": 0,
        "child_dep": 0,
        "income_ratios": {
            "ordinary": 0.0,
            "business": 0.5,
            "ss": 0.0,
            "qualified": 0.5},
        "payroll": 0,
        "step": 200
    },
    {
        "main_income_type": "Ordinary Income",
        "file_name": "married_0_ordinary",
        "filing_status": 1,
        "child_dep": 0,
        "income_ratios": {
            "ordinary": 1.0,
            "business": 0.0,
            "ss": 0.0,
            "qualified": 0.0},
        "payroll": 0,
        "step": 10
    },
    {
        "main_income_type": "Ordinary Income",
        "file_name": "hoh_0_ordinary",
        "filing_status": 2,
        "child_dep": 0,
        "income_ratios": {
            "ordinary": 1.0,
            "business": 0.0,
            "ss": 0.0,
            "qualified": 0.0},
        "payroll": 0,
        "step": 10
    },
    {
        "main_income_type": "Ordinary Income",
        "file_name": "hoh_2_ordinary_payroll",
        "filing_status": 2,
        "child_dep": 0,
        "income_ratios": {
            "ordinary": 1.0,
            "business": 0.0,
            "ss": 0.0,
            "qualified": 0.0},
        "payroll": 1,
        "step": 10
    },
    {
        "main_income_type": "Ordinary Income",
        "file_name": "married_2_ordinary",
        "filing_status": 1,
        "child_dep": 2,
        "income_ratios": {
            "ordinary": 1.0,
            "business": 0.0,
            "ss": 0.0,
            "qualified": 0.0},
        "payroll": 0,
        "step": 10
    },
    {
        "main_income_type": "Ordinary Income",
        "file_name": "hoh_2_ordinary",
        "filing_status": 2,
        "child_dep": 2,
        "income_ratios": {
            "ordinary": 1.0,
            "business": 0.0,
            "ss": 0.0,
            "qualified": 0.0},
        "payroll": 0,
        "step": 10
    }
]

if __name__ == '__main__':
    logging.info("Begining graph calculations. This should reasonably take 1-5 seconds per graph.")
    position = 0
    for graph in tqdm(graphs, desc='Rendering graphs', unit='graph', ascii=True, leave=True, position=position):
        logging.info("Rendering: " + graph["file_name"])
        position =+ 1
        make_graph(graph["main_income_type"],
                   graph["file_name"],
                   graph["filing_status"],
                   graph["child_dep"],
                   graph["income_ratios"],
                   graph["payroll"],
                   graph["step"],
                   position)
