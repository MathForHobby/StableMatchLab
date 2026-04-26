# Stable Match Lab v2.2 single-file fixed

이 버전은 `matching_engine.py`와 `app.py`의 버전 불일치로 생기는 오류를 방지하기 위해 핵심 로직을 `app.py` 안에 모두 포함한 단일 파일 안정화 버전입니다.

## 반영된 기능

- 선호도 랜덤 변경
- M1, W1 대신 한국 이름 사용
- 한국어 UI
- 안정 매칭 / 최적 안정 매칭 / Gale-Shapley 챌린지

## 실행

```bash
pip install -r requirements.txt
streamlit run app.py
```

## GitHub 업로드 시 권장

가장 안전한 방법은 저장소의 기존 `.py` 파일을 정리하고 아래 파일들만 남기는 것입니다.

```text
app.py
requirements.txt
README.md
.gitignore
.streamlit/config.toml
```

`matching_engine.py`는 더 이상 필요하지 않습니다.
