CATEGORIES: dict[str, str] = {
    # INGRESOS
    "NOMINA ROBERT": "Ingresos",
    "NOMINA MARTA": "Ingresos",
    "RETORNO SEGURO AXA": "Ingresos",
    "INGRESO MUFACE": "Ingresos",
    "MUFACE": "Ingresos",
    "INGRESO AHORROS": "Ingresos",
    "BIZUM RECIBIDO": "Ingresos",

    # GASTOS FIJOS
    "SEGURO SALUD AXA": "Gastos Fijos",
    "PRESTAMO COCHE": "Gastos Fijos",
    "CETELEM": "Gastos Fijos",
    "TELEFONO VODAFONE": "Gastos Fijos",
    "VODAFONE": "Gastos Fijos",
    "SEGURO LUCIA": "Gastos Fijos",
    "MAPFRE": "Gastos Fijos",
    "ONG CRUZ ROJA": "Gastos Fijos",
    "CRUZ ROJA": "Gastos Fijos",
    "ONG ACNUR": "Gastos Fijos",
    "ANNUR": "Gastos Fijos",
    "ACNUR": "Gastos Fijos",
    "DEPURADOR AGUA": "Gastos Fijos",
    "WATER SYSTEM": "Gastos Fijos",
    "COMUNIDAD DE PROPIETARIOS": "Gastos Fijos",
    "LAIETANIA": "Gastos Fijos",
    "CLUB DEPORTIVO LAIETANIA": "Gastos Fijos",
    "IMPUESTO IVTM": "Gastos Fijos",
    "IMPUESTO IBI": "Gastos Fijos",
    "TASA BASURAS": "Gastos Fijos",
    "SEGURO COCHE AXA": "Gastos Fijos",
    "SEGURO COCHE": "Gastos Fijos",
    "METLIFE": "Gastos Fijos",
    "AHORRO LUCIA": "Gastos Fijos",
    "COMUNIDAD PARKING": "Gastos Fijos",
    "AGUAS MATARO": "Gastos Fijos",

    # TENIS LUCÍA
    "ENTRENADOR LUCIA": "Tenis Lucía",
    "ROYDONCES": "Tenis Lucía",
    "JC FERRERO": "Tenis Lucía",
    "EQUELITE": "Tenis Lucía",
    "COMIDAS TENIS": "Tenis Lucía",
    "FISIO LUCIA": "Tenis Lucía",
    "EQUIPAMIENTO TENIS": "Tenis Lucía",
    "DESPLAZAMIENTOS TENIS": "Tenis Lucía",

    # GASTOS VARIABLES
    "LUZ ENDESA": "Gastos Variables",
    "GAS ENDESA": "Gastos Variables",
    "ENDESA": "Gastos Variables",
    "ALIMENTACION": "Gastos Variables",
    "FARMACIA": "Gastos Variables",
    "SALUD": "Gastos Variables",
    "TRANSPORTE": "Gastos Variables",
    "COMBUSTIBLE": "Gastos Variables",
    "GASOLINA": "Gastos Variables",
    "ROPA": "Gastos Variables",
    "CALZADO": "Gastos Variables",
    "HOGAR": "Gastos Variables",

    # DISCRECIONAL
    "SIATSHU": "Discrecional",
    "SHIATSU": "Discrecional",
    "RESTAURANTE": "Discrecional",
    "OCIO": "Discrecional",
    "REGALO": "Discrecional",
    "VIAJE": "Discrecional",
    "SUSCRIPCION": "Discrecional",
    "NETFLIX": "Discrecional",
    "SPOTIFY": "Discrecional",
    "BIZUM ENVIADO": "Discrecional",

    # AHORRO / INVERSIÓN
    "TRANSFERENCIA REVOLUT": "Ahorro/Inversión",
    "AHORRO ING": "Ahorro/Inversión",
    "GASTOS LUCIA": "Ahorro/Inversión",
    "KRAKEN": "Ahorro/Inversión",
    "INVERSION CRYPTO": "Ahorro/Inversión",
    "TRANSFERENCIA KRAKEN": "Ahorro/Inversión",
}

CATEGORY_META: dict[str, dict] = {
    "Ingresos": {"color": "#10b981", "bg": "#d1fae5", "icon": "savings", "is_income": True},
    "Gastos Fijos": {"color": "#f59e0b", "bg": "#fef3c7", "icon": "home", "is_income": False},
    "Tenis Lucía": {"color": "#8b5cf6", "bg": "#ede9fe", "icon": "sports_tennis", "is_income": False},
    "Gastos Variables": {"color": "#ef4444", "bg": "#fee2e2", "icon": "shopping_cart", "is_income": False},
    "Discrecional": {"color": "#f97316", "bg": "#ffedd5", "icon": "theater_comedy", "is_income": False},
    "Ahorro/Inversión": {"color": "#3b82f6", "bg": "#dbeafe", "icon": "trending_up", "is_income": False},
    "Sin categoría": {"color": "#6b7280", "bg": "#f3f4f6", "icon": "help_outline", "is_income": False},
}

EXTRA_PAY_MONTHS = {6, 12}

ALL_CATEGORIES = list(CATEGORY_META.keys())

TENNIS_CONCEPTS = {
    "ENTRENADOR LUCIA", "ROYDONCES", "JC FERRERO", "EQUELITE",
    "COMIDAS TENIS", "FISIO LUCIA", "EQUIPAMIENTO TENIS", "DESPLAZAMIENTOS TENIS",
}


def map_category(concepto: str, amount: float = 0.0) -> str:
    if not concepto or not concepto.strip():
        return "Sin categoría"

    upper = concepto.upper().strip()

    if upper in CATEGORIES:
        return CATEGORIES[upper]

    for key, category in CATEGORIES.items():
        if key in upper:
            return category

    if "BIZUM" in upper:
        return "Ingresos" if amount > 0 else "Discrecional"

    return "Sin categoría"
