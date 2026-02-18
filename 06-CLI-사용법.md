# 제6장 CLI 사용법

## 6.1 개요

본 시스템은 그래픽 사용자 인터페이스(GUI) 외에 명령줄 인터페이스(CLI)를 통한 실행을 지원합니다. CLI 진입점은 `main/restoration_workflow.py` 스크립트이며, 이 스크립트는 손상 영역 검출, 레이저 커팅 레이아웃 생성, 복원 가이드 생성의 전체 파이프라인을 GUI 없이 순차적으로 실행합니다.

CLI 실행 방식은 다음과 같은 환경에서 특히 유용합니다.

- 디스플레이가 연결되지 않은 원격 서버 환경
- 다수의 작품을 일괄 처리하는 배치 작업
- 자동화 스크립트 또는 CI/CD 파이프라인과의 연동
- 재현 가능한 처리 조건의 명시적 기록이 필요한 학술 연구

전체 워크플로우는 다음의 세 단계로 구성됩니다.

1. **검출(Detection)**: `extract_whiteness_based.py`를 호출하여 입력 이미지에서 손상 영역을 검출하고, 개별 SVG 벡터 파일을 생성합니다.
2. **레이아웃(Layout)**: `create_cutting_layout.py`를 호출하여 검출된 조각들을 지정 용지 크기에 자동 배치합니다.
3. **가이드(Guide)**: `create_restoration_guide.py`를 호출하여 원본 이미지 위에 번호가 부여된 복원 위치 가이드를 생성합니다.

각 단계는 `--skip-detection`, `--skip-layout`, `--skip-guide` 옵션을 통해 개별적으로 생략할 수 있으며, 하위 모듈을 독립적으로 실행하는 것도 가능합니다.

---

## 6.2 기본 사용법

가장 기본적인 실행 형태는 입력 이미지 경로와 출력 디렉토리 경로를 지정하는 것입니다.

```bash
python main/restoration_workflow.py \
  --input "datasets/document.tif" \
  --output-dir "results/document"
```

상기 명령은 다음의 작업을 순차적으로 수행합니다.

1. `datasets/document.tif` 파일에서 손상 영역을 자동 검출합니다.
2. 검출된 조각들을 A4 용지 크기의 레이저 커팅 레이아웃으로 배치합니다.
3. 원본 이미지 위에 번호가 표시된 복원 가이드를 생성합니다.
4. 모든 결과물을 `results/document/` 디렉토리 하위에 저장합니다.

입력 이미지는 `--input` 옵션으로 단일 파일을 지정하거나, `--multi-images` 옵션으로 분할 스캔된 다수의 파일을 지정할 수 있습니다. 두 옵션 중 하나는 반드시 제공하여야 합니다.

---

## 6.3 전체 옵션 참조

### 6.3.1 입출력 옵션

| 옵션 | 기본값 | 설명 |
|------|--------|------|
| `--input` | (필수*) | 입력 한국화 이미지 파일 경로입니다. 단일 이미지 모드에서 사용합니다. |
| `--output-dir` | (필수) | 모든 결과물이 저장될 출력 디렉토리 경로입니다. |
| `--multi-images` | -- | 분할 스캔 모드에서 사용할 다수의 이미지 파일 경로 목록입니다. |
| `--layout` | `3x1` | 분할 이미지의 타일 배치 구성입니다 (예: `3x1`, `2x2`). |

(*) `--input` 또는 `--multi-images` 중 하나는 반드시 지정하여야 합니다.

### 6.3.2 검출 파라미터

| 옵션 | 기본값 | 설명 |
|------|--------|------|
| `--method` | `whiteness` | 검출 방법입니다. `whiteness`, `lab_b`, `hsv`, `lab_a` 중 선택합니다. |
| `--threshold` | `138` | LAB b 채널 임계값입니다. 값이 낮을수록 검출 기준이 엄격해집니다. |
| `--threshold-loose` | `145` | 간극 채움(gap filling)용 완화 임계값입니다. |
| `--hsv-saturation` | `30` | HSV 채도 임계값입니다. 채도(S)가 이 값 미만인 픽셀을 흰색 후보로 판정합니다. |
| `--hsv-value` | `200` | HSV 명도 임계값입니다. 명도(V)가 이 값을 초과하는 픽셀을 흰색 후보로 판정합니다. |
| `--min-area` | `100` | 최소 손상 영역 면적 (픽셀 단위)입니다. 이 값 미만의 영역은 무시됩니다. |
| `--max-area` | `500000` | 최대 손상 영역 면적 (픽셀 단위)입니다. 이 값 초과의 영역은 무시됩니다. |
| `--svg-simplify` | `0.1` | SVG 윤곽선 단순화 수준입니다. 값이 클수록 꼭짓점 수가 감소합니다. |

### 6.3.3 번호 부여 파라미터

| 옵션 | 기본값 | 설명 |
|------|--------|------|
| `--numbering-method` | `grid` | 번호 부여 방법입니다. `grid`, `row`, `column`, `simple` 중 선택합니다. |
| `--numbering-grid-size` | `500` | 그리드 기반 번호 부여 시 그리드 셀 크기 (픽셀 단위)입니다. |
| `--numbering-direction` | `ltr_ttb` | 번호 부여 방향입니다. `ltr_ttb`(좌상단 기준), `rtl_ttb`, `ttb_ltr`, `ttb_rtl` 중 선택합니다. |

### 6.3.4 레이아웃 파라미터

| 옵션 | 기본값 | 설명 |
|------|--------|------|
| `--paper-size` | `A4` | 출력 용지 크기입니다. `A4`, `A3`, `B4`, `B5`, `A2`, `A1` 중 선택합니다. |
| `--paper-width` | -- | 사용자 정의 용지 너비 (mm 단위)입니다. 지정 시 `--paper-size`를 무시합니다. |
| `--paper-height` | -- | 사용자 정의 용지 높이 (mm 단위)입니다. |
| `--paper-margin` | `10` | 용지 여백 (mm 단위)입니다. |
| `--sort-strategy` | `area` | 조각 정렬 전략입니다. `area`, `height`, `width`, `perimeter`, `maxside`, `none` 중 선택합니다. |
| `--allow-rotation` | 비활성 | 조각의 90도 회전 배치를 허용합니다. |
| `--external-numbers` | 활성 | 번호를 조각 외부에 표시합니다. (기본 동작) |
| `--internal-numbers` | 비활성 | 번호를 조각 내부에 표시합니다. |

### 6.3.5 워크플로우 제어 옵션

| 옵션 | 기본값 | 설명 |
|------|--------|------|
| `--skip-detection` | 비활성 | 검출 단계를 생략하고 기존 결과를 사용합니다. |
| `--skip-layout` | 비활성 | 레이아웃 생성 단계를 생략합니다. |
| `--skip-guide` | 비활성 | 복원 가이드 생성 단계를 생략합니다. |

---

## 6.4 사용 예시

### 6.4.1 기본 단일 이미지 처리

```bash
python main/restoration_workflow.py \
  --input "datasets/1첩/w_0001.tif" \
  --output-dir "results/1첩/w_0001"
```

모든 옵션을 기본값으로 사용하여 전체 파이프라인을 실행합니다.

### 6.4.2 사용자 정의 파라미터 지정

```bash
python main/restoration_workflow.py \
  --input "datasets/1첩/w_0001.tif" \
  --output-dir "results/1첩/w_0001" \
  --method hsv \
  --hsv-saturation 25 \
  --hsv-value 210 \
  --min-area 200 \
  --max-area 300000 \
  --paper-size A3 \
  --sort-strategy height \
  --allow-rotation
```

HSV 기반 검출 방법을 사용하고, 임계값과 면적 범위를 조정하며, A3 용지에 높이순 정렬과 회전 배치를 허용하여 실행합니다.

### 6.4.3 분할 스캔 이미지 처리 (3x1 레이아웃)

```bash
python main/restoration_workflow.py \
  --multi-images \
    "datasets/2첩/scan_left.tif" \
    "datasets/2첩/scan_center.tif" \
    "datasets/2첩/scan_right.tif" \
  --layout 3x1 \
  --output-dir "results/2첩/merged"
```

3장의 분할 스캔 이미지를 좌에서 우로 3x1 배치로 합친 후 전체 파이프라인을 실행합니다. 타일 경계에 걸친 손상 영역은 자동으로 병합됩니다.

### 6.4.4 기존 검출 결과 재사용

```bash
python main/restoration_workflow.py \
  --input "datasets/1첩/w_0001.tif" \
  --output-dir "results/1첩/w_0001" \
  --skip-detection
```

이전에 실행된 검출 결과가 출력 디렉토리에 존재하는 경우, 검출 단계를 생략하고 레이아웃 및 가이드 생성만 수행합니다. 레이아웃 파라미터를 변경하여 재실행할 때 유용합니다.

### 6.4.5 검출만 실행

```bash
python main/restoration_workflow.py \
  --input "datasets/1첩/w_0001.tif" \
  --output-dir "results/1첩/w_0001" \
  --skip-layout \
  --skip-guide
```

손상 영역 검출만 수행하고 레이아웃 및 가이드 생성을 생략합니다.

### 6.4.6 레이아웃만 재생성

```bash
python main/restoration_workflow.py \
  --input "datasets/1첩/w_0001.tif" \
  --output-dir "results/1첩/w_0001" \
  --skip-detection \
  --skip-guide \
  --paper-size A3 \
  --allow-rotation
```

기존 검출 결과를 사용하여 A3 용지 기준의 레이아웃만 재생성합니다.

### 6.4.7 가이드만 재생성

```bash
python main/restoration_workflow.py \
  --input "datasets/1첩/w_0001.tif" \
  --output-dir "results/1첩/w_0001" \
  --skip-detection \
  --skip-layout
```

기존 검출 결과와 레이아웃을 유지한 채 복원 가이드만 재생성합니다.

---

## 6.5 개별 모듈 실행

통합 워크플로우(`restoration_workflow.py`)를 사용하지 않고, 각 하위 모듈을 독립적으로 실행할 수 있습니다. 이 방식은 파이프라인의 특정 단계에 대해 세밀한 제어가 필요한 경우에 적합합니다.

### 6.5.1 extract_whiteness_based.py -- 손상 영역 검출

본 모듈은 입력 이미지에서 손상 영역을 검출하고, 개별 SVG 벡터 파일과 시각화 이미지를 생성합니다.

```bash
python main/extract_whiteness_based.py \
  --input "datasets/1첩/w_0001.tif" \
  --output-dir "results/1첩/w_0001/detection" \
  --method whiteness \
  --hsv-saturation 30 \
  --hsv-value 200 \
  --min-area 100 \
  --max-area 500000 \
  --crop-document \
  --corner-method edges \
  --export-svg \
  --svg-simplify 0.1 \
  --svg-individual \
  --numbering-method grid \
  --numbering-grid-size 500 \
  --numbering-direction ltr_ttb
```

주요 옵션은 다음과 같습니다.

| 옵션 | 기본값 | 설명 |
|------|--------|------|
| `--input` | (필수) | 입력 이미지 파일 경로입니다. |
| `--output-dir` | `results/whiteness` | 결과 출력 디렉토리입니다. |
| `--method` | `auto_color` | 검출 방법입니다. `whiteness`, `lab_b`, `hsv`, `lab_a`, `auto_color`, `combined` 중 선택합니다. |
| `--crop-document` | 비활성 | 작품 영역을 자동으로 감지하여 배경을 제거합니다. |
| `--corner-method` | `edges` | 작품 경계 감지 방법입니다. `edges`, `contours` 중 선택합니다. |
| `--export-svg` | 비활성 | 검출 결과를 SVG 벡터 파일로 내보냅니다. |
| `--svg-simplify` | `1.0` | SVG 경로 단순화 수준입니다. |
| `--svg-individual` | 비활성 | 각 손상 영역을 개별 SVG 파일로 저장합니다. |
| `--svg-unified` | 활성 | 모든 손상 영역을 단일 SVG 파일로 통합 저장합니다. |
| `--svg-dpi` | `300` | SVG 변환 시 사용할 DPI 값입니다. |
| `--enhance-holes` | 비활성 | 팽창 연산을 통해 검출된 영역을 확장합니다. |
| `--dilation-size` | `5` | 팽창 연산 커널 크기입니다. |
| `--hole-color` | -- | 구멍 색상을 HEX 값으로 직접 지정합니다 (예: `#DBCFBF`). |
| `--color-tolerance` | `12` | 색상 허용 오차입니다. |

### 6.5.2 create_cutting_layout.py -- 레이저 커팅 레이아웃 생성

본 모듈은 개별 SVG 파일들을 읽어 지정 용지 크기에 자동 배치하는 레이저 커팅 레이아웃을 생성합니다.

```bash
python main/create_cutting_layout.py \
  --svg-dir "results/1첩/w_0001/detection/svg_vectors" \
  --output-dir "results/1첩/w_0001/cutting_layout" \
  --paper-size A4 \
  --paper-margin 10 \
  --sort-strategy area \
  --stroke-width 0.1 \
  --external-numbers
```

주요 옵션은 다음과 같습니다.

| 옵션 | 기본값 | 설명 |
|------|--------|------|
| `--svg-dir` | (필수) | 개별 SVG 파일이 저장된 디렉토리 경로입니다. |
| `--output-dir` | `cutting_layout` | 레이아웃 결과 출력 디렉토리입니다. |
| `--paper-size` | `A4` | 출력 용지 크기입니다. `A4`, `A3`, `B4`, `B5`, `A2`, `A1` 중 선택합니다. |
| `--paper-width` | -- | 사용자 정의 용지 너비 (mm)입니다. |
| `--paper-height` | -- | 사용자 정의 용지 높이 (mm)입니다. |
| `--paper-margin` | `10` | 용지 여백 (mm)입니다. |
| `--scale` | `1.0` | 전체 조각에 적용할 배율입니다. |
| `--scale-config` | -- | 개별 조각 배율 설정 JSON 파일 경로입니다. |
| `--stroke-width` | `0.1` | SVG 선 두께 (mm)입니다. |
| `--sort-strategy` | `area` | 조각 정렬 전략입니다. |
| `--allow-rotation` | 비활성 | 90도 회전 배치를 허용합니다. |
| `--label-space` | `0` | 레이블을 위한 추가 여백 (mm)입니다. |
| `--use-nfp` | 비활성 | NFP(No-Fit Polygon) 알고리즘을 사용하여 공간 활용도를 향상시킵니다. |

### 6.5.3 create_restoration_guide.py -- 복원 가이드 생성

본 모듈은 원본 이미지 위에 각 손상 영역의 위치와 번호를 오버레이한 복원 가이드를 생성합니다.

```bash
python main/create_restoration_guide.py \
  --image "datasets/1첩/w_0001.tif" \
  --svg-dir "results/1첩/w_0001/detection/svg_vectors" \
  --output-dir "results/1첩/w_0001/restoration_guide"
```

주요 옵션은 다음과 같습니다.

| 옵션 | 기본값 | 설명 |
|------|--------|------|
| `--image` | (필수) | 원본 입력 이미지 파일 경로입니다. |
| `--svg` | -- | 통합 SVG 파일 경로입니다 (모든 손상 영역이 포함된 단일 파일). |
| `--svg-dir` | -- | 개별 SVG 파일이 저장된 디렉토리 경로입니다. `--svg` 또는 `--svg-dir` 중 하나를 지정합니다. |
| `--output-dir` | `restoration_guide` | 가이드 결과 출력 디렉토리입니다. |
| `--scale` | `1.0` | 미리보기 배율입니다. |
| `--scale-config` | -- | 개별 조각 배율 설정 JSON 파일 경로입니다. |

---

## 6.6 배치 처리

다수의 작품을 연속적으로 처리해야 하는 경우, `main/batch_process_all.py` 스크립트를 사용할 수 있습니다.

```bash
python main/batch_process_all.py
```

본 스크립트는 `datasets/` 디렉토리 하위의 모든 첩(1첩~8첩)에 포함된 TIFF 이미지를 자동으로 탐색하여 순차적으로 처리합니다. 주요 동작 특성은 다음과 같습니다.

- **자동 탐색**: `datasets/` 하위 디렉토리에서 `.tif` 확장자의 파일을 자동으로 수집합니다.
- **이미 처리된 파일 건너뛰기**: 출력 디렉토리에 `restoration_guide.png` 파일이 이미 존재하는 경우 해당 이미지의 처리를 생략합니다.
- **특별 케이스 처리**: 코드 내 `SPECIAL_CASES` 딕셔너리에 등록된 이미지에 대해서는 개별 임계값을 적용합니다.
- **타임아웃**: 단일 이미지당 최대 600초(10분)의 처리 시간 제한이 적용됩니다.
- **중간 저장**: 10개 이미지를 처리할 때마다 중간 결과를 `results/batch_processing_results.json` 파일에 저장합니다.
- **결과 요약**: 처리 완료 후 성공/실패/건너뛰기/타임아웃별 통계와 총 검출 구멍 수, 평균 처리 시간 등의 요약 정보를 출력합니다.

배치 처리의 기본 설정을 변경하고자 하는 경우, `batch_process_all.py` 파일 상단의 다음 상수를 수정합니다.

```python
DATASETS_DIR = "datasets"    # 입력 데이터셋 디렉토리
RESULTS_DIR = "results"      # 결과 출력 디렉토리
THRESHOLD = 138              # 기본 임계값
PAPER_SIZE = "A4"            # 기본 용지 크기
```

---

## 6.7 출력 디렉토리 구조

`restoration_workflow.py`를 실행하면 지정된 `--output-dir` 하위에 다음과 같은 디렉토리 구조가 생성됩니다.

### 6.7.1 단일 이미지 모드

```
{output-dir}/
  +-- detection/
  |     +-- document_boundary.png         # 작품 경계 감지 결과 시각화
  |     +-- comparison.png                # 손상 영역 검출 전후 비교 이미지
  |     +-- holes_combined.svg            # 모든 손상 영역을 포함하는 통합 SVG 파일
  |     +-- svg_vectors/                  # 개별 SVG 파일 디렉토리
  |           +-- hole_001.svg            # 1번 손상 영역의 벡터 윤곽선
  |           +-- hole_002.svg            # 2번 손상 영역의 벡터 윤곽선
  |           +-- ...
  +-- cutting_layout/
  |     +-- cutting_layout_page_1.svg     # 1페이지 레이저 커팅 레이아웃
  |     +-- cutting_layout_page_2.svg     # 2페이지 레이저 커팅 레이아웃 (필요 시)
  |     +-- ...
  |     +-- cutting_layout_info.json      # 레이아웃 메타데이터 (배치 정보, 페이지 수 등)
  +-- restoration_guide/
        +-- restoration_guide.png         # 번호가 표시된 상세 복원 가이드 이미지
        +-- simple_overlay.png            # 간략 번호 오버레이 이미지
        +-- piece_locations.csv           # 각 조각의 좌표 데이터 (CSV 형식)
```

### 6.7.2 분할 이미지 모드 (multi-images)

분할 이미지 모드에서는 상기 구조에 추가로 다음의 디렉토리가 생성됩니다.

```
{output-dir}/
  +-- merged/
  |     +-- merged_image.tif              # 분할 이미지를 합친 결과 이미지
  +-- detection/
  |     +-- holes_info.json               # 검출 결과 JSON (경계 병합 정보 포함)
  |     +-- ...
  +-- cutting_layout/
  |     +-- ...
  +-- restoration_guide/
        +-- ...
```

### 6.7.3 주요 출력 파일 설명

| 파일 | 형식 | 용도 |
|------|------|------|
| `holes_combined.svg` | SVG | 모든 손상 영역의 벡터 윤곽선을 단일 파일로 통합한 것입니다. 전체 현황 확인용입니다. |
| `hole_NNN.svg` | SVG | 개별 손상 영역의 벡터 윤곽선입니다. 레이아웃 생성의 입력으로 사용됩니다. |
| `cutting_layout_page_N.svg` | SVG | 레이저 커터에 직접 입력 가능한 커팅 레이아웃입니다. |
| `cutting_layout_info.json` | JSON | 각 조각의 배치 위치, 페이지 번호, 원본 크기 등의 메타데이터입니다. |
| `restoration_guide.png` | PNG | 원본 이미지 위에 각 조각의 번호와 위치를 표시한 가이드 이미지입니다. |
| `piece_locations.csv` | CSV | 각 조각의 중심 좌표, 경계 상자, 면적 등의 수치 데이터입니다. |

---

## 6.8 종료 코드 및 오류 처리

### 6.8.1 종료 코드

`restoration_workflow.py`는 실행 결과에 따라 다음의 종료 코드를 반환합니다.

| 종료 코드 | 의미 |
|-----------|------|
| `0` | 전체 워크플로우가 정상적으로 완료되었습니다. |
| `1` | 검출 단계에서 오류가 발생하여 워크플로우가 중단되었습니다. 또는 SVG 파일이 존재하지 않습니다. |

검출 단계의 오류는 워크플로우를 즉시 중단시키나, 레이아웃 생성 또는 가이드 생성 단계의 오류는 경고 메시지를 출력한 후 나머지 단계를 계속 진행합니다.

### 6.8.2 일반적 오류 유형 및 대응 방법

**입력 파일을 찾을 수 없는 경우**

```
Error: Cannot load image: datasets/missing_file.tif
```

지정한 입력 이미지 경로가 올바른지 확인합니다. 한글이 포함된 경로도 지원되나, 파일 시스템의 인코딩 설정에 따라 문제가 발생할 수 있습니다.

**SVG 파일이 생성되지 않은 경우**

```
Error: No SVG files found in results/document/detection/svg_vectors
Please run hole detection first or check the output directory
```

검출 단계에서 유효한 손상 영역이 발견되지 않았거나, `--skip-detection` 옵션을 사용하였으나 이전 검출 결과가 존재하지 않는 경우에 발생합니다. 임계값 파라미터를 조정하거나 검출 단계를 다시 실행합니다.

**검출 결과가 과도하게 적은 경우**

임계값이 지나치게 엄격하게 설정되었을 가능성이 있습니다. `--hsv-saturation` 값을 높이거나 `--hsv-value` 값을 낮추어 검출 감도를 완화합니다. 또한 `--min-area` 값을 줄여 소면적 손상 영역의 검출을 허용할 수 있습니다.

**검출 결과가 과도하게 많은 경우**

배경 잡음이나 얼룩이 손상 영역으로 오검출되고 있을 가능성이 있습니다. `--hsv-saturation` 값을 낮추거나 `--hsv-value` 값을 높여 검출 기준을 강화합니다. `--min-area` 값을 높여 미세 영역을 제외하는 것도 효과적입니다.

**메모리 부족 오류**

초고해상도 이미지(267MP 이상)를 처리할 때 발생할 수 있습니다. 시스템의 가용 메모리를 확인하고, 필요한 경우 이미지를 분할하여 `--multi-images` 옵션으로 처리하는 것을 권장합니다.

**배치 처리 시 타임아웃**

`batch_process_all.py`는 단일 이미지당 600초의 타임아웃을 적용합니다. 이 시간을 초과하는 이미지는 `timeout` 상태로 기록되며, 해당 이미지에 대해서는 입력 해상도를 줄이거나 파라미터를 조정하여 개별적으로 재처리할 것을 권장합니다.
