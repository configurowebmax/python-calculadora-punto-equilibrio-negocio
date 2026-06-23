/* ============================================================
   ConfiguroWeb · Helpers JS para apps PyScript
   - Persistencia con localStorage
   - Interacción UI mínima (este archivo NO lleva lógica de negocio;
     la lógica vive en app.py para que Python domine el % del repo)
   (Marcado como linguist-vendored en .gitattributes)
   ============================================================ */

/* ---------- Persistencia localStorage ---------- */
const CWEB = {
  /** Guarda un valor (objeto/string/número) bajo una clave. */
  save(key, value) {
    try {
      localStorage.setItem(key, JSON.stringify(value));
      return true;
    } catch (e) {
      console.warn("No se pudo guardar en localStorage:", e);
      return false;
    }
  },

  /** Recupera y parsea un valor. Devuelve fallback si no existe. */
  load(key, fallback = null) {
    try {
      const raw = localStorage.getItem(key);
      return raw === null ? fallback : JSON.parse(raw);
    } catch (e) {
      return fallback;
    }
  },

  /** Elimina una clave. */
  remove(key) {
    localStorage.removeItem(key);
  },

  /** Limpia todas las claves con un prefijo (ej: "breakeven_"). */
  clearPrefix(prefix) {
    Object.keys(localStorage)
      .filter(k => k.startsWith(prefix))
      .forEach(k => localStorage.removeItem(k));
  }
};

/* ---------- Estado de carga de PyScript ---------- */
window.addEventListener("py:ready", () => {
  const status = document.getElementById("py-status");
  if (status) {
    status.classList.add("ready");
    status.textContent = "Python listo ✓";
  }
  const loader = document.getElementById("py-loading");
  if (loader) loader.classList.add("hidden");
});

/* ---------- Copiar al portapapeles ---------- */
function copiarTexto(texto, btn) {
  navigator.clipboard.writeText(texto).then(() => {
    const original = btn.textContent;
    btn.textContent = "¡Copiado! ✓";
    setTimeout(() => { btn.textContent = original; }, 1500);
  });
}

/* ---------- Imprimir sección ---------- */
function imprimirSeccion(selector) {
  const el = document.querySelector(selector);
  if (!el) return;
  const w = window.open("", "_blank");
  w.document.write("<html><head><title>Imprimir</title>");
  w.document.write("<style>body{font-family:sans-serif;padding:2rem;}" +
    "table{border-collapse:collapse;width:100%;}th,td{border:1px solid #ccc;padding:6px;}</style>");
  w.document.write("</head><body>" + el.innerHTML + "</body></html>");
  w.document.close();
  w.focus();
  setTimeout(() => { w.print(); w.close(); }, 300);
}