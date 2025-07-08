import streamlit as st
import pandas as pd

# Usamos plotly para las gráficas
import plotly.express as px
# Y ya tenemos cargados los reportes gracias a los Jupyter Notebooks

# PATHS CLEAN
categorias_clean = "limpio/categorias_maestras.xlsx"
productos_clean = "limpio/productos_departamento_clean.xlsx"
proveedores_clean = "limpio/proveedores_clean.xlsx"
relacion_variantes_clean = "limpio/relacion_variantes_clean.xlsx"
ventas_clean = "limpio/ventas_ultimos_6_meses_clean.xlsx"

# PATHS SAMPLES
productos_sample = "sample/productos_departamento_object.xlsx"
proveedores_sample = "sample/proveedores_object.xlsx"
ventas_sample = "sample/ventas_ultimos_6_meses_object.xlsx"
relacion_sample = "sample/relacion_variantes_object.xlsx"

# PATHS REPORTS
productos_report = "limpio/reporte_productos_departamento.html"
proveedores_report = "limpio/reporte_proveedores.html"
relacion_report = "limpio/reporte_relacion_variantes.html"
ventas_report = "limpio/reporte_ventas_ultimos_6_meses.html"

with open("documentacion.md", "r", encoding="utf-8") as f:
    markdown_text = f.read()

st.set_page_config(
    layout="wide",
    page_title="Caso Técnico Hanova",
    page_icon=":bar_chart:",
)


# Usamos cache para evitar leer varias veces los mismos archivos
@st.cache_data
def load_data(path: str):
    data = pd.read_excel(path)
    return data


# Sencillo display de los excels
def data_display(df_path: str, df_clean_path: str):
    st.title(options)
    df = load_data(df_path)
    df_clean = load_data(df_clean_path)

    clean_stats(df, df_clean)
    st.write("Datos Originales")
    st.write(df)
    st.write("Datos Limpiados")
    st.write(df_clean)


def clean_stats(df: pd.DataFrame, df_clean: pd.DataFrame):
    col1, col2, col3 = st.columns(3)

    # Col1 y 2 mostramos diferencias entre datasets originales y limpios
    with col1:
        print_null_counts(df, "Datos Originales")

    with col2:
        print_null_counts(df_clean, "Datos Limpiados")

    # Col3 mostramos entradas duplicadas
    with col3:
        print_duplicates(df_clean)


def print_duplicates(df: pd.DataFrame):
    st.markdown("#### Entradas duplicadas")
    num_duplicates = df.duplicated().sum()
    percent_duplicates = (num_duplicates / len(df)) * 100 if len(df) > 0 else 0
    if num_duplicates > 0:
        st.write(
            f"Número de filas duplicadas: {num_duplicates} ({percent_duplicates:.2f}%)"
        )
        st.write("Primeras 5 filas duplicadas:")
        st.write(df[df.duplicated()].head())
    else:
        st.write("No hay filas duplicadas")


def print_null_counts(df, label):
    st.markdown(f"#### Valores nulos por columna ({label})")
    null_counts = df.isnull().sum()
    total_rows = len(df)
    if (null_counts > 0).any():
        for col, null_count in null_counts.items():
            if null_count > 0:
                percent = (null_count / total_rows) * 100 if total_rows > 0 else 0
                st.write(f"{col}: {null_count} ({percent:.2f}%)")
    else:
        st.write("No hay valores nulos")


def print_report(report_path: str):
    with open(report_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    st.components.v1.html(html_content, height=1200, scrolling=True)


# ------------------------------------- GRAFICAS ------------------------------------ #
def print_cross_validation_analysis():
    st.title("Validación Cruzada de SKUs y Proveedores")

    # Cargar todos los datasets limpios
    df_productos = load_data(productos_clean)
    df_proveedores = load_data(proveedores_clean)
    df_relacion = load_data(relacion_variantes_clean)

    # 1. ANÁLISIS DE PROVIDER_ID INVÁLIDOS (VENTAS - PROVEEDORES)
    st.subheader("Provider_IDs en ventas que no existen en proveedores")

    # Obtener IDs únicos de cada dataset
    ventas_provider_ids = set(df_productos["Provider_ID"].dropna().unique())
    proveedores_ids = set(df_proveedores["Provider_ID"].dropna().unique())

    # Provider_IDs inválidos (en ventas pero no en proveedores)
    invalid_provider_ids = ventas_provider_ids - proveedores_ids

    # Crear Dataframe graficable
    if len(invalid_provider_ids) > 0:
        # Preparación para gráfica 1
        # Contamos las veces que aparecen los Provider_IDs inválidos
        invalid_counts = (
            df_productos[df_productos["Provider_ID"].isin(invalid_provider_ids)][
                "Provider_ID"
            ]
            .value_counts()  # Usamos value_counts para contar ocurrencias
            .reset_index()  # Convertimos a DataFrame
        )

        # Asignamos nombres a las columnas
        invalid_counts.columns = ["Provider_ID", "Ocurrencias"]

        # GRAFICAS

        # Grafica 1 - Barra de Provider_IDs inválidos
        fig = px.bar(
            invalid_counts,
            x="Provider_ID",
            y="Ocurrencias",
            title=f"Provider_IDs inválidos en ventas ({len(invalid_provider_ids)} encontrados)",
            color="Ocurrencias",
            labels={
                "Provider_ID": "ID de Proveedor",
                "Ocurrencias": "Número de Ventas",
            },
        )
        st.plotly_chart(fig)

        # Preparación para gráfica 2
        # Valores bool invertidos para Proveedor Válido (ya que checamos ids inválidos)
        df_productos["Valid_Provider"] = ~df_productos["Provider_ID"].isin(
            invalid_provider_ids
        )
        # Agrupamos por Proveedor Válido
        provider_valid_counts = (
            df_productos.groupby("Valid_Provider").size().reset_index()
        )
        # Renombramos las columnas
        provider_valid_counts.columns = ["Proveedor Válido", "Ventas"]

        # Grafica 2 - Pie de proporción de ventas válidas vs inválidas
        fig_pie = px.pie(
            provider_valid_counts,
            values="Ventas",
            names="Proveedor Válido",
            title="Proporción de ventas con proveedores válidos vs inválidos",
            color_discrete_map={True: "green", False: "red"},
        )
        st.plotly_chart(fig_pie)

    else:
        st.success(
            "¡Todos los Provider_IDs en ventas tienen proveedores válidos!!!! Wow! 👍🏻👍🏻"
        )

    # 2. ANÁLISIS DE SKUs INVÁLIDOS
    st.subheader("SKUs en ventas que no existen en relación de variantes")

    # Extraer SKUs únicos
    ventas_skus = set(df_productos["SKU"].dropna().unique())
    relacion_skus = set()

    # Combinar todos los SKUs posibles de la tabla relación_variantes
    if "Variant_SKU" in df_relacion.columns:
        relacion_skus.update(df_relacion["Variant_SKU"].dropna().unique())
    if "Base_SKU" in df_relacion.columns:
        relacion_skus.update(df_relacion["Base_SKU"].dropna().unique())

    # SKUs inválidos (en ventas pero no en relación de variantes)
    invalid_skus = ventas_skus - relacion_skus

    if len(invalid_skus) > 0:
        invalid_sku_counts = (
            df_productos[df_productos["SKU"].isin(invalid_skus)]["SKU"]
            .value_counts()
            .reset_index()
        )
        invalid_sku_counts.columns = ["SKU", "Ocurrencias"]

        fig = px.bar(
            invalid_sku_counts.head(20),  # Limitar a 20 para mejor visualización
            x="SKU",
            y="Ocurrencias",
            title=f"Top 20 SKUs inválidos en ventas (de {len(invalid_skus)} encontrados)",
            color="Ocurrencias",
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig)

        # Gráfica de pie para proporción
        df_productos["SKU_Válido"] = ~df_productos["SKU"].isin(invalid_skus)
        sku_valid_counts = df_productos.groupby("SKU_Válido").size().reset_index()
        sku_valid_counts.columns = ["SKU Válido", "Ventas"]

        fig_pie = px.pie(
            sku_valid_counts,
            values="Ventas",
            names="SKU Válido",
            title="Proporción de ventas con SKUs válidos vs inválidos",
            color_discrete_map={True: "green", False: "red"},
        )
        st.plotly_chart(fig_pie)

    else:
        st.success("Ningun SKUs en ventas falta de la relación de variantes. 👍🏻")


def print_sku_network():
    st.title("Red de relaciones Base_SKU -> Variant_SKU")

    # Cargar datos
    df_relacion = load_data(relacion_variantes_clean)

    # Contar variantes por cada Base_SKU
    variants_per_base = df_relacion.groupby("Base_SKU").size().reset_index()
    variants_per_base.columns = ["Base_SKU", "Número de Variantes"]

    # Gráfica de barras - Top 15 Base_SKUs con más variantes (Al final solo hay 11 variantes)
    fig = px.bar(
        variants_per_base.sort_values("Número de Variantes", ascending=False).head(16),
        x="Base_SKU",
        y="Número de Variantes",
        title="Top 15 Base_SKUs con más variantes",
        color="Número de Variantes",
    )
    st.plotly_chart(fig)


# ------------------------------------ PAGINA ------------------------------------ #
st.title("Caso Técnico Hanova")
st.markdown("Por Rogelio Villarreal")
st.markdown("Análisis de datos de ventas y productos")

st.sidebar.title("Navegación")
options = st.sidebar.radio(
    "Páginas",
    options=[
        "Inicio",
        "Ventas 6 meses",
        "Productos Departamento",
        "Proveedores",
        "Relacion Variantes",
        "Analisis",
        "Documentación",
    ],
)

if options == "Inicio":
    st.markdown("Para navegar por las secciones, utiliza el menú de la izquierda.")

elif options == "Ventas 6 meses":
    data_display(ventas_sample, ventas_clean)
    print_report(ventas_report)

elif options == "Productos Departamento":
    data_display(productos_sample, productos_clean)
    print_report(productos_report)

elif options == "Proveedores":
    data_display(proveedores_sample, proveedores_clean)
    print_report(proveedores_report)

elif options == "Relacion Variantes":
    data_display(relacion_sample, relacion_variantes_clean)
    print_report(relacion_report)

elif options == "Analisis":
    st.title("Análisis de Datos")

    tab1, tab2 = st.tabs(["Validación de SKUs y Proveedores", "Relaciones entre SKUs"])

    with tab1:
        print_cross_validation_analysis()

    with tab2:
        print_sku_network()

elif options == "Documentación":
    st.markdown(markdown_text)
