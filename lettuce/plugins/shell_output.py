# -*- coding: utf-8 -*-
# <Lettuce - Behaviour Driven Development for python>
# Copyright (C) <2010>  Gabriel Falcão <gabriel@nacaolivre.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERsteps.pyCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import re
import os
import sys
from lettuce import strings
from lettuce.terrain import after
from lettuce.terrain import before

def wrt(what):
    sys.stdout.write(what)

@before.each_step
def print_step_running(step):
    wrt(step.represent_string(step.original_sentence))
    if step.hashes:
        wrt(step.represent_hashes())

@after.each_step
def print_step_ran(step):
    if step.scenario.outlines:
        return

    if step.hashes:
        wrt("\033[A" * (len(step.hashes) + 1))

    if step.defined_at:
        wrt("\033[A" + step.represent_string(step.original_sentence))

    else:
        wrt(step.represent_string(step.original_sentence).rstrip() + " (undefined)\n")

    if step.hashes:
        wrt(step.represent_hashes())

    if step.failed:
        print_spaced = lambda x: wrt("%s%s\n" % (" " * step.indentation, x))

        for line in step.why.traceback.splitlines():
            print_spaced(line)

@before.each_scenario
def print_scenario_running(scenario):
    wrt(scenario.represented())

@after.outline
def print_outline(scenario, order, outline, reasons_to_fail):
    table = strings.dicts_to_string(scenario.outlines, scenario.keys)
    lines = table.splitlines()
    head = lines.pop(0)

    wline = lambda x: wrt("%s%s\n" % (" " * scenario.table_indentation, x))
    if order is 0:
        wrt("\n")
        wrt("%sExamples:\n" % (" " * scenario.indentation))
        wline(head)

    line = lines[order]
    wline(line)
    if reasons_to_fail:
        print_spaced = lambda x: wrt("%s%s\n" % (" " * scenario.table_indentation, x))
        elines = reasons_to_fail[0].traceback.splitlines()
        for line in elines:
            print_spaced(line)

@before.each_feature
def print_feature_running(feature):
    wrt("\n")
    wrt(feature.represented())
    wrt("\n")

@after.all
def print_end(total):
    wrt("\n")
    word = total.features_ran > 1 and "features" or "feature"
    wrt("%d %s (%d passed)\n" % (
        total.features_ran,
        word,
        total.features_passed
        )
    )

    word = total.scenarios_ran > 1 and "scenarios" or "scenario"
    wrt("%d %s (%d passed)\n" % (
        total.scenarios_ran,
        word,
        total.scenarios_passed
        )
    )

    steps_details = []
    for kind in ("failed","skipped",  "undefined"):
        attr = 'steps_%s' % kind
        stotal = getattr(total, attr)
        if stotal:
            steps_details.append(
                "%d %s" % (stotal, kind)
            )

    steps_details.append("%d passed" % total.steps_passed)
    word = total.steps > 1 and "steps" or "step"
    wrt("%d %s (%s)\n" % (
        total.steps,
        word,
        ", ".join(steps_details)
        )
    )

    if total.proposed_definitions:
        wrt("\nYou can implement step definitions for undefined steps with these snippets:\n\n")
        wrt("from lettuce import step\n\n")
        for step in total.proposed_definitions:
            method_name = "_".join(re.findall("\w+", step.original_sentence)).lower()
            wrt("@step(r'%s')\n" % re.escape(step.original_sentence).replace(r'\ ', ' '))
            wrt("def %s(step):\n" % method_name)
            wrt("    pass\n")

def print_no_features_found(where):
    where = os.path.relpath(where)
    if not where.startswith(os.sep):
        where = '.%s%s' % (os.sep, where)

    wrt('Oops!\n')
    wrt(
        'could not find features at '
        '%s\n' % where
    )

