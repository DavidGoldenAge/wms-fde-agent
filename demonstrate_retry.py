"""Demonstrate feedback to the model from a deliberately failing baseline.

The first candidate is hand-written baseline code, not a model attempt; the
result must not be counted as Pass@1 or as a model self-correction rate.
"""
import json, time
import benchmark, fde

def main():
    start = time.monotonic()
    baseline_ok, feedback = fde.verify(benchmark.BASELINE)
    if baseline_ok:
        raise SystemExit('Expected the deliberately buggy baseline to fail.')
    model = fde.generate(fde.evidence('SKU-8821'), feedback)
    try:
        passed, output = fde.verify(model['fixed_code'])
    except (ValueError, SyntaxError) as e:
        passed, output = False, str(e)
    print(json.dumps({'baseline_passed': baseline_ok, 'baseline_feedback':feedback,
                      'model_report':model, 'model_passed':passed, 'model_feedback':output,
                      'elapsed_seconds':round(time.monotonic()-start,2)}, indent=2, ensure_ascii=False))
if __name__ == '__main__': main()
