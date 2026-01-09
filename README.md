# VinCoder

Supported languages: 🇬🇧 English | 🇺🇦 Українська

This tool helps you work with VIN data for BMW MS41 and MS43 engine control units. It can convert VIN strings to their hexadecimal representation and find/replace VINs in binary DME files.

![Converter](assets/converter.png)
![Replacer](assets/replacer.png)

## Features

- **VIN Converter**: Convert between VIN string and hex bytes
- **VIN Replacer**: Replace VIN in binary files

## Installation

Download pre-built binaries for different distributions from the [Releases](https://github.com/sprytnyk/vincoder/releases) page.

Or run from source:

```bash
python3.11 -m pip install -r requirements.txt
python main.py
```

## Inspired By

This project was inspired by [pyms41](https://github.com/OpenMS41/pyms41).

## License

MIT License - see [LICENSE](LICENSE) file for details.
