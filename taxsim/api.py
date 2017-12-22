from context import *
import taxsim.taxsim as taxsim
import taxsim.misc_funcs as misc_funcs
from collections import OrderedDict

from flask import Flask, abort, request, jsonify
app = Flask(__name__)

tax_calc = taxsim.calc_federal_taxes
policy = taxsim.current_law_policy

alt_tax_calc = taxsim.calc_senate_2018_taxes
alt_policy = taxsim.senate_2018_policy


@app.route("/taxcalc/tcja_submit", methods=['POST'])
def hello():
    if not request.json:
        abort(400)
    submission = request.json
    taxpayer = misc_funcs.create_taxpayer()
    taxpayer['filing_status'] = submission['filing_status']
    taxpayer['child_dep'] = submission['child_dep']
    taxpayer['nonchild_dep'] = submission['nonchild_dep']
    taxpayer['ordinary_income1'] = submission['ordinary_income1']
    taxpayer['ordinary_income2'] = submission['ordinary_income2']
    taxpayer['business_income'] = submission['business_income']
    taxpayer['ss_income'] = submission['ss_income']
    taxpayer['qualified_income'] = submission['qualified_income']
    taxpayer['401k_contributions'] = submission['401k_contributions']
    taxpayer['medical_expenses'] = submission['medical_expenses']
    taxpayer['sl_income_tax'] = submission['sl_income_tax']
    taxpayer['sl_property_tax'] = submission['sl_property_tax']
    taxpayer['interest_paid'] = submission['interest_paid']
    taxpayer['charity_contributions'] = submission['charity_contributions']
    taxpayer['other_itemized'] = submission['other_itemized']
    result = tax_calc(taxpayer, policy)
    alt_result = alt_tax_calc(taxpayer, alt_policy)
    return jsonify({"pre-tcja": result, "tcja": alt_result})

if __name__ == "__main__":
    app.config['DEBUG'] = True
    app.run(port=8080)