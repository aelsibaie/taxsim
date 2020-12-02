from collections import OrderedDict
import logging
import os
import subprocess


def calc_effective_rates(income_tax_after_credits, payroll_taxes, gross_income, results):
    # sum PRT
    results['total_payroll_tax'] = payroll_taxes["employee"] + payroll_taxes["employer"]  # TODO: add sched se

    # cash income
    results['cash_income'] = gross_income + payroll_taxes["employer"]

    # Tax burden
    results['tax_burden'] = income_tax_after_credits + payroll_taxes["employee"]

    # Tax wedge
    results['tax_wedge'] = income_tax_after_credits + payroll_taxes["employee"] + payroll_taxes["employer"]

    results['take_home_pay'] = results['cash_income'] - results['tax_wedge']

    # Tax Rates
    # Wrap all division in the same try-except block since they all use the same denominator
    try:
        # Average effective tax rate
        #results['avg_effective_tax_rate'] = income_tax_after_credits / (gross_income + payroll_taxes["employer"])
        results['avg_effective_tax_rate'] = results['tax_wedge'] / results['cash_income'] 
        # Average effective tax rate without payroll
        results['avg_effective_tax_rate_wo_payroll'] = income_tax_after_credits / gross_income
    except ZeroDivisionError as e:
        logging.warning("Taxpayer has gross_income of $0. Potential refund not reflected in rates.")
        results['avg_effective_tax_rate'] = 0
        results['avg_effective_tax_rate_wo_payroll'] = 0

    return results


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
         ('other_itemized', 0),
         ('business_income_service', 0)])
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
