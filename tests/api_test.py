from context import *

import json

import api


def test_api_200():
    with api.app.test_client() as web:
        resp = web.post('/taxcalc/tcja_submit', data=json.dumps(
            {
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
            }
        ), follow_redirects=True, headers={'content-type': 'application/json'})

        assert resp.status_code == 200


def test_api_failure_single_with_kids():
    with api.app.test_client() as web:
        resp = web.post('/taxcalc/tcja_submit', data=json.dumps(
            {
                "filing_status": 0,
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
            }
        ), follow_redirects=True, headers={'content-type': 'application/json'})

        assert resp.status_code == 400


def test_api_failure_decimal_kids():
    with api.app.test_client() as web:
        resp = web.post('/taxcalc/tcja_submit', data=json.dumps(
            {
                "filing_status": 1,
                "child_dep": 1.123,
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
            }
        ), follow_redirects=True, headers={'content-type': 'application/json'})

        assert resp.status_code == 400


def test_api_failure_string():
    with api.app.test_client() as web:
        resp = web.post('/taxcalc/tcja_submit', data=json.dumps(
            {
                "filing_status": 1,
                "child_dep": 1,
                "nonchild_dep": 1,
                "ordinary_income1": "bad stuff!",
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
            }
        ), follow_redirects=True, headers={'content-type': 'application/json'})

        assert resp.status_code == 400
