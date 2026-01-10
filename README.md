# MSCoder

> **⚠️ DISCLAIMER:** Modifying firmware carries risks, including the potential to brick your DME. **Always create a backup of your original firmware before making any modifications.** Use this tool at your own risk. I am not responsible for any damage.

Supported languages: 🇬🇧 English | 🇺🇦 Українська  
Supported platforms: Linux | macOS | Windows

This tool helps you work with VIN data for BMW MS43 engine control units. It can convert VIN strings to their hexadecimal representation and find/replace VINs in binary DME files.

![Converter](assets/converter.png)
![Replacer](assets/replacer.png)

## Compatibility

This tool updates VIN in binary DME files for **MS41**, **MS42** and **MS43** engine control units. It has been thoroughly tested and confirmed to work with MS43. It may also work with other MS4X variants but requires additional testing to confirm full compatibility.

**ISN Copier functionality is solely for MS43.**

## Features

- **VIN Converter**: Convert between VIN string and hex bytes
- **VIN Replacer**: Replace VIN in binary files
- **ISN Copier**: Copy ISN (Immobilizer Sequence Number) from one MS43 firmware to another, with optional EWS  bypass functionality

## Installation

Download pre-built binaries for different distributions from the [Releases](https://github.com/sprytnyk/mscoder/releases) page.

Or run from source:

```bash
python3.11 -m pip install -r requirements.txt
python -m mscoder
```

## References

This project wouldn't exist without:

- [pyms41](https://github.com/OpenMS41/pyms41).
- [MS4X Community Patchlist](https://www.ms4x.net/index.php?title=TunerPro_MS43_Community_Patchlist)

And it was inspired by [E46 Temperature Gauge Hex Generator v1.0](https://www.e46fanatics.com/threads/diy-changing-temperature-gauge-buffer-range-with-pa-soft-1-4.1013600/)

## License

MIT License - see [LICENSE](LICENSE) file for details.
