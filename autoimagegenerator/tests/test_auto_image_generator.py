from autoimagegenerator.auto_image_generator import AutoImageGenerator

def test_weapon_validation():
    """武器検証機能のテスト"""
    # 武器検証を有効にしたケース
    generator_with_validation = AutoImageGenerator(
        style="illustration",
        category="rpg_icon",
        subcategory="weapon",
        enable_weapon_validation=True
    )
    assert generator_with_validation.enable_weapon_validation is True
    assert generator_with_validation.weapon_validator is not None

    # 武器検証を無効にしたケース
    generator_without_validation = AutoImageGenerator(
        style="illustration",
        category="rpg_icon",
        subcategory="weapon",
        enable_weapon_validation=False
    )
    assert generator_without_validation.enable_weapon_validation is False
    assert generator_without_validation.weapon_validator is None

    # 武器以外のカテゴリで武器検証を有効にしたケース
    generator_non_weapon = AutoImageGenerator(
        style="illustration",
        category="rpg_icon",
        subcategory="monster",
        enable_weapon_validation=True
    )
    assert generator_non_weapon.enable_weapon_validation is True
    assert generator_non_weapon.weapon_validator is not None