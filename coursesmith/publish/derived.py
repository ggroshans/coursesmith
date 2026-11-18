"""Derived numbers: arithmetic on sourced numbers, recorded and checked, never trusted.

A worked answer to a design question does back-of-the-envelope math: a billion writes a day is about 11,600
writes a second. The sourced-numbers rule (a number in prose must be in the entry's facts) would reject "11,600".
Instead of loosening the rule, a derived number is declared with the facts it comes from and the expression that
produces it, and the checker recomputes it:

    {"values": [11574, 11600], "from": ["<sent_id>", ...],
     "expr": "1000000000 / 86400", "reason": "writes per day to writes per second"}

It holds only if every sentence in `from` is one the entry cites, `expr` uses only + - * / ** and parentheses on
numbers, every number in `expr` is in the entry's facts (or is a unit constant such as 86400 or 1024, or a small
integer), and each declared value is the result within 1%, or its rounding. A writer records these in the batch
file (`"derived": {"<entry id>": [...]}`); a person may add them to waivers.json. Nothing else widens the rule.
"""
import ast
import math
import operator

SAFE_CONSTANTS = {60.0, 3600.0, 86400.0, 24.0, 7.0, 30.0, 365.0, 100.0, 1000.0, 1024.0, 1e6, 1e9, 1e12, 8.0}
OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv,
       ast.Pow: operator.pow, ast.USub: operator.neg, ast.UAdd: operator.pos}


class DerivedError(ValueError):
    pass


def evaluate(expr):
    """(value, set of the numeric literals used) for an arithmetic expression, or DerivedError."""
    try:
        tree = ast.parse(str(expr), mode="eval")
    except SyntaxError:
        raise DerivedError(f"cannot read expression {expr!r}")
    literals = set()

    def go(n):
        if isinstance(n, ast.Expression):
            return go(n.body)
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)) and not isinstance(n.value, bool):
            literals.add(float(n.value))
            return float(n.value)
        if isinstance(n, ast.BinOp) and type(n.op) in OPS:
            a, b = go(n.left), go(n.right)
            if isinstance(n.op, ast.Pow) and (abs(b) > 12 or abs(a) > 1e6):
                raise DerivedError("exponent too large")
            try:
                return OPS[type(n.op)](a, b)
            except ZeroDivisionError:
                raise DerivedError("division by zero")
        if isinstance(n, ast.UnaryOp) and type(n.op) in OPS:
            return OPS[type(n.op)](go(n.operand))
        raise DerivedError(f"only numbers and + - * / ** ( ) are allowed in {expr!r}")

    value = go(tree)
    if not math.isfinite(value):
        raise DerivedError("not a finite number")
    return value, literals


def cited_sids(e):
    ids = list((e.get("definition") or {}).get("sent_ids") or [])
    for k in ("facts", "events"):
        for f in e.get(k) or []:
            ids += f.get("sent_ids") or []
    for c in e.get("conflicts") or []:
        ids += ([c["sent_id"]] if c.get("sent_id") else []) + list(c.get("sent_ids") or [])
    ids += e.get("mention_sent_ids") or []
    return set(ids)


def _matches(value, result):
    if abs(value - result) <= 0.01 * abs(result):
        return True
    return any(round(result, d) == value for d in range(0, 4)) or round(result) == value


def check_item(item, e, allowed):
    """Problems with one derived-number declaration for entry `e` (empty when it holds)."""
    probs = []
    values = item.get("values")
    if not values or not all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in values):
        probs.append("needs `values`, a list of numbers")
    src = item.get("from")
    if not src or not isinstance(src, list):
        probs.append("needs `from`, the sentence ids the inputs come from")
    else:
        miss = [s for s in src if s not in cited_sids(e)]
        if miss:
            probs.append(f"`from` names sentences the entry does not cite: {miss[:3]}")
    if not item.get("expr"):
        probs.append("needs `expr`, the arithmetic")
        return probs
    try:
        result, literals = evaluate(item["expr"])
    except DerivedError as ex:
        return probs + [str(ex)]
    foreign = sorted(x for x in literals if x not in allowed and x not in SAFE_CONSTANTS
                     and not (x <= 12 and x == int(x)))
    if foreign:
        probs.append(f"`expr` uses numbers that are not in the entry's facts: {foreign[:4]}")
    for v in values or []:
        if isinstance(v, (int, float)) and not _matches(float(v), result):
            probs.append(f"value {v} is not the result of `{item['expr']}` (that is {result:.6g})")
    return probs


def waived(items, e, allowed):
    """(set of waived numbers, problems) for the derived declarations of one entry. Only declarations that hold
    waive anything."""
    out, probs = set(), []
    for item in items or []:
        p = check_item(item, e, allowed)
        if p:
            probs += p
        else:
            out |= {float(v) for v in item["values"]}
    return out, probs
