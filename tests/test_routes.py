def test_404(app):
    with app.test_client() as client:
        res = client.get("/url-che-non-esiste")
        assert res.status_code == 404

def test_tipi_eventi(app):
    with app.test_client() as client:
        res = client.get("/tipi_eventi")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "success"


def test_transazione_importo_non_valido_non_salvata(app):
    from models import Transazione

    with app.test_client() as client:
        res = client.post("/transazioni/1", json={
            "tipo_transazione": 1,
            "descrizione": "Quota evento",
            "data": "2026-01-15",
            "importo": "non numerico",
        })

        assert res.status_code == 200
        assert res.get_json() == {
            "status": "error",
            "response": "importo non numerico non valido",
        }
        assert Transazione.query.count() == 0
