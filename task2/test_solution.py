import pytest
from solution import WikiAnimalParser
import os
from unittest.mock import Mock, patch

@pytest.fixture
def parser():
    with patch('requests.Session') as mock_session:
        parser = WikiAnimalParser()
        mock_response = Mock()
        mock_response.text = "<html>Test content</html>"
        mock_response.raise_for_status = Mock()
        parser.session.get.return_value = mock_response
        yield parser

def test_count_animals_by_letter(parser):
    test_animals = ['Аист', 'Антилопа', 'Барс', 'Волк']
    parser.count_animals_by_letter(test_animals)
    assert parser.animals_by_letter['А'] == 2
    assert parser.animals_by_letter['Б'] == 1
    assert parser.animals_by_letter['В'] == 1

def test_save_to_csv(parser, tmp_path):
    test_file = tmp_path / "test_beasts.csv"
    parser.animals_by_letter = {'А': 2, 'Б': 1, 'В': 1}
    parser.save_to_csv(test_file)
    
    assert os.path.exists(test_file)
    with open(test_file, 'r', encoding='utf-8') as f:
        content = f.read()
        assert 'А,2' in content
        assert 'Б,1' in content
        assert 'В,1' in content

@pytest.mark.parametrize("input_text,expected_first_letter", [
    ("Аист", "А"),
    ("(Белка)", "Б"),
    ("«Волк»", "В"),
])
def test_special_characters_handling(parser, input_text, expected_first_letter):
    parser.count_animals_by_letter([input_text])
    assert parser.animals_by_letter[expected_first_letter] == 1

def test_get_page_content(parser):
    content = parser.get_page_content(parser.base_url)
    assert content == "<html>Test content</html>"
    parser.session.get.assert_called_once_with(
        parser.base_url,
        headers=parser.headers,
        verify=False,
        timeout=30
    )

def test_parse_page(parser):
    test_html = '''
    <div class="mw-category">
        <a>Аист</a>
        <a>Барс</a>
    </div>
    '''
    animals = parser.parse_page(test_html)
    assert len(animals) == 2
    assert 'Аист' in animals
    assert 'Барс' in animals

def test_get_next_page_url_no_next_page(parser):
    test_html = '<html><body>Нет следующей страницы</body></html>'
    next_url = parser.get_next_page_url(test_html)
    assert next_url is None

def test_get_next_page_url_with_next_page(parser):
    test_html = '''
    <html>
        <body>
            <a href="/wiki/next_page">Следующая страница</a>
        </body>
    </html>
    '''
    next_url = parser.get_next_page_url(test_html)
    assert next_url == 'https://ru.wikipedia.org/wiki/next_page'

def test_full_run(parser):
    parser.session.get.return_value.text = '''
    <html>
        <div class="mw-category">
            <a>Аист</a>
            <a>Белка</a>
            <a>Волк</a>
        </div>
    </html>
    '''
    
    parser.run()
    
    assert parser.animals_by_letter['А'] == 1
    assert parser.animals_by_letter['Б'] == 1
    assert parser.animals_by_letter['В'] == 1