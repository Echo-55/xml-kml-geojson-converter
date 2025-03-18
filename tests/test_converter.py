import pytest
import json
import lxml.etree as et
from pathlib import Path
from src.converter import Converter, EConverterType


# helper function to load test files
def load_test_file(file_name: str) -> Path:
    """Load a test file and return its content."""
    return Path(__file__).cwd() / "test_files" / file_name


@pytest.fixture
def xml_converter():
    """Fixture to create a Converter instance for XML."""
    input_file = load_test_file("test.xml")
    return Converter(input_file)


@pytest.fixture
def geojson_converter():
    """Fixture to create a Converter instance for GeoJSON."""
    input_file = load_test_file("test.geojson")
    return Converter(input_file)


@pytest.fixture
def kml_converter():
    """Fixture to create a Converter instance for KML."""
    input_file = load_test_file("test.kml")
    return Converter(input_file)


def test_parse_xml(xml_converter):
    """Test parsing of XML file."""
    data = xml_converter.data
    assert isinstance(data, list)
    assert len(data) > 0
    assert "geo" in data[0]
    assert isinstance(data[0]["geo"], tuple)
    assert len(data[0]["geo"]) == 2
    assert "name" in data[0]


def test_parse_geojson(geojson_converter):
    """Test parsing of GeoJSON file."""
    data = geojson_converter.data
    assert len(data) == 1
    assert data[0]["name"] == "Test Location"
    assert data[0]["address"] == "123 Test Street"
    assert data[0]["state"] == "TX"
    assert data[0]["geo"] == (30.123456, -97.123456)
    assert data[0]["type"] == "A"
    assert data[0]["note"] == "Test note"


def test_parse_kml(kml_converter):
    """Test parsing of KML file."""
    data = kml_converter.data
    assert isinstance(data, list)
    assert len(data) > 0
    assert "geo" in data[0]
    assert isinstance(data[0]["geo"], tuple)
    assert len(data[0]["geo"]) == 2
    assert "name" in data[0]


def test_convert_xml_to_geojson(xml_converter):
    """Test XML to GeoJSON conversion"""
    geojson_str = xml_converter.convert(EConverterType.GEOJSON)
    geojson = json.loads(geojson_str)

    assert geojson["type"] == "FeatureCollection"
    assert len(geojson["features"]) == 2

    # First feature
    feature_one = geojson["features"][0]
    assert feature_one["type"] == "Feature"
    assert feature_one["properties"]["name"] == "Test Location"
    assert feature_one["properties"]["address"] == "123 Test Street"  # Fixed key
    assert feature_one["properties"]["state"] == "TX"
    assert feature_one["properties"]["type"] == "A"
    assert feature_one["properties"]["note"] == "Test note"
    assert feature_one["geometry"]["type"] == "Point"
    assert feature_one["geometry"]["coordinates"] == [-97.123456, 30.123456]

    # Second feature
    feature_two = geojson["features"][1]
    assert feature_two["type"] == "Feature"
    assert feature_two["properties"]["name"] == "Another Location"
    assert feature_two["properties"]["address"] == "456 Another Ave"  # Fixed key
    assert feature_two["properties"]["state"] == "CA"
    assert feature_two["properties"]["type"] == "B"
    assert feature_two["properties"]["note"] == "Another note"
    assert feature_two["geometry"]["type"] == "Point"
    assert feature_two["geometry"]["coordinates"] == [-118.123456, 34.567890]  # Fixed coordinates


def test_convert_xml_to_kml(xml_converter):
    """Test XML to KML conversion"""
    kml_str = xml_converter.convert(EConverterType.KML)
    root = et.fromstring(kml_str.encode("utf-8"))

    placemark = root.find(".//{http://www.opengis.net/kml/2.2}Placemark")
    assert placemark is not None

    name = placemark.find("{http://www.opengis.net/kml/2.2}name")
    assert name is not None and name.text == "Test Location"

    extended_data = placemark.find("{http://www.opengis.net/kml/2.2}ExtendedData")
    assert extended_data is not None

    # Check metadata in ExtendedData
    for data in extended_data.findall("{http://www.opengis.net/kml/2.2}Data"):
        key = data.get("name")
        value = data.find("{http://www.opengis.net/kml/2.2}value").text

        if key == "adr":
            assert value == "123 Test Street"
        elif key == "state":
            assert value == "TX"
        elif key == "type":
            assert value == "A"
        elif key == "note":
            assert value == "Test note"

    point = placemark.find("{http://www.opengis.net/kml/2.2}Point")
    assert point is not None

    coordinates = point.find("{http://www.opengis.net/kml/2.2}coordinates")
    assert coordinates is not None and coordinates.text == "-97.123456,30.123456"
