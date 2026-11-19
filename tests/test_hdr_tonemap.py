import pytest

from render import hdr_tonemap as mod

CASES = [
    pytest.param('tonemap', ((0.5, 0.5, 0.5), 0.0, False), (0.5, 0.5, 0.5), True, id='01_tonemap_linear'),
    pytest.param('tonemap', ((0.5, 0.5, 0.5), 1.0, False), (1.0, 1.0, 1.0), True, id='02_tonemap_exposure'),
    pytest.param('tonemap', ((1.0, 1.0, 1.0), 0.0, True), (0.8037974683544302, 0.8037974683544302, 0.8037974683544302), True, id='03_tonemap_aces'),
    pytest.param('tonemap', ((10.0, 10.0, 10.0), 0.0, True), (1.0, 1.0, 1.0), True, id='04_tonemap_aces_high'),
    pytest.param('tonemap', ((-1.0, 0.2, 2.0), 0.0, False), (0.0, 0.2, 1.0), True, id='05_tonemap_negative'),
    pytest.param('pq_to_nits', (0.0,), 0.0, True, id='06_pq_zero'),
    pytest.param('pq_to_nits', (1.0,), 10000.0, True, id='07_pq_one'),
    pytest.param('pq_to_nits', (0.5,), 0.0, True, id='08_pq_mid'),
    pytest.param('pq_to_nits', (0.1,), 0.0, True, id='09_pq_small'),
    pytest.param('pq_to_nits', (0.9,), 0.0, True, id='10_pq_high'),
    pytest.param('display_encode', ((1.2, 0.5, -0.1), 'sdr', (0, 0)), (0.9980392156862745, 0.4980392156862745, -0.00196078431372549), True, id='11_encode_sdr'),
    pytest.param('display_encode', ((1.2, 0.5, -0.1), 'hdr', (0, 0)), (1.1980392156862745, 0.4980392156862745, -0.00196078431372549), True, id='12_encode_hdr'),
    pytest.param('display_encode', ((0.5, 0.5, 0.5), 'sdr', (3, 5)), (0.49950980392156863, 0.49950980392156863, 0.49950980392156863), True, id='13_encode_dither'),
    pytest.param('display_encode', ((0.0, 0.0, 0.0), 'sdr', (0, 0)), (-0.00196078431372549, -0.00196078431372549, -0.00196078431372549), True, id='14_encode_gamut'),
    pytest.param('display_encode', ((1.0, 1.0, 1.0), 'hdr', (1, 1)), (0.9990196078431373, 0.9990196078431373, 0.9990196078431373), True, id='15_encode_white'),
]


def assert_close(actual, expected):
    if isinstance(expected, tuple):
        assert isinstance(actual, tuple) and len(actual) == len(expected)
        for a, e in zip(actual, expected):
            assert_close(a, e)
    elif isinstance(expected, list):
        assert isinstance(actual, list) and len(actual) == len(expected)
        for a, e in zip(actual, expected):
            assert_close(a, e)
    elif isinstance(expected, dict):
        assert actual.keys() == expected.keys()
        for key in expected:
            assert_close(actual[key], expected[key])
    else:
        assert actual == pytest.approx(expected)


@pytest.mark.parametrize("func_name,args,expected,approx", CASES)
def test_hdr_tonemap_contract(func_name, args, expected, approx):
    func = getattr(mod, func_name)
    result = func(*args)
    if approx:
        assert_close(result, expected)
    else:
        assert result == expected
