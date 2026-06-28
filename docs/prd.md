# Product Requirements Document (PRD)

## Producto

**Nombre:** Presupuesto Familiar  
**Descripción:** App web local para gestionar el presupuesto y la contabilidad del hogar de Robert y Marta.  
**Estado:** En desarrollo — v1.0

---

## Problema que resuelve

Robert y Marta son dos funcionarios de la AEAT con 14 pagas al año, múltiples cuentas bancarias y gastos significativos vinculados al tenis de su hija Lucía (~2.400€/mes en entrenador). Necesitan una herramienta para:
- Importar movimientos reales desde Google Sheets (CaixaBank y Santander)
- Ver ingresos vs gastos mensuales frente a presupuesto definido
- Controlar el gasto de tenis de Lucía por separado
- Identificar visualmente los meses de paga extra (junio y diciembre)

---

## Usuarios

- **Robert** — gestión principal de la app, importa sheets, define presupuestos
- **Marta** — consulta resúmenes, añade movimientos Revolut

---

## Cuentas bancarias

| Cuenta | Fuente | Notas |
|--------|--------|-------|
| CaixaBank | Google Sheet (import manual) | Nómina Robert, MetLife, entrenador Lucía |
| Santander | Google Sheet (import manual) | Nómina Marta, gastos fijos domiciliados |
| Revolut | Entrada manual en app | Gastos hormiga Marta |
| Kraken | Solo línea de gasto | Inversión crypto (interno no entra) |

**IDs de Sheets:**
- CaixaBank: `154ovBGpaMOwoLAKN0wVHc12Ebr72t9LtzjHhjvy-oeM`
- Santander: `1KfGcbeJYaoxJHfAwZuqEHflYcZsX1zfnUVowopS9cPk`

---

## Funcionalidades — v1.0

1. **Importar desde Sheets** — botón manual, deduplicación automática
2. **Entrada manual Revolut** — formulario simple
3. **Resumen mensual** — ingresos / gastos / balance con gráficas
4. **Presupuesto definible** — por categoría y mes, con barra de progreso
5. **Control de cuentas** — saldo actual + movimientos por cuenta
6. **Vista Tenis Lucía** — total mensual + anual + desglose por concepto
7. **Distinción paga extra** — badge visual en junio y diciembre
8. **Exportar CSV** — compatible con Excel (UTF-8 BOM)
9. **Base de datos persistente** — SQLite local, no se pierde al cerrar

---

## Categorías

### Ingresos
NOMINA ROBERT, NOMINA MARTA, RETORNO SEGURO AXA, INGRESO MUFACE, BIZUM recibido, INGRESO AHORROS

### Gastos Fijos
SEGURO SALUD AXA, PRESTAMO COCHE Cetelem, TELEFONO VODAFONE, SEGURO LUCIA Mapfre, ONG CRUZ ROJA, ONG ACNUR, DEPURADOR AGUA, COMUNIDAD PROPIETARIOS, LAIETANIA, Impuestos (IVTM, IBI, basuras), SEGURO COCHE AXA, METLIFE, AHORRO LUCIA, COMUNIDAD PARKING, AGUAS MATARO

### Tenis Lucía (categoría especial)
ENTRENADOR LUCIA (Roydonces/JC Ferrero), COMIDAS TENIS, FISIO LUCIA, EQUIPAMIENTO TENIS, DESPLAZAMIENTOS TENIS

### Gastos Variables
LUZ ENDESA, GAS ENDESA, Alimentación, Farmacia/Salud, Transporte/Combustible, Ropa/Calzado, Hogar

### Discrecional
SIATSHU, Restaurantes/Ocio, Regalos, Viajes, Suscripciones, BIZUM enviados

### Ahorro / Inversión
TRANSFERENCIA REVOLUT, AHORRO ING, GASTOS LUCIA, TRANSFERENCIA KRAKEN

---

## Fuera de alcance

- Movimientos internos de Kraken (contabilidad crypto separada)
- Datos anteriores a enero 2026
- App móvil
- Multi-usuario / autenticación
