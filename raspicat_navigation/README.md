# raspicat_navigation

Raspberry Pi Cat で Nav2 によるナビゲーションを行うためのパッケージです。
launch ファイルは `launch/`、地図は `config/map/`、パラメータは `config/param/`、ウェイポイントは `config/waypoint/` にあります。

## 使える launch ファイル

いずれも `ros2 launch raspicat_navigation <launch ファイル>` で起動します。

### 地図ごとのラッパー（`template.launch.py` を呼び出す）

地図・パラメータ・GNSS の有無がファイル内で固定されているので、引数なしで起動できます。
**コマンドラインから引数を渡しても反映されません**。変更したいときはファイルを直接編集してください。

| launch | 地図（`config/map/`） | パラメータ | GNSS（`gnss2map`） |
|---|---|---|---|
| `tsudanuma_2_19.launch.py` | `tsudanuma_2_19` | `nav2.param.yaml` | 使わない |
| `tsudanuma_campus.launch.py` | `tsudanuma_campus` | `nav2.param.yaml` / `tsudanuma_gnss2map.param.yaml` | 使う |
| `tsukuba.launch.py` | `tsukuba` | `nav2.param.yaml` / `tsukuba_gnss2map.param.yaml` | 使う |
| `tsukuba_full.launch.py` | `tsukuba_full` | `nav2.param.yaml` / `tsukuba_gnss2map.param.yaml` | 使う |

```bash
ros2 launch raspicat_navigation tsudanuma_2_19.launch.py
```

### 自己位置推定用とナビゲーション用で地図を分けるもの（emcl2）

`loc_map`（自己位置推定用）と `nav_map`（経路計画用）を別々の `map_server` で配信します。

| launch | 既定の地図 | パラメータ | 備考 |
|---|---|---|---|
| `2sep_emcl2_raspicat_nav2.launch.py` | `tsudanuma_2_19` | `sep_emcl2_nav2.param.yaml` | `map:=<地図名>` で `config/map/` 内の地図を切り替えられる |
| `sep_emcl2_raspicat_nav2.launch.py` | `tsudanuma_2_19` | `sep_emcl2_nav2.param.yaml` | |
| `exp_219.launch.py` | `tsudanuma_2_19` | `exp_219.param.yaml` | 実験用 |
| `exp_campus.launch.py` | `tsudanuma_campus` | `exp_campus.param.yaml` | 実験用。`gnss2map` / `wall_tracking_executor` も起動 |

```bash
# 地図名で切り替え（tsudanuma_2_19 / tsudanuma_campus / tsukuba_full など）
ros2 launch raspicat_navigation 2sep_emcl2_raspicat_nav2.launch.py map:=tsudanuma_campus

# 地図ファイルを直接指定
ros2 launch raspicat_navigation sep_emcl2_raspicat_nav2.launch.py \
  loc_map:=/path/to/loc_map.yaml nav_map:=/path/to/nav_map.yaml
```

### 地図が 1 枚のもの

| launch | 自己位置推定 | 既定の地図 | パラメータ |
|---|---|---|---|
| `emcl2_raspicat_nav2.launch.py` | emcl2 | `tsudanuma_2_19` | `emcl2_nav2.param.yaml` |
| `amcl_raspciat_nav2.launch.py` | AMCL | `tsudanuma_2_19` | `amcl_nav2.param.yaml` |

`amcl_raspciat_nav2` はファイル名の綴りが "raspciat" になっています。

```bash
ros2 launch raspicat_navigation emcl2_raspicat_nav2.launch.py map:=$HOME/map.yaml
```

### シミュレーション（Gazebo）

既定の地図は `raspicat_slam` パッケージの `config/maps/iscas_museum_map.yaml`（Gazebo の iscas_museum ワールド用）です。

| launch | 自己位置推定 | パラメータ |
|---|---|---|
| `sim_nav2.launch.py` | AMCL | `sim_nav2.param.yaml` |
| `raspicat_nav2_sim_emcl2.launch.py` | emcl2 | `nav2_emcl2_sim.param.yaml` |
| `sim_nav2_emcl2.launch.py` | emcl2 | `sim_nav2_emcl2.param.yaml` |

どれも `use_sim_time` の既定値は `true` です（RViz にも渡しています）。Gazebo はシミュレーション時刻で動くので、`false` にすると TF の時刻がずれてゴールが aborted になります。

```bash
ros2 launch raspicat_gazebo raspicat_with_iscas_museum.launch.py
ros2 launch raspicat_navigation sim_nav2.launch.py                 # AMCL 版
# ros2 launch raspicat_navigation raspicat_nav2_sim_emcl2.launch.py  # emcl2 版
ros2 service call /motor_power std_srvs/SetBool '{data: true}'
```

- AMCL 版は、RViz の「2D Pose Estimate」で初期位置を入れるまで Nav2 が active になりません（パネルのボタンも押せません）。
- モータを有効化しないと、ロボットが動かず `Failed to make progress` で中断されます。
- `raspicat_nav2_emcl2.launch.py` も同じ地図を既定で使いますが、`use_sim_time` の既定値が `False` の emcl2 版です（パラメータは `emcl2.param.yaml`）。

### センサー

| launch | 内容 |
|---|---|
| `livox_2d.launch.py` | Livox MID360 を起動し、点群を LaserScan に変換 |
| `livox_dual_2d.launch.py` | Livox MID360 を起動し、点群を 2 本の LaserScan に変換（`pointcloud_to_dual_laserscan`） |

### 共通の引数

ラッパー以外の launch では次の引数が使えます。

| 引数 | 既定値 | 内容 |
|---|---|---|
| `use_sim_time` | `False`（sim 用は `true`） | シミュレーション時刻を使う |
| `use_rviz` | `true` | RViz を起動する |
| `params_file` | （launch ごと） | Nav2 のパラメータファイル |
| `use_composition` | `False` | コンポーザブルノードで起動する |
| `autostart` | `True` | ライフサイクルノードを自動で有効化する |
| `log_level` | `info` | ログレベル |

## そのままでは使えない launch ファイル

| launch | 理由 | 対処 |
|---|---|---|
| `template.launch.py` | ラッパーから呼ばれる土台で、地図・パラメータの既定値が空 | `loc_map` / `nav_map` / `nav2_params_file`（GNSS を使うなら `gnss2map_params_file`）を指定する |

## ライフサイクルマネージャについて

RViz の Nav2 パネルは、`lifecycle_manager_navigation` が active になるまでボタンを有効にしません。launch でライフサイクルマネージャを起動するときは、次の2点を守ってください（`test/test_launch_files.py` で確認しています）。

- ナビゲーション用のマネージャの名前を `lifecycle_manager_navigation` にする。
- `lifecycle_manager_localization` も使う場合、2つのマネージャで同じノードを管理しない（地図サーバと AMCL は localization 側、それ以外は navigation 側）。同じノードを両方で管理すると起動時に取り合いになり、どちらかがランダムに失敗します。

## テスト

```bash
colcon build --symlink-install --packages-select raspicat_navigation
colcon test --packages-select raspicat_navigation
colcon test-result --verbose
```

launch ファイルが参照する地図・パラメータが存在するか、マネージャの名前と管理対象、sim 用 launch の `use_sim_time` を確認します。
