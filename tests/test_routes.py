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
