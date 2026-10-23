"""Run a bounded captured landing torque assessment with the selected engine.

Invocation: app .venv Python contact_study.py --request-stdin; stdin is the
ordinary contact request plus study='minimum-landing-torque'. Builder units
are mm/deg/kg/N, run time seconds and torque N*m. Outputs a JSON sampled torque
bracket/trials; this is neither a certified global minimum nor motor rating.
Shared laws/assessment are reused, but analytical and Pymunk integrators differ.
"""
import argparse
import json
import sys


def study(payload):
    from contact_cases import minimum_required_torque
    if not isinstance(payload, dict) or payload.get('study') != 'minimum-landing-torque':
        raise ValueError('Choose the bounded minimum-landing-torque study.')
    request = {key: value for key, value in payload.items() if key != 'study'}
    if request.get('engine') == 'analytical':
        from analytical_contact import simulate_contact
    elif request.get('engine') == 'pymunk':
        from contact_dynamics import simulate_contact
    else:
        raise ValueError('Choose analytical or Pymunk.')
    result=minimum_required_torque(request,lambda trial:simulate_contact(trial,stop_at_assessment=True),iterations=5)
    result['assessmentStopPolicy']='Each trial stops at first chassis arrest, compression bottom-out, underside threshold, jam or requested duration; ordinary full runs are unchanged.'
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--request-stdin', action='store_true', required=True)
    parser.parse_args()
    try:
        print(json.dumps(study(json.load(sys.stdin)), allow_nan=False))
        return 0
    except (ValueError, KeyError, TypeError, ArithmeticError, ImportError) as error:
        print(json.dumps({'error': str(error)}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
