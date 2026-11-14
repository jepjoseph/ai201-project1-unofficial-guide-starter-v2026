"""Structured request instrumentation for Unit 9; no secrets or prompts logged."""
import contextvars
import functools
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import config

_request_gate = contextvars.ContextVar('request_gate', default=None)


def _write(record):
    path = Path(os.getenv('AI201_LOG_PATH', str(config.RESULTS_DIR / 'milestone5_requests.jsonl')))
    path.parent.mkdir(parents=True, exist_ok=True)
    record['timestamp'] = datetime.now(timezone.utc).isoformat()
    with path.open('a', encoding='utf-8') as stream:
        stream.write(json.dumps(record, ensure_ascii=False, default=str) + '\n')


def set_request_gate(decision, sources=None):
    _request_gate.set({
        'best_distance': decision.best_distance,
        'threshold': decision.threshold,
        'refused': not decision.passed,
        'sources': sorted(set(sources or [])),
    })


def instrument_request(*, kind):
    def decorator(function):
        @functools.wraps(function)
        def wrapped(*args, **kwargs):
            token = _request_gate.set(None)
            started = time.perf_counter()
            question = args[0] if kind == 'ask' and args else getattr(args[0], 'question', '') if args else kwargs.get('question', '')
            retrieval = kwargs.get('retrieval', 'semantic') if kind == 'ask' else getattr(args[0], 'retrieval', 'semantic')
            corpus = kwargs.get('corpus') if kind == 'ask' else getattr(args[0], 'corpus', None)
            variant = kwargs.get('variant', 'default') if kind == 'ask' else getattr(args[0], 'variant', 'default')
            status = 'success'
            error_type = None
            outcome = None
            try:
                outcome = function(*args, **kwargs)
                gate = _request_gate.get()
                if gate and gate['refused']:
                    status = 'refused'
                return outcome
            except Exception as exc:
                status = 'error'
                error_type = type(exc).__name__
                raise
            finally:
                gate = _request_gate.get() or {}
                if isinstance(outcome, dict):
                    sources = outcome.get('sources', [])
                    gate = {**gate, 'sources': sources, 'refused': outcome.get('refused', False)}
                record = {
                    'event': 'rag_request', 'kind': kind,
                    'question': str(question), 'retrieval_mode': str(retrieval),
                    'corpus': corpus or config.CORPUS, 'variant': variant,
                    'duration_ms': round((time.perf_counter() - started) * 1000, 3),
                    'status': status, 'error_type': error_type,
                    'best_distance': gate.get('best_distance'),
                    'threshold': gate.get('threshold'),
                    'refused': gate.get('refused'),
                    'sources': gate.get('sources', []),
                }
                try:
                    _write(record)
                except OSError as log_error:
                    import sys
                    print(f'[instrumentation] log write failed: {type(log_error).__name__}', file=sys.stderr)
                _request_gate.reset(token)
        return wrapped
    return decorator


def log_http_error(*, question, retrieval, status_code, duration_ms):
    try:
        _write({
            'event': 'http_request_error', 'kind': 'http',
            'question': str(question), 'retrieval_mode': str(retrieval),
            'corpus': config.CORPUS, 'variant': 'default',
            'duration_ms': round(duration_ms, 3), 'status': 'error',
            'http_status': status_code, 'error_type': 'HTTPError',
            'best_distance': None, 'threshold': None, 'refused': None,
            'sources': [],
        })
    except OSError as log_error:
        import sys
        print(f'[instrumentation] log write failed: {type(log_error).__name__}', file=sys.stderr)
