"""Unit 9 retrieval comparison. No model calls or index writes."""
import argparse
import csv
import json
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path

import config
import gate
import questions


def evaluate_one(question, mode, top_k, corpus, variant):
    start = time.perf_counter()
    if mode == 'hybrid':
        from hybrid import hybrid_search
        results, semantic = hybrid_search(question, top_k=top_k, corpus=corpus, variant=variant)
        decision = gate.check(semantic)
    else:
        from store import search
        results = search(question, top_k=top_k, corpus=corpus, variant=variant)
        decision = gate.check(results)
    duration = round((time.perf_counter() - start) * 1000, 3)
    return {
        'duration_ms': duration, 'refused': not decision.passed,
        'best_distance': round(decision.best_distance, 6),
        'sources': [r.source for r in results],
        'labels': [r.label for r in results],
        'texts': [r.text for r in results],
    }


def summarize(records):
    groups = {}
    for r in records:
        groups.setdefault((r['mode'], r['scope']), []).append(r)
    summary = []
    for (mode, scope), rows in sorted(groups.items()):
        durations = [r['duration_ms'] for r in rows]
        summary.append({
            'mode': mode, 'scope': scope, 'trials': len(rows),
            'mean_ms': round(statistics.mean(durations), 3),
            'median_ms': round(statistics.median(durations), 3),
            'gate_correct': sum(r['gate_correct'] for r in rows),
            'expected_source_top1': sum(r['expected_source_top1'] for r in rows),
            'expected_source_topk': sum(r['expected_source_topk'] for r in rows),
        })
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--runs', type=int, default=3)
    parser.add_argument('--top-k', type=int, default=5)
    parser.add_argument('--corpus', default='campus_life')
    parser.add_argument('--variant', default='default')
    args = parser.parse_args()
    if args.runs < 3 or args.top_k < 1:
        parser.error('runs must be >= 3 and top-k must be >= 1')
    from store import index_exists
    if not index_exists(args.corpus, variant=args.variant):
        raise RuntimeError('Existing index missing; refusing to build or modify it')
    cases = [
        {'question': q['question'], 'scope': 'in', 'expects': q['expects']}
        for q in questions.answered()
    ]
    if len(cases) != 5 or len(questions.OUT_OF_SCOPE) != 5:
        raise RuntimeError('Expected exactly 5 in-scope and 5 out-of-scope questions')
    cases += [{'question': q, 'scope': 'out', 'expects': None} for q in questions.OUT_OF_SCOPE]
    rows = []
    for mode in ('semantic', 'hybrid'):
        for case in cases:
            for trial in range(1, args.runs + 1):
                result = evaluate_one(case['question'], mode, args.top_k, args.corpus, args.variant)
                row = {
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'mode': mode, 'scope': case['scope'], 'trial': trial,
                    'question': case['question'], 'expects': case['expects'],
                    **result,
                    'gate_correct': (not result['refused']) if case['scope'] == 'in' else result['refused'],
                    'expected_source_top1': bool(case['expects'] and result['texts'] and ' '.join(case['expects'].casefold().split()) in ' '.join(result['texts'][0].casefold().split())),
                    'expected_source_topk': bool(case['expects'] and any(' '.join(case['expects'].casefold().split()) in ' '.join(t.casefold().split()) for t in result['texts'])),
                }
                rows.append(row)
                print(f"{mode:8} {case['scope']:3} trial={trial} gate={'refused' if row['refused'] else 'passed'} top1={row['expected_source_top1']} ms={row['duration_ms']}")
    summary = summarize(rows)
    outdir = config.RESULTS_DIR
    outdir.mkdir(exist_ok=True)
    stamp = datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    json_path = outdir / f'unit9_compare_{stamp}.json'
    csv_path = outdir / f'unit9_compare_{stamp}.csv'
    md_path = outdir / f'unit9_compare_{stamp}.md'
    payload = {'metadata': {'runs': args.runs, 'top_k': args.top_k, 'corpus': args.corpus, 'variant': args.variant, 'generation_calls': 0}, 'summary': summary, 'records': rows}
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding='utf-8')
    with csv_path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        for row in rows:
            writer.writerow({**row, 'sources': '; '.join(row['sources']), 'labels': '; '.join(row['labels']), 'texts': ' || '.join(row['texts'])})
    lines = ['# Unit 9 â€” Semantic vs Hybrid Retrieval', '', f'- Corpus: `{args.corpus}`', f'- top-k: {args.top_k}', f'- Trials per question per mode: {args.runs}', '- No generation/API calls; measures retrieval and gate only', '- Expected-source matches are filename-based proxies; manual review is needed for answer-bearing evidence', '', '| Mode | Scope | Trials | Gate correct | Top-1 expected phrase | Top-k expected phrase | Mean ms | Median ms |', '|---|---|---:|---:|---:|---:|---:|---:|']
    for s in summary:
        lines.append(f"| {s['mode']} | {s['scope']} | {s['trials']} | {s['gate_correct']} | {s['expected_source_top1']} | {s['expected_source_topk']} | {s['mean_ms']} | {s['median_ms']} |")
    lines += ['', '## Limitations', '', '- Fixed index and queries make repeated retrieval deterministic; latency varies with runtime conditions.', '- Expected-phrase matching is a strict text proxy; paraphrases require manual review and generated answers are not scored here.', '- Existing criteria for source naming, answer correctness and chunk integrity require separate verification.', '- Hybrid constructs BM25 on each request, so these timings include that cost.', '']
    md_path.write_text('\n'.join(lines), encoding='utf-8')
    print('\nSaved:')
    for path in (json_path, csv_path, md_path):
        print(path)


if __name__ == '__main__':
    main()
