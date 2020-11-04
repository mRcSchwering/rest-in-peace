"""Types with serializers and parsers"""
import datetime as dt
from ariadne import ScalarType  # type: ignore

date_scalar = ScalarType("Date")


@date_scalar.serializer
def serialize_datetime(d: dt.date) -> str:
    return d.strftime("%Y-%m-%d")


@date_scalar.value_parser
def parse_datetime_value(d: str) -> dt.date:
    return dt.datetime.strptime(d, "%Y-%m-%d").date()


types = (date_scalar,)

