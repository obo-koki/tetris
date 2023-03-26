# tetris/evaluation

* tetris 開発用の自動評価環境（評価ソフト）

# DEMO

Comming soon...

# Features

* シナリオはエクセル(loop_exec_option.xlsx)で指定。
* SEEDや時間などのオプションを自在に設定可能
* Gitのbranch/tag毎に実行可能。
* ローカル／リモート どちらのレポジトリも可能。

# Requirement

* test環境：Windows10 + python 3.9 + VSCode
* https://github.com/seigot/tetris （2022年7月6日）が動作すること

# Installation

ルールベース
```pwrsh
pip install pyqt5
pip install numpy
```
ＡＩ
```pwrsh
pip install torch torchvision torchaudio
pip install omegaconf
pip install hydra-core --upgrade
pip install tensorboardX
```
に加えて、
以下、追加で必要
```pwrsh
pip install pandas
pip install openpyxl
```

# Usage

以下の手続きでevaluationフォルダだけ持ってこれるはず

ベースのクローン（自分のクローンで良い。例はseigotさん）
```pwrsh
git clone https://github.com/seigot/tetris.git
```
cloneしたフォルダに移動
```pwrsh
cd tetris
```
isshy-youのtetris/evaluation だけを持ってくる
```pwrsh
git remote add isshy-you https://github.com/isshy-you/tetris.git
```
```pwrsh
git fetch isshy-you
```
最新版に更新(evaluatonのみ)(通常はこれ)
```pwrsh
git checkout isshy-you/feature/evaluation ./evaluation/
```
最新版に不具合があったら、安定版のつもりのリリースタグで更新(evaluatonのみ)
```pwrsh
git checkout eva_220813 ./evaluation/
```

評価リストを編集（Libre Office 可）
./evaluation/loop_exec_option.xlsx

評価ソフトを実行
```pwrsh
python ./evaluation/loop_exec.py
```

result/ に結果が生成される。(*.log , *.json)

result/result.csv に *.json をまとめた CSV を生成して終了

最後に以下のプログラムを実行している。

いつでも使用可能。今ある result/*.json すべてを集計。
```pwrsh
python ./evaluation/read_result.py
```

# Note

* Git操作をしますので自分のWorking内での作業は危険ですのでご注意ください

# Author

ISHIKAWA Yuichi

isshy@kit.hi-ho.ne.jp

# License

under [MIT license](https://en.wikipedia.org/wiki/MIT_License).

