"""
=====================================================================
 Calculadora de Punto de Equilibrio para Negocios
 ConfiguroWeb · 2026
---------------------------------------------------------------------
 App hecha con Python ejecutándose en el navegador mediante PyScript.
 Toda la lógica de negocio vive en este archivo; el HTML solo pinta
 la interfaz y llama a estas funciones.

 Autor: ConfiguroWeb (https://configuroweb.com)
 Licencia: MIT
=====================================================================
"""

from pyscript import document, window
from js import localStorage
import json
import math


# =====================================================================
#  Constantes de la app
# =====================================================================
APP_CLAVE = "python_breakeven_datos"
VERSION = "1.0.0"


# =====================================================================
#  Clase de dominio: contiene la lógica pura de negocio
# =====================================================================
class AnalisisPuntoEquilibrio:
    """
    Representa un análisis de punto de equilibrio para un negocio.

    El punto de equilibrio es la cantidad mínima de unidades que se
    deben vender para que los ingresos igualesen a los costos totales.

    Fórmulas:
        Margen de contribución unitario = Precio - Costo Variable
        Punto de equilibrio (unidades)  = Costos Fijos / Margen unitario
        Punto de equilibrio ($ )        = Unidades * Precio
    """

    def __init__(self, costos_fijos, precio_unitario, costo_variable):
        if costos_fijos < 0:
            raise ValueError("Los costos fijos no pueden ser negativos.")
        if precio_unitario < 0:
            raise ValueError("El precio no puede ser negativo.")
        if costo_variable < 0:
            raise ValueError("El costo variable no puede ser negativo.")

        self.costos_fijos = float(costos_fijos)
        self.precio_unitario = float(precio_unitario)
        self.costo_variable = float(costo_variable)

    @property
    def margen_contribucion_unitario(self):
        """Lo que aporta cada unidad vendida a cubrir los costos fijos."""
        return self.precio_unitario - self.costo_variable

    @property
    def margen_contribucion_porcentual(self):
        """Margen de contribución como % del precio de venta."""
        if self.precio_unitario == 0:
            return 0.0
        return self.margen_contribucion_unitario / self.precio_unitario * 100

    def punto_equilibrio_unidades(self):
        """Unidades mínimas a vender para no perder ni ganar."""
        if self.margen_contribucion_unitario <= 0:
            return float("inf")
        return math.ceil(self.costos_fijos / self.margen_contribucion_unitario)

    def punto_equilibrio_dinero(self):
        """Ingresos mínimos necesarios para no perder ni ganar."""
        unidades = self.punto_equilibrio_unidades()
        if math.isinf(unidades):
            return float("inf")
        return unidades * self.precio_unitario

    def utilidad_para_unidades(self, unidades):
        """Calcula la utilidad (ganancia/pérdida) si se venden N unidades."""
        ingresos = unidades * self.precio_unitario
        costos_totales = self.costos_fijos + (unidades * self.costo_variable)
        return ingresos - costos_totales

    def escenario(self, unidades):
        """Devuelve un dict con el análisis de un escenario de venta."""
        utilidad = self.utilidad_para_unidades(unidades)
        pe = self.punto_equilibrio_unidades()
        if math.isinf(pe):
            estado = "⚠️ Inviable"
        elif unidades > pe:
            estado = "✅ Ganancia"
        elif unidades == pe:
            estado = "⚖️ Equilibrio"
        else:
            estado = "❌ Pérdida"
        return {
            "unidades": unidades,
            "ingresos": unidades * self.precio_unitario,
            "costos_totales": self.costos_fijos + (unidades * self.costo_variable),
            "utilidad": utilidad,
            "estado": estado,
        }

    def generar_escenarios(self, base=None):
        """Genera una tabla de escenarios ±50% alrededor del punto de equilibrio."""
        pe = base or self.punto_equilibrio_unidades()
        if math.isinf(pe):
            return []
        # Multiplicadores para mostrar variedad
        multiplicadores = [0.50, 0.75, 1.00, 1.25, 1.50]
        return [self.escenario(int(pe * m)) for m in multiplicadores]

    def diagnostico(self):
        """Texto explicativo del estado del negocio."""
        m = self.margen_contribucion_unitario
        if m <= 0:
            return ("⚠️ Tu costo variable es mayor o igual al precio. "
                    "Estás perdiendo con cada venta. Sube el precio o baja "
                    "el costo variable antes de calcular el equilibrio.")
        if self.costos_fijos == 0:
            return "✅ No tienes costos fijos: con la primera unidad ya ganas."
        pe = self.punto_equilibrio_unidades()
        return (f"Debes vender {pe:,} unidades para cubrir costos. "
                f"A partir de la unidad {pe + 1:,} empiezas a ganar.")


# =====================================================================
#  Formateadores de moneda y números
# =====================================================================
def formatear_moneda(valor):
    """Formatea un número como moneda con separadores de millar."""
    if math.isinf(valor):
        return "∞"
    return f"${valor:,.0f}"


def formatear_numero(valor):
    """Formatea un número entero con separadores de millar."""
    if math.isinf(valor):
        return "∞"
    return f"{int(valor):,}"


def formatear_porcentaje(valor):
    """Formatea un porcentaje con un decimal."""
    return f"{valor:.1f}%"


# =====================================================================
#  Persistencia con localStorage
# =====================================================================
def cargar_datos_guardados():
    """Carga los datos guardados previamente en localStorage."""
    try:
        raw = localStorage.getItem(APP_CLAVE)
        if raw:
            return json.loads(raw)
    except Exception:
        pass
    return None


def guardar_en_localstorage(datos):
    """Guarda un dict de datos en localStorage como JSON."""
    try:
        localStorage.setItem(APP_CLAVE, json.dumps(datos))
        return True
    except Exception:
        return False


# =====================================================================
#  Funciones de interfaz (conectadas al HTML)
# =====================================================================
def obtener_input_float(elemento_id):
    """Lee un valor numérico de un input por su ID. Vacío = 0."""
    el = document.querySelector(f"#{elemento_id}")
    if not el or not el.value:
        return 0.0
    try:
        return float(el.value)
    except (ValueError, TypeError):
        return 0.0


def mostrar_resultado(html, clase=""):
    """Inyecta HTML en la caja de resultado y la hace visible."""
    caja = document.querySelector("#resultado")
    caja.innerHTML = html
    caja.classList.remove("hidden", "is-error", "is-success")
    if clase:
        caja.classList.add(clase)


def mostrar_escenarios(filas):
    """Construye una tabla HTML con los escenarios de venta."""
    if not filas:
        document.querySelector("#escenarios").classList.add("hidden")
        return
    cabecera = """
        <table>
            <thead>
                <tr>
                    <th>Unidades vendidas</th>
                    <th>Ingresos</th>
                    <th>Costos totales</th>
                    <th>Utilidad / Pérdida</th>
                    <th>Estado</th>
                </tr>
            </thead>
            <tbody>
    """
    cuerpo = ""
    for f in filas:
        cuerpo += f"""
            <tr>
                <td>{formatear_numero(f['unidades'])}</td>
                <td>{formatear_moneda(f['ingresos'])}</td>
                <td>{formatear_moneda(f['costos_totales'])}</td>
                <td>{formatear_moneda(f['utilidad'])}</td>
                <td>{f['estado']}</td>
            </tr>
        """
    pie = "</tbody></table>"
    document.querySelector("#tabla-escenarios").innerHTML = cabecera + cuerpo + pie
    document.querySelector("#escenarios").classList.remove("hidden")


# =====================================================================
#  Handlers de eventos (PyScript los llama vía py-click)
# =====================================================================
def calcular_punto_equilibrio(event=None):
    """
    Función principal: lee los inputs, instancia el análisis,
    calcula y muestra resultados.
    """
    costos_fijos = obtener_input_float("costos-fijos")
    precio = obtener_input_float("precio-unitario")
    costo_var = obtener_input_float("costo-variable")

    # Validar que haya datos
    if costos_fijos == 0 and precio == 0 and costo_var == 0:
        mostrar_resultado(
            "⚠️ Ingresa al menos los costos fijos y el precio para calcular.",
            clase="is-error",
        )
        document.querySelector("#escenarios").classList.add("hidden")
        return

    try:
        analisis = AnalisisPuntoEquilibrio(costos_fijos, precio, costo_var)
    except ValueError as e:
        mostrar_resultado(f"❌ {e}", clase="is-error")
        return

    # Caso inviable: costo variable >= precio
    if analisis.margen_contribucion_unitario <= 0:
        html = f"""
            <div class="result-value" style="color:var(--cweb-danger);">
                ⚠️ Negocio inviable
            </div>
            <p>Tu costo variable por unidad
               (<strong>{formatear_moneda(costo_var)}</strong>)
               es mayor o igual al precio
               (<strong>{formatear_moneda(precio)}</strong>).</p>
            <p class="result-detail">{analisis.diagnostico()}</p>
        """
        mostrar_resultado(html, clase="is-error")
        document.querySelector("#escenarios").classList.add("hidden")
        return

    # Caso normal
    pe_unidades = analisis.punto_equilibrio_unidades()
    pe_dinero = analisis.punto_equilibrio_dinero()
    margen = analisis.margen_contribucion_unitario
    margen_pct = analisis.margen_contribucion_porcentual
    diag = analisis.diagnostico()

    html = f"""
        <div class="result-value">
            🎯 {formatear_numero(pe_unidades)} unidades
        </div>
        <p class="result-detail">
            Para cubrir todos tus costos necesitas vender
            <strong>{formatear_numero(pe_unidades)}</strong> unidades,
            equivalentes a <strong>{formatear_moneda(pe_dinero)}</strong> en ventas.
        </p>
        <hr style="margin:.8rem 0; border:none; border-top:1px solid var(--cweb-border);">
        <p class="result-detail">
            💡 Margen de contribución por unidad:
            <strong>{formatear_moneda(margen)}</strong>
            ({formatear_porcentaje(margen_pct)} del precio)
        </p>
        <p class="result-detail">{diag}</p>
    """
    mostrar_resultado(html, clase="is-success")

    # Mostrar tabla de escenarios
    escenarios = analisis.generar_escenarios()
    mostrar_escenarios(escenarios)


def guardar_datos(event=None):
    """Lee los inputs actuales y los persiste en localStorage."""
    datos = {
        "costos_fijos": obtener_input_float("costos-fijos"),
        "precio_unitario": obtener_input_float("precio-unitario"),
        "costo_variable": obtener_input_float("costo-variable"),
        "version": VERSION,
    }
    ok = guardar_en_localstorage(datos)
    if ok:
        mostrar_resultado(
            "💾 Datos guardados en este navegador. "
            "La próxima vez que abras esta página los podrás cargar.",
            clase="is-success",
        )
    else:
        mostrar_resultado(
            "❌ No se pudieron guardar los datos (navegador en modo privado).",
            clase="is-error",
        )


def cargar_datos_al_inicio():
    """Si hay datos guardados, precarga los inputs y avisa al usuario."""
    datos = cargar_datos_guardados()
    if not datos:
        return
    try:
        if "costos_fijos" in datos:
            document.querySelector("#costos-fijos").value = datos["costos_fijos"]
        if "precio_unitario" in datos:
            document.querySelector("#precio-unitario").value = datos["precio_unitario"]
        if "costo_variable" in datos:
            document.querySelector("#costo-variable").value = datos["costo_variable"]
        # Aviso discreto
        aviso = document.querySelector("#resultado")
        aviso.innerHTML = (
            "📂 Cargamos tus datos guardados. Pulsa <em>Calcular</em> "
            "para ver el resultado actualizado."
        )
        aviso.classList.remove("hidden")
    except Exception:
        pass


# =====================================================================
#  Inicialización al cargar la página
# =====================================================================
def inicializar():
    """Punto de entrada: carga datos previos y marca Python como listo."""
    cargar_datos_al_inicio()
    # Avisar al JS que Python ya está listo
    window.dispatchEvent(window.Event.new("py:ready"))


# Ejecutar la inicialización cuando el DOM esté listo
inicializar()