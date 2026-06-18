# 양자 뉴스 분석기 (Quantum News Analyzer) 🚀

이 앱은 양자 컴퓨팅(Quantum Computing)과 관련된 뉴스 기사나 주장이 **과장(Hype)**인지 **현실(Reality)**인지 분석해 주는 인공지능 & 양자 알고리즘 기반 웹 애플리케이션입니다.

사용자가 텍스트를 입력하면, 대규모 언어 모델(LLM)이 텍스트의 '기술적 현실성', '타임라인 타당성', '과장 정도'를 수치화합니다. 이후 이 데이터는 Qiskit의 변분 양자 분류기(VQC, Variational Quantum Classifier)를 거쳐 최종적인 "과장 지수(Hype Score)"로 산출됩니다.

---

## 🛠️ 실행 방법 (How to Run)

이 앱을 로컬 환경에서 실행하려면 파이썬(Python 3.8 이상)이 설치되어 있어야 합니다.

### 1. 가상환경 생성 및 종속성 설치
터미널(Terminal) 또는 명령 프롬프트(CMD)를 열고 압축을 푼 폴더로 이동한 뒤, 아래 명령어들을 순서대로 실행합니다.

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. (선택 사항) API 키 설정
실제 AI 모델을 사용하여 텍스트를 분석하려면 Google Gemini API 키가 필요합니다. 
앱 최상단 폴더에 `.env` 파일을 만들고 아래와 같이 입력해 주세요.
```env
GEMINI_API_KEY=여러분의_API_키를_여기에_입력하세요
```
*(주의: API 키를 설정하지 않더라도 'Mock Mode(모의 모드)'로 앱이 정상적으로 작동하여 UI와 양자 회로 동작을 테스트해 볼 수 있습니다!)*

### 3. 서버 실행
모든 준비가 끝났다면 아래 명령어로 FastAPI 서버를 실행합니다:
```bash
uvicorn backend.app:app --reload
```

### 4. 앱 접속
서버가 실행되면 웹 브라우저를 열고 아래 주소로 접속하세요:
👉 **http://127.0.0.1:8000**

멋진 양자 뉴스 분석기를 직접 체험해 보세요!
