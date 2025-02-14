# Contributing

We welcome contributions to the AIR Plugin! Here's how you can help:

## Development Setup

1. Fork the repository
2. Clone your fork
3. Install dependencies
4. Create a branch
5. Make changes
6. Submit PR

## Guidelines

- Follow PEP 8 style guide
- Write tests for new features
- Update documentation
- Keep commits atomic
- Make sure the pipeline checks pass


## Testing
Always make sure to run the tests after your changes. Only push code which passes all of the tests.
```bash
# Running the tests
pytest
```

If you create new code which does not have any tests, create the tests for your components by placing your tests file in the tests folder. 
The name of your test file should be test_thenameofthecomponentyoucreated.
