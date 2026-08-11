# GitHub Actions + results.json 자동 업데이트 구조

## 변경 완료된 구조

```text
index.html
/data/results.json
/data/results.csv
/data/last_updated.json
/scripts/update_miniloto.py
/.github/workflows/update-miniloto.yml
```

## 작동 방식

1. 사이트는 먼저 내장 데이터를 로딩합니다.
2. 배포 환경에서는 `./data/results.json`을 자동으로 불러옵니다.
3. GitHub Actions가 매주 화요일 추첨 후 `scripts/update_miniloto.py`를 실행합니다.
4. 새 결과가 있으면 `data/results.json`, `data/results.csv`, `data/last_updated.json`을 갱신하고 자동 커밋합니다.
5. 사이트는 다음 접속/새로고침 때 최신 JSON을 반영합니다.

## 자동 실행 시간

GitHub Actions는 UTC 기준이므로 일본 시간 기준으로 아래처럼 실행됩니다.

| 실행 | 일본 시간 |
|---|---|
| 1차 | 화요일 20:40 JST |
| 2차 | 화요일 22:00 JST |
| 예비 | 수요일 09:10 JST |

## 데이터 소스

스크립트는 아래 순서로 소스를 시도합니다 (전부 묣요, API 키 불필요).

| 순서 | 소스 | 비고 |
|---|---|---|
| ① | 미즈호 공식 페이지 직접 | 은행 보안(Akamai)이 서버 IP를 차단해 현재는 403. 열리면 자동 사용 |
| ② | 공개 백넘버 표 (정적 HTML 직접 파싱) | **주력 소스 — 현재 정상 작동 중** |
| ③ | ②와 같은 표를 읽기 프록시(r.jina.ai) 경유 마크다운 파싱 | ② 차단 시 대비 |
| ④ | `BACKUP_MINILOTO_URL` 시크릿 | 운영자가 설정하면 마지막 예비로 사용 |

특징:
- 당월 표의 **모든 회차**를 파싱하므로, 1~2주 놓쳐도 다음 실행 때 자동 추적(캐치업)됩니다.
- 숫자 범위/중복/개수 검증(validate) 통과분만 저장합니다.
- 중요: 사이트 공개 화면에는 특정 참고 사이트명을 노출하지 않습니다. "구매/환급 전 공식 발표 확인" 문구는 그대로 유지됩니다.

실제 실행 결과 (2026-08-11, 제1398회 추가 성공):

```text
source: backnumber-table
latestDraw: 1398
latestDate: 2026/8/4
changed: true
updatedDraws: [1398]
```

## 중요 운영 원칙

- 공식 미즈호 페이지가 접근 가능해지거나 API 구조를 확인하면 `parse_mizuho_latest()`를 실제 DOM/API에 맞게 보강하세요.
- 백업 소스를 사용할 때도 공개 화면에는 특정 참고 사이트명을 노출하지 말고, "구매/환급 전 공식 발표 확인" 문구를 유지하세요.
- 자동 업데이트 실패 시 GitHub Actions 실패 알림을 확인하세요. (빨간 X 표시 → Run 눌러 로그 확인)

## 로컬 테스트

스크립트 수동 실행:

```bash
python scripts/update_miniloto.py
```

결과 파일 확인:

```bash
cat data/last_updated.json
```

## 배포 방법

1. GitHub 저장소에 전체 파일 업로드
2. Settings → Pages에서 GitHub Pages 활성화
3. Actions 탭에서 `Update Miniloto Results` workflow 활성 확인
4. 필요하면 `workflow_dispatch`로 수동 실행

## 주의: 로컬 file:// 직접 열기

`index.html`을 파일로 직접 열면 브라우저 정책 때문에 `data/results.json` fetch가 막힐 수 있습니다.  
이 경우 내장 데이터 fallback으로 동작합니다.

실제 자동 업데이트를 확인하려면 GitHub Pages 또는 로컬 서버를 사용하세요.

로컬 서버 예:

```bash
python -m http.server 8000
```

접속:

```text
http://localhost:8000/index.html
```


## 비공개 백업 소스 설정

공식 페이지가 자동 요청을 차단할 경우, GitHub 저장소의 Secrets에 `BACKUP_MINILOTO_URL`을 설정하면 스크립트가 해당 URL을 백업 소스로 사용합니다. 이 값은 저장소 파일에 기록되지 않으므로 공개 사이트에 노출되지 않습니다.


---

## 확정 브랜드 / 연락처

- 사이트명: ミニロト分析ナビ / 미니로또 분석 내비
- 도메인: https://miniloto-navi.com/
- 문의 이메일: storykim1980@gmail.com
