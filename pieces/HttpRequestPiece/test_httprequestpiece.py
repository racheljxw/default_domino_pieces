from domino.testing import piece_dry_run
import base64
import json


def _decode(entry):
    return json.loads(base64.b64decode(entry['base64_content'].encode('utf-8')))


def test_httprequest_get_multiple_urls():
    input_data = {
        'urls': [
            'https://jsonplaceholder.typicode.com/posts',
            'https://jsonplaceholder.typicode.com/todos',
        ],
        'method': 'GET',
    }
    piece_output = piece_dry_run(
        piece_name="HttpRequestPiece",
        input_data=input_data
    )
    results = piece_output['results']
    assert len(results) == 2
    assert [r['url'] for r in results] == input_data['urls']
    assert all(r['status'] == 'success' for r in results)
    assert all(isinstance(_decode(r), list) for r in results)


def test_httprequest_failure_isolation():
    input_data = {
        'urls': [
            'https://jsonplaceholder.typicode.com/posts',
            'https://thisdomain.invalid/whatever',
        ],
        'method': 'GET',
    }
    piece_output = piece_dry_run(
        piece_name="HttpRequestPiece",
        input_data=input_data
    )
    results = piece_output['results']
    assert len(results) == 2

    assert results[0]['status'] == 'success'
    assert results[0]['base64_content'] is not None
    assert results[0]['error'] is None

    assert results[1]['status'] == 'failed'
    assert results[1]['base64_content'] is None
    assert results[1]['error'] is not None


def test_httprequest_post():
    input_data = {
        'urls': ['https://httpbin.org/post'],
        'method': 'POST',
        'body_json_data': json.dumps({
            'key_1': 'domino',
            'key_2': 'testing-post'
        })
    }
    piece_output = piece_dry_run(
        piece_name="HttpRequestPiece",
        input_data=input_data
    )
    results = piece_output['results']
    assert len(results) == 1
    assert results[0]['status'] == 'success'
    body = _decode(results[0])
    assert body['json']['key_1'] == 'domino'
    assert body['json']['key_2'] == 'testing-post'


def test_httprequest_put():
    input_data = {
        'urls': ['https://httpbin.org/put'],
        'method': 'PUT',
        'body_json_data': json.dumps({
            'key_1': 'domino',
            'key_2': 'testing-put'
        })
    }
    piece_output = piece_dry_run(
        piece_name="HttpRequestPiece",
        input_data=input_data
    )
    results = piece_output['results']
    assert results[0]['status'] == 'success'
    body = _decode(results[0])
    assert body['json']['key_1'] == 'domino'
    assert body['json']['key_2'] == 'testing-put'


def test_httprequest_delete():
    input_data = {
        'urls': ['https://httpbin.org/delete'],
        'method': 'DELETE'
    }
    piece_output = piece_dry_run(
        piece_name="HttpRequestPiece",
        input_data=input_data
    )
    results = piece_output['results']
    assert results[0]['status'] == 'success'
    body = _decode(results[0])
    assert body['url'] == 'https://httpbin.org/delete'
