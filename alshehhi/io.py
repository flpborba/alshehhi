"""This module provides functions to encode finite finite elements and related
objects such as lists, matrices, and vectors of finite field elements.
"""

from math import ceil
from textwrap import wrap

import sage.all  # noqa: F401 (required by sage)
from Crypto.Util import number
from Crypto.Util.number import long_to_bytes
from more_itertools import grouper
from sage.matrix.constructor import matrix
from sage.matrix.matrix_space import MatrixSpace
from sage.modules.free_module import FreeModule_ambient_field as VectorSpace
from sage.modules.free_module_element import vector
from sage.rings.finite_rings.finite_field_base import FiniteField
from sage.rings.finite_rings.finite_field_constructor import GF
from sage.rings.integer import Integer
from sage.structure.element import FieldElement, Matrix, Vector

"""The size of a byte."""
BYTE_SIZE = 8


def encode(object):
    """Encode a finite field element, a vector, or a matrix according to
    `encode_elem` rules.

    Parameters
    ----------
    object : {FieldElement, Matrix, Vector}
        An element of a finite field of characteristic 2, or a matrix or a
        vector over a finite field of characteristic 2.

    Returns
    -------
    bytes
        The encoded object.

    Raises
    ------
    ValueError
        If the object is not a finite field element, a matrix, or a vector.
    """
    if isinstance(object, FieldElement):
        return encode_elem(object)

    elif isinstance(object, Vector) or isinstance(object, Matrix):
        return encode_elem_list(object.list())

    else:
        raise ValueError(f"unsupported element type: {type(object)}")


def decode(data, space):
    """Decode bytes into an object in the given space.

    This function interprets as an element the minimum number of bytes such
    that the number of bits are greater than or equal the degree of `field`.
    So, if `field` has degree 13 and `BYTE_SIZE == 8` then, each group of 2
    bytes corresponds to a different element.

    Parameters
    ----------
    data : bytes
        The object representation.
    space : {FiniteField, MatrixSpace, VectorSpace}
        A finite field of characteristic 2, or a matrix space or vector space
        over a finite field of characteristic 2.

    Returns
    -------
    {FieldElement, Matrix, Vector}
        The decoded object.

    Raises
    ------
    ValueError
        If `space` is not a finite field, a matrix space, or a vector space.
    """
    if isinstance(space, FiniteField):
        return decode_elem(data, space)

    elif isinstance(space, VectorSpace):
        elems = decode_elem_list(data, space.base_ring())
        n = space.degree()

        return vector(elems[-n:])

    elif isinstance(space, MatrixSpace):
        elems = decode_elem_list(data, space.base_ring())
        n = space.dimension()

        return matrix(space=space, entries=elems[-n:])

    else:
        raise ValueError(f"unsupported space: {type(space)}")


def encode_elem_list(elems):
    """Encode a list of elements into bytes.

    Each element occupy a number of bits equal to its degree. If the sum of the
    degrees of `elems` is not a mutiple of `BYTE_SIZE`, the result is filled
    with zeros.

    Parameters
    ----------
    elems : list
        A list of elements over a finite field of characteristic 2.

    Returns
    -------
    list
        The encoded elements.

    See Also
    --------
    encode_elem
    decode_elem_list

    Notes
    -----
    The `decode_list` function can revert the encoding done by this function.
    However, this function does not check if all elements belongs to the same
    field, and in this case `decode_list` will raise an error.
    """
    bits = "".join(to_str(e) for e in elems)
    num_bytes = ceil(len(bits) / BYTE_SIZE)

    return int(bits, 2).to_bytes(num_bytes, "big")


def decode_elem_list(data, field, num_of_elems=None):
    """Decode bytes into a list of finite field elements.

    This function inteprets each group of _n_ bits in `data`, where _n_ is the
    degree of `field`, as an element of `field`. `num_of_elems` are returned
    and, if there are remaining bits, these are discarded. If `num_of_elems` is
    `None`, the maximum number of elements that fit in `data` is returned and
    any remaining bits are discarded.

    Parameters
    ----------
    data : bytes
        Representation of the elements.
    field : FiniteField
        The field the elements belong.
    num_of_elems : int, optional
        Number of elements to decode.

    Returns
    -------
    list
        A list of FiniteRingElement.

    Raises
    ------
    RuntimeError
        If there are not sufficient bytes to fully represent elements.

    See Also
    --------
    decode_elem
    encode_elem_list
    """
    if field.characteristic() != 2:
        raise ValueError("the element is not in a field of characteristic two")

    bits = "".join(f"{byte:08b}" for byte in data)
    num_bits = len(data) * BYTE_SIZE

    if num_of_elems is None:
        padding_len = num_bits % field.degree()
    else:
        padding_len = num_bits - field.degree() * num_of_elems

    if padding_len < 0:
        raise ValueError("there are not enough bytes to decode")

    if field is GF(2):
        return [field(b) for b in bits]

    chunks = wrap(bits[padding_len:], field.degree())
    return [field.fetch_int(int(c, 2)) for c in chunks]


def encode_elem(elem):
    """Encode a finite field element into bytes.

    If the degree of the element is not multple of `BITE_SIZE`, the result is
    filled with zeros.

    Parameters
    ----------
    elem : FiniteRingElement
        An element over a finite field of characteristic 2.

    Returns
    -------
    bytes
        The encoded element.

    Raises
    ------
    ValueError
        If the characteristic of the field `elem` belongs is different from 2.

    See Also
    --------
    decode
    """
    field = elem.parent()

    if field.characteristic() != 2:
        raise ValueError("the element is not in a field of characteristic two")

    if field is GF(2):
        return b"\x00" if elem == 0 else b"\x01"

    num_bytes = ceil(field.degree() / BYTE_SIZE)
    return elem.integer_representation().to_bytes(num_bytes, "big")


def decode_elem(data, field=None):
    """Decode bytes into a finite field element.

    If `field` is None, this function defines the element in a finite field of
    degree equal to the number of bits in `data`.

    Parameters
    ----------
    data : bytes
        The element representation.
    field : FiniteField, optional
        The field the element belongs.

    Returns
    -------
    FiniteRingElement
        The decoded element.

    Raises
    ------
    ValueError
        If the characteristic `field` is different from 2.

    See Also
    --------
    encode
    """
    if field is None:
        deg = len(data) * BYTE_SIZE
        field = GF(2 ** deg)

    if field.characteristic() != 2:
        raise ValueError("finite field has not characteristic two")

    if field is GF(2):
        return field(0) if data == b"\x00" else field(1)

    return field.fetch_int(int.from_bytes(data, "big"))


def to_str(elem):
    """Convert a finite field element into a string.

    The characters in the resulting string contains the coefficients of the
    element.

    Parameters
    ----------
    elem : FiniteRingElement
        An element over a finite field of characteristic 2.

    Returns
    -------
    str
        A string with the element coefficients.

    Raises
    ------
    ValueError
        If the characteristic `field` is different from 2.
    """
    field = elem.parent()

    if field.characteristic() != 2:
        raise ValueError("the element is not in a field of characteristic two")

    if field is GF(2):
        return "0" if elem == 0 else "1"

    coefficients = Integer(elem.integer_representation()).binary()
    padding = "0" * (field.degree() - len(coefficients))

    return padding + coefficients
