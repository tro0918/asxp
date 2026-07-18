# Agent Skill Exchange Protocol 0.1 구현 명세

문서 상태: 공개 검토용 초안(Draft)  
프로토콜 식별자: `ASXP/0.1`  
기준일: 2026-07-13

이 문서는 에이전트의 재사용 가능한 instruction과 tool contract를 다른 에이전트로 이전하고, 선택적으로 원본 에이전트에 동기화·위임하는 상호운용 규칙을 정의한다. ASXP는 현재 공인 표준화 기구가 채택한 표준이 아니라 구현 가능한 오픈 프로토콜 제안이다.

`MUST`, `MUST NOT`, `SHOULD`, `SHOULD NOT`, `MAY`는 RFC 2119 및 RFC 8174의 의미로 사용한다.

## 1. 범위

ASXP가 표준화하는 항목은 다음과 같다.

1. portable `skill.md` 문서 형식
2. skill export, import, activation 상태 전이
3. tool contract의 host runtime 평탄화
4. sibling/origin 기반 Re-sync
5. 선택적 agent-to-agent delegation
6. registry publish, resolve, revoke API
7. digest, JWS 서명, JWKS 기반 출처 검증
8. 권한·개인정보·순환 호출 제어

ASXP는 모델 API, 추론 방식, RAG 구현, UI, billing 정책을 규정하지 않는다.

## 2. 역할과 식별자

| 용어 | 정의 |
|---|---|
| Exporter | 에이전트 정의를 `skill.md`로 생성하는 구현체 |
| Importer | `skill.md`를 검증·저장·활성화하는 구현체 |
| Host agent | 가져온 skill을 instruction/tool로 실행하는 에이전트 |
| Origin agent | 원본 skill과 비공개 지식을 보유한 에이전트 |
| Registry | immutable release를 저장·resolve·revoke하는 서비스 |
| Snapshot | origin 연결이 없는 정적 import |
| Linked skill | origin URI와 revision을 보존한 import |

Skill ID는 다음 URI 형식을 권장한다.

```text
asxp://<publisher>/<skill-name>
```

예: `asxp://example.org/refund-policy`

Skill release는 `(id, version, revision)`으로 식별한다. 동일한 revision의 bytes는 변경될 수 없다.

## 3. 적합성 프로필

구현체는 아래 프로필 중 지원 범위를 선언해야 한다.

| 프로필 | 필수 기능 |
|---|---|
| Core | `skill.md` parse/export/import, validation, inline instruction, tool flattening |
| Linked | Core + origin, revision, conditional Re-sync |
| Delegating | Linked + delegated task 요청과 cycle/depth 제어 |
| Registry | release publish/resolve/revoke, digest, JWS, JWKS |

예:

```json
{
  "protocol": "ASXP/0.1",
  "profiles": ["core", "linked", "delegating"]
}
```

## 4. Portable skill 문서

### 4.1 파일과 media type

- 권장 파일명: `<name>.skill.md` 또는 `SKILL.md`
- 문자 인코딩: UTF-8
- media type: `application/vnd.asxp.skill+markdown;version=0.1`
- 구조: YAML scalar frontmatter + Markdown body
- 최대 권장 크기: 256 KiB

### 4.2 최소 유효 문서

```yaml
---
name: refund-policy
description: 주문의 환불 가능 여부와 수수료를 판단할 때 사용하는 스킬.
asxp-version: 0.1
version: 1.0.0
ae-tools-json: '[]'
---

# Refund policy

주문 번호, 수령일, 개봉 여부를 확인하세요.
```

### 4.3 Frontmatter 필드

| 필드 | 타입 | 필수 | 제약/의미 |
|---|---:|---:|---|
| `name` | scalar string | MUST | `^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$` |
| `description` | scalar string | MUST | 1~4096자, 사용 시점 포함 |
| `asxp-version` | scalar string | MUST | 본 명세에서는 `0.1` |
| `version` | scalar string | MUST | SemVer |
| `ae-tools-json` | JSON string | MUST | 한 줄 JSON array, 최대 128개 |
| `id` | URI string | SHOULD | stable skill URI |
| `revision` | string | Linked MUST | immutable revision 또는 digest |
| `publisher` | string/URI | SHOULD | 발행자 식별자 |
| `license` | string | SHOULD | SPDX expression |
| `permissions` | space-separated string | SHOULD | 활성화에 필요한 permission 목록 |
| `privacy` | enum | SHOULD | `local`, `delegated`, `external` |
| `origin-url` | HTTPS URI | Linked MUST | Re-sync metadata endpoint |
| `delegation-url` | HTTPS URI | Delegating MUST | delegated task endpoint |
| `signing-key-id` | string | Signed release SHOULD | JWKS의 `kid` |
| `homepage` | HTTPS URI | MAY | 설명·지원 페이지 |
| `extensions-json` | JSON string | MAY | namespaced extension object |

Frontmatter 값은 호환성을 위해 scalar만 사용한다. 배열과 객체는 JSON 문자열 또는 공백 구분 문자열로 표현한다. 알 수 없는 `x-*` 필드는 round-trip 시 보존해야 한다.

### 4.4 Tool contract

`ae-tools-json`의 각 항목은 다음 구조를 사용한다.

```json
{
  "name": "lookup_order",
  "description": "주문 상태를 조회한다.",
  "kind": "http",
  "inputSchema": {
    "type": "object",
    "properties": {
      "order_id": { "type": "string" }
    },
    "required": ["order_id"],
    "additionalProperties": false
  },
  "outputSchema": {
    "type": "object",
    "properties": {
      "status": { "type": "string" }
    },
    "required": ["status"]
  },
  "binding": {
    "url": "https://api.example.org/orders/lookup",
    "method": "POST"
  },
  "permissions": ["orders.read"]
}
```

필수 필드는 `name`, `description`, `inputSchema`이다. `kind`는 `function`, `http`, `mcp`, `booking`, `mock` 중 하나다. 구현체 전용 kind는 `x-<vendor>-<kind>`를 사용한다.

Credential은 binding에 포함할 수 없다. Importer가 자신의 credential store에서 permission과 endpoint를 기준으로 주입해야 한다.

### 4.5 Canonical manifest

서명과 registry wire format에서는 `skill.md`를 다음 JSON으로 변환한다.

```json
{
  "protocolVersion": "0.1",
  "id": "asxp://example.org/refund-policy",
  "name": "refund-policy",
  "description": "주문의 환불 가능 여부와 수수료를 판단할 때 사용하는 스킬.",
  "version": "1.0.0",
  "revision": "sha256:7e91c4d8...",
  "publisher": "example.org",
  "privacy": "delegated",
  "permissions": ["orders.read", "refunds.evaluate"],
  "instructions": "# Refund policy\n...",
  "tools": [],
  "origin": {
    "url": "https://agents.example.org/v1/skills/refund-policy",
    "delegationUrl": "https://agents.example.org/v1/delegations"
  }
}
```

Canonical bytes는 RFC 8785 JSON Canonicalization Scheme을 사용한다. Digest는 canonical bytes의 SHA-256을 다음과 같이 표현한다.

```text
sha256:<64 lowercase hex characters>
```

## 5. 상태 모델

Importer는 각 skill에 대해 다음 상태를 관리한다.

```text
ABSENT ──import──> STAGED ──approve──> ENABLED
                     │                    │
                     ├──reject──> ABSENT  ├──disable──> DISABLED
                     │                    │
                     └──invalid──> ERROR  └──revoke───> REVOKED

ENABLED/DISABLED ──sync──> STAGED_UPDATE ──approve──> ENABLED
```

| 상태 | 의미 |
|---|---|
| `STAGED` | parse와 schema 검증 완료, 사용자/정책 승인 전 |
| `ENABLED` | instructions와 tools가 runtime에 노출됨 |
| `DISABLED` | 설치되어 있으나 runtime에는 노출되지 않음 |
| `STAGED_UPDATE` | 새 revision 검증 완료, 권한 차이 검토 중 |
| `ERROR` | 유효성 또는 서명 검증 실패 |
| `REVOKED` | registry/publisher에 의해 폐기됨 |

Importer는 새 permission, 외부 endpoint 또는 privacy 수준 증가가 있는 업데이트를 자동 활성화하면 안 된다.

## 6. Export 알고리즘

Exporter는 다음 순서를 따라야 한다.

1. agent 정의에서 재사용 가능한 instruction만 추출한다.
2. 공개 가능한 tool contract를 ASXP tool schema로 변환한다.
3. permission과 privacy를 계산한다.
4. knowledge file, conversation, credential, hidden host policy를 제거한다.
5. `skill.md`를 생성하고 재-parse한다.
6. schema validation과 secret scan을 실행한다.
7. canonical manifest와 digest를 계산한다.
8. linked export라면 origin과 immutable revision을 붙인다.
9. signed release라면 detached JWS를 생성한다.

Exporter는 다음 정보를 포함하면 안 된다.

- API key, OAuth token, cookie, password, private certificate
- LINE/Slack 등 channel credential
- raw RAG 문서, embedding, private index
- 사용자 대화 기록과 개인정보
- host의 숨겨진 system policy
- 공개가 승인되지 않은 내부 endpoint

## 7. Import 및 활성화 알고리즘

Importer는 다음 순서를 따라야 한다.

1. 문서 크기와 UTF-8을 확인한다.
2. frontmatter와 Markdown body를 분리한다.
3. 필수 필드와 protocol major version을 확인한다.
4. `ae-tools-json`을 parse하고 JSON Schema를 검증한다.
5. URL을 검증하고 SSRF 정책을 적용한다.
6. signed release라면 digest와 JWS를 검증한다.
7. publisher, permissions, privacy, endpoints를 사용자에게 표시한다.
8. local policy와 사용자 승인을 적용한다.
9. 충돌 없는 runtime tool name을 생성한다.
10. origin이 있으면 sync metadata를 저장한다.
11. 활성화 후 audit event를 기록한다.

Tool 이름 충돌 시 다음 규칙을 권장한다.

```text
<skill-name>__<tool-name>
```

Importer는 기존 tool을 조용히 덮어쓰면 안 된다.

## 8. Runtime 결합

### 8.1 Instruction injection

활성화된 skill body는 host의 skill instruction 영역에 삽입한다.

```text
Host policy
  > User instruction
    > Imported skill instruction
```

Imported skill은 host policy를 변경하거나 자신의 permission을 확대할 수 없다.

### 8.2 Tool flattening

활성화된 tool은 host의 native tool representation으로 변환한다. 모든 호출은 실행 전에 input schema와 permission을 검사한다. 출력 schema가 있으면 결과도 검사해야 한다.

권장 실행 envelope:

```json
{
  "tool": "refund-policy__lookup_order",
  "arguments": {"order_id": "ORD-2048"},
  "skill": "asxp://example.org/refund-policy",
  "revision": "sha256:7e91c4d8...",
  "idempotencyKey": "01J2...",
  "traceId": "tr_01J2..."
}
```

## 9. Re-sync

파일/텍스트 import는 origin이 없으므로 snapshot이며 Re-sync를 지원하지 않는다. Sibling/origin import는 `id`, `origin-url`, `revision`을 저장한다.

```http
GET /v1/skills/example.org/refund-policy?version=latest HTTP/1.1
Host: registry.example.org
Accept: application/json
If-None-Match: "sha256:7e91c4d8..."
```

변경이 없으면:

```http
HTTP/1.1 304 Not Modified
ETag: "sha256:7e91c4d8..."
```

새 release가 있으면 `200 SignedRelease`를 반환한다. Importer는 digest/signature를 검증하고 installed manifest와 다음 항목을 비교해야 한다.

- 추가/삭제된 permissions
- 추가/변경된 tool endpoint
- privacy 수준 변화
- origin/delegation URL 변화
- publisher 또는 signing key 변화
- instruction 변경

Material change가 있으면 `STAGED_UPDATE`로 전환한다.

## 10. Agent delegation

Linked skill에 `delegation-url`이 있으면 host는 다음 로컬 tool을 합성할 수 있다.

```text
ask_<safe-skill-name>
```

이 tool은 exported `tools[]`에 포함하지 않는다. origin 연결에서 파생되는 runtime binding이다.

### 10.1 요청

```http
POST /v1/delegations HTTP/1.1
Host: agents.example.org
Authorization: Bearer <audience-bound-token>
Content-Type: application/json
Idempotency-Key: 01J2D7MM4G3V4JQ8ME9Y0MFA2B
```

```json
{
  "skill": "asxp://example.org/refund-policy",
  "revision": "sha256:7e91c4d8...",
  "task": "원본 약관 12조의 예외 조건을 확인한다.",
  "artifacts": [],
  "traceId": "tr_01J2D7...",
  "parentTraceId": "tr_01J2D6...",
  "maxDepth": 3,
  "visited": [
    "asxp://host.example/ops-agent@rev-19"
  ],
  "dataClasses": ["order.metadata"],
  "consentToken": "<short-lived-purpose-bound-token>"
}
```

### 10.2 동기 응답

```http
HTTP/1.1 200 OK
Content-Type: application/json
```

```json
{
  "traceId": "tr_01J2D7...",
  "output": {
    "answer": "약관 12조 예외는 위생 밀봉 상품, 주문 제작 상품, 디지털 콘텐츠다.",
    "confidence": "source-grounded"
  },
  "artifacts": [],
  "usage": {"delegations": 1}
}
```

### 10.3 비동기 응답

```http
HTTP/1.1 202 Accepted
Location: /v1/operations/op_01J2D7
Retry-After: 2
```

```json
{"id":"op_01J2D7","status":"queued"}
```

Client는 `GET /v1/operations/{operationId}`로 상태를 조회한다. 상태는 `queued`, `running`, `succeeded`, `failed`, `cancelled` 중 하나다.

### 10.4 순환 호출 방지

Origin은 다음 중 하나면 요청을 거절해야 한다.

- `maxDepth`가 0
- 자신의 `(skill id, revision)`이 `visited`에 이미 존재
- 동일 idempotency key의 완료 요청을 다시 실행하려는 경우
- host policy가 허용한 시간·비용·payload 한도 초과

권장 기본 최대 depth는 3이다.

## 11. Registry API

상세 OpenAPI는 `spec/openapi.yaml`을 따른다.

| Method | Path | 목적 | Scope |
|---|---|---|---|
| `POST` | `/v1/skills` | immutable release publish | `skill.publish` |
| `GET` | `/v1/skills/{publisher}/{name}` | release resolve/fetch | public 또는 registry 정책 |
| `PUT` | `/v1/skills/{publisher}/{name}/releases/{revision}/revocation` | release revoke | `skill.revoke` |
| `POST` | `/v1/delegations` | delegated task 실행 | `skill.delegate` |
| `GET` | `/v1/operations/{operationId}` | 비동기 작업 조회 | `skill.delegate` |
| `GET` | `/.well-known/jwks.json` | public signing keys | public |

Publish body:

```json
{
  "manifest": {"protocolVersion":"0.1","name":"refund-policy"},
  "digest": "sha256:<64 hex>",
  "signature": "<protected-header>..<signature>"
}
```

Registry는 release를 immutable하게 저장해야 한다. `latest` 같은 mutable tag를 제공할 수 있지만 응답에는 반드시 실제 immutable revision과 digest를 포함한다.

## 12. 인증, 서명, 신뢰

### 12.1 Transport authorization

- 모든 외부 endpoint는 TLS를 사용해야 한다.
- Registry write 및 delegation은 OAuth 2.1 계열 authorization을 사용한다.
- 권장 scope: `skill.publish`, `skill.revoke`, `skill.delegate:<skill-id>`
- Access token은 `skill.md`에 저장할 수 없다.
- Consent token은 audience, purpose, data class, expiry에 묶여야 한다.

### 12.2 Detached JWS

서명 대상은 RFC 8785 canonical manifest bytes다. Detached compact JWS를 사용한다.

```text
BASE64URL(protected-header)..BASE64URL(signature)
```

Protected header 예:

```json
{"alg":"EdDSA","kid":"publisher-2026-01","typ":"ASXP+JWS"}
```

초기 상호운용 알고리즘은 `EdDSA`(Ed25519)와 `ES256`이다. `alg=none`은 금지한다. Public key는 publisher 또는 registry의 HTTPS JWKS에서 조회한다.

서명 검증 순서:

1. allowlist에서 `alg` 확인
2. `kid`로 JWK 선택
3. canonical manifest bytes로 signature 검증
4. SHA-256 digest 재계산 및 비교
5. publisher identity와 key trust policy 확인
6. revocation 상태 확인

유효한 서명은 무결성과 key possession만 증명하며 skill의 안전성을 증명하지 않는다.

## 13. 오류 모델

HTTP 오류는 `application/problem+json`을 사용한다.

```json
{
  "type": "https://asxp.org/problems/delegation-cycle",
  "title": "Delegation cycle detected",
  "status": 409,
  "detail": "The target skill is already present in visited.",
  "traceId": "tr_01J2D7..."
}
```

표준 error code:

| Code | HTTP | 의미 |
|---|---:|---|
| `invalid_document` | 400 | frontmatter/Markdown parse 실패 |
| `schema_validation_failed` | 422 | manifest/tool schema 불일치 |
| `unsupported_protocol` | 400 | 지원하지 않는 major version |
| `signature_invalid` | 401 | JWS/digest 검증 실패 |
| `publisher_untrusted` | 403 | trust policy에서 발행자 거부 |
| `permission_denied` | 403 | 필요한 scope/consent 없음 |
| `skill_not_found` | 404 | skill/release 없음 |
| `revision_conflict` | 409 | immutable revision content 충돌 |
| `delegation_cycle` | 409 | visited에 target 존재 |
| `depth_exceeded` | 422 | maxDepth 소진 |
| `release_revoked` | 410 | release 폐기됨 |
| `payload_too_large` | 413 | 크기 제한 초과 |
| `rate_limited` | 429 | 호출 제한 초과 |
| `origin_unavailable` | 503 | origin agent 사용 불가 |

## 14. 보안 요구사항

Importer/Host는 최소한 다음을 구현해야 한다.

- prompt injection을 host policy보다 낮은 우선순위로 격리
- tool input/output schema 검증
- credential을 model-visible context와 분리
- local, loopback, link-local URL에 대한 SSRF 방어
- instruction, schema, request, response 크기 제한
- timeout, rate limit, cost limit
- idempotency, trace, audit log
- delegation depth와 visited cycle detection
- 민감 데이터 redaction과 최소 전송
- 즉시 skill disable과 release revoke 처리

Delegation 시 전체 대화를 보내면 안 된다. 현재 task 수행에 필요한 최소 excerpt와 artifact reference만 전송해야 한다.

## 15. Audit event

권장 audit event 구조:

```json
{
  "time": "2026-07-13T12:34:56Z",
  "event": "asxp.skill.activated",
  "actor": "user:123",
  "hostAgent": "agent:ops-assistant",
  "skill": "asxp://example.org/refund-policy",
  "revision": "sha256:7e91c4d8...",
  "permissions": ["orders.read", "refunds.evaluate"],
  "traceId": "tr_01J2D7...",
  "result": "success"
}
```

권장 event 이름:

- `asxp.skill.exported`
- `asxp.skill.imported`
- `asxp.skill.approved`
- `asxp.skill.activated`
- `asxp.skill.disabled`
- `asxp.skill.synced`
- `asxp.skill.revoked`
- `asxp.tool.called`
- `asxp.delegation.created`
- `asxp.delegation.completed`
- `asxp.policy.denied`

## 16. 호환성 매핑

| ASXP | Anthropic-style SKILL.md | ai-plugin.json | OpenAPI |
|---|---|---|---|
| `name` | `name` | `name_for_model` | `info.title` 부분 매핑 |
| `description` | `description` | `description_for_model` | `info.description` |
| `instructions` | Markdown body | 직접 필드 없음 | 직접 필드 없음 |
| `tools[]` | `ae-tools-json` 확장 | `api.url`을 통해 간접 표현 | operations + schemas |
| `permissions` | 확장 | `auth` 부분 매핑 | security schemes 부분 매핑 |
| `origin` | 확장 | `api.url`과 의미가 다름 | server URL과 의미가 다름 |
| `revision/signature` | 확장 | 직접 필드 없음 | 직접 필드 없음 |
| `delegation` | 확장 | 직접 필드 없음 | custom operation으로 표현 가능 |

변환기는 손실 필드를 반드시 보고해야 한다. 특히 ASXP에서 plugin manifest로 변환하면 inline instructions, sync, provenance, delegation 의미가 확장 없이 손실된다.

## 17. 최소 적합성 테스트

Core 구현체는 다음 테스트를 통과해야 한다.

1. 최소 유효 `skill.md` parse 성공
2. UTF-8 BOM 문서 parse 성공
3. 필수 필드 누락 거부
4. 잘못된 `ae-tools-json` 거부
5. tool input schema가 object가 아니면 거부
6. 128개 초과 tool 거부
7. HTTP origin/delegation URL 거부
8. credential 유사 frontmatter 필드 거부
9. tool name 충돌 시 기존 tool 비덮어쓰기
10. unknown `x-*` field round-trip 보존

Linked/Delegating/Registry 구현체는 추가로 다음을 검사한다.

11. ETag 일치 시 `304` 처리
12. permission 증가 업데이트 승인 대기
13. 동일 idempotency key 중복 실행 방지
14. delegation cycle 거부
15. maxDepth 0 요청 거부
16. 잘못된 digest/JWS 거부
17. revoked release 활성화 거부
18. JWKS key rotation 시 `kid` 기준 검증

## 18. 버전 진화

- `asxp-version`은 protocol version이다.
- `version`은 skill release version이다.
- Minor protocol version은 optional field를 추가할 수 있다.
- Major protocol version은 의미를 변경할 수 있다.
- Reader는 지원하지 않는 major version을 거부해야 한다.
- Reader는 알 수 없는 optional extension을 가능한 한 보존해야 한다.

## 19. Normative artifacts

이 저장소에서 기계 판독 가능한 명세는 다음 파일이다.

- `schemas/skill-manifest.schema.json`
- `schemas/tool.schema.json`
- `spec/openapi.yaml`
- `examples/customer-support.skill.md`
- `examples/linked-policy.skill.md`

문서와 schema가 충돌하면 `0.1` 초안에서는 JSON Schema와 OpenAPI를 wire validation의 기준으로 사용하고, 충돌을 명세 issue로 기록한다.
