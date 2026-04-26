# Stable Match Lab v2.3 UI fixed

이 버전은 v2.2 단일 파일 버전의 UI 문제를 개선한 버전입니다.

## 수정 내용

- 상단 버튼이 잘려 보이던 문제 개선
- 게임 메뉴를 스테이지 제목 아래의 명확한 조작 패널로 이동
- 사이드바에 항상 “첫 화면으로 돌아가기” 버튼 추가
- 게임 화면 오른쪽 결과 영역에도 첫 화면 복귀 버튼 추가
- `matching_engine.py`를 사용하지 않는 단일 파일 구조 유지

## 실행

```bash
pip install -r requirements.txt
streamlit run app.py
```

## GitHub 업로드

아래 파일만 올리면 됩니다.

```text
app.py
requirements.txt
README.md
.gitignore
.streamlit/config.toml
```

`matching_engine.py`는 필요하지 않습니다.
