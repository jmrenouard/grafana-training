# Grafana Configuration Generator (`configuration/`)

This directory contains a standalone browser-based `grafana.ini` configuration builder with English and French UI translations.

## Files

| File | Description |
| :--- | :--- |
| `grafana_config.html` | Interactive HTML/Alpine.js configuration generator defaulting to `fr` with an EN/FR language selector |
| `grafana_enhanced.json` | French schema definitions and parameter descriptions loaded when `lang` is `fr` |
| `grafana_enhanced_en.json` | English schema definitions and parameter descriptions loaded when `lang` is `en` |
| `grafana.json` | Base structured Grafana configuration parameter metadata |
| `grafana.txt` | Plaintext `grafana.ini` reference dump |

## Usage

Serve this folder over HTTP so browser `fetch()` calls can load the JSON schema files:

```bash
python3 -m http.server --directory configuration 8090
```

Open `http://localhost:8090/grafana_config.html` in a browser, switch between **FR** and **EN**, edit settings, and copy the generated `grafana.ini` output.

[Back to Repository Overview](../README.md)
