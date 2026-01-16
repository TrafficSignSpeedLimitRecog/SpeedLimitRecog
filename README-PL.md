# 🚦 System Detekcji Ograniczeń Prędkości

System wykrywania znaków ograniczenia prędkości wykorzystujący YOLOv8. Rozpoznaje znaki ograniczenia prędkości zarówno na zdjęciach, jak i w plikach wideo.

![Python](https://img.shields.io/badge/python-3.12-blue) ![PyTorch](https://img.shields.io/badge/pytorch-2.5-red) ![YOLOv8](https://img.shields.io/badge/yolo-v8-orange)

---

## 🛠️ Stack Technologiczny

- **YOLOv8m** (Ultralytics) - Model produkcyjny
- **PyTorch 2.5** + **CUDA 12.1**
- **PySide6** (Qt6) - Interfejs graficzny
- **OpenCV** - Przetwarzanie obrazu

## 📊 Statystyki Zbioru Danych

- **Łączna liczba zdjęć:** 6,304
- **Trening:** 4,656 (73.8%)
- **Walidacja:** 1,086 (17.2%)
- **Test:** 562 (8.9%)
- **Klasy:** 10 ['20', '30', '40', '50', '60', '70', '80', '100', '120', 'speed-sign-end']
- **Format:** YOLO v8 PyTorch

## 🎯 Wydajność (YOLOv8m)

Model został wytrenowany na architekturze `yolov8m` z wykorzystaniem agresywnej augmentacji, aby zapewnić stabilność na nagraniach wideo z rzeczywistych warunków drogowych.

| Metryka                  | Wartość              | Uwagi                                   |
|--------------------------|----------------------|-----------------------------------------|
| **mAP@50**               | **98.9%**            | Ekstremalnie niezawodna detekcja        |
| **mAP@50-95**            | **84.4%**            | Wysoka precyzja ramek (bounding boxes)  |
| **Precision**            | **99.1%**            | Prawie zerowa liczba fałszywych alarmów |
| **Recall**               | **98.1%**            | Pomija mniej niż 2% znaków              |
| **Prędkość (Inference)** | **3.4ms (~294 FPS)** | Testowano na RTX 4090 (Batch=16)        |
| **Czas Treningu**        | **2.0h**             | 300 epok (Early Stopping przy 196)      |

### Wydajność dla poszczególnych klas (Zbiór Testowy)

| Klasa          | Precision | Recall   | mAP@50 | mAP@50-95 |
|----------------|-----------|----------|--------|-----------|
| 20 km/h        | 98.2%     | 96.7%    | 97.3%  | 82.5%     |
| 30 km/h        | **100%**  | 97.3%    | 99.4%  | 82.3%     |
| 40 km/h        | 98.0%     | **100%** | 99.5%  | 85.6%     |
| 50 km/h        | 99.8%     | 97.2%    | 99.3%  | **88.3%** |
| 60 km/h        | 97.5%     | 97.9%    | 96.2%  | 81.2%     |
| 70 km/h        | 99.7%     | **100%** | 99.5%  | 81.3%     |
| 80 km/h        | 99.6%     | 98.5%    | 99.4%  | 87.4%     |
| 100 km/h       | **100%**  | 94.9%    | 99.5%  | 84.1%     |
| 120 km/h       | 99.9%     | 98.7%    | 99.4%  | 82.3%     |
| speed-sign-end | 98.8%     | **100%** | 99.5%  | **88.6%** |

### 🏆 Porównanie Treningu: YOLOv8s vs YOLOv8m

Poniższa tabela przedstawia różnice w wydajności po przejściu z modelu bazowego (Small - zoptymalizowany pod zdjęcia) na obecny model produkcyjny (Medium - zoptymalizowany pod wideo i trudne warunki).

| Metryka       | YOLOv8s (Poprzedni) | YOLOv8m (Obecny) |  Zmiana   | Interpretacja                                                                                                                                            |
|:--------------|:-------------------:|:----------------:|:---------:|:---------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Precision** |        98.1%        |    **99.1%**     | **+1.0%** | **Kluczowa poprawa.** Model M generuje znacznie mniej fałszywych alarmów (np. mylenie billboardów ze znakami).                                           |
| **mAP@50**    |        99.0%        |      98.9%       |   -0.1%   | Pomijalna różnica. Zdolność detekcji pozostaje na perfekcyjnym poziomie.                                                                                 |
| **mAP@50-95** |        85.9%        |      84.4%       |   -1.5%   | Oczekiwany spadek spowodowany silną augmentacją. Model poświęcił idealne dopasowanie pikseli na zdjęciach na rzecz lepszej generalizacji w deszczu/nocy. |
| **Recall**    |        98.2%        |      98.1%       |   -0.1%   | Stabilnie. Model nadal wykrywa niemal każdy widoczny znak.                                                                                               |
| **Prędkość**  |       0.7 ms        |      3.4 ms      |  +2.7 ms  | Mimo że wolniejszy, ~290 FPS na RTX 4090 to wciąż znacznie powyżej wymagań czasu rzeczywistego.                                                          |

**Wniosek:**
Przejście na model **Medium** z agresywną augmentacją skutecznie rozwiązało problem "migania detekcji" na materiale wideo. Wzrost Precyzji do 99.1% gwarantuje znacznie bardziej niezawodny system w rzeczywistych warunkach drogowych.

### 🏆 Porównanie Modeli: YOLOv8m vs YOLOv8l

W celu wyboru optymalnego modelu przeprowadziliśmy analizę porównawczą między architekturami **Medium** i **Large**. Mimo teoretycznej przewagi modelu Large (więcej parametrów), nasze testy empiryczne na wideo i metryki walidacyjne wykazały, że **YOLOv8m jest lepszy** do tego konkretnego zastosowania.

| Cecha / Metryka            |   YOLOv8m (Medium)   |   YOLOv8l (Large)    | Zwycięzca  | Analiza                                                                                                       |
|:---------------------------|:--------------------:|:--------------------:|:----------:|:--------------------------------------------------------------------------------------------------------------|
| **Parametry**              |        25.9 M        |        43.7 M        | **Medium** | Mniejszy model lepiej generalizuje na naszym zbiorze ~6k zdjęć, wykazując mniejszą tendencję do overfittingu. |
| **mAP@50-95** (Dokładność) |      **84.4%**       |        83.4%         | **Medium** | Model M zapewnia precyzyjniejszą lokalizację ramek (bounding boxes).                                          |
| **Precision** (Pewność)    |      **99.1%**       |        98.8%         | **Medium** | Zaobserwowano mniej fałszywych detekcji (False Positives) w modelu Medium.                                    |
| **Prędkość** (RTX 4090)    |     **~3.4 ms**      |       ~5.4 ms        | **Medium** | Model M jest o ok. **37% szybszy**, pozostawiając więcej zasobów dla potoku przetwarzania wideo.              |
| **Weight Decay**           |        0.0005        |        0.0005        |     -      | Użyto identycznych ustawień regularyzacji.                                                                    |
| **Wynik Treningu**         | Najlepsza Epoka: 176 | Najlepsza Epoka: 166 |     -      | Oba modele zbiegły się podobnie, ale M zachował lepszą stabilność.                                            |

**Wniosek:**
Wybraliśmy **YOLOv8m** jako model produkcyjny. Oferuje on najlepszy balans między szybkością a precyzją. Jego wyższy wynik **mAP@50-95** zapewnia stabilniejsze detekcje na nagraniach wideo, eliminując migotanie ramek często obserwowane w modelach z nadmiarem parametrów (over-parameterized).

### 📈 Pipeline Augmentacji Danych

Aby zasypać przepaść między statycznymi zdjęciami treningowymi a dynamicznym wideo ("Reality Gap"), wdrożyliśmy agresywną strategię augmentacji online. Poniższe transformacje są nakładane dynamicznie podczas treningu (Parametry dla YOLOv8m):

| Kategoria         | Metoda              |  Wartość  | Cel                                                                           |
|:------------------|:--------------------|:---------:|:------------------------------------------------------------------------------|
| **Fotometryczne** | **Nasycenie (HSV)** |   `0.8`   | Symuluje dni o wysokim kontraście (słońce) oraz szarugę/deszcz.               |
|                   | **Jasność (HSV)**   |   `0.5`   | Symuluje jazdę w cieniu, tunelach lub pod słońce (zmienność oświetlenia).     |
|                   | **Odcień (HSV)**    |  `0.025`  | Drobne przesunięcia kolorów uwzględniające różne sensory kamer.               |
| **Geometryczne**  | **Obrót**           |  `±15°`   | Obsługuje krzywe znaki lub przechył pojazdu na zakrętach.                     |
|                   | **Przesunięcie**    |  `±20%`   | Uczy model wykrywania znaków, które nie znajdują się w centrum kadru.         |
|                   | **Skala**           |  `±70%`   | Kluczowe dla wykrywania znaków z różnych odległości (autostrada vs miasto).   |
|                   | **Ścinanie**        |   `±5°`   | Symuluje zniekształcenia perspektywy.                                         |
| **Regularyzacja** | **Mosaic**          |   `1.0`   | Skleja 4 zdjęcia w jedno; zmusza model do nauki kontekstu i małych obiektów.  |
|                   | **MixUp**           |  `0.15`   | Miesza dwa zdjęcia (prawdopodobieństwo 15%) wygładzając granice decyzyjne.    |
|                   | **Copy-Paste**      |   `0.1`   | Losowo wkleja instancje znaków na inne zdjęcia, zwiększając gęstość obiektów. |
|                   | **Odbicie**         | `Poziome` | Lustrzane odbicie zdjęć (lewo/prawo) podwaja różnorodność zbioru danych.      |

> **Uwaga:** Te agresywne ustawienia (szczególnie MixUp i wysoka wariancja Skali) były kluczowe dla osiągnięcia stabilnej detekcji na nieznanym materiale wideo.

## 🧪 Analiza Wpływu Augmentacji Danych (Eksperyment A/B)

W celu weryfikacji przyjętej strategii treningowej przeprowadziliśmy kontrolowany eksperyment, trenując model (`yolov8m`) w dwóch wariantach: bez augmentacji (Baseline) oraz z pełną augmentacją (Production). Nasza analiza wykazuje, dlaczego augmentacja jest kluczowa dla systemów wizyjnych działających w trybie wideo.

### 1. Porównanie Ilościowe

| Metryka                  | Bez Augmentacji (Baseline) | Z Augmentacją (Production) |  Różnica   | Analiza Inżynierska                                                                                                                |
|:-------------------------|:--------------------------:|:--------------------------:|:----------:|:-----------------------------------------------------------------------------------------------------------------------------------|
| **Recall (Czułość)**     |           95.2%            |         **98.1%**          | **+2.9%**  | Wzrost kluczowy. Model bez augmentacji pomija ok. 5% znaków, co dyskwalifikuje go jako system bezpieczeństwa.                      |
| **Precision (Precyzja)** |           98.6%            |         **99.1%**          |   +0.5%    | Augmentacja nie zwiększyła liczby fałszywych alarmów (False Positives), wręcz przeciwnie - model jest pewniejszy.                  |
| **Współczynnik Błędu**   |            4.8%            |          **1.9%**          |  **-60%**  | **Najważniejsza statystyka.** Zredukowaliśmy liczbę niewykrytych znaków o ponad **60%** (z 48 błędów na 1000 prób do zaledwie 19). |
| **Recall dla "50 km/h"** |           90.6%            |         **97.2%**          | **+6.6%**  | Model bazowy nie wykrywał co dziesiątego znaku "50". Augmentacja wyeliminowała tę "ślepotę" na różne skale znaku.                  |
| **mAP@50-95**            |           82.7%            |         **84.4%**          |   +1.7%    | Lepsze dopasowanie ramki (bounding box) do rzeczywistego obrysu znaku.                                                             |
| **Czas Treningu**        |      1.5h (124 epoki)      |      2.0h (196 epok)       |   +0.5h    | Model bazowy uległ szybkiemu **przeuczeniu (overfitting)**. Wersja z augmentacją uczyła się dłużej, budując solidne cechy.         |
| **Prędkość Działania**   |           3.4 ms           |           3.4 ms           | **0.0 ms** | **Koszt zerowy.** Złożoność obliczeniowa gotowego modelu jest identyczna; augmentacja obciąża tylko proces treningu.               |

### 2. Analiza Jakościowa (Nasze uzasadnienie)

Dlaczego numeryczny wzrost o ~3% przekłada się na drastyczną różnicę w jakości działania aplikacji?

#### A. Pułapka "Łatwego Zbioru Testowego"
Statystyki (mAP, Recall) liczone są na statycznym zbiorze testowym.
* **Problem:** Zbiór testowy składa się z wyraźnych klatek, zbliżonych charakterystyką do zbioru treningowego.
* **Efekt:** Model BEZ augmentacji "wkuł na pamięć" (overfitting) te idealne kształty.
* **Rzeczywistość (Wideo):** W warunkach drogowych występuje rozmycie ruchu (motion blur), deszcz, cienie i nietypowe kąty. Model "bez augmentacji" tego nie widział, więc traci detekcję. Model "z augmentacją" (trenowany na `Mosaic`, `MixUp`, `HSV`) jest odporny na szum.

#### B. Błedy (Redukcja o 60%)
Patrząc na wzrost Recall z 95.2% na 98.1%, łatwo ulec złudzeniu, że to mała różnica. W inżynierii ADAS patrzymy jednak na **Redukcję Błędu**:
* Błąd Baseline: **4.8%**
* Błąd Finalny: **1.9%**
* **Wniosek:** Zredukowaliśmy ryzyko niewykrycia znaku o ponad **60%**.

#### C. Stabilność (Problem migotania)
To najważniejszy aspekt wizualny w naszej aplikacji:
* **Scenariusz:** Wideo 60 FPS.
* **Model 95% (Bez Augmentacji):** Statystycznie gubi detekcję co 20 klatek. Oznacza to, że ramka znika i pojawia się ("miga") 3 razy na sekundę. Dla użytkownika system wygląda na uszkodzony.
* **Model 98% (Z Augmentacją):** Utrzymuje ciągłość detekcji (lock) przez większość czasu, zapewniając płynny i czytelny interfejs.

## 🚀 Wydajne Przetwarzanie Wideo (Optymalizacja RTX 4090)

Aby w pełni wykorzystać ogromną moc obliczeniową równoległą karty **NVIDIA RTX 4090**, odeszliśmy od standardowego przetwarzania klatka-po-klatce. Zamiast tego zaimplementowaliśmy architekturę **Wielowątkowego Przetwarzania Wsadowego (Threaded Batch Processing)**.

### Jak to działa:
1.  **Wzorzec Producent-Konsument:** System używa oddzielnych wątków do czytania klatek wideo (obciążenie I/O) i ich przetwarzania (obciążenie GPU).
2.  **Dynamiczne Batchowanie:** Zamiast wysyłać pojedyncze zdjęcie do GPU, detektor zbiera grupę klatek (np. 4, 8 lub 16) z kolejki.
3.  **Równoległa Inferencja:** Taka paczka (batch) jest wysyłana do GPU w jednym wywołaniu. RTX 4090 przetwarza wszystkie obrazy w paczce jednocześnie, wykorzystując tysiące rdzeni CUDA.

**Korzyść:** Drastyczna redukcja narzutu komunikacyjnego CPU-GPU. Podczas gdy inferencja pojedynczej klatki mogłaby trwać ~6ms (przez narzut), przetwarzanie wsadowe pozwala osiągnąć przepustowość rzędu **~3ms na klatkę**, umożliwiając analizę w wysokim FPS nawet przy dużej rozdzielczości.

## 🚀 Szybki Start

### Sklonuj repozytorium
`git clone https://github.com/TrafficSignSpeedLimitRecog/SpeedLimitRecog.git`

`cd SpeedLimitRecog`

### Utwórz środowisko wirtualne
`python -m venv .venv`

`.venv\Scripts\activate`  # Windows

### Zainstaluj zależności
`pip install -r requirements.txt`

- Python 3.12
- PyTorch 2.5
- CUDA 12.1

### Pobierz Zbiór Danych

Wejdź na [Roboflow](https://universe.roboflow.com/speedlimitrecog-qazyk/speedlimitrecog-xgxlz/dataset/3) i pobierz format **YOLO v8 PyTorch**.

Wypakuj do `datasets/yolo_detection/`

### Trenuj Model
`python src/simple_trainer.py`

Czas treningu: ~1.5-2h (RTX 4090, 300 epok)

### Uruchom GUI
`python src/main.py --gui`

## 📁 Struktura projektu

```
SpeedLimitRecog/
├── src/
│   ├── main.py              # Entry point
│   ├── simple_trainer.py    # Training script
│   ├── core/
│   │   ├── detector.py      # YOLO detector
│   │   └── video_processor.py
│   └── gui/
│       ├── main_window.py   # Main GUI
│       ├── components.py    # UI components
│       └── styles.py        # Dark theme
├── datasets/
│   ├── yolo_detection/      # Training dataset
│   ├── test_images/         # Test images
│   └── test_videos/         # Test videos
├── models/
│   └── speed_limit_recog/
│       └── weights/
│           └── best.pt      # Trained model
├── config/
│   └── settings.yaml        # Configuration
└── requirements.txt
```

## ⚙️ Konfiguracja

Edytuj `config/settings.yaml`:

```
model:
  confidence_threshold: 0.5
  iou_threshold: 0.45

processing:
  fps_target: 60
  use_gpu: true
```

## 🎨 Funkcjonalności

**Detekcja na Obrazach:**
- Wczytywanie folderu ze zdjęciami
- Nawigacja klawiszami A/D lub strzałkami
- Detekcja spacją
- Regulowany suwak pewności (confidence)

**Przetwarzanie Wideo:**
- Drag & drop plików wideo
- Przetwarzanie z nakładką detekcji
- Odtwarzanie w czasie rzeczywistym
- Pasek postępu

## 📝 Komendy

### Trenuj model
`python src/simple_trainer.py`

### Uruchom GUI
`python src/main.py --gui`

### Waliduj model
`python -c "from ultralytics import YOLO; m = YOLO('models/speed_limit_recog/weights/best.pt'); m.val(data='datasets/yolo_detection/data.yaml')"`

## 🔧 Rozwiązywanie Problemów

**CUDA Out of Memory:**

W `simple_trainer.py`, zmniejsz rozmiar batcha:
batch=8 # zamiast 16

**Model Not Found:**

Pobierz dataset i najpierw przeprowadź trening:
`python src/simple_trainer.py`


## 📄 Licencja

Licencja MIT

- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)
- [Roboflow](https://roboflow.com/)

## 👥 Zespół i Podział Obowiązków

Projekt został zrealizowany przez zespół inżynierski z podziałem odpowiedzialności według modułów systemu. Każdy członek zespołu był odpowiedzialny za implementację przypisanych komponentów.

### **Jakub Kleban** - *Optymalizacja Treningu i Implementacja Backend*
* **Implementacja Trenera:** Programowanie klasy Trenera oraz logiki zarządzającej cyklem życia treningu (callbacks, checkpoints).
* **Logika Augmentacji:** Kodowanie potoku dynamicznych transformacji obrazu (HSV, MixUp) w celu uodpornienia modelu na rzeczywiste warunki drogowe.
* **Analiza i Optymalizacja:** Implementacja skryptów walidacyjnych oraz wybór optymalnej architektury sieci (migracja z `s` na `m`) na podstawie wyników metrycznych.

### **Łukasz Kaszewski** - *Silnik Detekcji i Narzędzia Danych*
* **Silnik Detekcji:** Współtworzenie logiki klasy `SpeedSignDetector` - implementacja ładowania modelu, zarządzania wagami i post-processingu inferencji.
* **Narzędzia Datasetu:** Projektowanie i programowanie automatycznego ekstraktora klatek (`yt_cut.py`) oraz skryptów mapujących etykiety (Label Resolving).
* **Integracja Komponentów:** Programowanie warstwy komunikacji między backendem detekcji a strukturami danych aplikacji.

### **Oskar Jaworski** - *Architektura Systemu i Przetwarzanie Wielowątkowe*
* **Video Pipeline:** Implementacja wielowątkowego rdzenia przetwarzania wideo (wzorzec Producent-Konsument) w `video_processor.py`.
* **Optymalizacja GPU:** Oprogramowanie mechanizmu **Batch Processing** (kolejkowanie i przesyłanie paczek do VRAM) dla optymalizacji RTX 4090.
* **Refaktoryzacja i GUI:** Scalanie kodu, refaktoryzacja głównej pętli aplikacji oraz implementacja sterowania parametrami w czasie rzeczywistym.

### 🤝 Współpraca Zespołowa
Poza indywidualnymi specjalizacjami, cały zespół wspólnie pracował nad:
* **Tworzenie Datasetu:** Wspólna anotacja, czyszczenie i agregacja zbioru ponad 6,300 zdjęć w Roboflow.
* **Zapewnienie Jakości (QA):** Testowanie całego systemu, debugowanie przypadków brzegowych i weryfikacja dokładności detekcji na rzeczywistych nagraniach z kamer samochodowych.
* **Dokumentacja:** Wspólne przygotowanie dokumentacji technicznej, raportu końcowego oraz tego pliku README.