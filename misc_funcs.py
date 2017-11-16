from collections import OrderedDict
import logging
import os


def calc_effective_rates(income_tax_after_credits, payroll_taxes, gross_income):
    rates = OrderedDict()
    # Tax burden
    rates['tax_burden'] = round(
        income_tax_after_credits + payroll_taxes["employee"], 2)

    # Tax wedge
    rates['tax_wedge'] = round(
        income_tax_after_credits + payroll_taxes["employee"] + payroll_taxes["employer"], 2)

    # Tax Rates
    # Wrap all division in the same try-except block since they all use the same denominator
    try:
        # Average effective tax rate
        rates['avg_effective_tax_rate'] = round(
            (rates['tax_burden'] / gross_income), 4)
        # Average effective tax rate without payroll
        rates['avg_effective_tax_rate_wo_payroll'] = round(
            (income_tax_after_credits / gross_income), 4)
    except ZeroDivisionError as e:
        logging.warning("Taxpayer has gross_income of $0. Potential refund not reflected in rates.")
        rates['avg_effective_tax_rate'] = 0
        rates['avg_effective_tax_rate_wo_payroll'] = 0

    return rates


def require_dir(directory):
    if not os.path.exists(directory):
        logging.warning(directory + " Does not exist.")
        os.makedirs(directory)
        logging.info(directory + " Successfully created.")
    return directory

def create_taxpayer():
    default_taxpayer = OrderedDict(
        [('filing_status', 0),
         ('child_dep', 0),
         ('nonchild_dep', 0),
         ('ordinary_income1', 0),
         ('ordinary_income2', 0),
         ('business_income', 0),
         ('ss_income', 0),
         ('qualified_income', 0),
         ('401k_contributions', 0),
         ('medical_expenses', 0),
         ('sl_income_tax', 0),
         ('sl_property_tax', 0),
         ('interest_paid', 0),
         ('charity_contributions', 0),
         ('other_itemized', 0)])
    return default_taxpayer
