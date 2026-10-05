from routes import eval_expr, calcola_formula

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

def test_calcola_formula_variabili_ripetute_con_prefisso_comune():
    formula = "([[quota]] + [[quota_saldo]]) * [[partecipanti]] - [[quota]]"
    variabili = {"quota": 12.5, "quota_saldo": 7.5, "partecipanti": 3}

    assert calcola_formula(formula, variabili) == 47.5
