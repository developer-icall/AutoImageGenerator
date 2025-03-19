import unittest
import os
import json
import shutil
from unittest.mock import MagicMock, patch, mock_open
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auto_image_generator import AutoImageGenerator


class TestLoraBikeGeneration(unittest.TestCase):

    def setUp(self):
        """テストの前準備"""
        # 一時的な設定ファイルを作成
        self.test_settings = {
            "image_generate_batch_execute_count": 1,
            "another_version_generate_count": 1,
            "default_image_sizes": {
                "realistic": {
                    "vehicle": {"width": 768, "height": 512}
                },
                "illustration": {
                    "vehicle": {"width": 768, "height": 512}
                }
            }
        }

        # モックデータ
        self.mock_json_data = "{}"

        # 一時的な出力、入力ディレクトリを作成
        os.makedirs("temp_output", exist_ok=True)
        os.makedirs("temp_input", exist_ok=True)
        os.makedirs("temp_prompts", exist_ok=True)

        # AutoImageGeneratorクラスのインスタンス作成用の引数
        self.test_args = {
            "image_generate_batch_execute_count": 1,
            "another_version_generate_count": 1,
            "input_folder": "temp_input",
            "output_folder": "temp_output",
            "prompts_folder": "temp_prompts",
            "sd_model_checkpoint": "sd_xl_base_1.0.safetensors",
            "sd_model_prefix": "sd_xl_base_1.0",
            "enable_hr": False,
            "style": "realistic",
            "category": "vehicle",
            "subcategory": "motorcycle",
            "use_custom_checkpoint": True,
            "width": 768,
            "height": 512
        }

    def tearDown(self):
        """テスト終了後のクリーンアップ"""
        # 一時ディレクトリの削除
        if os.path.exists("temp_output"):
            shutil.rmtree("temp_output")
        if os.path.exists("temp_input"):
            shutil.rmtree("temp_input")
        if os.path.exists("temp_prompts"):
            shutil.rmtree("temp_prompts")

    @patch('builtins.open', new_callable=mock_open, read_data='{"test": []}')
    @patch('auto_image_generator.AutoImageGenerator._load_settings')
    @patch('auto_image_generator.AutoImageGenerator.set_model')
    @patch('auto_image_generator.AutoImageGenerator._generate_single_image')
    @patch('auto_image_generator.AutoImageGenerator._create_prompts')
    @patch('auto_image_generator.AutoImageGenerator._get_prompt_folder_path')
    @patch('auto_image_generator.os.path.exists')
    @patch('auto_image_generator.json.load')
    def test_kawasaki_ninja_lora_setup(self, mock_json_load, mock_path_exists, mock_get_prompt_folder_path, mock_create_prompts, mock_generate_single_image, mock_set_model, mock_load_settings, mock_open_file):
        """KawasakiNinja300 LoRAが正しく設定されるかをテスト"""
        # モックの設定
        mock_load_settings.return_value = self.test_settings
        mock_set_model.return_value = True
        mock_get_prompt_folder_path.return_value = "mocked_path"
        mock_path_exists.return_value = True
        mock_json_load.return_value = {}
        mock_create_prompts.return_value = (
            "test positive prompt",
            "test negative prompt",
            12345,
            {"reusable_base_prompts": [], "reusable_base_prompt_dict": {}, "seed": 12345}
        )

        # LoRAを有効にした状態でインスタンスを作成
        args = self.test_args.copy()
        args.update({
            "use_lora": True,
            "lora_name": "KawasakiNinja300"
        })

        with patch('main.LORA_SETTINGS', {
            "KawasakiNinja300": {
                "model": "sd_xl_base_1.0",
                "weight": 0.8,
                "trigger_word": "kawasaki ninja 300, motorcycle, realistic"
            }
        }):
            generator = AutoImageGenerator(**args)

            # ファイル読み込みエラーを避けるためにダミーデータを設定
            generator.DATA_POSITIVE_BASE = {}
            generator.DATA_POSITIVE_POSE = {}
            generator.DATA_POSITIVE_OPTIONAL = {}
            generator.DATA_NEGATIVE = {}
            generator.DATA_CANCEL_SEEDS = {"Seeds": []}

            # _generate_imagesメソッドを実行
            generator._generate_images(1, 1)

            # _generate_single_imageが呼ばれたことを確認
            mock_generate_single_image.assert_called_once()

            # _generate_single_imageが呼ばれた際のpayloadを取得
            call_args = mock_generate_single_image.call_args[0]
            payload = call_args[0]

            # LoRAの設定が正しく含まれているか確認
            self.assertIn("alwayson_scripts", payload)
            self.assertIn("Additional Networks for Generating", payload["alwayson_scripts"])

            lora_args = payload["alwayson_scripts"]["Additional Networks for Generating"]["args"]
            self.assertEqual(lora_args[0], True)  # enabled
            self.assertEqual(lora_args[1], "LoRA")  # type
            self.assertEqual(lora_args[2][0][0], "KawasakiNinja300.safetensors")  # model name
            self.assertEqual(lora_args[2][0][1], 0.8)  # weight

    @patch('builtins.open', new_callable=mock_open, read_data='{"test": []}')
    @patch('auto_image_generator.AutoImageGenerator._load_settings')
    @patch('auto_image_generator.AutoImageGenerator.set_model')
    @patch('auto_image_generator.AutoImageGenerator._generate_single_image')
    @patch('auto_image_generator.AutoImageGenerator._create_prompts')
    @patch('auto_image_generator.AutoImageGenerator._get_prompt_folder_path')
    @patch('auto_image_generator.os.path.exists')
    @patch('auto_image_generator.json.load')
    def test_waifu_motorcycle_lora_setup(self, mock_json_load, mock_path_exists, mock_get_prompt_folder_path, mock_create_prompts, mock_generate_single_image, mock_set_model, mock_load_settings, mock_open_file):
        """waifu_on_Motorcycle_v2 LoRAが正しく設定されるかをテスト"""
        # モックの設定
        mock_load_settings.return_value = self.test_settings
        mock_set_model.return_value = True
        mock_get_prompt_folder_path.return_value = "mocked_path"
        mock_path_exists.return_value = True
        mock_json_load.return_value = {}
        mock_create_prompts.return_value = (
            "test positive prompt",
            "test negative prompt",
            12345,
            {"reusable_base_prompts": [], "reusable_base_prompt_dict": {}, "seed": 12345}
        )

        # LoRAを有効にした状態でインスタンスを作成
        args = self.test_args.copy()
        args.update({
            "style": "illustration",
            "use_lora": True,
            "lora_name": "waifu_on_Motorcycle_v2"
        })

        with patch('main.LORA_SETTINGS', {
            "waifu_on_Motorcycle_v2": {
                "model": "sd_xl_base_1.0",
                "weight": 0.7,
                "trigger_word": "waifu on motorcycle, illustration, anime style"
            }
        }):
            generator = AutoImageGenerator(**args)

            # ファイル読み込みエラーを避けるためにダミーデータを設定
            generator.DATA_POSITIVE_BASE = {}
            generator.DATA_POSITIVE_POSE = {}
            generator.DATA_POSITIVE_OPTIONAL = {}
            generator.DATA_NEGATIVE = {}
            generator.DATA_CANCEL_SEEDS = {"Seeds": []}

            # _generate_imagesメソッドを実行
            generator._generate_images(1, 1)

            # _generate_single_imageが呼ばれたことを確認
            mock_generate_single_image.assert_called_once()

            # _generate_single_imageが呼ばれた際のpayloadを取得
            call_args = mock_generate_single_image.call_args[0]
            payload = call_args[0]

            # LoRAの設定が正しく含まれているか確認
            self.assertIn("alwayson_scripts", payload)
            self.assertIn("Additional Networks for Generating", payload["alwayson_scripts"])

            lora_args = payload["alwayson_scripts"]["Additional Networks for Generating"]["args"]
            self.assertEqual(lora_args[0], True)  # enabled
            self.assertEqual(lora_args[1], "LoRA")  # type
            self.assertEqual(lora_args[2][0][0], "waifu_on_Motorcycle_v2.safetensors")  # model name
            self.assertEqual(lora_args[2][0][1], 0.7)  # weight

    @patch('builtins.open', new_callable=mock_open, read_data='{"test": []}')
    @patch('auto_image_generator.AutoImageGenerator._load_settings')
    @patch('auto_image_generator.AutoImageGenerator.set_model')
    @patch('auto_image_generator.AutoImageGenerator._generate_single_image')
    @patch('auto_image_generator.AutoImageGenerator._create_prompts')
    @patch('auto_image_generator.AutoImageGenerator._get_prompt_folder_path')
    @patch('auto_image_generator.os.path.exists')
    @patch('auto_image_generator.json.load')
    def test_cybervehicle_lora_setup(self, mock_json_load, mock_path_exists, mock_get_prompt_folder_path, mock_create_prompts, mock_generate_single_image, mock_set_model, mock_load_settings, mock_open_file):
        """cybervehiclev4 LoRAが正しく設定されるかをテスト"""
        # モックの設定
        mock_load_settings.return_value = self.test_settings
        mock_set_model.return_value = True
        mock_get_prompt_folder_path.return_value = "mocked_path"
        mock_path_exists.return_value = True
        mock_json_load.return_value = {}
        mock_create_prompts.return_value = (
            "test positive prompt",
            "test negative prompt",
            12345,
            {"reusable_base_prompts": [], "reusable_base_prompt_dict": {}, "seed": 12345}
        )

        # LoRAを有効にした状態でインスタンスを作成
        args = self.test_args.copy()
        args.update({
            "use_lora": True,
            "lora_name": "cybervehiclev4"
        })

        with patch('main.LORA_SETTINGS', {
            "cybervehiclev4": {
                "model": "sd_xl_base_1.0",
                "weight": 0.75,
                "trigger_word": "cyberpunk vehicle, futuristic motorcycle"
            }
        }):
            generator = AutoImageGenerator(**args)

            # ファイル読み込みエラーを避けるためにダミーデータを設定
            generator.DATA_POSITIVE_BASE = {}
            generator.DATA_POSITIVE_POSE = {}
            generator.DATA_POSITIVE_OPTIONAL = {}
            generator.DATA_NEGATIVE = {}
            generator.DATA_CANCEL_SEEDS = {"Seeds": []}

            # _generate_imagesメソッドを実行
            generator._generate_images(1, 1)

            # _generate_single_imageが呼ばれたことを確認
            mock_generate_single_image.assert_called_once()

            # _generate_single_imageが呼ばれた際のpayloadを取得
            call_args = mock_generate_single_image.call_args[0]
            payload = call_args[0]

            # LoRAの設定が正しく含まれているか確認
            self.assertIn("alwayson_scripts", payload)
            self.assertIn("Additional Networks for Generating", payload["alwayson_scripts"])

            lora_args = payload["alwayson_scripts"]["Additional Networks for Generating"]["args"]
            self.assertEqual(lora_args[0], True)  # enabled
            self.assertEqual(lora_args[1], "LoRA")  # type
            self.assertEqual(lora_args[2][0][0], "cybervehiclev4.safetensors")  # model name
            self.assertEqual(lora_args[2][0][1], 0.75)  # weight


if __name__ == '__main__':
    unittest.main()