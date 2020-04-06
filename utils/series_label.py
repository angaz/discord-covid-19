def series_label(name: str, series: str, multiple_series: bool) -> str:
    return f"{name} ({series})" if multiple_series else name
