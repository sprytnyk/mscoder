"""Ukrainian translations."""

# Common translations
COMMON = {
    "window_title": "MSCoder",
    "language": "Мова:",
    "tab_converter": "Конвертер",
    "tab_replacer": "Заміна у файлі",
    "tab_isn_copier": "Копіювання ISN",
    "tab_about": "Про програму",
}

# Converter tab
CONVERTER = {
    "title": "VIN Конвертер",
    "description": "Конвертувати VIN рядки у hex формат і навпаки для блоків BMW DME.",
    "vin_string": "VIN рядок:",
    "hex_bytes": "HEX байти:",
    "btn_to_hex": "РЯДОК → HEX",
    "btn_to_str": "HEX → РЯДОК",
    "error_vin_length": "Помилка: VIN повинен бути довжиною 17 символів",
    "error_hex_length": "Помилка: Hex повинен бути 26 hex цифр (13 байтів)",
    "error_hex_format": "Помилка: Невірний hex формат",
    "warning_decoded": "Попередження: Декодований VIN має {0} символів (очікується 17)",
    "ok": "OK",
    "supported": "Підтримується: MS41, MS42, MS43",
}

# File Replacer tab
REPLACER = {
    "title": "Заміна VIN у бінарних файлах",
    "description": "Знайти та замінити VIN HEX у бінарному файлі. Змінений файл буде збережено з UTC datetime суфіксом.",
    "original_vin": "Оригінальний VIN (рядок):",
    "replace_vin": "VIN для заміни (рядок):",
    "binary_file": "Бінарний файл (512kb для MS42/MS43, 256kb для MS41):",
    "btn_select": "Вибрати файл",
    "btn_process": "Оновити VIN",
    "select_file_title": "Виберіть бінарний файл",
    "all_files": "Всі файли (*.*)",
    "file_selected": "Файл вибрано",
    "error_required": "Помилка: Всі поля обов'язкові",
    "error_original_length": "Помилка: Оригінальний VIN повинен бути довжиною 17 символів",
    "error_replace_length": "Помилка: VIN для заміни повинен бути довжиною 17 символів",
    "no_matches": "Співпадінь не знайдено у файлі",
    "success": "Успішно: {0} рядків замінено. Збережено у: {1}",
    "supported": "Підтримується: MS41, MS42, MS43",
}

# ISN Copier tab
ISN_COPIER = {
    "title": "Копіювання ISN",
    "description": "Копіювати значення ISN з одного файлу прошивки в інший (файли 512kb для MS42/MS43). ISN це 6 байтів за різними адресами залежно від типу DME.",
    "source_file": "Вхідний файл (зчитати ISN з):",
    "target_file": "Кінцевий файл (записати ISN в):",
    "value_label": "Значення ISN з вхідного файлу:",
    "btn_select": "Вибрати файл",
    "btn_process": "Копіювати ISN в файл",
    "select_source_title": "Виберіть вхідний файл прошивки",
    "select_target_title": "Виберіть кінцевий файл прошивки",
    "all_files": "Всі файли (*.*)",
    "source_selected": "Вхідний файл вибрано та значення ISN зчитано",
    "target_selected": "Кінцевий файл вибрано",
    "error_required": "Помилка: Потрібні обидва файли (вхідний та кінцевий)",
    "error_file_too_small": "Помилка: Вхідний файл занадто малий (потрібна адреса 0x3ED4 + 6 байтів)",
    "error_target_too_small": "Помилка: Кінцевий файл занадто малий (потрібна адреса 0x3ED4 + 6 байтів)",
    "success": "Успішно: значення ISN {0} скопійовано в кінцевий файл. Збережено у: {1}",
    "immobiliser_bypass": "Вимкнення імобілайзера",
    "immobiliser_revert": "Відновити імобілайзер",
}

# About tab
ABOUT = {
    "title": "MSCoder",
    "author": 'Автор: <a href="https://sprytnyk.dev">https://sprytnyk.dev</a><br>GitHub: <a href="https://github.com/sprytnyk/mscoder">https://github.com/sprytnyk/mscoder</a>',
    "version": "Версія: {version}",
    "header": "Про програму",
}
