# LionScribe Backend

멋사 활동 보고서를 마크다운으로 작성하면 PDF로 변환해주는 서비스의 백엔드.

> 이 레포에는 4단계 챌린지를 위한 결함이 의도적으로 내장되어 있습니다.

## 기술 스택

- Backend: Django 5 + DRF + simplejwt
- 마크다운: `markdown`
- PDF: `weasyprint` (markdown → HTML → PDF). **system 패키지 의존성 있음**
- Project name: `seminar` (작년 가이드와 동일)
- DB: SQLite (로컬) / MySQL (배포)
- WSGI: gunicorn

## weasyprint system 의존성

weasyprint는 OS 수준 라이브러리가 필요. EC2 Ubuntu(또는 로컬 Linux)에서 다음을
먼저 설치하세요. **이 step은 `pip install -r requirements.txt`보다 *먼저***
실행되어야 합니다.

```bash
sudo apt update
sudo apt install -y libpango-1.0-0 libpangoft2-1.0-0 \
    libharfbuzz0b libffi-dev libcairo2 fonts-noto-cjk
```

macOS 로컬은 `brew install pango cairo libffi`.

## 환경변수

- `SECRET_KEY` — Django 시크릿 키
- `CHAOS_TOKEN` — **챌린지 채점기가 백엔드를 죽일 때 사용하는 토큰**. 진행자에게
  발급받은 값을 사용

## 로컬 실행

```bash
# (먼저 위 weasyprint system deps 설치)
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# SECRET_KEY, CHAOS_TOKEN 채움
python manage.py migrate
python manage.py runserver
```

## AWS 배포

**작년 AWS 배포 가이드** ("4. 배포해보자!" 페이지)를 그대로 따라가면 됩니다.
차이점:

- 가이드의 `11th-week-back` → `lionscribe-backend`
- 추가 환경변수: `CHAOS_TOKEN` (`.env`에 추가)
- 추가 requirements 패키지: `markdown`, `weasyprint` (이미 포함)
- **apt 패키지 추가** — 가이드 step "`sudo apt-get install build-essential
  libpq-dev`"와 같은 자리에:
  ```bash
  sudo apt install -y libpango-1.0-0 libpangoft2-1.0-0 \
      libharfbuzz0b libffi-dev libcairo2 fonts-noto-cjk
  ```
- nginx 설정에 `/media/` 경로 static 서빙 추가 (PDF 다운로드용)
- ⚠️ 챌린지 채점기가 `/api/_chaos/restart/`로 백엔드를 강제 종료시킬 수 있다.
  gunicorn systemd 유닛에 `Restart=always`가 `[Service]` 섹션에 *반드시*
  들어가야 함 — 가이드의 systemd unit 파일에 한 줄 추가

## API 요약

| Method | Path | 인증 | 설명 |
|---|---|---|---|
| POST | `/api/auth/signup/` | X | 회원가입 |
| POST | `/api/auth/login/` | X | JWT 발급 |
| GET | `/api/users/me/` | O | 본인 정보 |
| GET | `/api/jobs/` | O | 내 작업 목록 |
| POST | `/api/jobs/` | O | 작업 제출. `{ title, input_text }`. 즉시 pending |
| GET | `/api/jobs/<id>/` | O | 작업 상태 + PDF URL (완료 시) |
| POST | `/api/_chaos/restart/` | (X-Chaos-Token) | 챌린지 채점기 전용 — 백엔드 강제 종료 |
