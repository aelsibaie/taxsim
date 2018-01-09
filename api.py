from taxsim.context import *
import taxsim.taxsim as taxsim
import taxsim.misc_funcs as misc_funcs
from collections import OrderedDict
from datetime import datetime

from flask import Flask, abort, request, jsonify
app = Flask(__name__)

tax_calc = taxsim.calc_federal_taxes
policy = taxsim.current_law_policy

alt_tax_calc = taxsim.calc_senate_2018_taxes
alt_policy = taxsim.senate_2018_policy

'''
curl --request POST \
  --url http://localhost:8080/taxcalc/tcja_submit \
  --header 'content-type: application/json' \
  --data '{
        "filing_status": 2,
        "child_dep": 1,
        "nonchild_dep": 1,
        "ordinary_income1": 10000,
        "ordinary_income2": 0,
        "business_income": 0,
        "ss_income": 0,
        "qualified_income": 0,
        "401k_contributions": 0,
        "medical_expenses": 0,
        "sl_income_tax": 0,
        "sl_property_tax": 0,
        "interest_paid": 0,
        "charity_contributions": 0,
        "other_itemized": 0
}'
'''


@app.route("/taxcalc/tcja_submit", methods=['POST'])
def hello():
    if not request.json:
        taxsim.logging.warn("Received non-json data from " + request.remote_addr)
        abort(400)
    taxsim.logging.info("Received input taxpayer from " + request.remote_addr)
    taxsim.logging.debug(request.json)
    submission = request.json
    taxpayer = misc_funcs.create_taxpayer()
    try:
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
    except KeyError:
        taxsim.logging.warn("Received malformed json data from " + request.remote_addr)
        abort(400)
    try:
        result = tax_calc(taxpayer, policy)
        alt_result = alt_tax_calc(taxpayer, alt_policy)
    except BaseException:
        taxsim.logging.warn("Taxpayer failed input validation for " + request.remote_addr)
        abort(400)
    taxsim.logging.info("Calculations complete for " + request.remote_addr)
    return jsonify({"pre-tcja": result, "tcja": alt_result})


if __name__ == "__main__":
    #app.debug = True
    app.run()
