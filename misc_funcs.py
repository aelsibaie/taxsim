from collections import OrderedDict

def calc_effective_rates(income_tax_after_credits, employee_payroll_tax, employer_payroll_tax, gross_income):
    rates = OrderedDict()
    # Tax burden
    tax_burden = round(income_tax_after_credits + employee_payroll_tax, 2)
    rates['tax_burden'] = tax_burden

    # Tax wedge
    tax_wedge = round(income_tax_after_credits + employee_payroll_tax + employer_payroll_tax, 2)
    rates['tax_wedge'] = tax_wedge

    # Average effective tax rate
    avg_effective_tax_rate = round((tax_burden / gross_income), 4)
    rates['avg_effective_tax_rate'] = avg_effective_tax_rate

    # Average effective tax rate without payroll
    avg_effective_tax_rate_wo_payroll = round((income_tax_after_credits / gross_income), 4)
    rates['avg_effective_tax_rate_wo_payroll'] = avg_effective_tax_rate_wo_payroll

    return rates
