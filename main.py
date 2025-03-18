import shutil

from src.converter import Converter, EConverterType
from src.utils import Config, Logger
from pathlib import Path
from argparse import ArgumentParser, Namespace


class Main:
    target_types: list[EConverterType]

    def __init__(self, prog_args: Namespace) -> None:
        """Initialize the main class with command line arguments."""
        self.config: Config = Config(Path("config.ini"))
        self._should_copy_original_to_output = self.config.get("Converter", "copy_original_to_output",
                                                               fallback=True)
        self.logger: Logger = Logger(self.config)

        self.target_types = []
        self._parse_args(prog_args)

    def run(self) -> None:
        """Run conversion process."""
        with self.logger.status("[bold green]Initializing conversion...[/bold green]") as status:
            for convert_type in self.target_types:
                for file in self.files:
                    converter = Converter(file, self.logger, self.config)
                    status.update(f"Processing: {file}")
                    self._convert_and_save(converter, convert_type)
                    status.update(f"Converted: {file} to {convert_type.value}")

            status.update("[bold green]Conversion completed![/bold green]")

        status.stop()

    def _convert_and_save(self, converter: Converter, convert_type: EConverterType) -> None:
        """Convert and save the output file while maintaining folder structure."""
        converted_data = converter.convert(convert_type)

        # Get relative path from input directory to maintain structure
        relative_path = converter.input_file.relative_to(self.input_path)

        if converted_data is None:  # skip conversion
            if not self._should_copy_original_to_output:
                return
            # copy to the output folder
            output_file = self.output_dir / relative_path
            output_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(converter.input_file, output_file)
            return
            # return  # Skip if already in target format

        output_file = self.output_dir / relative_path.with_suffix(f".{convert_type.value}")

        # Ensure subdirectories exist in output directory
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Save the converted file
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(converted_data)

        # print(f"Saved: {output_file}")
        self.logger.print(f"Saved: {output_file}", style="bold green")

    def _parse_args(self, prog_args: Namespace) -> None:
        """Parse command line arguments."""
        self.input_path = Path(prog_args.input)
        self.output_dir = Path(prog_args.output) if prog_args.output else self.input_path.parent

        if prog_args.xml:
            self.target_types.append(EConverterType.XML)
        if prog_args.geojson:
            self.target_types.append(EConverterType.GEOJSON)
        if prog_args.kml:
            self.target_types.append(EConverterType.KML)

        if not self.target_types:
            raise ValueError("No target type specified. Use --xml, --geojson, or --kml.")

        # Recursively search for XML, KML, and GeoJSON files in all subdirectories
        self.files = list(self.input_path.rglob("*.xml")) + \
                     list(self.input_path.rglob("*.geojson")) + \
                     list(self.input_path.rglob("*.kml"))

        if not self.files:
            raise ValueError("No valid files found for conversion.")


if __name__ == '__main__':
    parser = ArgumentParser(description="Batch Convert XML, KML, and GeoJSON Files")
    parser.add_argument("-i", "--input", type=str, required=True, help="Input file or directory")
    parser.add_argument("-o", "--output", type=str, help="Optional output directory (defaults to input location)")
    parser.add_argument("-x", "--xml", action="store_true", help="Convert to XML")
    parser.add_argument("-g", "--geojson", action="store_true", help="Convert to GeoJSON")
    parser.add_argument("-k", "--kml", action="store_true", help="Convert to KML")

    args = parser.parse_args()
    Main(args).run()
