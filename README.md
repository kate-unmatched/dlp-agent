# DLP-Агент
A lightweight software module that monitors certain user actions in real time, extracts formalized features from them and transmits them to a central analysis system.

```
dlp_agent/
├── agent.py
├── config.py
├── features/
│   ├── __init__.py
│   ├── file_features.py         # Семантический анализ содержимого
│   └── network_features.py      # Метрики сетевой активности
├── triggers/
│   └── check_triggers.py        # Обнаружение событий
├── utils/
│   └── system.py                # Вспомогательные функции
```
# Структура поведенческих признаков

Этот документ описывает структуру данных, собираемых DLP-агентом для передачи в основной модуль поведенческого анализа и оценки риска.

---

## 1. Файловая активность

| Название признака                | Тип    | Описание |
|----------------------------------|--------|----------|
| `file_create_count`              | int    | Кол-во созданных файлов за интервал |
| `file_delete_count`              | int    | Кол-во удалённых файлов |
| `file_copy_count`                | int    | Кол-во скопированных файлов |
| `file_rename_count`              | int    | Кол-во переименованных файлов |
| `file_access_sensitive_docs`     | bool   | Были ли обращения к .doc/.xls/.pdf |
| `file_sensitive_word_matches`    | int    | Кол-во совпадений с чувствительными словами |
| `file_contains_card_number`      | bool   | Обнаружены номера карт |
| `file_contains_passport_data`    | bool   | Обнаружены паспортные данные |
| `total_data_written_MB`          | float  | Общий объём записанных данных |
| `usb_file_copy_count`            | int    | Файлы, скопированные на USB |

---

## 2. Сетевая активность

| Название признака                      | Тип     | Описание |
|----------------------------------------|----------|----------|
| `http_requests_count`                 | int      | Кол-во HTTP/HTTPS-запросов за интервал |
| `upload_volume_MB`                   | float    | Объём исходящего трафика в мегабайтах |
| `distinct_domains_accessed`          | int      | Количество уникальных доменных имён |
| `visited_webmail`                    | bool     | Посещались ли веб-почты (mail.ru, gmail, yandex и т.д.) |
| `visited_file_sharing_site`          | bool     | Обнаружены ли сайты хранения файлов (Google Drive, Dropbox и др.) |
| `vpn_activated`                      | bool     | В системе запущен VPN-клиент или туннель |
| `proxy_used`                         | bool     | Использовался прокси-сервер или нестандартный прокси-порт |
| `external_ip_contacted`              | int      | Количество соединений с внешними IP-адресами |
| `site_contains_sensitive_words`      | bool     | В заголовках или теле сайтов обнаружены чувствительные термины |
| `dns_request_count`                  | int      | Кол-во DNS-запросов, сгенерированных системой |
| `suspicious_dns_queries`             | bool     | Были обращения к подозрительным или туннельным доменам |
| `non_http_traffic_count`             | int      | Кол-во соединений не по HTTP/HTTPS (например, FTP, SSH, SMTP) |
| `used_ftp_or_smtp`                   | bool     | Зафиксирована передача через FTP или SMTP |
| `upload_spike_detected`              | bool     | Резкий рост исходящего трафика за малый промежуток времени |
| `visited_risky_category_sites`       | int      | Кол-во посещённых сайтов из категорий: файлообмен, webmail, прокси, darknet |
| `site_category_diversity`            | int      | Кол-во разных категорий сайтов за интервал |
| `external_upload_without_web_activity` | bool   | Зафиксирована передача данных при отсутствии активности в браузере |

---

## 3. Активность процессов и системных команд

| Название признака                | Тип    | Описание |
|----------------------------------|--------|----------|
| `process_count`                 | int    | Общее число активных процессов |
| `unknown_processes_started`     | int    | Запущены неразрешённые программы |
| `admin_tools_used`              | bool   | Использовались средства администрирования |
| `time_in_terminal_sec`          | int    | Время в командной строке / PowerShell |
| `automation_tool_detected`      | bool   | AutoHotKey, Selenium и др. |
| `screen_capture_tools_used`     | bool   | Запуск средств захвата экрана |

---

## 4. Поведение пользователя

| Название признака                | Тип    | Описание |
|----------------------------------|--------|----------|
| `keyboard_input_events`          | int    | Кол-во нажатий клавиш |
| `mouse_clicks`                   | int    | Кол-во кликов мыши |
| `active_window_changes`          | int    | Кол-во переключений окон |
| `clipboard_contains_sensitive_data` | bool | В буфере — номера, e-mail, пароли |
| `copy_paste_activity_count`      | int    | Кол-во операций копирования/вставки |

---

## 5. Внешние устройства

| Название признака                | Тип    | Описание |
|----------------------------------|--------|----------|
| `usb_devices_connected`          | int    | Кол-во подключений USB |
| `usb_vendor_blacklisted`         | bool   | Устройство из чёрного списка |
| `usb_copy_volume_MB`             | float  | Объём копирования на USB |
| `usb_last_vendor`                | str    | Последний идентификатор USB-устройства |

---

## 🕒 6. Временной и поведенческий контекст

| Название признака                | Тип    | Описание |
|----------------------------------|--------|----------|
| `hour_of_day`                    | int    | Час суток (0–23) |
| `activity_outside_work_hours`   | bool   | Активность вне рабочих часов |
| `login_time_sec`                | int    | Время входа в систему |
| `time_since_last_activity_sec`  | int    | Пауза перед активностью (в секундах) |

---

## 7. Триггеры (событийные индикаторы)

> Эти признаки фиксируются по факту события, инициируют немедленную отправку.

| Название триггера                 | Тип    | Описание |
|----------------------------------|--------|----------|
| `usb_connected`                 | bool   | Обнаружено подключение USB-накопителя |
| `vpn_activated`                 | bool   | Обнаружен запуск VPN-клиента или туннеля |
| `proxy_config_changed`         | bool   | Изменены настройки прокси или маршрутизации |
| `disable_antivirus`            | bool   | Отключён антивирус или защитное ПО |
| `mass_file_actions`            | bool   | Зафиксировано большое число операций с файлами за короткое время |
| `unknown_exe_started`          | bool   | Запущен исполняемый файл вне белого списка |
| `ftp_activity_detected`        | bool   | Зафиксирована активность по FTP-протоколу |
| `smtp_activity_detected`       | bool   | Зафиксирована отправка через SMTP |
| `non_http_upload_detected`     | bool   | Исходящий трафик без активного браузера |
| `access_to_blacklisted_site`   | bool   | Попытка доступа к запрещённому сайту |
| `screenshot_tool_detected`     | bool   | Обнаружен запуск программ захвата экрана |
| `sensitive_doc_opened`         | bool   | Открыт документ, классифицированный как чувствительный |
| `clipboard_sensitive_data`     | bool   | В буфере обмена — ИНН, карты, пароли и т.п. |
| `explorer_archiving_detected`  | bool   | Создание или упаковка большого архива |
| `process_spike_detected`       | bool   | Резкое увеличение количества процессов (возможно, автоматизация) |

---

## Формат отправки данных в основной модуль (пример)

```json
{
  "user_id": "user42",
  "timestamp": "2025-05-01T22:00:00",
  "features": {
    "file_create_count": 4,
    "http_requests_count": 37,
    "vpn_activated": 1,
    "...": "..."
  },
  "trigger": "vpn_activated"
}
