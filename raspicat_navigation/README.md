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

| launch | 自己位置推定 | パラメータ | `use_sim_time` の既定値 |
|---|---|---|---|
| `raspicat_nav2_sim_emcl2.launch.py` | emcl2 | `nav2_emcl2_sim.param.yaml` | `false` |
| `sim_nav2.launch.py` | AMCL | `sim_nav2.param.yaml` | `False` |
| `sim_nav2_emcl2.launch.py` | emcl2 | `sim_nav2_emcl2.param.yaml` | `True` |

launch 側でパラメータファイルの `use_sim_time` を引数の値で上書きしているので、既定値が `false` のものは `use_sim_time:=true` を付けて起動してください。

```bash
ros2 launch raspicat_gazebo raspicat_with_iscas_museum.launch.py
ros2 launch raspicat_navigation raspicat_nav2_sim_emcl2.launch.py use_sim_time:=true
ros2 service call /motor_power std_srvs/SetBool '{data: true}'
```

`raspicat_nav2_emcl2.launch.py` も同じ地図を既定で使いますが、`use_sim_time` の既定値が `False` の emcl2 版です（パラメータは `emcl2.param.yaml`）。

### センサー

| launch | 内容 |
|---|---|
| `livox_2d.launch.py` | Livox MID360 を起動し、点群を LaserScan に変換 |
| `livox_dual_2d.launch.py` | Livox MID360 を起動し、点群を 2 本の LaserScan に変換（`pointcloud_to_dual_laserscan`） |

### 共通の引数

ラッパー以外の launch では次の引数が使えます。

| 引数 | 既定値 | 内容 |
|---|---|---|
| `use_sim_time` | `False` | シミュレーション時刻を使う |
| `use_rviz` | `true` | RViz を起動する |
| `params_file` | （launch ごと） | Nav2 のパラメータファイル |
| `use_composition` | `False` | コンポーザブルノードで起動する |
| `autostart` | `True` | ライフサイクルノードを自動で有効化する |
| `log_level` | `info` | ログレベル |

## そのままでは使えない launch ファイル

| launch | 理由 | 対処 |
|---|---|---|
| `tsukuba.launch.py` | 参照している `map_tsukuba_loc_2410271328.yaml` / `map_tsukuba_nav_2410271328.yaml` が存在しない | ファイル内のパスを `config/map/tsukuba/` 内の `map_tsukuba.yaml` に直す |
| `template.launch.py` | ラッパーから呼ばれる土台で、地図・パラメータの既定値が空 | `loc_map` / `nav_map` / `nav2_params_file`（GNSS を使うなら `gnss2map_params_file`）を指定する |
