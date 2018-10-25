from fuzzywuzzy import fuzz


from yui.util import (
    b64_redirect,
    bold,
    bool2str,
    code,
    fuzzy_korean_partial_ratio,
    fuzzy_korean_ratio,
    italics,
    normalize_korean_nfc_to_nfd,
    preformatted,
    quote,
    strike,
    strip_tags,
)


def test_strip_tags():

    assert strip_tags('aaa<b>bbb<span>ccc</span>ddd</b>eee<img>fff') == (
        'aaabbbcccdddeeefff'
    )


def test_bool2str():
    """True -> 'true', False -> 'false'"""

    assert bool2str(True) == 'true'
    assert bool2str(False) == 'false'


def test_slack_syntax():
    """Test slack syntax helpers."""

    assert bold('item4') == '*item4*'
    assert code('item4') == '`item4`'
    assert italics('item4') == '_item4_'
    assert preformatted('item4') == '```item4```'
    assert strike('item4') == '~item4~'
    assert quote('item4') == '>item4'


def test_normalize_nfd():
    """Test Korean to NFD tool."""

    assert normalize_korean_nfc_to_nfd('123asdf가나다라밯맣희QWERTY') == ''.join(
        chr(x) for x in
        [
            49, 50, 51,  # 123
            97, 115, 100, 102,  # asdf
            4352, 4449, 4354, 4449, 4355, 4449, 4357, 4449,  # 가나다라
            4359, 4449, 4546, 4358, 4449, 4546, 4370, 4468,  # 밯맣희
            81, 87, 69, 82, 84, 89,  # QWERTY
        ]
    )

    assert normalize_korean_nfc_to_nfd('ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ') == (
        ''.join(chr(x) for x in range(4352, 4370+1))
    )

    assert normalize_korean_nfc_to_nfd('ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ') == (
        ''.join(chr(x) for x in range(4449, 4469+1))
    )


def test_fuzzy_korean_partial_ratio():
    title = '소드 아트 온라인 3기 엘리시제이션 인계편'
    assert fuzzy_korean_partial_ratio('소드', title) == 72
    assert fuzzy_korean_partial_ratio('소드 아트', title) == 77
    assert fuzzy_korean_partial_ratio('소드 아트 온라인', title) == 85
    assert fuzzy_korean_partial_ratio('소드 아트 온라인 3기', title) == 88
    assert fuzzy_korean_partial_ratio('소드 아트 온라인 3기 엘리시', title) == 93
    assert fuzzy_korean_partial_ratio('소드 아트 온라인 3기 엘리시제이션', title) == 96
    assert fuzzy_korean_partial_ratio(title, title) == 100


def test_fuzzy_korean_ratio():
    """Test Korean-specific fuzzy search."""

    assert fuzz.ratio('강', '공') == 0
    assert fuzzy_korean_ratio('강', '공') == 67

    assert fuzz.ratio('안녕', '인형') == 0
    assert fuzzy_korean_ratio('안녕', '인형') == 67

    assert fuzz.ratio('사당', 'ㅅㄷ') == 0
    assert fuzzy_korean_ratio('사당', 'ㅅㄷ') == 57

    assert fuzz.ratio('사당', 'ㅏㅏ') == 0
    assert fuzzy_korean_ratio('사당', 'ㅏㅏ') == 57

    assert fuzz.ratio('사당', 'ㅅㅏㄷㅏㅇ') == 0
    assert fuzzy_korean_ratio('사당', 'ㅅㅏㄷㅏㅇ') == 80


def test_b64_redirect():

    assert b64_redirect('item4').startswith(
        'https://item4.github.io/yui/helpers/b64-redirect.html?b64='
    )
