#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import unittest
import json
import argparse
import logging
import shutil
from pathlib import Path
from datetime import datetime

# ログディレクトリの作成
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)

# run_testsログ用のサブディレクトリを作成
run_tests_log_dir = os.path.join(log_dir, 'run_tests')
os.makedirs(run_tests_log_dir, exist_ok=True)

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(run_tests_log_dir, f"test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"))
    ]
)
logger = logging.getLogger(__name__)

def clean_test_output_directory():
    """テスト出力ディレクトリを削除して再作成する関数"""
    output_dir = os.path.join(os.path.dirname(__file__), 'output')
    images_dir = os.path.join(output_dir, 'images')

    try:
        # 画像ディレクトリが存在する場合は削除
        if os.path.exists(images_dir):
            logger.info(f"以前のテスト画像を削除しています: {images_dir}")
            shutil.rmtree(images_dir)
            logger.info("以前のテスト画像を削除しました")

        # 出力ディレクトリを作成（存在しない場合）
        os.makedirs(images_dir, exist_ok=True)
        logger.info(f"テスト出力ディレクトリを作成しました: {images_dir}")

        return True
    except Exception as e:
        logger.error(f"テスト出力ディレクトリのクリーンアップ中にエラーが発生しました: {e}")
        return False

def run_tests(pattern=None, style=None, category=None, subcategory=None, model=None, model_checkpoint=None, generate_report=True, clean_output=True, run_all=False, failfast=False, test_files=None):
    """
    テストを実行する関数

    Args:
        pattern (str, optional): 実行するテストパターンの名前
        style (str, optional): 実行するテストのスタイル（realistic/illustration）
        category (str, optional): 実行するテストのカテゴリー（female/male/animal等）
        subcategory (str, optional): 実行するテストのサブカテゴリー（normal/selfie/transparent等）
        model (str, optional): 実行するテストのモデル（brav6/brav7等）
        model_checkpoint (str, optional): 使用するモデルチェックポイントファイル名（例: RPGIcon.safetensors）
        generate_report (bool, optional): テスト結果のレポートを生成するかどうか
        clean_output (bool, optional): テスト実行前に以前のテスト出力を削除するかどうか
        run_all (bool, optional): 全てのテストを実行するかどうか
        failfast (bool, optional): テストが失敗した時点で実行を中止するかどうか
        test_files (list, optional): 実行する特定のテストファイル名のリスト

    Returns:
        bool: テストが成功したかどうか
    """
    # テスト出力ディレクトリをクリーンアップ
    if clean_output:
        if not clean_test_output_directory():
            logger.warning("テスト出力ディレクトリのクリーンアップに失敗しました。テストは続行されます。")

    # 既存の一時設定ファイルを削除
    temp_settings_file = os.path.join(os.path.dirname(__file__), 'temp_test_settings.json')
    try:
        if os.path.exists(temp_settings_file):
            os.remove(temp_settings_file)
            logger.info("既存の一時設定ファイルを削除しました")
    except Exception as e:
        logger.warning(f"既存の一時設定ファイルの削除中にエラーが発生しました: {e}")

    # テスト設定を読み込む
    try:
        with open(os.path.join(os.path.dirname(__file__), 'test_settings.json'), 'r', encoding='utf-8') as f:
            settings = json.load(f)
    except FileNotFoundError:
        logger.error("テスト設定ファイルが見つかりません。")
        return False

    # テストパターンのフィルタリング
    original_patterns = settings["test_patterns"]
    filtered_patterns = original_patterns.copy()

    # パターン名でフィルタリング
    if pattern:
        filtered_patterns = [p for p in filtered_patterns if p["name"] == pattern]

    # スタイルでフィルタリング
    if style:
        filtered_patterns = [p for p in filtered_patterns if p["style"] == style]

    # カテゴリーでフィルタリング
    if category:
        filtered_patterns = [p for p in filtered_patterns if p["category"] == category]

    # サブカテゴリーでフィルタリング
    if subcategory:
        filtered_patterns = [p for p in filtered_patterns if p["subcategory"] == subcategory]

    # モデルでフィルタリング
    if model:
        filtered_patterns = [p for p in filtered_patterns if p["model"] == model]

    if not filtered_patterns:
        logger.error(f"指定された条件に一致するテストパターンが見つかりません。")
        logger.info(f"利用可能なパターン: {[p['name'] for p in original_patterns]}")
        return False

    # モデルチェックポイントが指定されている場合、全てのパターンに適用
    if model_checkpoint:
        for pattern in filtered_patterns:
            pattern["model_checkpoint"] = model_checkpoint
        logger.info(f"モデルチェックポイントを指定: {model_checkpoint}")

    # フィルタリングされたパターンを設定に適用
    settings["test_patterns"] = filtered_patterns

    # テスト設定を一時ファイルに保存
    temp_settings_file = os.path.join(os.path.dirname(__file__), 'temp_test_settings.json')
    with open(temp_settings_file, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)

    # テストを実行
    logger.info(f"テストを開始します... ({len(filtered_patterns)}個のパターンをテスト)")

    # テストディレクトリをPythonパスに追加
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

    # テストスイートを作成
    suite = unittest.TestSuite()

    if test_files:
        # 特定のテストファイルのみを実行
        logger.info(f"指定されたテストファイルのみを実行します: {test_files}")
        test_loader = unittest.TestLoader()

        for test_file in test_files:
            # ファイル名からモジュール名を取得（拡張子を除去）
            if test_file.endswith('.py'):
                test_module = test_file[:-3]
            else:
                test_module = test_file

            try:
                # モジュールをインポート
                module = __import__(test_module, fromlist=[''])
                # モジュール内のテストを検出して追加
                tests = test_loader.loadTestsFromModule(module)
                suite.addTests(tests)
                logger.info(f"テストモジュール {test_module} を追加しました")
            except (ImportError, AttributeError) as e:
                logger.warning(f"テストモジュール {test_module} の追加に失敗しました: {e}")
    elif run_all:
        # 全てのテストを実行
        logger.info("全てのテストを実行します")

        # テストディスカバリーを使用して全てのテストを検出
        test_loader = unittest.TestLoader()
        test_dir = os.path.dirname(__file__)
        discovered_tests = test_loader.discover(test_dir, pattern="test_*.py")
        suite.addTests(discovered_tests)

        # 明示的に各テストファイルを追加する方法は使用しない（重複を避けるため）
        # テストディスカバリーで十分にテストが検出されるはず
        logger.info("テストディスカバリーを使用してテストを検出しました")
    else:
        # 特定のテストのみ実行
        from test_image_generation import TestImageGeneration
        suite.addTest(unittest.makeSuite(TestImageGeneration))

    # テストを実行
    runner = unittest.TextTestRunner(verbosity=2, failfast=failfast)
    result = runner.run(suite)

    # テスト結果を取得
    success = result.wasSuccessful()

    if success:
        logger.info("すべてのテストが成功しました。")
    else:
        logger.error("テストが失敗しました。")

    # テスト結果のレポートを生成
    if generate_report:
        # テスト結果の詳細情報を収集
        test_results = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'success': success,
            'total_tests': result.testsRun,
            'failures': len(result.failures),
            'errors': len(result.errors),
            'skipped': len(result.skipped) if hasattr(result, 'skipped') else 0,
            'test_details': []
        }

        # 失敗したテストの詳細を追加
        for test, traceback in result.failures:
            test_results['test_details'].append({
                'test_name': str(test),
                'status': 'failure',
                'traceback': traceback
            })

        # エラーが発生したテストの詳細を追加
        for test, traceback in result.errors:
            test_results['test_details'].append({
                'test_name': str(test),
                'status': 'error',
                'traceback': traceback
            })

        # スキップされたテストの詳細を追加（存在する場合）
        if hasattr(result, 'skipped'):
            for test, reason in result.skipped:
                test_results['test_details'].append({
                    'test_name': str(test),
                    'status': 'skipped',
                    'reason': reason
                })

        # 成功したテストの詳細を追加
        for test in result.successes if hasattr(result, 'successes') else []:
            test_results['test_details'].append({
                'test_name': str(test),
                'status': 'success'
            })

        # テスト結果をJSONファイルに保存
        output_dir = os.path.join(os.path.dirname(__file__), 'output')
        os.makedirs(output_dir, exist_ok=True)

        with open(os.path.join(output_dir, 'test_results_summary.json'), 'w', encoding='utf-8') as f:
            json.dump(test_results, f, indent=4, ensure_ascii=False)

        # 既存のテスト結果ファイルも使用してレポートを生成
        generate_test_report(test_results)

    # 一時設定ファイルを削除
    try:
        if os.path.exists(temp_settings_file):
            os.remove(temp_settings_file)
            logger.info("一時設定ファイルを削除しました")
    except Exception as e:
        logger.warning(f"一時設定ファイルの削除中にエラーが発生しました: {e}")

    return success

def generate_test_report(test_results_summary=None):
    """
    テスト結果のレポートを生成する関数

    Args:
        test_results_summary (dict, optional): テスト実行の概要結果

    Returns:
        str: 生成されたレポートファイルのパス
    """
    try:
        # テスト結果の概要を取得
        if test_results_summary is None:
            try:
                with open(os.path.join(os.path.dirname(__file__), 'output', 'test_results_summary.json'), 'r', encoding='utf-8') as f:
                    test_results_summary = json.load(f)
            except FileNotFoundError:
                logger.warning("テスト結果の概要ファイルが見つかりません。")
                test_results_summary = {
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'success': False,
                    'total_tests': 0,
                    'failures': 0,
                    'errors': 0,
                    'skipped': 0,
                    'test_details': []
                }

        # 詳細なテスト結果を取得（存在する場合）
        detailed_results = []
        try:
            with open(os.path.join(os.path.dirname(__file__), 'output', 'test_results.json'), 'r', encoding='utf-8') as f:
                detailed_results = json.load(f)
        except FileNotFoundError:
            logger.warning("詳細なテスト結果ファイルが見つかりません。")

        # レポートディレクトリを作成
        report_dir = Path(os.path.join(os.path.dirname(__file__), 'reports'))
        report_dir.mkdir(parents=True, exist_ok=True)

        # レポートファイル名を生成
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        report_file = report_dir / f"test_report_{timestamp}.html"

        # HTMLレポートを生成
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>AutoImageGenerator テスト結果</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1, h2, h3, h4 {{ color: #333; }}
        .summary {{ margin: 20px 0; padding: 10px; background-color: #f5f5f5; border-radius: 5px; }}
        .test-case {{ margin: 10px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .success {{ background-color: #dff0d8; }}
        .failure {{ background-color: #f2dede; }}
        .error {{ background-color: #fcf8e3; }}
        .skipped {{ background-color: #d9edf7; }}
        .details {{ margin-top: 10px; }}
        .validation-section {{ margin: 15px 0; padding: 10px; background-color: #f9f9f9; border-radius: 5px; }}
        .validation-item {{ margin: 5px 0; }}
        .seed-folder {{ margin: 10px 0; padding: 10px; border: 1px solid #eee; border-radius: 5px; }}
        .seed-folder-success {{ background-color: #dff0d8; }}
        .seed-folder-failure {{ background-color: #f2dede; }}
        .file-validation {{ margin-left: 20px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .valid {{ color: green; }}
        .invalid {{ color: red; }}
        .toggle-button {{ cursor: pointer; padding: 5px; background-color: #f0f0f0; border-radius: 3px; display: inline-block; }}
        .hidden {{ display: none; }}
        pre {{ background-color: #f8f8f8; padding: 10px; border-radius: 5px; overflow-x: auto; }}
    </style>
    <script>
        function toggleDetails(id) {{
            var element = document.getElementById(id);
            if (element.classList.contains('hidden')) {{
                element.classList.remove('hidden');
            }} else {{
                element.classList.add('hidden');
            }}
        }}
    </script>
</head>
<body>
    <h1>AutoImageGenerator テスト結果</h1>
    <div class="summary">
        <p><strong>実行日時:</strong> {test_results_summary['timestamp']}</p>
        <p><strong>テスト数:</strong> {test_results_summary['total_tests']}</p>
        <p><strong>成功数:</strong> {test_results_summary['total_tests'] - test_results_summary['failures'] - test_results_summary['errors'] - test_results_summary['skipped']}</p>
        <p><strong>失敗数:</strong> {test_results_summary['failures']}</p>
        <p><strong>エラー数:</strong> {test_results_summary['errors']}</p>
        <p><strong>スキップ数:</strong> {test_results_summary['skipped']}</p>
        <p><strong>全体結果:</strong> <span class="{'valid' if test_results_summary['success'] else 'invalid'}">{batch_status_text(test_results_summary['success'])}</span></p>
    </div>

    <h2>テスト詳細</h2>
""")

            # テスト詳細の表示
            if test_results_summary['test_details']:
                for i, test_detail in enumerate(test_results_summary['test_details']):
                    status = test_detail['status']
                    status_class = {
                        'success': 'success',
                        'failure': 'failure',
                        'error': 'error',
                        'skipped': 'skipped'
                    }.get(status, '')

                    f.write(f"""
    <div class="test-case {status_class}">
        <h3>{test_detail['test_name']} - {status}</h3>
""")

                    if status == 'failure' or status == 'error':
                        f.write(f"""
        <div class="toggle-button" onclick="toggleDetails('traceback-{i}')">トレースバックを表示/非表示</div>
        <div id="traceback-{i}" class="hidden">
            <pre>{test_detail['traceback']}</pre>
        </div>
""")
                    elif status == 'skipped':
                        f.write(f"""
        <p><strong>スキップ理由:</strong> {test_detail['reason']}</p>
""")

                    f.write("""
    </div>
""")

            # 詳細なテスト結果の表示（存在する場合）
            if detailed_results:
                f.write("""
    <h2>パターン別テスト結果</h2>
""")

                if isinstance(detailed_results, dict) and 'results' in detailed_results:
                    results = detailed_results['results']
                else:
                    results = detailed_results

                for i, result in enumerate(results):
                    status_class = "success" if result.get('success', False) else "failure"
                    status_text = "成功" if result.get('success', False) else "失敗"

                    f.write(f"""
    <div class="test-case {status_class}">
        <h3>{result.get('pattern', f'テスト {i+1}')} - {status_text}</h3>
        <div class="details">
            <p><strong>開始時間:</strong> {result.get('start_time', 'N/A')}</p>
            <p><strong>終了時間:</strong> {result.get('end_time', 'N/A')}</p>
            <p><strong>実行時間:</strong> {result.get('elapsed_time', 0):.2f}秒</p>
""")

                    if result.get('success', False):
                        f.write(f"""
            <p><strong>出力パス:</strong> {result.get('output_path', 'N/A')}</p>
""")
                    else:
                        f.write(f"""
            <p><strong>エラー:</strong> {result.get('error', 'N/A')}</p>
""")

                    # 検証結果の詳細を表示
                    if 'validation_results' in result:
                        validation_results = result['validation_results']

                        # バッチ数の検証結果
                        if 'batch_count_valid' in validation_results:
                            batch_count_valid = validation_results['batch_count_valid']
                            expected_batch_count = validation_results['expected_batch_count']
                            actual_batch_count = validation_results['actual_batch_count']

                            batch_status = "valid" if batch_count_valid else "invalid"

                            f.write(f"""
            <div class="validation-section">
                <h4>バッチ数検証</h4>
                <div class="validation-item">
                    <p><strong>期待値:</strong> {expected_batch_count}</p>
                    <p><strong>実際の値:</strong> {actual_batch_count}</p>
                    <p><strong>結果:</strong> <span class="{batch_status}">{batch_status_text(batch_count_valid)}</span></p>
                </div>
            </div>
""")

                        # バージョン検証の結果
                        if 'version_validation' in validation_results:
                            version_validation = validation_results['version_validation']
                            all_versions_valid = validation_results.get('all_versions_valid', False)

                            f.write(f"""
            <div class="validation-section">
                <h4>バージョン検証</h4>
                <p><strong>全体結果:</strong> <span class="{'valid' if all_versions_valid else 'invalid'}">{batch_status_text(all_versions_valid)}</span></p>

                <div class="toggle-button" onclick="toggleDetails('version-details-{i}')">詳細を表示/非表示</div>
                <div id="version-details-{i}" class="hidden">
""")

                            # 各シードフォルダの検証結果
                            for j, version_result in enumerate(version_validation):
                                seed_folder = version_result['seed_folder']
                                all_valid = version_result['all_valid']
                                seed_status_class = "seed-folder-success" if all_valid else "seed-folder-failure"

                                f.write(f"""
                    <div class="seed-folder {seed_status_class}">
                        <h5>シードフォルダ: {seed_folder}</h5>
                        <p><strong>結果:</strong> <span class="{'valid' if all_valid else 'invalid'}">{batch_status_text(all_valid)}</span></p>

                        <div class="toggle-button" onclick="toggleDetails('seed-details-{i}-{j}')">詳細を表示/非表示</div>
                        <div id="seed-details-{i}-{j}" class="hidden">
""")

                                # ファイル検証の詳細
                                files_validation = version_result['files_validation']
                                for location, validation in files_validation.items():
                                    f.write(f"""
                            <div class="file-validation">
                                <h6>{location}</h6>
""")

                                    if 'error' in validation:
                                        f.write(f"""
                                <p class="invalid">{validation['error']}</p>
""")
                                    else:
                                        for file_type, file_validation in validation.items():
                                            if isinstance(file_validation, dict) and 'expected' in file_validation:
                                                expected = file_validation['expected']
                                                actual = file_validation['actual']
                                                valid = file_validation['valid']
                                                file_status = "valid" if valid else "invalid"

                                                f.write(f"""
                                <p><strong>{file_type}ファイル:</strong> 期待値={expected}, 実際={actual}, 結果=<span class="{file_status}">{batch_status_text(valid)}</span></p>
""")

                                f.write("""
                            </div>
""")

                                f.write("""
                        </div>
                    </div>
""")

                            f.write("""
                </div>
            </div>
""")

                    f.write("""
        </div>
    </div>
""")

            f.write("""
</body>
</html>
""")

        logger.info(f"テスト結果レポートを生成しました: {report_file}")
        return str(report_file)

    except Exception as e:
        logger.exception(f"レポート生成中にエラーが発生しました: {e}")
        return None

def batch_status_text(is_valid):
    """検証結果のテキストを返す"""
    return "成功" if is_valid else "失敗"

def list_test_patterns():
    """利用可能なテストパターンを一覧表示する関数"""
    try:
        with open(os.path.join(os.path.dirname(__file__), 'test_settings.json'), 'r', encoding='utf-8') as f:
            settings = json.load(f)

        patterns = settings.get("test_patterns", [])

        if not patterns:
            logger.info("テストパターンが定義されていません。")
            return []

        logger.info("利用可能なテストパターン:")
        for i, pattern in enumerate(patterns, 1):
            logger.info(f"{i}. {pattern['name']} - {pattern['style']}/{pattern['category']}/{pattern['subcategory']} (モデル: {pattern['model']})")

        # スタイル、カテゴリー、サブカテゴリー、モデルの一覧を表示
        styles = sorted(set(p["style"] for p in patterns))
        categories = sorted(set(p["category"] for p in patterns))
        subcategories = sorted(set(p["subcategory"] for p in patterns))
        models = sorted(set(p["model"] for p in patterns))

        logger.info("\n利用可能なスタイル:")
        for style in styles:
            logger.info(f"- {style}")

        logger.info("\n利用可能なカテゴリー:")
        for category in categories:
            logger.info(f"- {category}")

        logger.info("\n利用可能なサブカテゴリー:")
        for subcategory in subcategories:
            logger.info(f"- {subcategory}")

        logger.info("\n利用可能なモデル:")
        for model in models:
            logger.info(f"- {model}")

        return [p["name"] for p in patterns]

    except FileNotFoundError:
        logger.error("テスト設定ファイルが見つかりません。")
        return []
    except Exception as e:
        logger.exception(f"テストパターンの一覧表示中にエラーが発生しました: {e}")
        return []

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='AutoImageGenerator テスト実行スクリプト')
    parser.add_argument('--pattern', help='実行するテストパターンの名前')
    parser.add_argument('--style', help='実行するテストのスタイル（realistic/illustration）')
    parser.add_argument('--category', help='実行するテストのカテゴリー（female/male/animal等）')
    parser.add_argument('--subcategory', help='実行するテストのサブカテゴリー（normal/selfie/transparent等）')
    parser.add_argument('--model', help='実行するテストのモデル（brav6/brav7等）')
    parser.add_argument('--model-checkpoint', help='使用するモデルチェックポイントファイル名（例: RPGIcon.safetensors）')
    parser.add_argument('--list', action='store_true', help='利用可能なテストパターンを一覧表示')
    parser.add_argument('--no-report', action='store_true', help='テスト結果のレポートを生成しない')
    parser.add_argument('--no-clean', action='store_true', help='テスト実行前に以前のテスト出力を削除しない')
    parser.add_argument('--run-all', action='store_true', help='全てのテストを実行する')
    parser.add_argument('--failfast', action='store_true', help='テストが失敗した時点で実行を中止する')
    parser.add_argument('--test-files', nargs='+', help='実行する特定のテストファイル名のリスト（例: test_image_save test_image_generation）')

    args = parser.parse_args()

    if args.list:
        list_test_patterns()
    else:
        success = run_tests(
            pattern=args.pattern,
            style=args.style,
            category=args.category,
            subcategory=args.subcategory,
            model=args.model,
            model_checkpoint=args.model_checkpoint,
            generate_report=not args.no_report,
            clean_output=not args.no_clean,
            run_all=args.run_all,
            failfast=args.failfast,
            test_files=args.test_files
        )
        sys.exit(0 if success else 1)