---
name: mvc-skeleton
description: 새 파이썬 프로젝트를 처음 구성하거나, 파이썬 프로젝트에 MVC(Model-View-Controller) 디렉터리/파일 구조를 만들어달라고 요청받았을 때 사용한다. "MVC 스켈레톤 만들어줘", "MVC 구조로 초기화해줘", "새 프로젝트 세팅해줘" 같은 요청에 반응한다.
---

# MVC 스켈레톤 생성

파이썬 프로젝트에 아래의 `app` 패키지 기반 MVC 디렉터리/파일 구조를 생성한다.
각 파일은 빈 stub 수준으로 작성하며, 주석은 넣지 않는다.

## 생성 절차

1. 현재 작업 디렉터리를 프로젝트 루트로 간주한다.
2. 아래 목록에 있는 파일이 이미 존재하는지 먼저 확인한다.
   - 이미 존재하는 파일이 하나라도 있으면 어떤 파일이 충돌하는지 사용자에게
     알리고, 덮어쓸지 건너뛸지 확인받는다. 확인 없이 기존 파일을 덮어쓰지 않는다.
3. 존재하지 않는 파일들을 아래 내용 그대로 생성한다.
4. 생성이 끝나면 만들어진 디렉터리/파일 목록을 사용자에게 간단히 보고한다.

## 디렉터리 구조

```
project-root/
├── app/
│   ├── __init__.py
│   ├── models/
│   │   └── __init__.py
│   ├── views/
│   │   └── __init__.py
│   └── controllers/
│       └── __init__.py
├── config.py
├── main.py
└── requirements.txt
```

## 파일별 내용

### `app/__init__.py`

```python
```

(빈 파일)

### `app/models/__init__.py`

```python
class BaseModel:
    pass
```

### `app/views/__init__.py`

```python
class BaseView:
    pass
```

### `app/controllers/__init__.py`

```python
class BaseController:
    pass
```

### `config.py`

```python
class Config:
    pass
```

### `main.py`

```python
def main():
    pass


if __name__ == "__main__":
    main()
```

### `requirements.txt`

(빈 파일)

## 주의 사항

- 동작하는 예제 코드(Hello World 등)는 포함하지 않는다. 각 파일은 다음 확장을
  위한 최소한의 뼈대만 제공한다.
- 프로젝트에 이미 `pyproject.toml` 등 다른 패키지 관리 방식이 있다면
  `requirements.txt` 생성 여부를 사용자에게 먼저 확인한다.
- 이 Skill은 파일을 직접 생성(Write)하는 순수 지시문 기반으로 동작하며, 별도의
  실행 스크립트에 의존하지 않는다.
