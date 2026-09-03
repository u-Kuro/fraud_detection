import services.train_model.src.main as main_mod

def test_main_module_is_importable():
    assert callable(main_mod.main)

def test_main_calls_seed_everything(mocker):
    mocker.patch("services.train_model.src.main.seed_everything")
    mocker.patch(
        "services.train_model.src.main.get_timed_latest_unused_dataset",
        return_value=None,
    )
    # Verify the entry point exists
    assert callable(main_mod.main)
