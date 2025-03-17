from src.converters import Converter, EConverterType
from pathlib import Path
from argparse import ArgumentParser, Namespace


class Main:
    def __init__(self, prog_args: Namespace) -> None:
        # parse the command line arguments
        self.input_file = Path(prog_args.input)
        self.target_types = []
        if prog_args.xml:
            self.target_types.append(EConverterType.XML)
        if prog_args.geojson:
            self.target_types.append(EConverterType.GEOJSON)
        if prog_args.kml:
            self.target_types.append(EConverterType.KML)
        if not self.target_types:
            raise ValueError("No target type specified. Use --xml, --geojson, or --kml.")

        if prog_args.output:
            self.output_file = Path(prog_args.output)
        else:
            self.output_file = self.input_file.with_suffix('')

        self.converter = Converter(self.input_file)

    def run(self) -> None:
        """Run the conversion process based on the specified target types."""
        for target_type in self.target_types:
            print(f"Converting {self.input_file} to {target_type.value.upper()}...")
            converted_data = self.converter.convert(target_type)

            # Only save if conversion was performed
            # this prevents overwriting existing files with None
            if converted_data is not None:
                self._save_to_file(converted_data, target_type)
        print("Conversion completed.")

    def _convert_to_xml(self) -> None:
        """Convert the input file to XML format."""
        xml_data = self.converter.convert(EConverterType.XML)
        if xml_data is None: return
        self._save_to_file(xml_data, EConverterType.XML)

    def _convert_to_geojson(self) -> None:
        """Convert the input file to GeoJSON format."""
        geojson_data = self.converter.convert(EConverterType.GEOJSON)
        if geojson_data is None: return
        self._save_to_file(geojson_data, EConverterType.GEOJSON)

    def _convert_to_kml(self) -> None:
        """Convert the input file to KML format."""
        kml_data = self.converter.convert(EConverterType.KML)
        if kml_data is None: return
        self._save_to_file(kml_data, EConverterType.KML)

    def _save_to_file(self, data: str, convert_type: EConverterType) -> None:
        """Save the converted data to a file."""
        output_file = self.input_file.with_suffix(f'.{convert_type.value}')
        with open(output_file, 'w') as file:
            file.write(data)
        print(f"Saved data to {output_file}")


if __name__ == '__main__':
    prog = "xml2geojson2kml"
    version = "0.1.0"
    description = "XML, KML, and GeoJSON Converter."
    parser = ArgumentParser(description="")
    parser.add_argument("-i", "--input", type=str, required=True, help="Input XML file to convert")
    parser.add_argument("-x", "--xml", action="store_true", help="Convert to XML")
    parser.add_argument("-g", "--geojson", action="store_true", help="Convert to GeoJSON")
    parser.add_argument("-k", "--kml", action="store_true", help="Convert to KML")
    parser.add_argument("-o", "--output", type=str,
                        help="Optional output file name (Defaults to input file with new extension)")
    args = parser.parse_args()
    Main(args).run()
