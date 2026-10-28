# Copyright 2026 Junya Wada
# SPDX-License-Identifier: Apache-2.0
"""
Static checks for the launch files of raspicat_navigation.

Run with `colcon test --packages-select raspicat_navigation` after building, since the
launch files look up package share directories through the ament index.
"""

import os
import re
from pathlib import Path

from ament_index_python.packages import PackageNotFoundError
from launch import LaunchContext
from launch.actions import DeclareLaunchArgument, GroupAction, IncludeLaunchDescription
from launch.launch_description_sources import get_launch_description_from_python_launch_file
from launch.utilities import normalize_to_list_of_substitutions, perform_substitutions
import pytest

LAUNCH_DIR = Path(__file__).resolve().parent.parent / 'launch'
LAUNCH_FILES = sorted(LAUNCH_DIR.glob('*.launch.py'))
# template.launch.py has empty defaults on purpose and is only used through the wrappers.
TEMPLATE = 'template.launch.py'


def _load(path):
    try:
        return get_launch_description_from_python_launch_file(str(path))
    except (PackageNotFoundError, LookupError) as e:
        # e.g. livox_ros_driver2 is not installed on this machine
        pytest.skip(f'{path.name}: dependency not found ({e})')


def _walk(entities):
    for entity in entities:
        yield entity
        if isinstance(entity, GroupAction):
            yield from _walk(entity.get_sub_entities())


def _file_arguments(path):
    """Yield (name, value) of launch arguments that point to a file."""
    description = _load(path)
    context = LaunchContext()
    for entity in _walk(description.entities):
        if isinstance(entity, DeclareLaunchArgument):
            # Visiting sets the default as the configuration, so later defaults that refer
            # to earlier arguments (e.g. `map` in 2sep_emcl2_raspicat_nav2) resolve too.
            entity.visit(context)
            if entity.default_value is None:
                continue
            value = perform_substitutions(context, entity.default_value)
            yield entity.name, value
        elif isinstance(entity, IncludeLaunchDescription):
            for name, value in entity.launch_arguments:
                yield name, perform_substitutions(
                    context, normalize_to_list_of_substitutions(value))


@pytest.mark.parametrize(
    'path', [p for p in LAUNCH_FILES if p.name != TEMPLATE], ids=lambda p: p.name)
def test_default_files_exist(path):
    missing = [
        f'{name}: {value}' for name, value in _file_arguments(path)
        if value.endswith(('.yaml', '.rviz')) and not os.path.isfile(value)
    ]
    assert not missing, 'files referenced by default do not exist:\n' + '\n'.join(missing)


def _code_lines(path):
    return [line for line in path.read_text().splitlines() if not line.lstrip().startswith('#')]


@pytest.mark.parametrize('path', LAUNCH_FILES, ids=lambda p: p.name)
def test_navigation_lifecycle_manager_name(path):
    """Check the name the Nav2 RViz panel waits for before enabling its buttons."""
    code = '\n'.join(_code_lines(path))
    if "'nav2_lifecycle_manager'" not in code:
        pytest.skip('no lifecycle manager')
    names = set(re.findall(r"name='(lifecycle_manager[a-z_]*)'", code))
    assert 'lifecycle_manager_navigation' in names, (
        f'found {sorted(names)}; the Nav2 panel waits for lifecycle_manager_navigation')


def _managed_nodes(code):
    """Return {manager name: [node names]} by resolving the `node_names` list variables."""
    lists = {
        name: re.findall(r"'(\w+)'", body)
        for name, body in re.findall(r'(lifecycle_nodes\w*)\s*=\s*\[(.*?)\]', code, re.S)
    }
    managers = {}
    for block in re.split(r'\b(?:Node|ComposableNode)\(', code):
        name = re.search(r"name='(lifecycle_manager\w*)'", block)
        var = re.search(r"'node_names':\s*(\w+)", block)
        if name and var:
            managers.setdefault(name.group(1), lists.get(var.group(1), []))
    return managers


@pytest.mark.parametrize('path', LAUNCH_FILES, ids=lambda p: p.name)
def test_lifecycle_managers_do_not_share_nodes(path):
    """Two managers configuring the same node race each other and one of them fails."""
    managers = _managed_nodes('\n'.join(_code_lines(path)))
    if len(managers) < 2:
        pytest.skip('single lifecycle manager')
    seen = {}
    for manager, nodes in managers.items():
        for node in nodes:
            assert node not in seen, f'{node} is managed by both {seen[node]} and {manager}'
            seen[node] = manager


SIM_LAUNCH_FILES = [p for p in LAUNCH_FILES if 'sim' in p.name]


@pytest.mark.parametrize('path', SIM_LAUNCH_FILES, ids=lambda p: p.name)
def test_sim_launch_uses_sim_time(path):
    """Gazebo publishes simulation time, so every node (RViz too) must follow /clock."""
    defaults = dict(_file_arguments(path))
    assert defaults.get('use_sim_time', '').lower() == 'true'
    code = '\n'.join(_code_lines(path))
    rviz = re.search(r'Node\(\s*package=.rviz2.(.*?)\)\n', code, re.S)
    assert rviz and "'use_sim_time': use_sim_time" in rviz.group(1), (
        'pass use_sim_time to rviz2, or 2D Pose Estimate / Nav2 Goal are stamped with wall time')
