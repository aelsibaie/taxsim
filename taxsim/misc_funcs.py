from collections import OrderedDict
import logging
import os
import subprocess


def calc_effective_rates(income_tax_after_credits, payroll_taxes, gross_income):
    rates = OrderedDict()
    # Tax burden
    rates['tax_burden'] = income_tax_after_credits + payroll_taxes["employee"]

    # Tax wedge
    rates['tax_wedge'] = income_tax_after_credits + payroll_taxes["employee"] + payroll_taxes["employer"]

    # Tax Rates
    # Wrap all division in the same try-except block since they all use the same denominator
    try:
        # Average effective tax rate
        rates['avg_effective_tax_rate'] = rates['tax_wedge'] / (gross_income + payroll_taxes["employer"])
        # Average effective tax rate without payroll
        rates['avg_effective_tax_rate_wo_payroll'] = income_tax_after_credits / gross_income
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


def validate_taxpayer(taxpayer):
    # Check for proper inputs
    if (isinstance(taxpayer['child_dep'], float)) or (isinstance(taxpayer['nonchild_dep'], float)):
        if taxpayer['child_dep'].is_integer() is not True:
            raise ValueError
        elif taxpayer['nonchild_dep'].is_integer() is not True:
            raise ValueError
    if ((taxpayer['filing_status'] == 2) and ((taxpayer['child_dep'] == 0) and (taxpayer['nonchild_dep'] == 0))):
        raise ValueError
    elif ((taxpayer['filing_status'] == 0) and (taxpayer['child_dep'] > 0)):
        raise ValueError
