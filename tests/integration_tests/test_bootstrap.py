from epicevent.bootstrap import ApplicationFactory


def test_application_factory_create(session):
    factory = ApplicationFactory(lambda: session)

    with factory.create() as app:
        assert app is not None
        assert app.auth is not None
