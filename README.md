# Stable Match Lab v2.1 fixed

이 버전은 다음 오류를 방지하기 위해 `app.py`와 `matching_engine.py`를 함께 맞춘 수정본입니다.

- 한국 이름 사용
- 선호도 랜덤 변경
- 한국어 UI
- `generate_preferences(..., name_seed=...)` 지원

## 실행

```bash
pip install -r requirements.txt
streamlit run app.py
```

## GitHub 업로드 시 주의

반드시 `app.py`와 `matching_engine.py`를 둘 다 교체하세요.
둘 중 하나만 교체하면 함수 인자 불일치로 오류가 날 수 있습니다.
