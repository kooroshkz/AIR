# Contributing

We welcome contributions to the AIR Plugin! Follow these steps:

## 1️⃣ Fork & Clone
```bash
git clone https://github.com/johk3/AIR.git
cd AIR
```

## 2️⃣ Setup Development Environment
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e .[dev]
```

## 3️⃣ Coding Guidelines
- Follow **PEP 8** style guide.
- Write **docstrings** for functions.
- Run `pylint` to check formatting.
- Write tests for new features.
- Update documentation.
- Keep commits atomic.
- Make sure the pipeline checks pass.

## 4️⃣ Writing Tests
Always make sure to run the tests after your changes. Only push code which passes all of the tests.
```bash
# Running the tests
pytest
```
For more details, see the `tests/` folder. If you create new code which does not have any tests, create the tests for your components by placing your tests file in the tests folder. The name of your test file should be test_thenameofthecomponentyoucreated.

## 5️⃣ Submitting a PR
- Keep commits **small** and **clear**.
- Describe your changes in **pull requests**.
