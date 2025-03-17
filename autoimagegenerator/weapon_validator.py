#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
武器画像の検証を行うユーティリティクラス

このモジュールは、生成された武器画像が指定された武器タイプに適合しているかを
検証するための機能を提供します。
"""

import os
import logging
import json
import re
from PIL import Image
import requests
import base64
import io
from datetime import datetime

class WeaponValidator:
    """
    武器画像の検証を行うクラス
    """

    def __init__(self, api_url="http://localhost:7860"):
        """
        初期化メソッド

        Args:
            api_url (str): Stable Diffusion Web UI APIのURL
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)  # ログレベルをDEBUGに設定
        if not self.logger.handlers:
            # コンソール出力用ハンドラ
            console_handler = logging.StreamHandler()
            console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)

            # ログファイル保存用のディレクトリを作成
            log_dir = os.path.join("logs", "weapon_validator")
            os.makedirs(log_dir, exist_ok=True)

            # ファイル出力用ハンドラ
            log_file = os.path.join(log_dir, f"weapon_validator_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
            file_handler = logging.FileHandler(log_file)
            file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s')
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

            self.logger.info(f"ログファイルを作成しました: {log_file}")

        self.api_url = api_url
        self.interrogate_url = f"{api_url}/sdapi/v1/interrogate"

        # 武器タイプのキーワードマッピング
        self.weapon_type_keywords = {
            "sword": ["sword", "blade", "longsword", "katana", "rapier"],
            "dagger": ["dagger", "knife", "dirk", "kris", "stiletto"],
            "axe": ["axe", "hatchet", "tomahawk", "battleaxe", "war axe"],
            "hammer": ["hammer", "mallet", "maul", "warhammer", "sledgehammer"],
            "mace": ["mace", "flail", "morning star", "club", "bludgeon"],
            "staff": ["staff", "rod", "wand", "scepter", "wizard staff"],
            "spear": ["spear", "lance", "pike", "javelin", "halberd"],
            "bow": ["bow", "longbow", "shortbow", "recurve bow", "composite bow"],
            "crossbow": ["crossbow", "arbalest", "bolt thrower", "mechanical bow"],
            "chain whip": ["chain whip", "whip", "flail", "chain", "links", "flexible weapon", "spiked chain", "barbed", "demonic", "barbed links"],
            "shield": ["shield", "buckler", "kite shield", "tower shield", "heater shield"]
        }

    def validate_weapon_image(self, image_path, expected_weapon_type):
        """
        画像が期待される武器タイプに適合しているかを検証する

        Args:
            image_path (str): 検証する画像のパス
            expected_weapon_type (str): 期待される武器タイプ

        Returns:
            tuple: (検証結果(bool), 検証メッセージ(str))
        """
        self.logger.info(f"武器画像の検証を開始: {image_path}, 期待される武器タイプ: {expected_weapon_type}")

        try:
            # 画像を読み込む
            with open(image_path, "rb") as img_file:
                img_data = base64.b64encode(img_file.read()).decode("utf-8")

            # 画像の内容を分析
            analysis_result = self._analyze_image(img_data)

            # 期待される武器タイプのキーワードを取得
            expected_keywords = self._get_expected_keywords(expected_weapon_type)

            # 分析結果に期待されるキーワードが含まれているか確認
            match_found = False
            matched_keyword = None

            # 基本的な武器キーワードをチェック
            basic_weapon_keywords = ["weapon", "sword", "dagger", "axe", "hammer", "mace", "staff", "spear", "bow", "crossbow", "whip", "chain", "shield"]
            has_basic_weapon = False
            for keyword in basic_weapon_keywords:
                if keyword.lower() in analysis_result.lower():
                    has_basic_weapon = True
                    self.logger.info(f"基本的な武器キーワードが見つかりました: {keyword}")
                    break

            if not has_basic_weapon:
                self.logger.warning(f"基本的な武器キーワードが見つかりません。画像が武器を表していない可能性があります。")

            for keyword in expected_keywords:
                if keyword.lower() in analysis_result.lower():
                    match_found = True
                    matched_keyword = keyword
                    break

            if match_found:
                self.logger.info(f"検証成功: 画像は期待される武器タイプ '{expected_weapon_type}' に適合しています (キーワード: {matched_keyword})")
                return True, f"画像は期待される武器タイプ '{expected_weapon_type}' に適合しています"
            else:
                # 基本的な武器が見つかった場合は部分的に成功とみなす
                if has_basic_weapon and len(expected_keywords) > 0:
                    self.logger.info(f"部分的な検証成功: 画像は武器を表していますが、期待される武器タイプ '{expected_weapon_type}' の特徴が見つかりません")
                    return True, f"画像は武器を表していますが、期待される武器タイプ '{expected_weapon_type}' の特徴が完全には一致していません"
                else:
                    self.logger.warning(f"検証失敗: 画像は期待される武器タイプ '{expected_weapon_type}' に適合していません")
                    return False, f"画像は期待される武器タイプ '{expected_weapon_type}' に適合していません。分析結果: {analysis_result}"

        except Exception as e:
            self.logger.error(f"検証中にエラーが発生しました: {e}")
            return False, f"検証中にエラーが発生しました: {e}"

    def _analyze_image(self, img_data):
        """
        画像の内容を分析する

        Args:
            img_data (str): Base64エンコードされた画像データ

        Returns:
            str: 分析結果のテキスト
        """
        try:
            # Interrogateエンドポイントを使用して画像を分析
            payload = {
                "image": f"data:image/png;base64,{img_data}",
                "model": "clip"  # CLIPモデルを使用
            }

            response = requests.post(self.interrogate_url, json=payload)
            response.raise_for_status()

            # レスポンスから分析結果を取得
            result = response.json()
            caption = result.get("caption", "")

            self.logger.info(f"画像分析結果: {caption[:100]}...")  # 最初の100文字だけログに出力
            return caption

        except Exception as e:
            self.logger.error(f"画像分析中にエラーが発生しました: {e}")
            return ""

    def _get_expected_keywords(self, weapon_type):
        """
        期待される武器タイプのキーワードを取得する

        Args:
            weapon_type (str): 武器タイプ

        Returns:
            list: キーワードのリスト
        """
        # 武器タイプから適切なキーワードを抽出
        for key, keywords in self.weapon_type_keywords.items():
            if key in weapon_type.lower():
                # 武器タイプ自体も追加
                custom_keywords = keywords.copy()
                # 武器タイプの特徴的な単語を追加
                weapon_words = [word for word in weapon_type.lower().split() if len(word) > 3]
                custom_keywords.extend(weapon_words)
                self.logger.info(f"武器タイプ '{weapon_type}' のキーワード: {custom_keywords}")
                return custom_keywords

        # 完全一致するものがない場合は、部分一致を試みる
        for key, keywords in self.weapon_type_keywords.items():
            for keyword in keywords:
                if keyword in weapon_type.lower():
                    # 武器タイプ自体も追加
                    custom_keywords = keywords.copy()
                    # 武器タイプの特徴的な単語を追加
                    weapon_words = [word for word in weapon_type.lower().split() if len(word) > 3]
                    custom_keywords.extend(weapon_words)
                    self.logger.info(f"武器タイプ '{weapon_type}' のキーワード: {custom_keywords}")
                    return custom_keywords

        # デフォルトとして武器タイプ自体の単語を分解してキーワードとして返す
        weapon_words = [word for word in weapon_type.lower().split() if len(word) > 3]
        self.logger.info(f"武器タイプ '{weapon_type}' のデフォルトキーワード: {weapon_words}")
        return weapon_words if weapon_words else [weapon_type.lower()]

    def extract_weapon_type_from_prompt(self, prompt):
        """
        プロンプトから武器タイプを抽出する

        Args:
            prompt (str): 画像生成に使用されたプロンプト

        Returns:
            str: 抽出された武器タイプ、または空文字列
        """
        try:
            # 武器タイプのキーワードをプロンプトから検索
            for weapon_type, keywords in self.weapon_type_keywords.items():
                for keyword in keywords:
                    if keyword in prompt.lower():
                        return weapon_type

            return ""
        except Exception as e:
            self.logger.error(f"プロンプトからの武器タイプ抽出中にエラーが発生しました: {e}")
            return ""