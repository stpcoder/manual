# 제9장 API 레퍼런스

## 9.1 개요

본 장은 시스템의 각 모듈이 제공하는 공개(public) 함수 및 클래스의 인터페이스를 기술합니다. 각 항목에 대해 함수 시그니처, 매개변수 설명, 반환값 명세를 포함합니다.

## 9.2 코어 계층 API

### 9.2.1 Detector 클래스

소스 파일: gui_app/src/core/detector.py

Detector는 알고리즘 계층의 함수들을 감싸는 래퍼 클래스입니다. GUI와 알고리즘 사이의 어댑터 역할을 수행합니다.

#### Detector.auto_extract_color()

```python
@staticmethod
def auto_extract_color(image_path: str, image: numpy.ndarray = None) -> str
```

이미지에서 손상 부위(구멍)의 대표 색상을 자동으로 추출합니다. 이미지의 상위 1% 밝기 픽셀을 분석하여 대표 색상을 결정합니다.

매개변수:
- image_path (str): 이미지 파일 경로. image 매개변수가 None인 경우 이 경로에서 이미지를 로드합니다.
- image (numpy.ndarray, 선택적): BGR 형식의 이미지 배열. 제공 시 파일 로드를 생략합니다.

반환값:
- str: 16진수 색상 문자열 (예: "#DBCFBF")

#### Detector.detect()

```python
def detect(
    self,
    image_path: str,
    hsv_saturation: int = 30,
    hsv_value: int = 200,
    min_area: int = 100,
    max_area: int = 500000,
    progress_callback: callable = None
) -> tuple[list[dict], list[str]]
```

기본 HSV 색공간 기반으로 손상 부위를 검출합니다.

매개변수:
- image_path (str): 입력 이미지 파일 경로
- hsv_saturation (int): HSV 채도(S) 임계값. 이 값 미만의 채도를 가진 픽셀이 후보로 선택됩니다. 기본값 30.
- hsv_value (int): HSV 밝기(V) 임계값. 이 값 초과의 밝기를 가진 픽셀이 후보로 선택됩니다. 기본값 200.
- min_area (int): 최소 면적 필터. 이 값 미만의 면적을 가진 윤곽선은 제거됩니다. 단위: 제곱 픽셀. 기본값 100.
- max_area (int): 최대 면적 필터. 이 값 초과의 면적을 가진 윤곽선은 제거됩니다. 단위: 제곱 픽셀. 기본값 500000.
- progress_callback (callable, 선택적): 진행률 콜백 함수. f(percent: int, message: str) 형식.

반환값:
- tuple[list[dict], list[str]]: (holes, svg_paths) 튜플.
  - holes: Hole Dict 리스트. 각 요소는 id, bbox, area, center, contour 필드를 포함합니다.
  - svg_paths: 각 구멍에 대응하는 SVG path 문자열 리스트.

#### Detector.detect_with_filters()

```python
def detect_with_filters(
    self,
    image_path: str,
    filter_settings: dict = None,
    min_area: int = 100,
    max_area: int = 500000,
    boundary_detection: bool = True,
    progress_callback: callable = None
) -> tuple[list[dict], list[str]]
```

사용자 정의 필터 설정 또는 학습된 GMM 모델을 기반으로 손상 부위를 검출합니다. GMM 모델이 학습된 상태인 경우 Mahalanobis 거리 기반 분류를 우선 적용합니다.

매개변수:
- image_path (str): 입력 이미지 파일 경로
- filter_settings (dict, 선택적): Filter Settings Dict. None인 경우 기본 필터 설정을 사용합니다.
- min_area (int): 최소 면적 필터. 기본값 100.
- max_area (int): 최대 면적 필터. 기본값 500000.
- boundary_detection (bool): 작품 경계 검출 사용 여부. 기본값 True.
- progress_callback (callable, 선택적): 진행률 콜백 함수.

반환값:
- tuple[list[dict], list[str]]: detect()와 동일한 형식.

#### Detector.analyze_regions()

```python
def analyze_regions(
    self,
    image_path: str,
    bg_boxes: Union[tuple, list],
    fg_boxes: Union[tuple, list]
) -> dict
```

사용자가 지정한 다수의 배경(구멍) 영역과 전경(그림) 영역의 색상 분포를 분석하여 GMM 모델을 학습하고, 각 채널별 최적 임계값을 계산합니다.

매개변수:
- image_path (str): 입력 이미지 파일 경로
- bg_boxes (tuple 또는 list): 배경 영역 좌표. 단일 (x1, y1, x2, y2) 튜플 또는 해당 튜플의 리스트.
- fg_boxes (tuple 또는 list): 전경 영역 좌표. 형식은 bg_boxes와 동일합니다.

반환값:
- dict: Analysis Results Dict. 각 채널(S, L, b 등)에 대해 threshold, condition, separation, bg_mean, bg_std, fg_mean, fg_std를 포함합니다.

부수 효과:
- 내부의 _region_model 속성에 GMM 모델이 저장됩니다. 이후 detect_with_filters() 호출 시 이 모델이 자동으로 적용됩니다.

#### Detector.get_mask()

```python
def get_mask(self) -> numpy.ndarray
```

가장 최근 검출에서 생성된 이진 마스크를 반환합니다.

반환값:
- numpy.ndarray: uint8 단일 채널 이진 마스크. 값 0(배경) 또는 255(손상 부위).

#### Detector.get_boundary()

```python
def get_boundary(self) -> numpy.ndarray
```

가장 최근 검출에서 감지된 작품 경계 윤곽선을 반환합니다.

반환값:
- numpy.ndarray 또는 None: 작품 경계 윤곽선. 경계가 감지되지 않은 경우 None.

## 9.3 알고리즘 계층 API

### 9.3.1 extract_whiteness_based 모듈

소스 파일: main/extract_whiteness_based.py

#### detect_whiteness()

```python
def detect_whiteness(
    image: numpy.ndarray,
    method: str = 'hsv',
    s_threshold: int = 30,
    v_threshold: int = 200,
    b_threshold: int = 138,
    whiteness_threshold: float = 0.85,
    detect_boundary: bool = True,
    progress_callback: callable = None
) -> tuple[numpy.ndarray, dict]
```

이미지에서 손상 부위(흰색/밝은 영역)를 검출하여 이진 마스크를 생성합니다.

매개변수:
- image (numpy.ndarray): BGR 형식의 입력 이미지
- method (str): 검출 방법. 'hsv', 'lab_b', 'whiteness', 'auto_color' 중 하나. 기본값 'hsv'.
- s_threshold (int): HSV 채도 임계값. 기본값 30.
- v_threshold (int): HSV 밝기 임계값. 기본값 200.
- b_threshold (int): LAB b 채널 임계값. 기본값 138.
- whiteness_threshold (float): Whiteness Score 임계값. 기본값 0.85.
- detect_boundary (bool): 작품 경계 검출 사용 여부. 기본값 True.
- progress_callback (callable, 선택적): 진행률 콜백 함수.

반환값:
- tuple[numpy.ndarray, dict]:
  - numpy.ndarray: uint8 이진 마스크
  - dict: 진단 데이터 (사용된 방법, 임계값, 통계 등)

#### extract_individual_holes()

```python
def extract_individual_holes(
    image: numpy.ndarray,
    mask: numpy.ndarray,
    min_area: int = 100,
    max_area: int = 500000,
    boundary: numpy.ndarray = None
) -> list[dict]
```

이진 마스크에서 개별 손상 부위를 추출합니다.

매개변수:
- image (numpy.ndarray): BGR 형식의 원본 이미지
- mask (numpy.ndarray): uint8 이진 마스크
- min_area (int): 최소 면적 필터. 기본값 100.
- max_area (int): 최대 면적 필터. 기본값 500000.
- boundary (numpy.ndarray, 선택적): 작품 경계 윤곽선. 제공 시 경계 외부의 윤곽선을 제거합니다.

반환값:
- list[dict]: Hole Dict 리스트. 각 요소는 id, bbox, area, center, contour를 포함합니다.

#### contour_to_svg_path()

```python
def contour_to_svg_path(
    contour: numpy.ndarray,
    scale_factors: dict = None,
    simplification: float = 0.1
) -> str
```

OpenCV 윤곽선을 SVG path 문자열로 변환합니다.

매개변수:
- contour (numpy.ndarray): OpenCV 형식의 윤곽선 배열 (N, 1, 2)
- scale_factors (dict, 선택적): {'x': float, 'y': float} 형식의 스케일 계수. 제공 시 좌표를 실제 밀리미터로 변환합니다.
- simplification (float): Ramer-Douglas-Peucker 단순화 계수. 기본값 0.1.

반환값:
- str: SVG path의 d 속성 값 문자열

#### detect_document_boundary()

```python
def detect_document_boundary(image: numpy.ndarray) -> dict
```

스캔 이미지에서 실제 작품 영역의 경계를 자동으로 감지합니다.

매개변수:
- image (numpy.ndarray): BGR 형식의 입력 이미지

반환값:
- dict: 경계 정보. contour(윤곽선), mask(경계 마스크) 등을 포함합니다.

### 9.3.2 spatial_numbering 모듈

소스 파일: main/spatial_numbering.py

#### assign_spatial_numbers()

```python
def assign_spatial_numbers(
    holes: list[dict],
    method: str = 'grid',
    grid_size: int = 500,
    direction: str = 'ltr_ttb',
    start_number: int = 1
) -> list[dict]
```

검출된 손상 부위에 공간적 위치 기반 번호를 부여합니다.

매개변수:
- holes (list[dict]): Hole Dict 리스트. 각 요소에 bbox 또는 center 필드가 필요합니다.
- method (str): 번호 부여 방식. 'grid'(격자 기반), 'row'(행 기반), 'column'(열 기반). 기본값 'grid'.
- grid_size (int): 격자 셀 크기. 단위: 픽셀. 기본값 500.
- direction (str): 정렬 방향. 'ltr_ttb'(좌상단에서 우하단), 'rtl_ttb', 'ttb_ltr', 'ttb_rtl'. 기본값 'ltr_ttb'.
- start_number (int): 시작 번호. 기본값 1.

반환값:
- list[dict]: 각 요소의 id 필드가 갱신된 Hole Dict 리스트.

#### cluster_by_grid()

```python
def cluster_by_grid(
    holes: list[dict],
    grid_size: int = 500
) -> list[list[dict]]
```

구멍을 격자 셀 단위로 그룹핑합니다.

매개변수:
- holes (list[dict]): Hole Dict 리스트
- grid_size (int): 격자 셀 크기. 기본값 500.

반환값:
- list[list[dict]]: 격자 셀별로 그룹핑된 이중 리스트.

### 9.3.3 create_cutting_layout 모듈

소스 파일: main/create_cutting_layout.py

#### BinPacker2D 클래스

```python
class BinPacker2D:
    def __init__(self, width: float, height: float)
```

Skyline Bin Packing 알고리즘을 구현하는 클래스입니다.

생성자 매개변수:
- width (float): 용지 유효 너비 (mm)
- height (float): 용지 유효 높이 (mm)

주요 메서드:
- pack_piece(piece_width, piece_height) -> tuple 또는 None: 조각을 배치하고 (x, y) 좌표를 반환합니다. 배치 불가능 시 None을 반환합니다.

#### pack_pieces_to_pages()

```python
def pack_pieces_to_pages(
    pieces: list,
    paper_size: str = 'A4',
    margin: float = 10.0,
    spacing: float = 1.5,
    sort_strategy: str = 'area',
    allow_rotation: bool = False
) -> list
```

다수의 조각을 다중 페이지에 걸쳐 배치합니다.

매개변수:
- pieces (list): 조각 데이터 리스트
- paper_size (str): 용지 크기 프리셋. 기본값 'A4'.
- margin (float): 여백. 단위: mm. 기본값 10.0.
- spacing (float): 조각 간 간격. 단위: mm. 기본값 1.5.
- sort_strategy (str): 정렬 전략. 'area'(면적순). 기본값 'area'.
- allow_rotation (bool): 회전 허용 여부. 기본값 False.

반환값:
- list: 페이지별 배치 데이터 리스트.

### 9.3.4 create_restoration_guide 모듈

소스 파일: main/create_restoration_guide.py

#### create_restoration_guide()

```python
def create_restoration_guide(
    image: numpy.ndarray,
    holes: list[dict],
    output_path: str
) -> None
```

원본 이미지 위에 손상 부위 번호를 오버레이한 복원 가이드 이미지를 생성합니다.

매개변수:
- image (numpy.ndarray): BGR 형식의 원본 이미지
- holes (list[dict]): Hole Dict 리스트 (id, center 필드 필요)
- output_path (str): 출력 파일 경로

반환값:
- None

### 9.3.5 auto_threshold 모듈

소스 파일: main/auto_threshold.py

#### analyze_image_colors()

```python
def analyze_image_colors(image: numpy.ndarray) -> dict
```

이미지의 색상 분포를 분석하여 통계 데이터를 반환합니다.

매개변수:
- image (numpy.ndarray): BGR 형식의 입력 이미지

반환값:
- dict: 채널별 통계 데이터 (평균, 표준편차, 히스토그램 등)

#### get_threshold_recommendation()

```python
def get_threshold_recommendation(analysis: dict) -> dict
```

색상 분석 결과를 기반으로 최적 검출 임계값을 추천합니다.

매개변수:
- analysis (dict): analyze_image_colors()의 반환값

반환값:
- dict: 채널별 추천 임계값 및 신뢰도

### 9.3.6 restoration_workflow 모듈

소스 파일: main/restoration_workflow.py

CLI 전용 모듈로서 argparse를 통해 명령줄 인자를 처리하고, 검출-레이아웃-가이드 전체 파이프라인을 순차적으로 실행합니다. CLI 사용법은 제6장을 참조합니다.

## 9.4 GUI 계층 위젯 API

### 9.4.1 SVGOverlayViewer 클래스

소스 파일: gui_app/src/widgets/svg_overlay_viewer.py

부모 클래스: QGraphicsView

시그널:
- color_picked(str): 아이드로퍼로 추출된 16진수 색상 문자열
- hole_clicked(int): 클릭된 구멍의 인덱스
- region_selected(int, tuple): (선택 모드, (x1, y1, x2, y2)) 영역 좌표
- area_selected(int, int): (선택 모드, 면적) 면적 선택 결과
- deselect_area_selected(tuple): (x1, y1, x2, y2) 선택 해제 영역

주요 메서드:
- load_image(path: str) -> numpy.ndarray: 이미지를 로드하고 표시합니다.
- set_holes(holes: list, svg_paths: list) -> None: SVG 오버레이를 표시합니다.
- set_hole_active(index: int, active: bool) -> None: 개별 구멍의 활성/비활성 상태를 설정합니다.
- zoom_to_hole_id(hole_id: int) -> None: 지정된 번호의 구멍으로 화면을 이동합니다.
- fit_to_window() -> None: 이미지를 뷰 크기에 맞춥니다.
- start_region_selection(mode: int) -> None: 영역 선택 모드를 시작합니다.

### 9.4.2 LayoutViewer 클래스

소스 파일: gui_app/src/widgets/layout_viewer.py

부모 클래스: QWidget

시그널:
- layout_changed(): 레이아웃이 변경됨
- loading_started(): 레이아웃 계산 시작
- loading_finished(): 레이아웃 계산 완료

주요 메서드:
- set_holes(holes: list, svg_paths: list) -> None: 구멍 데이터를 설정하고 레이아웃을 실행합니다.
- export_layout_images(output_folder: str) -> None: 300 DPI PNG 파일로 내보냅니다.
- export_layout_svg(output_folder: str) -> None: SVG 벡터 파일로 내보냅니다.
- get_layout_data() -> dict: 레이아웃 메타데이터를 반환합니다.
- get_failed_pieces() -> list: 배치 실패한 조각 번호 리스트를 반환합니다.

### 9.4.3 ControlPanel 클래스

소스 파일: gui_app/src/widgets/control_panel.py

부모 클래스: QWidget

시그널:
- image_loaded(str): 이미지 파일 경로
- run_detection(): 검출 실행 요청
- save_requested(): 저장 요청
- select_background(): 배경 영역 선택 모드 진입
- select_foreground(): 전경 영역 선택 모드 진입
- analyze_regions(): 영역 분석 요청
- apply_filter(): 필터 적용 요청
- select_min_area(): 최소 면적 선택 모드 진입
- select_max_area(): 최대 면적 선택 모드 진입

### 9.4.4 FilterPanel 클래스

소스 파일: gui_app/src/widgets/filter_panel.py

부모 클래스: QWidget

주요 메서드:
- get_filter_settings() -> dict: 현재 필터 설정을 Filter Settings Dict 형식으로 반환합니다.
- set_filter_settings(settings: dict) -> None: 필터 설정을 적용합니다.
- set_model_status(has_model: bool, n_bg: int, n_fg: int) -> None: GMM 모델 상태를 표시합니다.

## 9.5 Worker 클래스 API

### 9.5.1 DetectionWorker 클래스

소스 파일: gui_app/src/workers/detection_worker.py

부모 클래스: QThread

시그널:
- finished(list, list): (holes, svg_paths) 검출 완료
- error(str): 오류 메시지
- progress(int, str): (백분율, 메시지) 진행률

### 9.5.2 AnalysisWorker 클래스

소스 파일: gui_app/src/workers/analysis_worker.py

부모 클래스: QThread

시그널:
- finished(dict): 분석 결과 (Analysis Results Dict)
- error(str): 오류 메시지
