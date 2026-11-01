# AutoEDA AI

CSV veya Excel dosyalarını sürükle-bırak yöntemiyle yükleyip Sweetviz ile keşifsel veri analizi (EDA), PyCaret ile otomatik makine öğrenmesi (AutoML) yapabileceğiniz Streamlit uygulaması.

## Özellikler

- CSV, XLSX ve XLS dosyalarını sürükleyip bırakarak yükleme
- Satır/sütun sayısı, eksik değer ve tekrarlı satır özeti
- Veri önizleme ve sütun bazında veri tipi / eksik / benzersiz değer tablosu
- Sweetviz ile interaktif EDA raporu oluşturma ve HTML olarak indirme
- PyCaret ile Classification veya Regression modeli karşılaştırma
- En iyi modeli ayarlama (tuning), tüm veriyle sonlandırma (finalize) ve `.pkl` olarak indirme
- Model karşılaştırma tablosunu CSV olarak indirme

## Gereksinimler

- Python 3.10 veya 3.11 önerilir.
- PyCaret 3.3.2, Python 3.11 ile uyumlu olacak şekilde sabitlenmiştir.
- AutoML için yeterli RAM ve işlemci kaynağı gerekir. Büyük veri setlerinde model eğitimi uzun sürebilir.

## Kurulum

### 1. Depoyu klonla

```bash
git clone https://github.com/KULLANICI_ADIN/autoeda-ai.git
cd autoeda-ai
```

`KULLANICI_ADIN` ve depo adını kendi GitHub bilgilerine göre değiştir.

### 2. Sanal ortam oluştur

Windows:

```bash
py -3.11 -m venv .venv
.venv\Scripts\activate
```

macOS / Linux:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

### 3. Paketleri yükle

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Uygulamayı başlat

```bash
streamlit run app.py
```

Tarayıcıda genellikle `http://localhost:8501` adresi açılır.

## Kullanım

1. Uygulama ekranındaki yükleme alanına CSV veya Excel dosyanı sürükleyip bırak.
2. Veri önizlemesini ve temel veri özetini incele.
3. **Sweetviz raporunu oluştur** düğmesine bas. Hazır olduğunda HTML raporunu indirebilir veya uygulama içinde görüntüleyebilirsin.
4. AutoML bölümünde tahmin edilecek hedef sütunu seç.
5. Problem türünü (Sınıflandırma / Regresyon) seç ve çapraz doğrulama kat sayısını belirle.
6. **PyCaret AutoML çalıştır** düğmesine bas.
7. Model karşılaştırma tablosunu CSV, eğitilmiş modeli PKL olarak indir.

## Önemli notlar

- Sweetviz ve PyCaret farklı amaçlara hizmet eder: Sweetviz veriyi keşfeder; PyCaret hedef değişken kullanarak model eğitir.
- Sınıflandırma; örneğin kredi temerrüdü gibi kategorik sınıfları tahmin etmek içindir. Regresyon; örneğin gelir veya fiyat gibi sayısal değerleri tahmin etmek içindir.
- Hedef değişkeni doğru seçmelisin. Hedefle doğrudan ilişkili veya tahmin anında bilinmeyecek sütunlar veri sızıntısına (data leakage) neden olabilir.
- Uygulama yüklenen dosyayı Git deposuna yazmaz. Dosyayı GitHub'a commit etme; `.gitignore` içinde veri dosyaları hariç tutulmuştur.
- `.pkl` model dosyalarını yalnızca güvendiğin kaynaklardan yükle. Pickle dosyalarının açılması güvenilmeyen dosyalarda kod çalıştırma riski taşır.
- Bu proje başlangıç amaçlıdır; finansal/kredi kararlarında kullanılmadan önce veri kalitesi, adalet, açıklanabilirlik, bağımsız test ve mevzuat kontrolleri yapılmalıdır.
- Uygulama şu an yerel kullanım içindir. Herkese açık sunucuya dağıtmadan önce kimlik doğrulama, dosya boyutu sınırı, kaynak kullanımı ve veri gizliliği önlemleri ekle.

## Proje yapısı

```text
autoeda-ai/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
└── LICENSE
```

## GitHub'a yükleme

GitHub'da boş bir depo oluşturduktan sonra proje klasöründe:

```bash
git init
git add .
git commit -m "Initial AutoEDA AI application"
git branch -M main
git remote add origin https://github.com/KULLANICI_ADIN/autoeda-ai.git
git push -u origin main
```

`finance_dataset.csv`, kişisel veri içeren dosyalar, sanal ortam ve model çıktıları depoya eklenmemelidir.

## Lisans

Bu proje MIT lisansı ile sunulmuştur. Ayrıntılar için `LICENSE` dosyasına bak.
