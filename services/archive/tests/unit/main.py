def test_main_calls_archive_transaction_inferences(mocker):
    mock_archive = mocker.patch("services.archive.src.main.archive_transaction_inferences")
    from services.archive.src.main import main
    main()
    mock_archive.assert_called_once()

def test_main_module_is_importable():
    import services.archive.src.main as m
    assert callable(m.main)
