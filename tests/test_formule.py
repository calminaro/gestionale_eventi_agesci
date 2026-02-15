from app import eval_expr, calcola_formula

def test_eval_expr_ok():
    assert eval_expr("2+3*4") == 14

def test_eval_expr_blocca_codice():
    import pytest
    with pytest.raises(Exception):
        eval_expr("__import__('os').system('rm -rf /')")

def test_calcola_formula():
    formula = "[[a]]+[[b]]*2"
    variabili = {"a": 10, "b": 3}
    assert calcola_formula(formula, variabili) == 16
