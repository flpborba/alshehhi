import sage.all  # noqa: F401 (required by sage)
from pytest import mark
from sage.rings.finite_rings.finite_field_constructor import GF

from alshehhi.io import (
    BYTE_SIZE,
    decode_elem,
    decode_elem_list,
    encode_elem,
    encode_elem_list,
)


@mark.parametrize(
    "field, coefficients, data",
    [
        (
            GF(2),
            0,
            b"\x00",
        ),
        (
            GF(2),
            1,
            b"\x01",
        ),
        (
            GF(2 ** 12),
            [1],
            b"\x00\x01",
        ),
        (
            GF(2 ** 12),
            [],
            b"\x00\x00",
        ),
        (
            GF(2 ** 12),
            [0, 1, 0, 0, 0, 0, 1, 0, 1],
            b"\x01\x42",
        ),
    ],
)
def test_encode_elem(field, coefficients, data):
    e = field(coefficients)
    assert encode_elem(e) == data


@mark.parametrize(
    "field, data, coefficients",
    [
        (
            GF(2),
            b"\x00",
            0,
        ),
        (
            GF(2),
            b"\x01",
            1,
        ),
        (
            GF(2 ** 12),
            b"\x00\x00",
            [],
        ),
        (
            GF(2 ** 12),
            b"\x00\x01",
            [1],
        ),
        (
            GF(2 ** 12),
            b"\x01\x42",
            [0, 1, 0, 0, 0, 0, 1, 0, 1],
        ),
    ],
)
def test_decode_elem(field, data, coefficients):
    # test the case the field is specified

    assert decode_elem(data, field) == field(coefficients)

    # test the case the field is not specified

    deg = len(data) * BYTE_SIZE
    field = GF(2 ** deg)

    assert decode_elem(data) == field(coefficients)


@mark.parametrize(
    "field, coefficients, data",
    [
        (
            GF(2),
            [1],
            b"\x01",
        ),
        (
            GF(2),
            [0, 0, 1, 0, 1, 0, 0],
            b"\x14",
        ),
        (
            GF(2 ** 11),
            [[1, 0, 0, 1, 0, 0, 1, 1, 0, 1]],
            b"\x02\xC9",
        ),
        (
            GF(2 ** 11),
            [
                [0, 1, 0, 0, 1, 0, 0, 1, 1, 1],
                [0, 0, 0, 1, 0, 1, 1, 0, 1, 0, 1],
                [1, 0, 1, 1, 1, 0, 0, 1, 1],
            ],
            b"\x00\xE4\xAB\x41\x9D",
        ),
    ],
)
def test_encode_list(field, coefficients, data):
    elems = [field(item) for item in coefficients]
    assert encode_elem_list(elems) == data


@mark.parametrize(
    "field, data, coefficients",
    [
        (
            GF(2),
            b"",
            [],
        ),
        (
            GF(2),
            b"\x14",
            [0, 0, 0, 1, 0, 1, 0, 0],
        ),
        (
            GF(2 ** 11),
            b"\x02\xC9",
            [[1, 0, 0, 1, 0, 0, 1, 1, 0, 1]],
        ),
        (
            GF(2 ** 11),
            b"\x00\xE4\xAB\x41\x9D",
            [
                [0, 1, 0, 0, 1, 0, 0, 1, 1, 1],
                [0, 0, 0, 1, 0, 1, 1, 0, 1, 0, 1],
                [1, 0, 1, 1, 1, 0, 0, 1, 1],
            ],
        ),
    ],
)
def test_decode_list(field, coefficients, data):
    elems = [field(item) for item in coefficients]
    assert decode_elem_list(data, field) == elems
