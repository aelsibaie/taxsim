from collections import OrderedDict
import logging
import os


def calc_effective_rates(income_tax_after_credits, employee_payroll_tax, employer_payroll_tax, gross_income):
    rates = OrderedDict()
    # Tax burden
    tax_burden = round(income_tax_after_credits + employee_payroll_tax, 2)
    rates['tax_burden'] = tax_burden

    # Tax wedge
    tax_wedge = round(income_tax_after_credits + employee_payroll_tax + employer_payroll_tax, 2)
    rates['tax_wedge'] = tax_wedge

    # Tax Rates
    # Wrap all division in the same try-except block since they all use the same denominator
    try:
        avg_effective_tax_rate = round((tax_burden / gross_income), 4)
        # Average effective tax rate
        rates['avg_effective_tax_rate'] = avg_effective_tax_rate
        # Average effective tax rate without payroll
        avg_effective_tax_rate_wo_payroll = round((income_tax_after_credits / gross_income), 4)
        rates['avg_effective_tax_rate_wo_payroll'] = avg_effective_tax_rate_wo_payroll
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