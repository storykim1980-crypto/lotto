# Cloudflare Pages에 `miniloto-navi.com` 배포하는 방법

대상 사이트: **ミニロト分析ナビ / 미니로또 분석 내비**  
도메인: **miniloto-navi.com**  
문의 이메일: **storykim1980@gmail.com**

아래는 초보자 기준으로 처음부터 따라 하는 순서입니다.

---

## 0. 전체 구조 이해하기

이 사이트는 서버 프로그램이 아니라 정적 사이트입니다.

```text
사용자 브라우저
  ↓
Cloudflare Pages
  ↓
index.html + data/results.json 표시
```

자동 업데이트는 GitHub Actions가 합니다.

```text
매주 화요일 추첨 후
  ↓
GitHub Actions 실행
  ↓
data/results.json 갱신
  ↓
GitHub에 자동 커밋
  ↓
Cloudflare Pages가 자동 재배포
  ↓
사이트 최신 데이터 반영
```

---

## 1. GitHub 저장소 만들기

### 1-1. GitHub 접속

```text
https://github.com/
```

### 1-2. 새 저장소 만들기

오른쪽 위 `+` 버튼 클릭 → `New repository`

추천 저장소 이름:

```text
miniloto-navi
```

### 1-3. 공개/비공개 선택

추천:

```text
Private
```

이유:

- 업데이트 스크립트와 운영 파일을 공개하지 않아도 됨
- Cloudflare Pages는 private repository도 연결 가능
- GitHub Actions 무료 한도 안에서 충분히 사용 가능

단, public으로 해도 사이트 운영 자체는 가능합니다.

---

## 2. 필요한 파일 업로드

현재 남겨둔 운영 파일 전체를 GitHub 저장소에 업로드합니다.

필수 파일:

```text
index.html
data/results.json
data/results.csv
data/last_updated.json
scripts/update_miniloto.py
scripts/build_site.py
.github/workflows/update-miniloto.yml
AUTO_UPDATE_GUIDE.md
MINILOTO_USER_MANUAL.md
DEPLOY_CHECKLIST.md
TEST_REPORT.md
CLOUDFLARE_PAGES_SETUP.md
```

### 중요

Cloudflare에는 전체 저장소를 그대로 공개하지 않습니다.  
`scripts/build_site.py`가 `public` 폴더를 만들고 아래 파일만 배포합니다.

```text
public/index.html
public/data/results.json
public/data/results.csv
public/data/last_updated.json
public/robots.txt
public/sitemap.xml
public/_headers
```

즉, 내부 스크립트와 문서는 웹사이트 방문자에게 노출되지 않습니다.

---

## 3. Cloudflare Pages 프로젝트 만들기

### 3-1. Cloudflare 접속

```text
https://dash.cloudflare.com/
```

### 3-2. 메뉴 이동

왼쪽 메뉴에서:

```text
Workers & Pages
```

또는:

```text
Compute → Workers & Pages
```

Cloudflare 화면은 시기에 따라 메뉴명이 조금 다를 수 있습니다.

### 3-3. Create application 클릭

```text
Create application
```

### 3-4. Pages 선택

```text
Pages
```

### 3-5. Connect to Git 선택

```text
Connect to Git
```

### 3-6. GitHub 연결

Cloudflare가 GitHub 접근 권한을 요청합니다.

선택:

```text
Only select repositories
```

그리고 방금 만든 저장소 선택:

```text
miniloto-navi
```

---

## 4. 빌드 설정 입력

Cloudflare Pages 설정에서 아래처럼 입력합니다.

| 항목 | 입력값 |
|---|---|
| Project name | `miniloto-navi` |
| Production branch | `main` |
| Framework preset | `None` |
| Build command | `python3 scripts/build_site.py` |
| Build output directory | `public` |
| Root directory | 비워둠 |

### 만약 `python3` 명령이 실패하면

Build command를 아래로 바꿔서 다시 시도하세요.

```text
python scripts/build_site.py
```

---

## 5. 첫 배포 실행

설정 완료 후:

```text
Save and Deploy
```

을 누릅니다.

처음 배포가 성공하면 임시 주소가 생깁니다.

예:

```text
https://miniloto-navi.pages.dev
```

이 주소로 먼저 사이트가 잘 보이는지 확인합니다.

---

## 6. 도메인 연결하기: miniloto-navi.com

### 6-1. 도메인을 Cloudflare에 추가

Cloudflare 메인 화면에서:

```text
Add a domain
```

입력:

```text
miniloto-navi.com
```

### 6-2. 네임서버 변경

Cloudflare가 네임서버 2개를 알려줍니다.

예:

```text
xxxx.ns.cloudflare.com
yyyy.ns.cloudflare.com
```

도메인을 구매한 곳에서 네임서버를 Cloudflare가 알려준 값으로 변경합니다.

도메인 구매처 예:

```text
お名前.com
ムームードメイン
Xserverドメイン
Namecheap
Cloudflare Registrar
```

네임서버 반영은 보통 몇 분~24시간 걸릴 수 있습니다.

---

## 7. Cloudflare Pages에 커스텀 도메인 추가

Cloudflare Pages 프로젝트로 이동:

```text
Workers & Pages → miniloto-navi → Custom domains
```

클릭:

```text
Set up a custom domain
```

입력:

```text
miniloto-navi.com
```

추가로 이것도 연결 추천:

```text
www.miniloto-navi.com
```

Cloudflare가 DNS를 자동으로 만들어줄 수 있습니다.

---

## 8. SSL 확인

Cloudflare에서 SSL이 자동 적용됩니다.

정상 주소:

```text
https://miniloto-navi.com
```

브라우저 주소창에 자물쇠가 보이면 정상입니다.

---

## 9. GitHub Actions 자동 업데이트 설정

이미 이 파일이 있습니다.

```text
.github/workflows/update-miniloto.yml
```

자동 실행 시간:

| 실행 | 일본 시간 |
|---|---|
| 1차 | 화요일 20:40 |
| 2차 | 화요일 22:00 |
| 예비 | 수요일 09:10 |

---

## 10. 비공개 백업 소스 설정

공식 페이지가 자동 요청을 차단할 수 있습니다.  
이 경우 GitHub Secrets에 백업 URL을 비공개로 넣을 수 있습니다.

GitHub 저장소에서:

```text
Settings → Secrets and variables → Actions → New repository secret
```

Name:

```text
BACKUP_MINILOTO_URL
```

Value:

```text
운영자가 사용하는 비공개 백업 데이터 URL
```

주의:

- 이 값은 공개 파일에 저장되지 않습니다.
- 사이트 방문자에게 보이지 않습니다.
- GitHub Actions 안에서만 사용됩니다.

---

## 11. 자동 업데이트가 잘 되는지 확인

GitHub 저장소에서:

```text
Actions → Update Miniloto Results
```

들어갑니다.

수동 실행:

```text
Run workflow
```

성공하면 아래 파일이 갱신될 수 있습니다.

```text
data/results.json
data/results.csv
data/last_updated.json
```

Cloudflare Pages는 GitHub에 변경이 생기면 자동으로 다시 배포합니다.

---

## 12. Cloudflare Pages 무료로 충분한가?

현재 사이트는 정적 사이트라서 Cloudflare Pages 무료 플랜으로 충분합니다.

현재 사이트 특징:

```text
로그인 없음
결제 없음
DB 없음
정적 HTML/JSON
이미지 거의 없음
업데이트는 GitHub Actions
```

따라서 초기 운영 비용은 거의 도메인 비용뿐입니다.

---

## 13. 문의 이메일 표시

현재 푸터에는 아래 이메일이 표시됩니다.

```text
storykim1980@gmail.com
```

더 전문적으로 보이게 하려면 Cloudflare Email Routing으로 아래 주소를 만들 수 있습니다.

```text
contact@miniloto-navi.com
info@miniloto-navi.com
```

이 주소로 온 메일을 Gmail로 전달할 수 있습니다.

추천:

```text
contact@miniloto-navi.com → storykim1980@gmail.com
```

---

## 14. Cloudflare Email Routing 설정 방법

Cloudflare에서 도메인 선택:

```text
miniloto-navi.com
```

메뉴:

```text
Email → Email Routing
```

활성화 후:

```text
Custom address: contact@miniloto-navi.com
Destination: storykim1980@gmail.com
```

Gmail에서 확인 메일을 승인하면 됩니다.

---

## 15. 최종 확인 체크리스트

배포 후 아래를 확인하세요.

- [ ] `https://miniloto-navi.com` 접속 가능
- [ ] 일본어 기본 화면 표시
- [ ] 최신 결과 표시
- [ ] 당첨금 표시
- [ ] CSV/JSON 다운로드 작동
- [ ] 번호 생성 작동
- [ ] 당첨 확인 작동
- [ ] 모바일 화면 확인
- [ ] 공식 발표 확인 버튼 작동
- [ ] 문의 이메일 표시
- [ ] GitHub Actions 수동 실행 성공
- [ ] Cloudflare Pages 자동 재배포 성공

---

## 16. 문제가 생겼을 때

### 사이트가 404로 나옴

확인:

```text
Build output directory = public
Build command = python3 scripts/build_site.py
```

### 도메인이 연결 안 됨

확인:

```text
도메인 네임서버가 Cloudflare로 바뀌었는지
Custom domains에 miniloto-navi.com을 추가했는지
```

### 자동 업데이트가 안 됨

확인:

```text
GitHub Actions가 활성화되어 있는지
BACKUP_MINILOTO_URL secret이 필요한지
scripts/update_miniloto.py 실행 로그에 에러가 있는지
```

### 최신 데이터가 안 바뀜

확인:

```text
data/results.json이 갱신되었는지
Cloudflare Pages가 재배포되었는지
브라우저 새로고침을 했는지
```

---

## 추천 운영 방식

처음에는 이 구조로 충분합니다.

```text
GitHub private repo
Cloudflare Pages 무료
miniloto-navi.com 도메인
GitHub Actions 자동 업데이트
Cloudflare Email Routing 문의메일
```

트래픽이 늘거나 회원/결제 기능을 추가할 때만 유료 서버를 검토하면 됩니다.
