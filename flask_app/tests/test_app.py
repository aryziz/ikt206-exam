
def test_home(client):
    response = client.get('/')
    
    assert b"<title>Flask Example</title>" in response.data
    
def test_public(client):
    response = client.get('/public/')
    
    assert response.status_code == 200