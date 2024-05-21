from __future__ import annotations

import os
from glob import glob

import click
import importlib_resources
from tutor import config, hooks

from .__about__ import __version__
from .commands import newrelic

########################################
# CONFIGURATION
########################################

hooks.Filters.CONFIG_DEFAULTS.add_items(
    [
        # Add your new settings that have default values here.
        # Each new setting is a pair: (setting_name, default_value).
        # Prefix your setting names with 'NEWRELIC_'.
        ("NEWRELIC_VERSION", __version__),
        ("NEWRELIC_NAME", "{{ K8S_NAMESPACE }}"),
        ("NEWRELIC_API_KEY", ""),
        ("NEWRELIC_ACCOUNT_ID", ""),
        ("NEWRELIC_REGION_CODE", ""),
        ("NEWRELIC_MONITORING_PERIOD", "EVERY_5_MINUTES"),
        ("NEWRELIC_MONITORING_LOCATION", "US_EAST_1"),
        # NEWRELIC_SYNTHETICS_MONITORS
        # [
        #   {
        #       recipient: "email@example.com",
        #       urls: [
        #           "https://courses.example.com/heartbeat",
        #           "https://courses.example.com/heartbeat?extended",
        #       ]
        #   }
        # ]
        ("NEWRELIC_SYNTHETICS_MONITORS", []),
    ]
)

hooks.Filters.CONFIG_UNIQUE.add_items(
    [
        # Add settings that don't have a reasonable default for all users here.
        # For instance: passwords, secret keys, etc.
        # Each new setting is a pair: (setting_name, unique_generated_value).
        # Prefix your setting names with 'NEWRELIC_'.
        # For example:
        ### ("NEWRELIC_SECRET_KEY", "{{ 24|random_string }}"),
    ]
)

hooks.Filters.CONFIG_OVERRIDES.add_items(
    [
        # Danger zone!
        # Add values to override settings from Tutor core or other plugins here.
        # Each override is a pair: (setting_name, new_value). For example:
        ### ("PLATFORM_NAME", "My platform"),
    ]
)

########################################
# INITIALIZATION TASKS
########################################

# To add a custom initialization task, create a bash script template under:
# tutornewrelic/templates/newrelic/tasks/
# and then add it to the MY_INIT_TASKS list. Each task is in the format:
# ("<service>", ("<path>", "<to>", "<script>", "<template>"))
MY_INIT_TASKS: list[tuple[str, tuple[str, ...]]] = [
    # For example, to add LMS initialization steps, you could add the script template at:
    # tutornewrelic/templates/newrelic/tasks/lms/init.sh
    # And then add the line:
    ### ("lms", ("newrelic", "tasks", "lms", "init.sh")),
]

# For each task added to MY_INIT_TASKS, we load the task template
# and add it to the CLI_DO_INIT_TASKS filter, which tells Tutor to
# run it as part of the `init` job.
for service, template_path in MY_INIT_TASKS:
    full_path: str = str(
        importlib_resources.files("tutornewrelic")
        / os.path.join("templates", *template_path)
    )
    with open(full_path, encoding="utf-8") as init_task_file:
        init_task: str = init_task_file.read()
    hooks.Filters.CLI_DO_INIT_TASKS.add_item((service, init_task))

########################################
# DOCKER IMAGE MANAGEMENT
########################################

# Images to be built by `tutor images build`.
# Each item is a quadruple in the form:
#     ("<tutor_image_name>", ("path", "to", "build", "dir"), "<docker_image_tag>", "<build_args>")
hooks.Filters.IMAGES_BUILD.add_items(
    [
        # To build `myimage` with `tutor images build myimage`,
        # you would add a Dockerfile to templates/newrelic/build/myimage,
        # and then write:
        ### (
        ###     "myimage",
        ###     ("plugins", "newrelic", "build", "myimage"),
        ###     "docker.io/myimage:{{ NEWRELIC_VERSION }}",
        ###     (),
        ### ),
    ]
)

# Images to be pulled as part of `tutor images pull`.
# Each item is a pair in the form:
#     ("<tutor_image_name>", "<docker_image_tag>")
hooks.Filters.IMAGES_PULL.add_items(
    [
        # To pull `myimage` with `tutor images pull myimage`, you would write:
        ### (
        ###     "myimage",
        ###     "docker.io/myimage:{{ NEWRELIC_VERSION }}",
        ### ),
    ]
)

# Images to be pushed as part of `tutor images push`.
# Each item is a pair in the form:
#     ("<tutor_image_name>", "<docker_image_tag>")
hooks.Filters.IMAGES_PUSH.add_items(
    [
        # To push `myimage` with `tutor images push myimage`, you would write:
        ### (
        ###     "myimage",
        ###     "docker.io/myimage:{{ NEWRELIC_VERSION }}",
        ### ),
    ]
)

########################################
# TEMPLATE RENDERING
# (It is safe & recommended to leave
#  this section as-is :)
########################################

hooks.Filters.ENV_TEMPLATE_ROOTS.add_items(
    # Root paths for template files, relative to the project root.
    [
        str(importlib_resources.files("tutornewrelic") / "templates"),
    ]
)

hooks.Filters.ENV_TEMPLATE_TARGETS.add_items(
    # For each pair (source_path, destination_path):
    # templates at ``source_path`` (relative to your ENV_TEMPLATE_ROOTS) will be
    # rendered to ``source_path/destination_path`` (relative to your Tutor environment).
    # For example, ``tutornewrelic/templates/newrelic/build``
    # will be rendered to ``$(tutor config printroot)/env/plugins/newrelic/build``.
    [
        ("newrelic/build", "plugins"),
        ("newrelic/apps", "plugins"),
    ],
)

########################################
# PATCH LOADING
# (It is safe & recommended to leave
#  this section as-is :)
########################################

# For each file in tutornewrelic/patches,
# apply a patch based on the file's name and contents.
for path in glob(str(importlib_resources.files("tutornewrelic") / "patches" / "*")):
    with open(path, encoding="utf-8") as patch_file:
        hooks.Filters.ENV_PATCHES.add_item((os.path.basename(path), patch_file.read()))

########################################
# CUSTOM JOBS (a.k.a. "do-commands")
########################################

#######################################
# CUSTOM CLI COMMANDS
#######################################

hooks.Filters.CLI_COMMANDS.add_item(newrelic)
