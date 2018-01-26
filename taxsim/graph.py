import pandas as pd
import matplotlib
matplotlib.use('agg', warn=False, force=True)
from matplotlib import pyplot as plt
from matplotlib.ticker import FuncFormatter
from collections import OrderedDict
from tqdm import tqdm
import logging
import json

from . import taxsim
from . import misc_funcs

plt.style.use('ggplot')

with open('average_graphs.json') as infile:
    average_graphs = json.load(infile)
with open('marginal_graphs.json') as infile:
    marginal_graphs = json.load(infile)


def make_graph(main_income_type,
               file_name,
               filing_status,
               child_dep,
               income_ratios,
               payroll,
               step,
               start=1,
               stop=10000,
               rate_type="average"):

    current_law_result_list = []
    house_2018_result_list = []
    senate_2018_result_list = []

    for i in range(start, stop):
        income = i * step
        default_taxpayer = misc_funcs.create_taxpayer()
        default_taxpayer['filing_status'] = filing_status
        default_taxpayer['child_dep'] = child_dep
        default_taxpayer['ordinary_income1'] = income * income_ratios["ordinary"]
        default_taxpayer['business_income'] = income * income_ratios["business"]
        default_taxpayer['ss_income'] = income * income_ratios["ss"]
        default_taxpayer['qualified_income'] = income * income_ratios["qualified"]

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
        '-current_law_graph_data.csv',
        index=False)
    house_2018_df.to_csv(
        taxsim.GRAPH_DATA_RESULTS_DIR +
        file_name +
        '-house_2018_graph_data.csv',
        index=False)
    senate_2018_df.to_csv(
        taxsim.GRAPH_DATA_RESULTS_DIR +
        file_name +
        '-senate_2018_graph_data.csv',
        index=False)

    filing_status_string = "Single"
    if filing_status == 1:
        filing_status_string = "Married"
    elif filing_status == 2:
        filing_status_string = "Head of Household"

    if payroll == 0:
        graph_rate_type = "avg_effective_tax_rate_wo_payroll"
        payroll_string = "without payroll taxes"
    else:
        graph_rate_type = "avg_effective_tax_rate"
        payroll_string = "with employee-side payroll taxes"

    type_string = "Average"
    drawstyle_string = "steps-pre"
    if rate_type == "marginal":
        drawstyle_string = "default"
        graph_rate_type = "marginal_income_tax_rate"
        if income_ratios["business"] > 0:
            graph_rate_type = "marginal_business_income_tax_rate"
        type_string = "Marginal"

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

    # Current Law
    ax.plot(
        current_law_df["gross_income"],
        current_law_df[graph_rate_type],
        drawstyle=drawstyle_string,
        label='Current Law')
    # House 2018 Proposal
    ax.plot(
        house_2018_df["gross_income"],
        house_2018_df[graph_rate_type],
        drawstyle=drawstyle_string,
        label='House 2018 Proposal')
    # Senate 2018 Proposal
    ax.plot(
        senate_2018_df["gross_income"],
        senate_2018_df[graph_rate_type],
        drawstyle=drawstyle_string,
        label='Senate 2018 Proposal')

    ax.legend(loc='upper left')
    ax.set_title(
        type_string +
        ' Federal Income Tax Rate by Gross Income, ' +
        filing_status_string +
        ' Filer, ' +
        child_string +
        ', ' +
        main_income_type)
    ax.set_xlabel('Gross Income')
    ax.set_ylabel(type_string + ' Tax Rate (' + payroll_string + ')')
    fig.set_size_inches(12, 6)
    fig.savefig(taxsim.RESULTS_DIR + file_name + ".png", dpi=100)
    # plt.show()  # Uncomment to debug plots


def render_graphs(plot_type):
    logging.info("Begining graph calculations. This should reasonably take 1-5 seconds per graph.")

    if plot_type == "marginal":
        graphs = marginal_graphs
    elif plot_type == "average":
        graphs = average_graphs

    for graph in tqdm(graphs, desc='Rendering graphs', unit='graph'):
        logging.info("Rendering: " + graph["file_name"])
        make_graph(graph["main_income_type"],
                   graph["file_name"],
                   graph["filing_status"],
                   graph["child_dep"],
                   graph["income_ratios"],
                   graph["payroll"],
                   graph["step"],
                   graph["start"],
                   graph["stop"],
                   graph["rate_type"])
