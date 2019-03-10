from bs4 import BeautifulSoup

from tests.unit.client import client


def test_get_text_classifications(client):
    with client.session_transaction() as session:
        session['text'] = 'foo bar baz fiz'
        session['types'] = ['toxic']

    response = client.get('/text-classifications')
    soup = BeautifulSoup(response.get_data())
    judgement = soup.find_all(id='judgement')[0].string
    prediction = soup.find_all(id='prediction')[0].string
    assert judgement == 'Not toxic'
    assert 0 < float(prediction) < 1
