from pathlib import Path
import io
import tempfile
import traceback

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import sweetviz as sv

st.set_page_config(
    page_title="AutoEDA AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📊 AutoEDA AI")
st.caption("Automated Exploratory Data Analysis & Machine Learning")
st.markdown(
    "CSV veya Excel dosyanı sürükleyip bırak; veri profilini incele, "
    "Sweetviz raporu oluştur ve istersen PyCaret ile AutoML çalıştır."
)

@st.cache_data(show_spinner=False)
def load_data(file_bytes: bytes, filename: str) -> pd.DataFrame:
    suffix = Path(filename).suffix.lower()
    if suffix == ".csv":
        # Common encodings are tried to support files exported from Excel.
        errors = []
        for encoding in ("utf-8", "utf-8-sig", "cp1254", "latin1"):
            try:
                return pd.read_csv(io.BytesIO(file_bytes), encoding=encoding)
            except Exception as exc:
                errors.append(str(exc))
        raise ValueError("CSV dosyası okunamadı. Dosya kodlamasını kontrol et.")
    if suffix in (".xlsx", ".xls"):
        return pd.read_excel(io.BytesIO(file_bytes))
    raise ValueError("Desteklenmeyen dosya türü. CSV veya Excel yükle.")

def display_report(report_path: str):
    html = Path(report_path).read_text(encoding="utf-8")
    components.html(html, height=900, scrolling=True)

def run_sweetviz(data: pd.DataFrame) -> bytes:
    with tempfile.TemporaryDirectory() as tmp:
        report_path = str(Path(tmp) / "sweetviz_report.html")
        report = sv.analyze(data, pairwise_analysis="on")
        report.show_html(filepath=report_path, open_browser=False, layout="widescreen")
        return Path(report_path).read_bytes()

def run_automl(data: pd.DataFrame, target: str, task: str, fold: int):
    # PyCaret is imported only when AutoML is requested, so EDA can still run
    # independently if the user has not installed PyCaret successfully.
    if task == "Sınıflandırma":
        from pycaret.classification import ClassificationExperiment
        experiment = ClassificationExperiment()
    else:
        from pycaret.regression import RegressionExperiment
        experiment = RegressionExperiment()

    experiment.setup(
        data=data,
        target=target,
        session_id=42,
        fold=fold,
        html=False,
        verbose=False,
        n_jobs=-1,
    )
    best_model = experiment.compare_models()
    leaderboard = experiment.pull().copy()
    tuned_model = experiment.tune_model(best_model)
    final_model = experiment.finalize_model(tuned_model)

    with tempfile.TemporaryDirectory() as tmp:
        model_stem = str(Path(tmp) / "autoeda_best_model")
        experiment.save_model(final_model, model_stem)
        model_file = Path(model_stem + ".pkl").read_bytes()

    return leaderboard, model_file

with st.sidebar:
    st.header("Ayarlar")
    st.write("1. Dosyanı yükle.")
    st.write("2. EDA raporunu oluştur.")
    st.write("3. İsteğe bağlı olarak AutoML çalıştır.")

uploaded_file = st.file_uploader(
    "Veri dosyanı buraya sürükle veya tıklayarak seç",
    type=["csv", "xlsx", "xls"],
    help="CSV, XLSX ve XLS dosyaları desteklenir.",
)

if uploaded_file is None:
    st.info("Başlamak için bir CSV veya Excel dosyası yükle.")
    st.markdown("**İçerik:** Sweetviz EDA · PyCaret AutoML · Model karşılaştırma · İndirilebilir rapor")
    st.stop()

try:
    df = load_data(uploaded_file.getvalue(), uploaded_file.name)
except Exception as exc:
    st.error(f"Dosya okunurken hata oluştu: {exc}")
    st.stop()

if df.empty:
    st.error("Yüklenen dosyada satır bulunamadı.")
    st.stop()

st.success(f"Dosya yüklendi: {uploaded_file.name}")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Satır", f"{df.shape[0]:,}")
c2.metric("Sütun", f"{df.shape[1]:,}")
c3.metric("Eksik hücre", f"{int(df.isna().sum().sum()):,}")
c4.metric("Tekrarlı satır", f"{int(df.duplicated().sum()):,}")

with st.expander("Veri önizleme", expanded=True):
    st.dataframe(df.head(100), use_container_width=True)
    st.caption("Önizlemede ilk 100 satır gösterilir.")
    info_df = pd.DataFrame({
        "Sütun": df.columns.astype(str),
        "Veri tipi": [str(x) for x in df.dtypes],
        "Eksik değer": [int(x) for x in df.isna().sum()],
        "Benzersiz değer": [int(df[c].nunique(dropna=True)) for c in df.columns],
    })
    st.dataframe(info_df, use_container_width=True, hide_index=True)

st.divider()
st.header("1. Keşifsel Veri Analizi — Sweetviz")

if st.button("Sweetviz raporunu oluştur", type="primary", use_container_width=False):
    try:
        with st.spinner("Sweetviz raporu hazırlanıyor... Veri setinin boyutuna göre biraz sürebilir."):
            report_bytes = run_sweetviz(df)
            st.session_state["sweetviz_report"] = report_bytes
        st.success("Sweetviz raporu hazır.")
    except Exception as exc:
        st.error(f"Sweetviz raporu oluşturulamadı: {exc}")
        st.exception(exc)

if "sweetviz_report" in st.session_state:
    report_bytes = st.session_state["sweetviz_report"]
    st.download_button(
        "⬇️ Sweetviz HTML raporunu indir",
        data=report_bytes,
        file_name="sweetviz_eda_report.html",
        mime="text/html",
    )
    with st.expander("Raporu uygulama içinde görüntüle", expanded=True):
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as temp:
            temp.write(report_bytes)
            temp_path = temp.name
        try:
            display_report(temp_path)
        finally:
            Path(temp_path).unlink(missing_ok=True)

st.divider()
st.header("2. Otomatik Makine Öğrenmesi — PyCaret")
st.caption("AutoML için hedef sütunu seçmelisin. Hedef sütun, modelin tahmin etmeye çalışacağı değişkendir.")

if df.shape[1] < 2:
    st.warning("AutoML için hedef değişken dışında en az bir özellik sütunu gerekir.")
else:
    target = st.selectbox("Hedef değişken (target)", options=list(df.columns))
    task = st.radio(
        "Problem türü",
        ["Sınıflandırma", "Regresyon"],
        horizontal=True,
        help="Sınıflandırma kategorileri/sınıfları; regresyon sayısal değerleri tahmin eder.",
    )
    fold = st.slider("Çapraz doğrulama kat sayısı", min_value=2, max_value=10, value=5)

    st.warning(
        "Not: AutoML seçilen hedef sütununu kullanır. Hedef sütununu doğru seçtiğinden "
        "ve kimlik, tarih veya sonuçtan türetilmiş sızıntı değişkenlerini kontrol ettiğinden emin ol."
    )

    if st.button("PyCaret AutoML çalıştır", use_container_width=False):
        if df[target].isna().all():
            st.error("Seçilen hedef sütunu tamamen boş.")
        elif len(df) < 20:
            st.error("PyCaret için en az 20 satır önerilir; bu veri seti çok küçük.")
        else:
            try:
                automl_data = df.dropna(subset=[target]).copy()
                with st.spinner("PyCaret modelleri eğitiyor ve karşılaştırıyor. Bu işlem zaman alabilir..."):
                    leaderboard, model_bytes = run_automl(automl_data, target, task, fold)
                st.session_state["automl_leaderboard"] = leaderboard
                st.session_state["automl_model"] = model_bytes
                st.session_state["automl_target"] = str(target)
                st.success("AutoML tamamlandı. En iyi model optimize edilip kaydedildi.")
            except ImportError as exc:
                st.error("PyCaret bulunamadı veya kurulumu tamamlanmamış. README içindeki kurulum adımlarını izle.")
                st.exception(exc)
            except Exception as exc:
                st.error(f"AutoML sırasında hata oluştu: {exc}")
                st.exception(exc)

if "automl_leaderboard" in st.session_state:
    st.subheader("Model karşılaştırma tablosu")
    st.dataframe(st.session_state["automl_leaderboard"], use_container_width=True)
    st.download_button(
        "⬇️ Model karşılaştırmasını CSV indir",
        data=st.session_state["automl_leaderboard"].to_csv(index=False).encode("utf-8-sig"),
        file_name="model_comparison.csv",
        mime="text/csv",
    )
    st.download_button(
        "⬇️ Eğitilmiş modeli indir (.pkl)",
        data=st.session_state["automl_model"],
        file_name="autoeda_best_model.pkl",
        mime="application/octet-stream",
    )

st.divider()
st.caption("AutoEDA AI · Yerel çalıştırma için: streamlit run app.py")
