from taxsim.context import *
import taxsim.taxsim as taxsim
import taxsim.misc_funcs as misc_funcs
from collections import OrderedDict
from datetime import datetime
import copy

from flask import Flask, abort, request, jsonify
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

tax_calc = taxsim.calc_federal_taxes
policy = taxsim.current_law_policy
policy_2019 = taxsim.current_law_2019_policy

alt_tax_calc = taxsim.calc_senate_2018_taxes
alt_policy = taxsim.senate_2018_policy
alt_policy_2019 = taxsim.senate_2019_policy
alt_policy_2019_ss = taxsim.senate_2019_ss_policy

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

logger = taxsim.logging.getLogger()
logger.disabled = True


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
        taxpayer['business_income_service'] = submission['business_income_service']
    except KeyError:
        taxsim.logging.warn("Received malformed json data from " + request.remote_addr)
        abort(400)
    try:
        # Copy taxpayers
        taxpayer1 = copy.deepcopy(taxpayer)
        taxpayer2 = copy.deepcopy(taxpayer)
        taxpayer3 = copy.deepcopy(taxpayer)
        taxpayer4 = copy.deepcopy(taxpayer)
        taxpayer5 = copy.deepcopy(taxpayer)
        
        # 2018
        result = tax_calc(taxpayer1, policy)
        alt_result = alt_tax_calc(taxpayer2, alt_policy)

        # 2019
        result_2019 = tax_calc(taxpayer3, policy_2019)
        alt_result_2019 = alt_tax_calc(taxpayer4, alt_policy_2019)
        alt_result_2019_ss = alt_tax_calc(taxpayer5, alt_policy_2019_ss)

    except BaseException:
        taxsim.logging.warn("Taxpayer failed input validation for " + request.remote_addr)
        abort(400)
    taxsim.logging.info("Calculations complete for " + request.remote_addr)

    results = []
    results.append({'plan': {
        'id': 'pre-tcja',
        'name': 'Previous Law',
        'year': 2018},
        'results': result})
    results.append({'plan': {
        'id': 'tcja',
        'name': 'Tax Cuts and Jobs Act',
        'year': 2018},
        'results': alt_result})
    results.append({'plan': {
        'id': 'pre-tcja',
        'name': 'Previous Law',
        'year': 2019},
        'results': result_2019})
    results.append({'plan': {
        'id': 'tcja',
        'name': 'Tax Cuts and Jobs Act',
        'year': 2019},
        'results': alt_result_2019})
    results.append({'plan': {
        'id': 'ss2100',
        'name': 'Social Security 2100 Act',
        'year': 2019},
        'results': alt_result_2019_ss})

    return jsonify(results)


if __name__ == "__main__":
    # app.debug = True
    app.run()
