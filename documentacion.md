# 📚 Documentación de Datos

## 🗂️ Tabla: `categorías_maestras`

### Campos

- **`Category_clean`** _(string)_  
  Categoría a la que pertenece un artículo (por ejemplo: `Ropa`, `Calzado`, etc.)

- **`Subcategory_clean`** _(string)_  
  Subcategoría a la que pertenece un artículo (por ejemplo: `Ropa → Camisas`, `Ropa → Pantalones`)

- **`ERP_Code`** _(string)_ — **PK**  
  Un código que representa la combinación de categoría y subcategoría con fines de identificación.

---

### 📝 Justificación

No se modificó.

---

## 🏢 Tabla: `proveedores`

### Campos

- **`Provider_ID`** _(int64)_ — **PK**  
  Identificador numérico único de cuatro dígitos, para proveedores de productos.

- **`Provider_Name`** _(string)_  
  Nombre de la empresa proveedora de productos.

- **`Region`** _(string)_  
  Ubicación de la empresa.

- **`Phone`** _(string)_  
  Número telefónico para contactar a la empresa. Incluye extensiones en algunos casos.

- **`Email`** _(string)_  
  Correo electrónico perteneciente a la empresa.

---

### 📝 Justificación

Se realizaron pocos cambios debido a la naturaleza de los datos y la intencionalidad de su formato final.  
Se estandarizó el formato de los teléfonos, y **no se creó una columna para extensiones** ya que sin la extensión el número no tiene utilidad.

Se contempló separar el campo de `Region` a subregiones, pero **se necesitaría más diálogo** ya que para la mayoría de las entradas se proporciona una sola región no estandarizada: una ciudad, un país, un estado, o un continente.

---

## 📦 Tabla: `productos_departamento`

### Campos

- **`Product_ID`** _(int64)_ — **PK**  
  Identificador numérico único de cuatro dígitos para un producto.

- **`Product_Name`** _(string)_  
  Nombre del producto.

- **`SKU`** _(string)_  
  Unidad de almacenamiento para el producto.

- **`Price`** _(float64)_  
  Precio del producto listado para su venta, en USD.

- **`Category`** _(string)_  
  Categoría principal del producto.

- **`Subcategory`** _(string)_  
  Categoría secundaria del producto.

- **`ERP_Code`** _(string)_  
  Código representando la combinación de categoría y subcategoría para propósito de identificación.

- **`Stock`** _(int64)_  
  Inventario del producto al momento de la fecha `Last_Update`.

- **`Provider_ID`** _(int64)_  
  Código de proveedor del producto.

- **`Last_Update`** _(date)_  
  Última vez que se actualizaron los datos del producto.

---

### 📝 Justificación

Se agregó un identificador `Product_ID` manteniendo el formato de otros campos como `Provider_ID` (empezando en 1001).  
Se normalizaron los nombres de productos, al igual que los precios. Aunque no se especifica la moneda, se asume **USD** debido a la escala global del caso.

Se limpiaron las columnas `Category` y `Subcategory`, también haciendo un **merge con `categorías_maestras`** para asignar su código `ERP_Code`.  
En cuanto a `Stock`, **no se eliminaron valores negativos**, ya que podrían representar productos faltantes en órdenes colocadas.

La columna `Last_Update` fue estandarizada al formato **YYYY-MM-DD**.

---

## 🔁 Tabla: `relacion_variantes`

### Campos

- **`Base_SKU`** _(string)_  
  Unidad principal de almacenamiento (SKU base) de un producto.

- **`Variant_SKU`** _(string)_  
  Variante alternativa del mismo producto (ej. diferente talla o color).

- **`Color`** _(string)_  
  Color del producto (normalizado en inglés para mantener consistencia).

- **`Size`** _(string)_  
  Talla del producto, en formato estandarizado (S, M, L, XL, XXL).

- **`Active`** _(bool)_  
  Indica si la variante del producto está activa (`TRUE`/`FALSE`).

---

### 📝 Justificación

Se estandarizó el formato de los campos para asegurar consistencia (por ejemplo, tallas y colores).  
El campo `Active` fue convertido a tipo **booleano**, ya que representa una opción binaria (activo/inactivo).

Se detectaron **filas duplicadas**, las cuales fueron **marcadas en el dashboard** en lugar de ser eliminadas automáticamente.  
Se eligió escribir los colores en inglés para mantener la coherencia con el sistema y facilitar futuras integraciones.

---

## 🧾 Tabla: `ventas_ultimos_6_meses`

### Campos

- **`Order_ID`** _(string)_ — **PK**  
  Identificador único para cada orden, con el formato `ORD-XX`.

- **`SKU`** _(string)_  
  Unidad de almacenamiento del producto vendido.

- **`Quantity_Sold`** _(float64)_  
  Cantidad de producto vendido. Un valor `-1` representa una devolución.

- **`Returned`** _(bool)_  
  Valor booleano que indica si la orden fue devuelta.

- **`Sale_Date`** _(date)_  
  Fecha en que se realizó la transacción.

- **`Total_Amount`** _(float64)_  
  Monto total de la venta en USD.

- **`Payment_Method`** _(string)_  
  Método de pago utilizado (`cash`, `card`, etc.).

---

### 📝 Justificación

Se agregó una nueva columna `Returned` para facilitar la detección de devoluciones sin depender de interpretar valores negativos en `Quantity_Sold`.

El campo `Payment_Method` se estandarizó en inglés para mantener coherencia con el sistema general.  
No se alteraron los valores negativos en `Total_Amount`, ya que pueden reflejar **devoluciones, reembolsos o pérdidas**.

Las fechas se limpiaron y estandarizaron en formato **YYYY-MM-DD**.
